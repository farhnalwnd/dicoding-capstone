from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.api.hr_endpoints import router as hr_router
from app.api.jobs_endpoints import router as jobs_router
import os

app = FastAPI(title="CV Summarizer & Job Matching System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(hr_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok"}

@app.get("/api/model-info")
def get_model_info():
    bi_encoder_path = os.getenv("MODEL_BI_ENCODER", "paraphrase-multilingual-MiniLM-L12-v2")
    cross_encoder_path = os.getenv("MODEL_CROSS_ENCODER")
    return {
        "bi_encoder": os.path.basename(bi_encoder_path),
        "cross_encoder": os.path.basename(cross_encoder_path) if cross_encoder_path else "None",
        "has_cross_encoder": cross_encoder_path is not None
    }
