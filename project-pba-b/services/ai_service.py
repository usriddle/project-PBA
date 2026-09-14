import httpx


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "qwen2.5:7b-instruct"


def split_text(
    text: str,
    chunk_size: int = 4000
) -> list[str]:

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


async def call_ollama(prompt: str) -> str:

    request_data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": 300
        }
    }

    async with httpx.AsyncClient(timeout=300.0) as client:

        response = await client.post(
            OLLAMA_URL,
            json=request_data
        )

        response.raise_for_status()

        result = response.json()

    return result["response"]


async def summarize_text(text: str) -> str:

    chunks = split_text(text)

    chunk_summaries = []

    for index, chunk in enumerate(chunks):

        prompt = f"""
다음은 문서의 일부입니다.

이 내용을 한국어로 핵심만 요약해주세요.

규칙:
- 핵심 주장과 정보를 유지하세요.
- 중요한 숫자와 날짜는 유지하세요.
- 문서에 없는 내용은 추가하지 마세요.
- 불필요한 서론이나 결론은 작성하지 마세요.

문서 일부:
{chunk}
"""

        summary = await call_ollama(prompt)

        chunk_summaries.append(summary)

    combined = "\n\n".join(chunk_summaries)

    final_prompt = f"""
다음은 하나의 문서를 여러 부분으로 나누어 요약한 결과입니다.

이 내용을 종합하여 하나의 자연스러운 한국어 문서 요약을 작성해주세요.

요구사항:
- 문서 전체의 핵심 내용을 포함하세요.
- 중복되는 내용을 제거하세요.
- 중요한 수치와 사실은 유지하세요.
- 문서에 없는 내용을 추가하지 마세요.
- 제목과 주요 항목을 적절히 사용하세요.

부분 요약:
{combined}
"""

    final_summary = await call_ollama(final_prompt)

    return final_summary