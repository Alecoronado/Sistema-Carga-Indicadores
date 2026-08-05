from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import models
import schemas
from datetime import datetime


# ── helpers ──────────────────────────────────────────────────────────────────

def _calc_avance_pct(unidad_medida: Optional[str], meta: Optional[float], avance_valor: Optional[float]) -> float:
    if avance_valor is None:
        return 0.0
    if unidad_medida == "%":
        return min(float(avance_valor), 100.0)
    if meta and meta > 0:
        return min(round(float(avance_valor) / float(meta) * 100, 2), 100.0)
    return 0.0


def _recalc_indicator_from_milestones(db: Session, indicator: models.Indicator):
    milestones = db.query(models.Milestone).filter(
        models.Milestone.id_indicador == indicator.id_indicador
    ).all()
    if milestones:
        avg = sum(m.avance_pct or 0 for m in milestones) / len(milestones)
        indicator.avance_pct = round(avg, 2)
        completed = all(m.estado == "Completado" for m in milestones)
        started = any((m.avance_pct or 0) > 0 for m in milestones)
        if completed:
            indicator.estado = "Completado"
        elif started:
            indicator.estado = "En Progreso"
    db.commit()
    db.refresh(indicator)


def _recalc_objective(db: Session, id_objetivo: str):
    indicators = db.query(models.Indicator).filter(
        models.Indicator.id_objetivo == id_objetivo
    ).all()
    # objective progress is read-only (computed on the fly in responses)
    _ = indicators


# ── Objectives ───────────────────────────────────────────────────────────────

def get_objectives(db: Session, skip: int = 0, limit: int = 200):
    return db.query(models.Objective).offset(skip).limit(limit).all()


def get_objective(db: Session, id_objetivo: str):
    return db.query(models.Objective).filter(
        models.Objective.id_objetivo == id_objetivo
    ).first()


def create_objective(db: Session, obj: schemas.ObjectiveCreate):
    db_obj = models.Objective(**obj.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_objective(db: Session, id_objetivo: str, data: schemas.ObjectiveUpdate):
    db_obj = get_objective(db, id_objetivo)
    if not db_obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_objective(db: Session, id_objetivo: str):
    db_obj = get_objective(db, id_objetivo)
    if not db_obj:
        return False
    db.delete(db_obj)
    db.commit()
    return True


def get_objective_stats(db: Session, id_objetivo: str):
    indicators = db.query(models.Indicator).filter(
        models.Indicator.id_objetivo == id_objetivo
    ).all()
    n = len(indicators)
    avg = round(sum(i.avance_pct or 0 for i in indicators) / n, 2) if n else 0
    return {"n_indicadores": n, "avance_promedio_pct": avg}


# ── Indicators ───────────────────────────────────────────────────────────────

def get_indicators(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    id_objetivo: Optional[str] = None,
    unidad_organizacional: Optional[str] = None,
    estado: Optional[str] = None,
    lineamiento: Optional[str] = None,
    clasificacion: Optional[str] = None,
    search: Optional[str] = None,
):
    q = db.query(models.Indicator)
    if id_objetivo:
        q = q.filter(models.Indicator.id_objetivo == id_objetivo)
    if unidad_organizacional:
        q = q.filter(models.Indicator.unidad_organizacional == unidad_organizacional)
    if estado:
        q = q.filter(models.Indicator.estado == estado)
    if lineamiento:
        q = q.filter(models.Indicator.lineamiento == lineamiento)
    if clasificacion:
        q = q.filter(models.Indicator.clasificacion == clasificacion)
    if search:
        q = q.filter(models.Indicator.indicador.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()


def get_indicator(db: Session, id_indicador: str):
    return db.query(models.Indicator).filter(
        models.Indicator.id_indicador == id_indicador
    ).first()


def create_indicator(db: Session, ind: schemas.IndicatorCreate):
    data = ind.model_dump()
    if data.get("tiene_hitos") == "Si":
        data["avance_pct"] = 0
    else:
        data["avance_pct"] = _calc_avance_pct(
            data.get("unidad_medida"), data.get("meta"), data.get("avance_valor")
        )
    db_ind = models.Indicator(**data)
    db.add(db_ind)
    db.commit()
    db.refresh(db_ind)
    return db_ind


def update_indicator(db: Session, id_indicador: str, data: schemas.IndicatorUpdate):
    db_ind = get_indicator(db, id_indicador)
    if not db_ind:
        return None
    updates = data.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(db_ind, field, value)
    # Recalculate avance_pct if needed
    if db_ind.tiene_hitos != "Si":
        db_ind.avance_pct = _calc_avance_pct(
            db_ind.unidad_medida, db_ind.meta, db_ind.avance_valor
        )
    db_ind.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_ind)
    return db_ind


def update_indicator_progress(db: Session, id_indicador: str, data: schemas.ProgressUpdate):
    db_ind = get_indicator(db, id_indicador)
    if not db_ind:
        return None

    old_valor = db_ind.avance_valor
    old_estado = db_ind.estado

    if data.avance_valor is not None:
        db_ind.avance_valor = data.avance_valor
        if db_ind.tiene_hitos != "Si":
            db_ind.avance_pct = _calc_avance_pct(
                db_ind.unidad_medida, db_ind.meta, data.avance_valor
            )
    if data.estado is not None:
        db_ind.estado = data.estado
    if data.notas is not None:
        db_ind.notas = data.notas
    db_ind.updated_at = datetime.utcnow()

    # Save history
    history = models.ProgressHistory(
        id_indicador=id_indicador,
        periodo=data.periodo,
        avance_valor=db_ind.avance_valor,
        avance_pct=db_ind.avance_pct,
        estado=db_ind.estado,
        notas=data.notas,
    )
    db.add(history)
    db.commit()
    db.refresh(db_ind)
    return db_ind


def delete_indicator(db: Session, id_indicador: str):
    db_ind = get_indicator(db, id_indicador)
    if not db_ind:
        return False
    db.delete(db_ind)
    db.commit()
    return True


# ── Milestones ───────────────────────────────────────────────────────────────

def get_milestones(db: Session, id_indicador: Optional[str] = None, skip: int = 0, limit: int = 1000):
    q = db.query(models.Milestone)
    if id_indicador:
        q = q.filter(models.Milestone.id_indicador == id_indicador)
    return q.order_by(models.Milestone.id_indicador, models.Milestone.orden).offset(skip).limit(limit).all()


def get_milestone(db: Session, id_hito: str):
    return db.query(models.Milestone).filter(models.Milestone.id_hito == id_hito).first()


def create_milestone(db: Session, hito: schemas.MilestoneCreate):
    db_hito = models.Milestone(**hito.model_dump())
    db.add(db_hito)
    db.commit()
    db.refresh(db_hito)
    ind = get_indicator(db, hito.id_indicador)
    if ind:
        ind.tiene_hitos = "Si"
        _recalc_indicator_from_milestones(db, ind)
    return db_hito


def update_milestone(db: Session, id_hito: str, data: schemas.MilestoneUpdate):
    db_hito = get_milestone(db, id_hito)
    if not db_hito:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_hito, field, value)
    db.commit()
    db.refresh(db_hito)
    ind = get_indicator(db, db_hito.id_indicador)
    if ind and ind.tiene_hitos == "Si":
        _recalc_indicator_from_milestones(db, ind)
    return db_hito


