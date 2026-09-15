from fastapi import APIRouter, UploadFile, File
from app import model_service
from enum import Enum

class SumType(str, Enum):
    MAIN = "main"
    SHORT = "short"
    KID = "kid"
    EN = "en"
    CHUNK = "chunk"

router = APIRouter()

@router.post("/summarize/{sum_type}")
async def choose_summary(sum_type: SumType, file: UploadFile = File(...)):
    return model_service.choose_summary(file, sum_type)
