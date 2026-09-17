from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.model_service import choose_summary
from app.schemas import SumType

router = APIRouter()


@router.post("/summary/{sum_type}")
def summarize(
    sum_type: SumType,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return choose_summary(file, sum_type, db)
