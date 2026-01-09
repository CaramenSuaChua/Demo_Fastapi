from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from ..llm_client import llm_client
from ..config import settings

router = APIRouter(prefix="/api", tags=["LLM API"])

class QuestionRequest(BaseModel):
    question: str

class LLMResponse(BaseModel):
    success: bool
    question: str
    answer: str
    model: str
    used_prompt: str  # PROMPT ĐƯỢC SỬ DỤNG
    prompt_length: int  # ĐỘ DÀI PROMPT

@router.get("/test/", response_model=LLMResponse)
async def test_llm_get(question: str):
    """API GET: nhận question qua query parameter - dùng prompt từ file"""
    try:
        # Log để debug
        print(f"📥 GET request received: {question[:50]}...")
        print(f"📝 Using prompt from: {settings.AI_CODE_REVIEW_PROMPT}")
        
        # Lấy prompt từ file
        review_prompt = settings.AI_CODE_REVIEW_PROMPT
        
        # Kiểm tra xem có prompt không
        if not review_prompt or review_prompt == "":
            print("⚠️  Warning: Prompt is empty!")
            review_prompt = "Bạn là một trợ lý AI hữu ích."
        
        result = llm_client.ask(
            question=question,
            system_prompt=review_prompt
        )
        
        print(f"✅ Response generated successfully")
        
        return {
            "success": True,
            "question": question,
            "answer": result["answer"],
            "model": result["model"],
            "used_prompt": result["used_prompt"],  # HIỂN THỊ PROMPT
            "prompt_length": len(result["used_prompt"])
        }
    except Exception as e:
        print(f"❌ Error in GET /test/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/review/", response_model=LLMResponse)
async def code_review(request: QuestionRequest):
    """API đặc biệt cho review code - dùng prompt từ file"""
    try:
        # Log để debug
        print(f"📥 POST /review request received: {request.question[:50]}...")
        print(f"📝 Using prompt from: {settings.AI_CODE_REVIEW_PROMPT}")
        
        # Lấy prompt từ file
        review_prompt = settings.AI_CODE_REVIEW_PROMPT
        print(review_prompt)
        # console.log(review_prompt)
        
        # Kiểm tra xem có prompt không
        if not review_prompt or review_prompt == "":
            print("⚠️  Warning: Prompt is empty!")
            review_prompt = "Bạn là một chuyên gia review code."
        
        result = llm_client.ask(
            question=request.question,
            system_prompt=review_prompt
        )
        
        print(f"✅ Code review completed successfully")
        
        return {
            "success": True,
            "question": request.question,
            "answer": result["answer"],
            "model": result["model"],
            "used_prompt": result["used_prompt"],  # HIỂN THỊ PROMPT
            "prompt_length": len(result["used_prompt"])
        }
    except Exception as e:
        print(f"❌ Error in POST /review/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prompts/")
async def get_prompts():
    """API lấy thông tin về prompt đang được sử dụng"""
    try:
        prompt_content = settings.AI_CODE_REVIEW_PROMPT
        
        return {
            "success": True,
            "prompt_info": {
                "source_file": settings.AI_CODE_REVIEW_PROMPT,
                "content": prompt_content,
                "length": len(prompt_content),
                "preview": prompt_content[:200] + "..." if len(prompt_content) > 200 else prompt_content
            },
            "model": settings.OLLAMA_MODEL,
            "ollama_url": settings.OLLAMA_BASE_URL
        }
    except Exception as e:
        print(f"❌ Error in /prompts/: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint cho server"""
    try:
        # Kiểm tra prompt
        prompt_content = settings.AI_CODE_REVIEW_PROMPT
        prompt_ok = bool(prompt_content and prompt_content.strip())
        
        # Kiểm tra kết nối LLM (cơ bản)
        import requests
        try:
            ollama_response = requests.get(settings.OLLAMA_BASE_URL.replace('/v1', '/api/tags'), timeout=5)
            ollama_ok = ollama_response.status_code == 200
        except:
            ollama_ok = False
        
        return {
            "status": "healthy" if prompt_ok and ollama_ok else "degraded",
            "prompt_loaded": prompt_ok,
            "prompt_length": len(prompt_content) if prompt_content else 0,
            "ollama_connected": ollama_ok,
            "model": settings.OLLAMA_MODEL,
            "server_time": "OK"
        }
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }