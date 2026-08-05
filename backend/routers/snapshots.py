from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import crud, schemas
from database import get_db
import json

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])


@router.get("/", response_model=List[schemas.Snapshot])
def list_snapshots(db: Session = Depends(get_db)):
    return crud.get_snapshots(db)


@router.get("/{snapshot_id}")
def get_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    snap = crud.get_snapshot(db, snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
    return {
        "id": snap.id,
        "periodo": snap.periodo,
        "fecha_creacion": snap.fecha_creacion,
        "descripcion": snap.descripcion,
        "data": json.loads(snap.data_json) if snap.data_json else None,
    }


@router.post("/", response_model=schemas.Snapshot, status_code=201)
def create_snapshot(data: schemas.SnapshotCreate, db: Session = Depends(get_db)):
    existing = db.query(__import__("models").MonthlySnapshot).filter(
        __import__("models").MonthlySnapshot.periodo == data.periodo
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Ya existe un snapshot para el período {data.periodo}")
    return crud.create_snapshot(db, data)


@router.delete("/{snapshot_id}", status_code=204)
def delete_snapshot(snapshot_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_snapshot(db, snapshot_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Snapshot no encontrado")
