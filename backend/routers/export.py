from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
import crud, models
from io import BytesIO
import json

router = APIRouter(prefix="/api/export", tags=["export"])


def _build_excel(db: Session, snapshot_data=None):
    import xlsxwriter

    output = BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})

    # Formats
    header_fmt = wb.add_format({
        "bold": True, "bg_color": "#1e3a5f", "font_color": "white",
        "border": 1, "align": "center", "valign": "vcenter", "text_wrap": True
    })
    cell_fmt = wb.add_format({"border": 1, "valign": "vcenter", "text_wrap": True})
    pct_fmt = wb.add_format({"border": 1, "num_format": "0.0%", "valign": "vcenter"})
    num_fmt = wb.add_format({"border": 1, "num_format": "#,##0.00", "valign": "vcenter"})

    if snapshot_data:
        objectives = snapshot_data.get("objectives", [])
        indicators = snapshot_data.get("indicators", [])
        milestones = snapshot_data.get("milestones", [])
        periodo = snapshot_data.get("periodo", "")
    else:
        objectives_db = db.query(models.Objective).all()
        indicators_db = db.query(models.Indicator).all()
        milestones_db = db.query(models.Milestone).all()
        stats_map = {
            o.id_objetivo: crud.get_objective_stats(db, o.id_objetivo)
            for o in objectives_db
        }
        objectives = [
            {
                "id_objetivo": o.id_objetivo,
                "objetivo_institucional": o.objetivo_institucional,
                "objetivo_anual": o.objetivo_anual,
                "lineamiento": o.lineamiento,
                "tipo_objetivo": o.tipo_objetivo,
                "unidades_organizacionales": o.unidades_organizacionales,
                "n_indicadores": stats_map[o.id_objetivo]["n_indicadores"],
                "avance_promedio_pct": stats_map[o.id_objetivo]["avance_promedio_pct"],
            }
            for o in objectives_db
        ]
        indicators = [
            {
                "id_indicador": i.id_indicador,
                "id_objetivo": i.id_objetivo,
                "indicador": i.indicador,
                "unidad_organizacional": i.unidad_organizacional,
                "division_area": i.division_area,
                "lineamiento": i.lineamiento,
                "tipo_objetivo": i.tipo_objetivo,
                "clasificacion": i.clasificacion,
                "unidad_medida": i.unidad_medida,
                "meta": i.meta,
                "avance_valor": i.avance_valor,
                "avance_pct": i.avance_pct,
                "estado": i.estado,
                "tiene_hitos": i.tiene_hitos,
                "fecha_inicio": i.fecha_inicio,
                "fecha_fin_original": i.fecha_fin_original,
                "fecha_fin_actual": i.fecha_fin_actual,
                "notas": i.notas,
            }
            for i in indicators_db
        ]
        milestones = [
            {
                "id_hito": m.id_hito,
                "id_indicador": m.id_indicador,
                "nombre_hito": m.nombre_hito,
                "orden": m.orden,
                "estado": m.estado,
                "avance_pct": m.avance_pct,
                "fecha_inicio": m.fecha_inicio,
                "fecha_fin_original": m.fecha_fin_original,
                "fecha_fin_actual": m.fecha_fin_actual,
            }
            for m in milestones_db
        ]
        periodo = "Actual"

    # ── Objectives sheet ──
    ws_obj = wb.add_worksheet("Objetivos")
    obj_headers = ["ID_Objetivo", "Objetivo_Institucional", "Objetivo_Anual", "Lineamiento",
                   "Tipo_Objetivo", "Unidades_Organizacionales", "N_Indicadores", "Avance_Promedio_Pct"]
    obj_widths = [12, 40, 40, 25, 18, 25, 15, 20]
    ws_obj.set_row(0, 30)
    for col, (h, w) in enumerate(zip(obj_headers, obj_widths)):
        ws_obj.write(0, col, h, header_fmt)
        ws_obj.set_column(col, col, w)
    for row, o in enumerate(objectives, 1):
        ws_obj.write(row, 0, o.get("id_objetivo"), cell_fmt)
        ws_obj.write(row, 1, o.get("objetivo_institucional"), cell_fmt)
        ws_obj.write(row, 2, o.get("objetivo_anual"), cell_fmt)
        ws_obj.write(row, 3, o.get("lineamiento"), cell_fmt)
        ws_obj.write(row, 4, o.get("tipo_objetivo"), cell_fmt)
        ws_obj.write(row, 5, o.get("unidades_organizacionales"), cell_fmt)
        ws_obj.write(row, 6, o.get("n_indicadores", 0), num_fmt)
        avp = (o.get("avance_promedio_pct") or 0) / 100
        ws_obj.write(row, 7, avp, pct_fmt)

    # ── Indicators sheet ──
    ws_ind = wb.add_worksheet("Indicadores")
    ind_headers = ["ID_Indicador", "ID_Objetivo", "Indicador", "Unidad_Org", "Division_Area",
                   "Lineamiento", "Tipo_Objetivo", "Clasificacion", "Unidad_Medida",
                   "Meta", "Avance_Valor", "Avance_Pct", "Estado", "Tiene_Hitos",
                   "Fecha_Inicio", "Fecha_Fin_Original", "Fecha_Fin_Actual", "Notas", "Periodo"]
    ind_widths = [14, 12, 45, 10, 20, 22, 15, 14, 14, 10, 12, 12, 15, 12, 14, 18, 15, 30, 10]
    ws_ind.set_row(0, 30)
    for col, (h, w) in enumerate(zip(ind_headers, ind_widths)):
        ws_ind.write(0, col, h, header_fmt)
        ws_ind.set_column(col, col, w)
    for row, i in enumerate(indicators, 1):
        ws_ind.write(row, 0, i.get("id_indicador"), cell_fmt)
        ws_ind.write(row, 1, i.get("id_objetivo"), cell_fmt)
        ws_ind.write(row, 2, i.get("indicador"), cell_fmt)
        ws_ind.write(row, 3, i.get("unidad_organizacional"), cell_fmt)
        ws_ind.write(row, 4, i.get("division_area"), cell_fmt)
        ws_ind.write(row, 5, i.get("lineamiento"), cell_fmt)
        ws_ind.write(row, 6, i.get("tipo_objetivo"), cell_fmt)
        ws_ind.write(row, 7, i.get("clasificacion"), cell_fmt)
        ws_ind.write(row, 8, i.get("unidad_medida"), cell_fmt)
        ws_ind.write(row, 9, i.get("meta"), num_fmt)
        ws_ind.write(row, 10, i.get("avance_valor"), num_fmt)
        avp = (i.get("avance_pct") or 0) / 100
        ws_ind.write(row, 11, avp, pct_fmt)
        ws_ind.write(row, 12, i.get("estado"), cell_fmt)
        ws_ind.write(row, 13, i.get("tiene_hitos"), cell_fmt)
        ws_ind.write(row, 14, str(i.get("fecha_inicio") or ""), cell_fmt)
        ws_ind.write(row, 15, str(i.get("fecha_fin_original") or ""), cell_fmt)
        ws_ind.write(row, 16, str(i.get("fecha_fin_actual") or ""), cell_fmt)
        ws_ind.write(row, 17, i.get("notas") or "", cell_fmt)
        ws_ind.write(row, 18, periodo, cell_fmt)

    # ── Milestones sheet ──
    ws_hit = wb.add_worksheet("Hitos")
    hit_headers = ["ID_Hito", "ID_Indicador", "Nombre_Hito", "Orden", "Estado",
                   "Avance_Pct", "Fecha_Inicio", "Fecha_Fin_Original", "Fecha_Fin_Actual", "Periodo"]
    hit_widths = [14, 14, 50, 8, 15, 12, 14, 18, 15, 10]
    ws_hit.set_row(0, 30)
    for col, (h, w) in enumerate(zip(hit_headers, hit_widths)):
        ws_hit.write(0, col, h, header_fmt)
        ws_hit.set_column(col, col, w)
    for row, m in enumerate(milestones, 1):
        ws_hit.write(row, 0, m.get("id_hito"), cell_fmt)
        ws_hit.write(row, 1, m.get("id_indicador"), cell_fmt)
        ws_hit.write(row, 2, m.get("nombre_hito"), cell_fmt)
        ws_hit.write(row, 3, m.get("orden"), cell_fmt)
        ws_hit.write(row, 4, m.get("estado"), cell_fmt)
        avp = (m.get("avance_pct") or 0) / 100
        ws_hit.write(row, 5, avp, pct_fmt)
        ws_hit.write(row, 6, str(m.get("fecha_inicio") or ""), cell_fmt)
        ws_hit.write(row, 7, str(m.get("fecha_fin_original") or ""), cell_fmt)
        ws_hit.write(row, 8, str(m.get("fecha_fin_actual") or ""), cell_fmt)
        ws_hit.write(row, 9, periodo, cell_fmt)

    # ── History sheet (only for current export) ──
    if not snapshot_data:
        history = db.query(models.ProgressHistory).order_by(
            models.ProgressHistory.fecha_actualizacion.desc()
        ).all()
        ws_hist = wb.add_worksheet("Historial")
        hist_headers = ["ID_Indicador", "Periodo", "Avance_Valor", "Avance_Pct", "Estado",
                        "Notas", "Fecha_Actualizacion"]
        hist_widths = [14, 10, 12, 12, 15, 40, 20]
        ws_hist.set_row(0, 30)
        for col, (h, w) in enumerate(zip(hist_headers, hist_widths)):
            ws_hist.write(0, col, h, header_fmt)
            ws_hist.set_column(col, col, w)
        for row, h in enumerate(history, 1):
            ws_hist.write(row, 0, h.id_indicador, cell_fmt)
            ws_hist.write(row, 1, h.periodo or "", cell_fmt)
            ws_hist.write(row, 2, h.avance_valor, num_fmt)
            avp = (h.avance_pct or 0) / 100
            ws_hist.write(row, 3, avp, pct_fmt)
            ws_hist.write(row, 4, h.estado or "", cell_fmt)
            ws_hist.write(row, 5, h.notas or "", cell_fmt)
            ws_hist.write(row, 6,
                          h.fecha_actualizacion.strftime("%Y-%m-%d %H:%M") if h.fecha_actualizacion else "",
                          cell_fmt)

    wb.close()
    output.seek(0)
    return output


@router.get("/excel")
def export_excel(db: Session = Depends(get_db)):
    from datetime import datetime
    output = _build_excel(db)
    filename = f"FONPLATA_Export_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/snapshot/{snapshot_id}/excel")
def export_snapshot_excel(snapshot_id: int, db: Session = Depends(get_db)):
    snap = crud.get_snapshot(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
    data = json.loads(snap.data_json) if snap.data_json else {}
    output = _build_excel(db, snapshot_data=data)
    filename = f"FONPLATA_Snapshot_{snap.periodo}.xlsx"
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
