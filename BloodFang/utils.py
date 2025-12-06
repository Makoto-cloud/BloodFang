# utils.py
import os
import shutil
import time
import random
import re
import getpass
import json
import urllib.request
import urllib.error
import subprocess
import stat
from config import Colors, KEY_FILE, GEMINI_MODEL

# --- UI EFFECTS ---
def matrix_intro():
    width = shutil.get_terminal_size().columns
    matrix_chars = ['0', '1', 'HEX', 'PWN', 'X', 'φ', 'Λ', 'Ω']
    end_time = time.time() + 2.5 
    try:
        while time.time() < end_time:
            line = ""
            for _ in range(width):
                if random.random() > 0.8:
                    line += f"{Colors.GREEN}{random.choice(matrix_chars)}{Colors.ENDC}"
                else:
                    line += " "
            print(line)
            time.sleep(0.05)
        os.system('cls' if os.name == 'nt' else 'clear')
    except KeyboardInterrupt:
        pass

def show_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    ascii_art = r"""
██████╗░██╗░░░░░░█████╗░░█████╗░██████╗░███████╗░█████╗░███╗░░██╗░██████╗░
██╔══██╗██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗░██║██╔════╝░
██████╦╝██║░░░░░██║░░██║██║░░██║██║░░██║█████╗░░███████║██╔██╗██║██║░░██╗░
██╔══██╗██║░░░░░██║░░██║██║░░██║██║░░██║██╔══╝░░██╔══██║██║╚████║██║░░╚██╗
██████╦╝███████╗╚█████╔╝╚█████╔╝██████╔╝██║░░░░░██║░░██║██║░╚███║╚██████╔╝
╚═════╝░╚══════╝░╚════╝░░╚════╝░╚═════╝░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚══╝░╚═════╝░
    """
    width = shutil.get_terminal_size().columns
    for line in ascii_art.strip().split('\n'):
        print(Colors.GREEN + line.center(width) + Colors.ENDC)
    
    tagline = f"{Colors.WHITE}PWN SUITE: {Colors.RED}AI-POWERED EXPLOITATION ENGINE{Colors.ENDC}"
    model_info = f"{Colors.GREY}(Model: {GEMINI_MODEL}){Colors.ENDC}"
    print(tagline.center(width + 10))
    print(model_info.center(width + 10))
    print("\n" + Colors.CYAN + "═"*width + Colors.ENDC + "\n")

# --- CLEANER ---
def extract_clean_code(text):
    pattern = r"```(?:python)?\s*(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        print(f"{Colors.GREEN}[✓] Blok kode terdeteksi & diekstrak.{Colors.ENDC}")
        return match.group(1).strip()
    else:
        lines = text.split('\n')
        clean_lines = []
        for line in lines:
            if line.strip().startswith("Here is") or line.strip().startswith("Berikut"): continue
            if "exploit" in line.lower() and "code" in line.lower(): continue
            clean_lines.append(line)
        return "\n".join(clean_lines)

# --- KEY MANAGER ---
def load_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if key: return key.strip()
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r") as f: return f.read().strip()
        except: pass
    print(f"\n{Colors.WARNING}[!] Setup Awal: Masukkan Google Gemini API Key.{Colors.ENDC}")
    try: input_key = getpass.getpass(f"{Colors.BOLD}API Key >> {Colors.ENDC}").strip()
    except: input_key = input(f"{Colors.BOLD}API Key >> {Colors.ENDC}").strip()
    if input_key:
        with open(KEY_FILE, "w") as f: f.write(input_key)
        if os.name != 'nt': os.chmod(KEY_FILE, 0o600)
        return input_key
    return None

# --- AI CLIENT ---
def query_gemini_native(api_key, full_prompt):
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    url = f"{base_url}/{GEMINI_MODEL}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 8192}
    }
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            try:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    return candidate['content']['parts'][0]['text']
                else: return f"# ERROR: {candidate.get('finishReason')}"
            except: return f"# Error parsing JSON: {result}"
    except urllib.error.HTTPError as e: return f"# HTTP Error {e.code}: {e.read().decode()}"
    except Exception as e: return f"# Connection Error: {str(e)}"

# --- SYSTEM UTILS ---
def run(cmd):
    try: return subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e: return e.output

def write(out, title, content):
    banner = "="*80
    out.write("\n" + banner + "\n== " + title + "\n" + banner + "\n" + content + "\n\n")
    print(f"{Colors.CYAN}[+] Analyzing: {title}...{Colors.ENDC}")

def make_executable(path):
    try:
        st = os.stat(path)
        os.chmod(path, st.st_mode | stat.S_IEXEC)
        print(f"{Colors.GREEN}[✓] Chmod +x applied: {path}{Colors.ENDC}")
    except: pass

def select_file_ext(extension=None, exclude=None):
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    if extension: files = [f for f in files if f.endswith(extension)]
    if exclude: files = [f for f in files if f not in exclude]
    if not files: return None
    for i, f in enumerate(files): print(f"{Colors.BOLD}[{i+1}]{Colors.ENDC} {f}")
    while True:
        try:
            choice = input(f"{Colors.WARNING}>> {Colors.ENDC}")
            idx = int(choice) - 1
            if 0 <= idx < len(files): return files[idx]
        except: pass
