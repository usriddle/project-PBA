from pydantic import BaseModel, Field
from enum import Enum

class SumType(str, Enum):
    MAIN = "main"
    SHORT = "short"
    KID = "kid"
    EN = "en"
    CHUNK = "chunk"

class SummarizeResponse(BaseModel):
    summary: str