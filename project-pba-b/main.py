from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.summary import router as summary_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PDF 요약 API
app.include_router(
    summary_router,
    prefix="/api/v1/pdf",
)


@app.get("/")
def root():
    return {
        "message": "PBA Backend Server"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }
