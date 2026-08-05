from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db

router = APIRouter(prefix="/api/objectives", tags=["objectives"])


@router.get("/", response_model=List[schemas.Objective])
def list_objectives(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    objectives = crud.get_objectives(db, skip, limit)
    result = []
    for o in objectives:
        stats = crud.get_objective_stats(db, o.id_objetivo)
        obj = schemas.Objective.model_validate(o)
        obj.n_indicadores = stats["n_indicadores"]
        obj.avance_promedio_pct = stats["avance_promedio_pct"]
        result.append(obj)
    return result


@router.get("/{id_objetivo}", response_model=schemas.ObjectiveWithIndicators)
def get_objective(id_objetivo: str, db: Session = Depends(get_db)):
    o = crud.get_objective(db, id_objetivo)
    if not o:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    stats = crud.get_objective_stats(db, id_objetivo)
    obj = schemas.ObjectiveWithIndicators.model_validate(o)
    obj.n_indicadores = stats["n_indicadores"]
    obj.avance_promedio_pct = stats["avance_promedio_pct"]
    obj.indicators = [schemas.IndicatorSummary.model_validate(i) for i in o.indicators]
    return obj


@router.post("/", response_model=schemas.Objective, status_code=201)
def create_objective(data: schemas.ObjectiveCreate, db: Session = Depends(get_db)):
    existing = crud.get_objective(db, data.id_objetivo)
    if existing:
        raise HTTPException(status_code=400, detail="ID de objetivo ya existe")
    return crud.create_objective(db, data)


@router.put("/{id_objetivo}", response_model=schemas.Objective)
def update_objective(id_objetivo: str, data: schemas.ObjectiveUpdate, db: Session = Depends(get_db)):
    o = crud.update_objective(db, id_objetivo, data)
    if not o:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
    stats = crud.get_objective_stats(db, id_objetivo)
    obj = schemas.Objective.model_validate(o)
    obj.n_indicadores = stats["n_indicadores"]
    obj.avance_promedio_pct = stats["avance_promedio_pct"]
    return obj


@router.delete("/{id_objetivo}", status_code=204)
def delete_objective(id_objetivo: str, db: Session = Depends(get_db)):
    ok = crud.delete_objective(db, id_objetivo)
    if not ok:
        raise HTTPException(status_code=404, detail="Objetivo no encontrado")
