import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def read_prompt_file(file_path: str) -> str:
    """Đọc nội dung prompt từ file"""
    try:
        # Nếu đường dẫn tương đối, bắt đầu từ thư mục gốc
        if not os.path.isabs(file_path):
            base_dir = Path(__file__).parent.parent
            file_path = base_dir / file_path
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        else:
            print(f"Warning: Prompt file not found: {file_path}")
            return ""
    except Exception as e:
        print(f"Error reading prompt file {file_path}: {e}")
        return ""

class Settings:
    # Server
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Ollama
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "sk-H9RCqvDaG5_NEPEyFOJxHw")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemini/gemini-2.0-flash-lite")
    
    # AI
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "4000"))
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.7"))
    
    # Prompt file paths
    AI_SYSTEM_PROMPT_FILE = os.getenv("AI_SYSTEM_PROMPT_FILE", "prompt.txt")
    AI_CODE_REVIEW_PROMPT_FILE = os.getenv("AI_CODE_REVIEW_PROMPT_FILE", "prompt.txt")
    
    # Lazy-loaded prompts
    _system_prompt = None
    _code_review_prompt = None
    
    @property
    def AI_SYSTEM_PROMPT(self) -> str:
        """Lấy system prompt từ file (lazy loading)"""
        if self._system_prompt is None:
            self._system_prompt = read_prompt_file(self.AI_SYSTEM_PROMPT_FILE)
        return self._system_prompt
    
    @property
    def AI_CODE_REVIEW_PROMPT(self) -> str:
        """Lấy code review prompt từ file (lazy loading)"""
        if self._code_review_prompt is None:
            self._code_review_prompt = read_prompt_file(self.AI_CODE_REVIEW_PROMPT_FILE)
        return self._code_review_prompt

settings = Settings()