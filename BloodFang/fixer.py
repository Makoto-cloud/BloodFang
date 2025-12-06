# fixer.py
import os
from config import Colors
import utils

def chat_debug_session(api_key):
    print(f"\n{Colors.HEADER}--- SMART DEBUGGER & FIXER ---{Colors.ENDC}")
    
    # 1. Load Fix Prompt
    fix_instructions = "You are a Python Exploit Fixer. Fix the code based on the error. OUTPUT ONLY CODE."
    if os.path.exists("promp_fix.txt"):
        with open("promp_fix.txt", "r") as f: fix_instructions = f.read()
        print(f"{Colors.GREEN}[✓] 'promp_fix.txt' loaded.{Colors.ENDC}")

    # 2. Load Broken Code
    current_code = ""
    if os.path.exists("exploit.py"):
        with open("exploit.py", "r") as f: current_code = f.read()
        print(f"{Colors.GREEN}[✓] Target: 'exploit.py' loaded.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[!] 'exploit.py' tidak ditemukan.{Colors.ENDC}")
        return

    # 3. AUTO DETECT ERROR LOG
    user_error_log = ""
    if os.path.exists("log_error.txt"):
        print(f"\n{Colors.WARNING}[!] Mendeteksi 'log_error.txt' hasil eksekusi terakhir.{Colors.ENDC}")
        with open("log_error.txt", "r") as f:
            file_log = f.read()
        
        print(f"{Colors.BLUE}--- Preview Log (Last 5 lines) ---{Colors.ENDC}")
        print("\n".join(file_log.strip().split("\n")[-5:]))
        print(f"{Colors.BLUE}----------------------------------{Colors.ENDC}")

        use_auto = input(f"Gunakan log ini untuk debugging otomatis? (y/n) >> ").lower()
        if use_auto == 'y':
            user_error_log = file_log
        else:
            print(f"{Colors.WARNING}Oke, silakan paste log manual di bawah.{Colors.ENDC}")

    # 4. Manual Input
    if not user_error_log:
        print(f"\n{Colors.CYAN}Paste Error Log (Ketik 'END' untuk kirim):{Colors.ENDC}")
        lines = []
        while True:
            try:
                line = input(f"{Colors.BLUE}│ {Colors.ENDC}")
                if line.strip().upper() == "END": break
                lines.append(line)
            except KeyboardInterrupt: return
        user_error_log = "\n".join(lines)

    if not user_error_log.strip(): return

    # 5. EXECUTE GEMINI QUERY
    full_query = f"{fix_instructions}\n\n[BROKEN SCRIPT - exploit.py]\n{current_code}\n\n[ERROR LOG / EXECUTION OUTPUT]\n{user_error_log}"

    print(f"\n{Colors.CYAN}[+] Analyzing Error & Fixing Code...{Colors.ENDC}")
    response = utils.query_gemini_native(api_key, full_query)
    
    new_code = utils.extract_clean_code(response)
    if new_code:
        print(f"\n{Colors.GREEN}{'='*40}{Colors.ENDC}")
        print(f"{Colors.GREEN}       FIXED CODE CANDIDATE       {Colors.ENDC}")
        print(f"{Colors.GREEN}{'='*40}{Colors.ENDC}")
        print("\n".join(new_code.split("\n")[:15]))
        print(f"{Colors.WARNING}... (code truncated) ...{Colors.ENDC}")

        ask = input(f"\n{Colors.HEADER}Update 'exploit.py' dengan perbaikan ini? (y/n) >> {Colors.ENDC}").lower()
        if ask == 'y':
            with open("exploit.py", "w") as f: f.write(new_code)
            print(f"{Colors.GREEN}[✓] Exploit diperbarui. Silakan coba eksekusi lagi (Menu 3).{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}[!] Update dibatalkan.{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}[!] AI tidak memberikan kode. Cek respons:{Colors.ENDC}\n{response}")
