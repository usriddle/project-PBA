import httpx
from app.schemas import SummarizeResponse
from app.ocr import run_ocr
from fastapi import File, UploadFile

OLLAMA_CHAT_URL = (
    "http://localhost:11434/api/chat"
)

MODEL_NAME = "qwen2.5:7b-instruct"

# 
def call_ollama(system_instructions: str, message: str, think_mode: bool) -> str:
    payload = {
        "model": MODEL_NAME, 
        # 시스템 지침과 사용자 입력 전달
        "messages": [
            { "role": "system","content": system_instructions },
            { "role": "user", "content": message }
        ],
        "stream": False, # 스트리밍 설정: 비활성화
        "think": think_mode, # 추가 추론 설정
        "options": {"num_predict": 500}, # 최대 Token 설정: 500
    }

    try:
        # ollama에게 request json으로 전달
        response = httpx.post(OLLAMA_CHAT_URL, json=payload, timeout=180.0)
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

def summarize(file: UploadFile = File(...)) -> SummarizeResponse:
    text = run_ocr(file)
    summary = call_ollama(
        """
        Role: You are a document summarization assistant.
        Task: Summarize the document concisely in fluent Korean.
        Constraints: 
        - Do not respond in Chinese, Japanese, or English.
        - Do not invent information.
        Output Requirements:
        - Preserve important facts and information from the original document.
        - Response in natural, professional Korean.
        """,
        text,
        False
    )
    return SummarizeResponse(model=MODEL_NAME, summary=summary)