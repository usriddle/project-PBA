import httpx
import time
import hashlib
from app.schemas import SummarizeResponse, SumType
from app.ocr_service import run_paddle_ocr
from app.models import Document
from fastapi import File, UploadFile, HTTPException
from pathlib import Path

OLLAMA_CHAT_URL = (
    "http://localhost:11434/api/chat"
)

MODEL_NAME = "qwen2.5:7b-instruct"

def call_ollama(system_instructions: str, message: str, output_token: int) -> str:
    payload = {
        "model": MODEL_NAME, 
        # 시스템 지침과 사용자 입력 전달
        "messages": [
            { "role": "system","content": system_instructions },
            { "role": "user", "content": message }
        ],
        "stream": False, # 스트리밍 설정: 비활성화
        "think": False, # 추가 추론 설정: 비활성화
        "options": {"num_predict": output_token}, # 최대 출력 Token 설정
    }

    try:
        # ollama에게 request json으로 전달
        response = httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=2400.0)
        # 전달 사항 확인
        response.raise_for_status()
        # JSON 내용을 dictionary로 변경
        data = response.json()
        print(f"prompt tokens: {data.get('prompt_eval_count')}, "
              f"gen tokens: {data.get('eval_count')}")
        # 모델 요약 전달  
        return data["message"]["content"]

    # HTTP 오류 처리 
    except httpx.HTTPError as e:
        raise RuntimeError(f"Ollama call failed: {e}")

def choose_summary(file: UploadFile, sum_type: SumType, db):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    original_filename = file.filename or "unknown.pdf"

    # 파일 내용 읽기
    file_content = file.file.read()

    # 파일 해시 생성
    file_hash = hashlib.sha256(file_content).hexdigest()

    # 파일 포인터 초기화
    file.file.seek(0)

    # 파일명 중복 방지
    import uuid

    safe_filename = Path(original_filename).name
    saved_filename = f"{uuid.uuid4().hex}_{safe_filename}"
    saved_path = upload_dir / saved_filename

    # 파일 저장
    saved_path.write_bytes(file_content)

    # 항상 새로운 Document 생성
    document = Document(
        original_filename=original_filename,
        file_path=str(saved_path),
        file_hash=file_hash,
        sum_type=sum_type.value,
        status="processing",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    file.file.seek(0)

    try:
        # 요약 실행
        if sum_type is SumType.MAIN:
            result = summarize_main(file)

        elif sum_type is SumType.SHORT:
            result = summarize_short(file)

        elif sum_type is SumType.KID:
            result = summarize_kid(file)

        elif sum_type is SumType.EN:
            result = summarize_en(file)

        elif sum_type is SumType.CHUNK:
            result = summarize_chunk(file)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"지원하지 않는 요약 타입입니다: {sum_type}"
            )

        # 요약 결과 DB 저장
        document.summary = result.summary
        document.status = "completed"

        db.commit()
        db.refresh(document)

        return result

    except Exception:
        document.status = "failed"
        db.commit()
        raise

def summarize_main(file: UploadFile = File(...)) -> SummarizeResponse:
    instructions = """
        역할: 문서 요약을 지원하는 전문 AI 어시스턴트입니다.
        응답 언어: 입력 문서의 언어와 관계없이 반드시 한국어로 응답합니다.
        작업: 문서의 핵심 내용을 간결하고 정확한 한국어로 요약합니다.
        제약사항:
        - 원문에 없는 내용을 임의로 추가하거나 추측하지 않습니다.
        - 지나치게 길게 이어지는 문장을 사용하지 않습니다.
        출력 요구사항:
        - 원문의 중요한 사실과 정보를 빠짐없이 반영합니다.
        - 자연스럽고 전문적인 한국어로 작성합니다.
        - 불필요한 반복이나 세부적인 표현은 줄입니다.
        - 출력 내용이 길 경우 여러 문단으로 나누어 작성합니다.
    """
    start = time.perf_counter()
    text = process_text(file)

    ai_start = time.perf_counter()
    summary = call_ollama(
        instructions,
        text,
        500
    )
    ai_time = time.perf_counter() - ai_start
    total_time = time.perf_counter() - start

    # OCR 및 모델 처리 시간 출력
    print(f"AI: {ai_time:.2f}s")
    print(f"Total: {total_time:.2f}s")

    return SummarizeResponse(model=MODEL_NAME, summary=summary)

