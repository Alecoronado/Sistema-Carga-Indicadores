"""Run this script once to import data from the Excel file into the database."""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

EXCEL_PATH = os.path.join(os.path.dirname(__file__), "..", "FONPLATA_Modelo_Datos_2026_1.xlsx")


def clean(val):
    if val is None:
        return None
    if isinstance(val, float):
        import math
        if math.isnan(val):
            return None
        return val
    s = str(val).strip()
    return s if s and s.lower() not in ("nan", "none", "nat") else None


def clean_date(val):
    if val is None:
        return None
    import math
    if isinstance(val, float) and math.isnan(val):
        return None
    s = str(val).strip()
    if not s or s.lower() in ("nan", "none", "nat"):
        return None
    try:
        import pandas as pd
        dt = pd.to_datetime(s, errors="coerce")
        if pd.isna(dt):
            return s
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return s


def import_data():
    db = SessionLocal()
    try:
        existing_obj = db.query(models.Objective).count()
        if existing_obj > 0:
            print(f"Base de datos ya tiene {existing_obj} objetivos. Saltando importación.")
            return

        print("Importando Objetivos...")
        df_obj = pd.read_excel(EXCEL_PATH, sheet_name="Objetivos")
        for _, row in df_obj.iterrows():
            obj = models.Objective(
                id_objetivo=clean(row.get("ID_Objetivo")),
                objetivo_institucional=clean(row.get("Objetivo_Institucional")),
                objetivo_anual=clean(row.get("Objetivo_Anual")),
                lineamiento=clean(row.get("Lineamiento")),
                tipo_objetivo=clean(row.get("Tipo_Objetivo")),
                unidades_organizacionales=clean(row.get("Unidades_Organizacionales")),
            )
            if obj.id_objetivo:
                db.add(obj)
        db.commit()
        print(f"  -> {df_obj.shape[0]} objetivos importados")

        # Ensure a placeholder objective exists for indicators without an ID_Objetivo
        placeholder = db.query(models.Objective).filter(
            models.Objective.id_objetivo == "SIN_ASIGNAR"
        ).first()
        if not placeholder:
            db.add(models.Objective(
                id_objetivo="SIN_ASIGNAR",
                objetivo_institucional="Indicadores sin objetivo asignado",
                objetivo_anual="Sin asignar",
                lineamiento=None,
                tipo_objetivo=None,
                unidades_organizacionales=None,
            ))
            db.commit()

        print("Importando Indicadores...")
        df_ind = pd.read_excel(EXCEL_PATH, sheet_name="Indicadores")
        for _, row in df_ind.iterrows():
            id_ind = clean(row.get("ID_Indicador"))
            id_obj = clean(row.get("ID_Objetivo")) or "SIN_ASIGNAR"
            if not id_ind:
                continue
            obj_exists = db.query(models.Objective).filter(
                models.Objective.id_objetivo == id_obj
            ).first()
            if not obj_exists:
                print(f"  WARN: Objetivo {id_obj} no encontrado para indicador {id_ind}, asignando SIN_ASIGNAR")
                id_obj = "SIN_ASIGNAR"
            meta_val = row.get("Meta")
            avance_val = row.get("Avance_Valor", 0) or 0
            unidad = clean(row.get("Unidad_Medida"))
            try:
                meta_val = float(meta_val) if meta_val is not None and str(meta_val).strip() not in ("nan", "") else None
            except Exception:
                meta_val = None
            try:
                avance_val = float(avance_val)
            except Exception:
                avance_val = 0

            if unidad == "%":
                avance_pct = min(avance_val, 100.0)
            elif meta_val and meta_val > 0:
                avance_pct = min(round(avance_val / meta_val * 100, 2), 100.0)
            else:
                avance_pct = 0.0

            tiene_hitos = clean(row.get("Tiene_Hitos")) or "No"
            estado = clean(row.get("Estado")) or "Por Comenzar"
            if avance_pct >= 100:
                estado = "Completado"
            elif avance_pct > 0 and estado == "Por Comenzar":
                estado = "En Progreso"

            ind = models.Indicator(
                id_indicador=id_ind,
                id_objetivo=id_obj,
                unidad_organizacional=clean(row.get("Unidad_Organizacional")),
                division_area=clean(row.get("Division_Area")),
                lineamiento=clean(row.get("Lineamiento")),
                objetivo_anual=clean(row.get("Objetivo_Anual")),
                indicador=clean(row.get("Indicador")),
                acciones=clean(row.get("Acciones")),
                resultado_esperado=clean(row.get("Resultado_Esperado")),
                tipo_objetivo=clean(row.get("Tipo_Objetivo")),
                clasificacion=clean(row.get("Clasificacion")),
                unidad_medida=unidad,
                meta=meta_val,
                avance_valor=avance_val,
                avance_pct=avance_pct,
                estado=estado,
                uo_colaboradora=clean(row.get("UO_Colaboradora")),
                area_colabora=clean(row.get("Area_Colabora")),
                tiene_hitos=tiene_hitos,
                fecha_inicio=clean_date(row.get("Fecha_Inicio")),
                fecha_fin_original=clean_date(row.get("Fecha_Fin_Original")),
                fecha_fin_actual=clean_date(row.get("Fecha_Fin_Actual")),
            )
            db.add(ind)
        db.commit()
        print(f"  -> {df_ind.shape[0]} indicadores importados")

        print("Importando Hitos...")
        df_hit = pd.read_excel(EXCEL_PATH, sheet_name="Hitos")
        for _, row in df_hit.iterrows():
            id_hito = clean(row.get("ID_Hito"))
            id_ind = clean(row.get("ID_Indicador"))
            if not id_hito or not id_ind:
                continue
            avance_pct = 0
            try:
                avance_pct = float(row.get("Avance_Pct", 0) or 0)
            except Exception:
                pass
            hito = models.Milestone(
                id_hito=id_hito,
                id_indicador=id_ind,
                nombre_hito=clean(row.get("Nombre_Hito")),
                orden=int(row.get("Orden", 1)) if row.get("Orden") else 1,
                estado=clean(row.get("Estado")) or "Por Comenzar",
                avance_pct=avance_pct,
                fecha_inicio=clean_date(row.get("Fecha_Inicio")),
                fecha_fin_original=clean_date(row.get("Fecha_Fin_Original")),
                fecha_fin_actual=clean_date(row.get("Fecha_Fin_Actual")),
            )
            db.add(hito)
        db.commit()
        print(f"  -> {df_hit.shape[0]} hitos importados")

        print("\nImportacion completada exitosamente.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import_data()
