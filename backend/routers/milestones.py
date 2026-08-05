from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import crud, schemas
from database import get_db

router = APIRouter(prefix="/api/milestones", tags=["milestones"])


@router.get("/", response_model=List[schemas.Milestone])
def list_milestones(
    id_indicador: Optional[str] = None,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    return crud.get_milestones(db, id_indicador, skip, limit)


@router.get("/{id_hito}", response_model=schemas.Milestone)
def get_milestone(id_hito: str, db: Session = Depends(get_db)):
    hito = crud.get_milestone(db, id_hito)
    if not hito:
        raise HTTPException(status_code=404, detail="Hito no encontrado")
    return hito


@router.post("/", response_model=schemas.Milestone, status_code=201)
def create_milestone(data: schemas.MilestoneCreate, db: Session = Depends(get_db)):
    existing = crud.get_milestone(db, data.id_hito)
    if existing:
        raise HTTPException(status_code=400, detail="ID de hito ya existe")
    ind = crud.get_indicator(db, data.id_indicador)
    if not ind:
        raise HTTPException(status_code=400, detail="Indicador no encontrado")
    return crud.create_milestone(db, data)


@router.put("/{id_hito}", response_model=schemas.Milestone)
def update_milestone(id_hito: str, data: schemas.MilestoneUpdate, db: Session = Depends(get_db)):
    hito = crud.update_milestone(db, id_hito, data)
    if not hito:
        raise HTTPException(status_code=404, detail="Hito no encontrado")
    return hito


@router.delete("/{id_hito}", status_code=204)
def delete_milestone(id_hito: str, db: Session = Depends(get_db)):
    ok = crud.delete_milestone(db, id_hito)
    if not ok:
        raise HTTPException(status_code=404, detail="Hito no encontrado")
