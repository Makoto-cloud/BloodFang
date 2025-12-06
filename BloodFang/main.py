#!/usr/bin/env python3
# main.py
import sys
import os
import time
import utils
import analyzer
import executor
import fixer
from config import Colors, KEY_FILE

def main():
    utils.matrix_intro()
    
    while True:
        utils.show_banner()
        key_status = f"{Colors.GREEN}Active{Colors.ENDC}" if os.path.exists(KEY_FILE) or os.getenv("GEMINI_API_KEY") else f"{Colors.FAIL}Not Set{Colors.ENDC}"
        
        print(f"{Colors.HEADER}┌── [ ATTACK VECTORS ] ────────────────────────┐{Colors.ENDC}")
        print(f"│  {Colors.GREEN}[1]{Colors.ENDC} {Colors.WHITE}🕷️  Deep Binary Analysis{Colors.ENDC}               │")
        print(f"│  {Colors.GREEN}[2]{Colors.ENDC} {Colors.WHITE}🧠  AI Exploit Generation{Colors.ENDC}              │")
        print(f"│  {Colors.GREEN}[3]{Colors.ENDC} {Colors.WHITE}💣  Execute Exploit{Colors.ENDC} {Colors.GREY}(Remote + Log){Colors.ENDC}    │")
        print(f"│  {Colors.GREEN}[4]{Colors.ENDC} {Colors.WHITE}🚑  Auto-Fixer{Colors.ENDC} {Colors.GREY}(Debug w/ AI){Colors.ENDC}        │")
        print(f"{Colors.HEADER}├── [ SYSTEM CONFIG ] ─────────────────────────┤{Colors.ENDC}")
        print(f"│  {Colors.YELLOW}[5]{Colors.ENDC} {Colors.WHITE}🔑  Check API Status{Colors.ENDC}                    │")
        print(f"│  {Colors.YELLOW}[6]{Colors.ENDC} {Colors.WHITE}🗑️  Reset API Key{Colors.ENDC}                       │")
        print(f"│  {Colors.YELLOW}[7]{Colors.ENDC} {Colors.WHITE}🚪  Exit{Colors.ENDC}                                │")
        print(f"{Colors.HEADER}└──────────────────────────────────────────────┘{Colors.ENDC}")
        print(f"\n{Colors.GREY}API Status: {key_status}{Colors.ENDC}")
        
        choice = input(f"\n{Colors.RED}root@bloodfang~#{Colors.ENDC} ")

        if choice == "1":
            print(f"\n{Colors.HEADER}--- PILIH BINARY TARGET ---{Colors.ENDC}")
            myself = os.path.basename(__file__)
            # Exclude file module kita sendiri
            excludes = [myself, "exploit.py", "cek.py", "config.py", "utils.py", "analyzer.py", 
                       "executor.py", "fixer.py", "promp_1.txt", "promp_fix.txt", "log_error.txt", KEY_FILE]
            
            target = utils.select_file_ext(exclude=excludes)
            if not target: print("File tidak ditemukan."); time.sleep(2); continue
            
            utils.make_executable(target)
            
            with open("analysis.txt", "w") as out:
                combined = ""
                cmds = [
                    ("FILE TYPE", f"file '{target}'"),
                    ("CHECKSEC", f"checksec --file='{target}'"),
                    ("READ ELF", f"readelf -a '{target}'"),
                    ("SYMBOL TABLE", f"readelf -s '{target}'"),
                    ("RELOCATIONS", f"readelf -r '{target}'"),
                    ("DISASSEMBLY", f"objdump -d -M intel '{target}' | head -n 500"),
                    ("STRINGS", f"strings -a '{target}' | grep -E 'flag|system|/bin/sh'"),
                    ("LTRACE", f"timeout 3 ltrace ./'{target}' < /dev/null"),
                    ("STRACE", f"timeout 3 strace ./'{target}' < /dev/null"),
                    ("ROP GADGETS", f"ROPgadget --binary '{target}' --only 'pop|ret' | head -n 20"),
                ]
                
                for title, c in cmds:
                    res = utils.run(c)
                    combined += res
                    utils.write(out, title, res)
                
                vuln_list = analyzer.detect_vulnerabilities(combined)
                vuln_text = "\n".join(vuln_list) if vuln_list else "No obvious vulnerabilities detected."
                utils.write(out, "AUTOMATIC VULNERABILITY ANALYSIS", vuln_text)
                
            print(f"\n{Colors.GREEN}[✓] Analisis selesai: analysis.txt{Colors.ENDC}")
            print(f"{Colors.BLUE}[INFO] Vulnerabilities Detected:{Colors.ENDC}")
            print(vuln_text)
            input("Enter...")

        elif choice == "2":
            print(f"\n{Colors.HEADER}--- AI AUTO EXPLOIT GENERATOR ---{Colors.ENDC}")
            api_key = utils.load_api_key()
            if not api_key: continue
            if not os.path.exists("analysis.txt"):
                print(f"{Colors.FAIL}File analysis.txt tidak ditemukan!{Colors.ENDC}"); time.sleep(2); continue
            
            print(f"{Colors.BLUE}Konfigurasi Target:{Colors.ENDC}")
            host = input("Target Host: ")
            port = input("Target Port: ")

            with open("analysis.txt", "r") as f: analysis_data = f.read()
            prompt_path = "promp_1.txt"
            if os.path.exists(prompt_path):
                with open(prompt_path, "r") as f: base_prompt = f.read()
                print(f"{Colors.GREEN}[✓] Prompt 'promp_1.txt' loaded.{Colors.ENDC}")
            else:
                base_prompt = "Create a pwntools exploit script. OUTPUT ONLY CODE."

            full_payload = f"{base_prompt}\n\n[STRICT CONTEXT]\n{analysis_data}\n\n[CONNECTION]\nTarget Host: {host}\nTarget Port: {port}"
            print(f"{Colors.CYAN}[+] Mengirim request ke Gemini...{Colors.ENDC}")
            
            response_text = utils.query_gemini_native(api_key, full_payload)
            clean_code = utils.extract_clean_code(response_text)
            
            if clean_code:
                with open("exploit.py", "w") as f: f.write(clean_code)
                print(f"\n{Colors.GREEN}[✓] Exploit saved to 'exploit.py'{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}[!] Gagal generate code.{Colors.ENDC}")
            input("\nTekan Enter...")

        elif choice == "3":
            print(f"\n{Colors.HEADER}--- EKSEKUSI EXPLOIT (LOGGING) ---{Colors.ENDC}")
            if not os.path.exists("exploit.py"):
                print(f"{Colors.FAIL}[!] File 'exploit.py' tidak ditemukan.{Colors.ENDC}")
                input("\nTekan Enter...")
            else:
                executor.run_exploit_and_log()
                
                ask_success = input(f"\n{Colors.WARNING}Exploit berhasil? (y/n) >> {Colors.ENDC}").lower()
                if ask_success == 'n':
                    print(f"\n{Colors.CYAN}[!] Mengalihkan ke Auto-Fixer...{Colors.ENDC}")
                    api_key = utils.load_api_key()
                    if api_key:
                        fixer.chat_debug_session(api_key)
                else:
                    print(f"{Colors.GREEN}[✓] Great! Kembali ke menu utama.{Colors.ENDC}")
                    time.sleep(1)

        elif choice == "4":
            api_key = utils.load_api_key()
            if api_key:
                fixer.chat_debug_session(api_key)

        elif choice == "5":
             if os.path.exists("cek.py"): os.system("python3 cek.py")
             else: print(f"{Colors.FAIL}cek.py missing.{Colors.ENDC}")
             input("\nEnter...")

        elif choice == "6":
            if os.path.exists(KEY_FILE): os.remove(KEY_FILE); print("Key reset.")
            time.sleep(1)

        elif choice == "7":
            sys.exit()

if __name__ == "__main__":
    main()
