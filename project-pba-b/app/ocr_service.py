import shutil
import tempfile
from pathlib import Path
from typing import Any
from fastapi import HTTPException, UploadFile
from paddleocr import PPStructureV3
import re

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

pipeline = PPStructureV3(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False,
    device="cpu",
    lang="korean"
)

def run_paddle_ocr(file: UploadFile) -> dict[str, Any]:
    validate_ocr(file)    
    try:
        temp_path = create_temp_path(file)
        results = list(
            pipeline.predict(input=str(temp_path))
        )
        validate_result(results)
        page_details = process_pages(results)
        text = extract_text(page_details.get("pages"))

        return {
            "text": text,
            "page_count": page_details.get("page_count"),
            "text_block_count": page_details.get("text_block_count"),
            "image_count": page_details.get("image_count"),
            "table_count": page_details.get("table_count"),
        }

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

def validate_ocr(file):
    if not file.filename:
        raise HTTPException(status_code=400, detail="파일 이름이 없습니다.")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="PDF, PNG, JPG, JPEG, WEBP 파일만 업로드할 수 있습니다.",
        )

def parse_result(res: Any, page_number: int) -> dict[str, Any]:
    raw = json_safe(res.json)
    page_data = raw.get("res", raw)
    parsing_res_list = page_data.get("parsing_res_list") or []
    overall_ocr_res = page_data.get("overall_ocr_res") or {}

    text_blocks = []
    rec_texts = overall_ocr_res.get("rec_texts") or []
    rec_scores = overall_ocr_res.get("rec_scores") or []
    rec_polys = overall_ocr_res.get("rec_polys") or []

    for i, text in enumerate(rec_texts):
        if text is None or not str(text).strip():
            continue
        text_blocks.append(
            {
                "text": str(text),
                "confidence": rec_scores[i] if i < len(rec_scores) else None,
                "bbox": rec_polys[i] if i < len(rec_polys) else None,
            }
        )

    layout = []
    for index, block in enumerate(parsing_res_list, start=1):
        layout.append(
            {
                "label": block.get("block_label"),
                "content": block.get("block_content"),
                "coordinate": block.get("block_bbox"),
                "block_id": block.get("block_id") or f"p{page_number}_b{index}",
                "block_order": block.get("block_order") or index,
                "score": block.get("block_score"),
            }
        )

    markdown_data = res.markdown or {}
    markdown_text = markdown_data.get("markdown_texts", "")

    return {
        "page": page_number,
        "page_index": page_data.get("page_index"),
        "page_count": page_data.get("page_count"),
        "width": page_data.get("width"),
        "height": page_data.get("height"),
        "text_blocks": text_blocks,
        "layout": layout,
        "markdown": markdown_text,
        "raw": raw,
    }
    
def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(v) for v in value]
    if hasattr(value, "tolist"):
        try:
            return json_safe(value.tolist())
        except Exception:
            pass
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)
    
def validate_result(results: list[str]) -> None:
    if not results:
        raise HTTPException(
            status_code=422,
            detail="OCR 결과가 없습니다."
        )

def process_pages(results: list[str]) -> dict[str, Any]:
    pages = [
        parse_result(res, page_number)
        for page_number, res in enumerate(results, start=1)
    ]

    original_page_count = next(
        (
            page["page_count"]
            for page in pages
            if page.get("page_count") is not None
        ),
        None,
    )
    page_count = original_page_count or len(pages)

    text_block_count = sum(
        len(page["text_blocks"])
        for page in pages
    )

    image_count = sum(
        1
        for page in pages
        for block in page["layout"]
        if str(block.get("label", "")).lower()
        in {"image", "figure"}
    )

    table_count = sum(
        1
        for page in pages
        for block in page["layout"]
        if str(block.get("label", "")).lower() == "table"
    )
    
    return  {
        "table_count": table_count,
        "image_count": image_count,
        "text_block_count": text_block_count,
        "page_count": page_count,
        "pages": pages
    }

def extract_text(pages: dict[str, Any]) -> str:
    text_parts = []
    for page in pages:
        markdown = page.get("markdown", "").strip()
        text_only = re.sub(r"<[^>]+>", "", markdown).strip()

        if text_only:
            text_parts.append(markdown)
        else:
            text_parts.extend(
                block["text"]
                for block in page.get("text_blocks", [])
                if block.get("text")
            )
    return "\n\n".join(text_parts)

def create_temp_path(file: UploadFile) -> str:
    suffix = Path(file.filename).suffix.lower()
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp_file:
        file.file.seek(0)
        shutil.copyfileobj(file.file, temp_file)
        temp_path = Path(temp_file.name)
    return temp_path
