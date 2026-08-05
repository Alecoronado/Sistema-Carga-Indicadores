from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import crud
from database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_dashboard_stats(db)


@router.get("/history")
def get_history(id_indicador: str = None, limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_history(db, id_indicador, limit)