def delete_milestone(db: Session, id_hito: str):
    db_hito = get_milestone(db, id_hito)
    if not db_hito:
        return False
    id_indicador = db_hito.id_indicador
    db.delete(db_hito)
    db.commit()
    ind = get_indicator(db, id_indicador)
    if ind:
        remaining = db.query(models.Milestone).filter(
            models.Milestone.id_indicador == id_indicador
        ).count()
        if remaining == 0:
            ind.tiene_hitos = "No"
            db.commit()
        else:
            _recalc_indicator_from_milestones(db, ind)
    return True


# ── Snapshots ────────────────────────────────────────────────────────────────

def get_snapshots(db: Session):
    return db.query(models.MonthlySnapshot).order_by(
        models.MonthlySnapshot.periodo.desc()
    ).all()


def get_snapshot(db: Session, snapshot_id: int):
    return db.query(models.MonthlySnapshot).filter(
        models.MonthlySnapshot.id == snapshot_id
    ).first()


def create_snapshot(db: Session, data: schemas.SnapshotCreate):
    import json

    indicators = db.query(models.Indicator).all()
    milestones = db.query(models.Milestone).all()
    objectives = db.query(models.Objective).all()

    def ind_stats(obj_id):
        inds = [i for i in indicators if i.id_objetivo == obj_id]
        n = len(inds)
        avg = round(sum(i.avance_pct or 0 for i in inds) / n, 2) if n else 0
        return n, avg

    snapshot_data = {
        "periodo": data.periodo,
        "fecha_creacion": datetime.utcnow().isoformat(),
        "objectives": [
            {
                "id_objetivo": o.id_objetivo,
                "objetivo_anual": o.objetivo_anual,
                "lineamiento": o.lineamiento,
                "tipo_objetivo": o.tipo_objetivo,
                "unidades_organizacionales": o.unidades_organizacionales,
                "n_indicadores": ind_stats(o.id_objetivo)[0],
                "avance_promedio_pct": ind_stats(o.id_objetivo)[1],
            }
            for o in objectives
        ],
        "indicators": [
            {
                "id_indicador": i.id_indicador,
                "id_objetivo": i.id_objetivo,
                "indicador": i.indicador,
                "unidad_organizacional": i.unidad_organizacional,
                "division_area": i.division_area,
                "lineamiento": i.lineamiento,
                "meta": i.meta,
                "avance_valor": i.avance_valor,
                "avance_pct": i.avance_pct,
                "estado": i.estado,
                "unidad_medida": i.unidad_medida,
                "tipo_objetivo": i.tipo_objetivo,
                "clasificacion": i.clasificacion,
                "tiene_hitos": i.tiene_hitos,
                "notas": i.notas,
                "fecha_fin_actual": i.fecha_fin_actual,
            }
            for i in indicators
        ],
        "milestones": [
            {
                "id_hito": m.id_hito,
                "id_indicador": m.id_indicador,
                "nombre_hito": m.nombre_hito,
                "orden": m.orden,
                "estado": m.estado,
                "avance_pct": m.avance_pct,
                "fecha_fin_actual": m.fecha_fin_actual,
            }
            for m in milestones
        ],
    }

    snap = models.MonthlySnapshot(
        periodo=data.periodo,
        descripcion=data.descripcion,
        data_json=json.dumps(snapshot_data, ensure_ascii=False),
    )
    db.add(snap)
    db.commit()
    db.refresh(snap)
    return snap


