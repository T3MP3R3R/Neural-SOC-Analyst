import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
API_URL       = "https://api.groq.com/openai/v1/chat/completions"
MODEL         = "llama-3.1-8b-instant"
HISTORY_FILE  = os.path.join(os.path.dirname(__file__), "history.json")
MAX_HISTORY   = 50

VT_API_KEY    = os.getenv("VT_API_KEY", "")
VT_BASE_URL   = "https://www.virustotal.com/api/v3"

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not set. Check your .env file.")