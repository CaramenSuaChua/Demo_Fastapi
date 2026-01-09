from openai import OpenAI
from .config import settings
from typing import Optional

class LLMClient:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OLLAMA_BASE_URL,
            api_key=settings.OLLAMA_API_KEY
        )
        self.model = settings.OLLAMA_MODEL
    
    def ask(self, question: str, system_prompt: Optional[str] = None, 
            prompt_source: str = "unknown") -> dict:
        """
        Gửi câu hỏi đến LLM và nhận câu trả lời
        Trả về dict chứa cả answer và prompt được sử dụng
        """
        
        messages = []
        
        # Sử dụng prompt được truyền vào, hoặc default từ settings
        final_system_prompt = system_prompt or settings.AI_SYSTEM_PROMPT
        used_prompt = final_system_prompt
        
        if final_system_prompt:
            messages.append({"role": "system", "content": final_system_prompt})
        
        # Thêm user question
        messages.append({"role": "user", "content": question})
        
        # Gọi API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=settings.AI_MAX_TOKENS,
            temperature=settings.AI_TEMPERATURE
        )
        
        answer = response.choices[0].message.content
        
        return {
            "answer": answer,
            "used_prompt": used_prompt,
            "prompt_source": prompt_source,
            "model": self.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }

# Tạo instance global
llm_client = LLMClient()