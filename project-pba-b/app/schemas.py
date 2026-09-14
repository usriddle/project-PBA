from pydantic import BaseModel, Field

class SummarizeResponse(BaseModel):
    summary: str