def summarize_chunk(file: UploadFile = File(...)) -> SummarizeResponse:
    instructions = """
        역할: 문서 요약을 지원하는 전문 AI 어시스턴트입니다.
        응답 언어: 입력 문서의 언어와 관계없이 반드시 한국어로 응답합니다.
        작업: 문서의 핵심 내용을 간결하고 정확한 한국어로 요약합니다.
        제약사항:
        - 원문에 없는 내용을 임의로 추가하거나 추측하지 않습니다.
        - 지나치게 길게 이어지는 문장을 사용하지 않습니다.
        출력 요구사항:
        - 원문의 중요한 사실과 정보를 빠짐없이 반영합니다.
        - 자연스럽고 전문적인 한국어로 작성합니다.
        - 불필요한 반복이나 세부적인 표현은 줄입니다.
        - 출력 내용이 길 경우 여러 문단으로 나누어 작성합니다.
    """
    start = time.perf_counter()
    text = process_text(file)
    chunks = generate_chunks(text) # 문서를 분할
    chunked_summary = chunk_call(chunks)
    summary = call_ollama(
        instructions,
        chunked_summary,
        500
    )
    total_time = time.perf_counter() - start
    print(f"Total: {total_time:.2f}s")

    return SummarizeResponse(model=MODEL_NAME, summary=summary)

def summarize_short(file: UploadFile = File(...)) -> SummarizeResponse:
    instructions = """
        역할: 문서의 성격과 목적을 설명하는 한국어 전문 AI 어시스턴트입니다.
        응답 언어: 입력 문서의 언어와 관계없이 반드시 한국어로 응답합니다.
        작업: 문서를 읽고 문서가 무엇인지와 주요 내용을 간결하게 설명합니다.
        제약사항:
        - 원문에 없는 내용을 추가하거나 추측하지 않습니다.
        - 문서의 세부 내용을 자세히 설명하지 않습니다.
        - 글머리 기호나 번호 목록을 사용하지 않습니다.
        출력 요구사항:
        - 먼저 문서가 실제로 무엇인지 설명합니다.
        - 각 문장은 한 줄에 하나씩 작성합니다.
        - 문서의 주요 내용이나 핵심 내용을 설명합니다.
        - 전체 내용을 4문장 이내로 작성합니다.
        - 짧고 명확하게 작성합니다.
        - 설명문만 출력합니다.
    """
    start = time.perf_counter()

    text = process_text(file)

    ai_start = time.perf_counter()
    summary = call_ollama(
        instructions,
        text,
        200
    )
    ai_time = time.perf_counter() - ai_start
    total_time = time.perf_counter() - start

    print(f"AI: {ai_time:.2f}s")
    print(f"Total: {total_time:.2f}s")

    return SummarizeResponse(model=MODEL_NAME, summary=summary)

def summarize_kid(file: UploadFile = File(...)) -> SummarizeResponse:
    instructions = """
        역할: 8살 어린이가 이해할 수 있는 수준으로 문서를 한국어로 요약하는 AI 어시스턴트야.
        응답 언어: 입력 문서의 언어와 관계없이 반드시 한국어로 응답해.
        작업: 문서의 핵심 내용을 8살 어린이에게 설명하듯 쉽고 간결하게 요약해줘.
        제약사항:
        - 존댓말이나 격식 있는 표현을 사용하지 마.
        - 반드시 해체를 사용해. 예: "~해", "~야", "~할 수 있어", "~하면 돼".
        - 원문에 없는 내용을 추가하거나 추측하지 마.
        - 중요한 내용은 빠뜨리지 마.
        - 불필요한 반복이나 지나치게 자세한 내용은 줄여줘.
        - 어려운 단어나 전문 용어는 8살 어린이가 이해할 수 있는 쉬운 말로 바꿔서 설명해줘.
        - 어린이가 쉽게 떠올릴 수 있는 간단한 예나 비유를 사용해줘.
        - 단순히 문장을 짧게 만드는 것이 아니라, 내용 자체를 어린이가 이해하기 쉽게 바꿔서 설명해줘.
        출력 요구사항:
        - 먼저 문서가 무엇에 관한 내용인지 설명해줘.
        - 2~4개의 짧은 문단으로 작성해줘.
        - 각 문단 사이에는 빈 줄을 하나 넣어줘.
        - 각 문단은 1~3개의 짧은 문장으로 작성해줘.
        - 도입 문구나 제목을 추가하지 마.
        - 설명만 출력해.
    """
    start = time.perf_counter()

    text = process_text(file)

    ai_start = time.perf_counter()
    summary = call_ollama(
        instructions,
        text,
        400
    )
    ai_time = time.perf_counter() - ai_start
    total_time = time.perf_counter() - start

    print(f"AI: {ai_time:.2f}s")
    print(f"Total: {total_time:.2f}s")

    return SummarizeResponse(model=MODEL_NAME, summary=summary)

