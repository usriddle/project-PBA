from fastapi import APIRouter, UploadFile, File, HTTPException
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text

import os
import shutil


router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/summary")
async def create_summary(file: UploadFile = File(...)):

    # PDF 확인
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="PDF 파일만 업로드할 수 있습니다."
        )

    # 저장 경로
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    # PDF 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # PDF → 텍스트
    text = extract_text_from_pdf(file_path)

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="PDF에서 텍스트를 추출할 수 없습니다."
        )

    summary = await summarize_text(text)

    return {
    "filename": file.filename,
    "summary": summary
    }