def delete_snapshot(db: Session, snapshot_id: int):
    snap = get_snapshot(db, snapshot_id)
    if not snap:
        return False
    db.delete(snap)
    db.commit()
    return True


# ── History ──────────────────────────────────────────────────────────────────

def get_history(db: Session, id_indicador: Optional[str] = None, limit: int = 100):
    q = db.query(models.ProgressHistory)
    if id_indicador:
        q = q.filter(models.ProgressHistory.id_indicador == id_indicador)
    return q.order_by(models.ProgressHistory.fecha_actualizacion.desc()).limit(limit).all()


# ── Dashboard ────────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session):
    objectives = db.query(models.Objective).all()
    indicators = db.query(models.Indicator).all()
    milestones = db.query(models.Milestone).all()

    total_ind = len(indicators)
    avance_general = round(sum(i.avance_pct or 0 for i in indicators) / total_ind, 2) if total_ind else 0

    by_estado = {}
    for i in indicators:
        e = i.estado or "Sin estado"
        by_estado[e] = by_estado.get(e, 0) + 1

    by_lineamiento = {}
    for i in indicators:
        lin = i.lineamiento or "Sin lineamiento"
        if lin not in by_lineamiento:
            by_lineamiento[lin] = {"count": 0, "avance_sum": 0}
        by_lineamiento[lin]["count"] += 1
        by_lineamiento[lin]["avance_sum"] += i.avance_pct or 0
    by_lineamiento_final = {
        k: {"count": v["count"], "avance_pct": round(v["avance_sum"] / v["count"], 2) if v["count"] else 0}
        for k, v in by_lineamiento.items()
    }

    by_unidad = {}
    for i in indicators:
        u = i.unidad_organizacional or "Sin unidad"
        if u not in by_unidad:
            by_unidad[u] = {"count": 0, "avance_sum": 0}
        by_unidad[u]["count"] += 1
        by_unidad[u]["avance_sum"] += i.avance_pct or 0
    by_unidad_final = {
        k: {"count": v["count"], "avance_pct": round(v["avance_sum"] / v["count"], 2) if v["count"] else 0}
        for k, v in by_unidad.items()
    }

    top_objectives = []
    for o in objectives:
        inds = [i for i in indicators if i.id_objetivo == o.id_objetivo]
        n = len(inds)
        avg = round(sum(i.avance_pct or 0 for i in inds) / n, 2) if n else 0
        top_objectives.append({
            "id_objetivo": o.id_objetivo,
            "objetivo_anual": o.objetivo_anual,
            "lineamiento": o.lineamiento,
            "n_indicadores": n,
            "avance_promedio_pct": avg,
        })
    top_objectives.sort(key=lambda x: x["avance_promedio_pct"], reverse=True)

    recent = db.query(models.ProgressHistory).order_by(
        models.ProgressHistory.fecha_actualizacion.desc()
    ).limit(10).all()
    recent_history = [
        {
            "id_indicador": h.id_indicador,
            "periodo": h.periodo,
            "avance_pct": h.avance_pct,
            "estado": h.estado,
            "notas": h.notas,
            "fecha_actualizacion": h.fecha_actualizacion.isoformat() if h.fecha_actualizacion else None,
        }
        for h in recent
    ]

    return {
        "total_objectives": len(objectives),
        "total_indicators": total_ind,
        "total_milestones": len(milestones),
        "avance_general": avance_general,
        "by_estado": by_estado,
        "by_lineamiento": by_lineamiento_final,
        "by_unidad": by_unidad_final,
        "top_objectives": top_objectives,
        "recent_history": recent_history,
    }
