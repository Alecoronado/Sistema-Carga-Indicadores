from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import crud, schemas, models
from database import get_db

router = APIRouter(prefix="/api/indicators", tags=["indicators"])


@router.get("/", response_model=List[schemas.IndicatorSummary])
def list_indicators(
    skip: int = 0,
    limit: int = 500,
    id_objetivo: Optional[str] = None,
    unidad_organizacional: Optional[str] = None,
    estado: Optional[str] = None,
    lineamiento: Optional[str] = None,
    clasificacion: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return crud.get_indicators(
        db, skip, limit, id_objetivo, unidad_organizacional,
        estado, lineamiento, clasificacion, search
    )


@router.get("/{id_indicador}", response_model=schemas.Indicator)
def get_indicator(id_indicador: str, db: Session = Depends(get_db)):
    ind = crud.get_indicator(db, id_indicador)
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    return ind


@router.post("/with-milestones", response_model=schemas.Indicator, status_code=201)
def create_with_milestones(data: schemas.IndicatorWithMilestonesCreate, db: Session = Depends(get_db)):
    existing = crud.get_indicator(db, data.id_indicador)
    if existing:
        raise HTTPException(status_code=400, detail="ID de indicador ya existe")
    obj = crud.get_objective(db, data.id_objetivo)
    if not obj:
        raise HTTPException(status_code=400, detail="Objetivo no encontrado")
    milestones_data = data.milestones or []
    ind_data = schemas.IndicatorCreate(**{k: v for k, v in data.model_dump().items() if k != 'milestones'})
    if milestones_data:
        ind_data.tiene_hitos = "Si"
    db_ind = crud.create_indicator(db, ind_data)
    for i, m in enumerate(milestones_data, 1):
        id_hito = f"{db_ind.id_indicador}_{i}"
        milestone = models.Milestone(
            id_hito=id_hito,
            id_indicador=db_ind.id_indicador,
            nombre_hito=m.nombre_hito,
            orden=m.orden or i,
            estado=m.estado or "Por Comenzar",
            avance_pct=m.avance_pct or 0,
            fecha_inicio=m.fecha_inicio,
            fecha_fin_original=m.fecha_fin_original,
            fecha_fin_actual=m.fecha_fin_actual,
            responsable=m.responsable,
        )
        db.add(milestone)
    db.commit()
    db.refresh(db_ind)
    return db_ind


@router.post("/", response_model=schemas.Indicator, status_code=201)
def create_indicator(data: schemas.IndicatorCreate, db: Session = Depends(get_db)):
    existing = crud.get_indicator(db, data.id_indicador)
    if existing:
        raise HTTPException(status_code=400, detail="ID de indicador ya existe")
    obj = crud.get_objective(db, data.id_objetivo)
    if not obj:
        raise HTTPException(status_code=400, detail="Objetivo no encontrado")
    return crud.create_indicator(db, data)


@router.put("/{id_indicador}", response_model=schemas.Indicator)
def update_indicator(id_indicador: str, data: schemas.IndicatorUpdate, db: Session = Depends(get_db)):
    ind = crud.update_indicator(db, id_indicador, data)
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    return ind


@router.post("/{id_indicador}/progress", response_model=schemas.Indicator)
def update_progress(id_indicador: str, data: schemas.ProgressUpdate, db: Session = Depends(get_db)):
    ind = crud.update_indicator_progress(db, id_indicador, data)
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    return ind


@router.delete("/{id_indicador}", status_code=204)
def delete_indicator(id_indicador: str, db: Session = Depends(get_db)):
    ok = crud.delete_indicator(db, id_indicador)
    if not ok:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")


@router.get("/{id_indicador}/history", response_model=List[schemas.ProgressHistory])
def get_history(id_indicador: str, db: Session = Depends(get_db)):
    ind = crud.get_indicator(db, id_indicador)
    if not ind:
        raise HTTPException(status_code=404, detail="Indicador no encontrado")
    return crud.get_history(db, id_indicador)