def summarize_en(file: UploadFile = File(...)) -> SummarizeResponse:
    instructions = """
        Role: You are a professional AI assistant that supports document summarization.
        Task: Summarize the key contents of the document concisely and accurately in English.
        Constraints:
        - Do not respond in Chinese, Japanese, Korean, or any language that is not English.
        - Do not add or speculate on information that is not present in the original document.
        - Avoid excessively long sentences.
        Output Requirements:
        - Include all important facts and key information from the original document.
        - Write in natural and professional English.
        - If the output is long, divide it into multiple paragraphs.
    """
    text = process_text(file)
    summary = call_ollama(
        instructions,
        text,
        500
    )
    return SummarizeResponse(model=MODEL_NAME, summary=summary)

def generate_chunks(text: str, chunk_size: int = 4000) -> list[str]:
    # 문서를 문단 단위로 분리
    paragraphs = text.split("\n\n")
    # 완성된 청크를 저장
    chunks = []
    # 현재 생성 중인 청크
    current = ""

    for paragraph in paragraphs:
        # 청크 크기를 초과하는 긴 문단은 4,000자 단위로 분할
        while len(paragraph) > chunk_size:
            chunks.append(paragraph[:chunk_size])
            paragraph = paragraph[chunk_size:]

        # 현재 청크에 문단을 추가해도 크기 제한을 넘지 않는지 확인
        if len(current) + len(paragraph) + (2 if current else 0) <= chunk_size:
            # 현재 청크에 문단 추가
            # 기존 문단이 있다면 문단 사이에 줄바꿈 추가
            current += ("\n\n" if current else "") + paragraph
        else:
            # 크기 제한을 초과하면 현재 청크를 저장
            chunks.append(current)

            # 현재 문단부터 새로운 청크 시작
            current = paragraph

    # 마지막으로 남은 청크 저장
    if current:
        chunks.append(current)

    return chunks

def chunk_call(chunks: list[str]) -> str:
    chunk_instructions = """
        역할: 문서 요약을 지원하는 전문 AI 어시스턴트입니다.
        목표: 문서의 일부 내용을 간결하고 정확한 한국어로 요약합니다.

        제약 사항:
        - 중국어, 일본어, 영어로 응답하지 않습니다.
        - 원문에 없는 내용을 임의로 추가하거나 추측하지 않습니다.
        - 원문의 핵심 정보와 중요한 사실을 유지합니다.
        - 문서의 일부만 제공되므로 전체 문서의 내용을 추측하지 않습니다.
        - 지나치게 길게 이어지는 문장을 사용하지 않습니다.

        출력 요구 사항:
        - 입력된 내용에서 중요한 정보와 핵심 내용을 빠짐없이 반영합니다.
        - 자연스럽고 전문적인 한국어로 작성합니다.
        - 불필요한 반복이나 세부적인 표현은 줄입니다.
    """
    chunk_summaries = []
    for chunk in chunks:
        summary = call_ollama(
            chunk_instructions,
            chunk,
            300
        )
        chunk_summaries.append(summary)
    return "\n\n".join(chunk_summaries)

def process_text(file: UploadFile = File(...)) -> str:
    return run_paddle_ocr(file)["text"]