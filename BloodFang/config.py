# config.py
import os

# --- CONFIG ---
KEY_FILE = ".gemini_key"
GEMINI_MODEL = "gemini-2.0-flash" 
SILENCE_TIMEOUT = 10  # Detik. Jika hening lebih dari ini, anggap stuck & kill.

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    YELLOW = '\033[93m' 
    RED = '\033[91m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    WHITE = '\033[97m'
    GREY = '\033[90m'
