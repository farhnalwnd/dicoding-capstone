import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from prometheus_client import make_asgi_app

from app.api.admin_endpoints import router as admin_router
from app.api.analytics_endpoints import router as analytics_router
from app.api.auth_endpoints import router as auth_router
from app.api.endpoints import router as api_router
from app.api.hr_endpoints import router as hr_router
from app.api.jobs_endpoints import router as jobs_router
from app.api.resume_advisor_endpoints import router as resume_advisor_router

app = FastAPI(title="HIREZY API", docs_url=None)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.11.0/swagger-ui.min.css",
    )


# ====================================
# Prometheus Metrics
# ====================================

metrics_app = make_asgi_app()

app.mount("/metrics", metrics_app)

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,https://hirezy.dev"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(api_router, prefix="/api")
app.include_router(hr_router, prefix="/api")
app.include_router(jobs_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(resume_advisor_router, prefix="/api/resume-advisor")
app.include_router(admin_router, prefix="/api/admin")


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/api/model-info")
def get_model_info():
    bi_encoder_path = os.getenv(
        "MODEL_BI_ENCODER", "paraphrase-multilingual-MiniLM-L12-v2"
    )
    return {"bi_encoder": os.path.basename(bi_encoder_path)}
