from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import api

# Khởi tạo FastAPI app
app = FastAPI(
    title="LLM API Server với Prompt từ File",
    description="Server kết nối với LLM nội bộ, prompt được đọc từ file",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware (nếu cần gọi từ web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký routers
app.include_router(api.router)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "LLM API Server với Prompt từ File",
        "status": "active",
        "model": settings.OLLAMA_MODEL,
        "prompt_sources": {
            "code_review": settings.AI_CODE_REVIEW_PROMPT
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "model": settings.OLLAMA_MODEL,
    }