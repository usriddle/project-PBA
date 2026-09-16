from fastapi import APIRouter, UploadFile, File
from app.model_service import choose_summary
from app.schemas import SumType

router = APIRouter()

@router.post("/summary/{sum_type}")
def summarize(sum_type: SumType, file: UploadFile = File(...)):
    return choose_summary(file, sum_type)