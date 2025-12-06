# executor.py
import subprocess
import threading
import queue
import time
import os
from config import Colors, SILENCE_TIMEOUT

def enqueue_output(out, q):
    """Helper untuk membaca stdout di thread terpisah"""
    try:
        for line in iter(out.readline, ''):
            q.put(line)
        out.close()
    except: pass

def run_exploit_and_log():
    """
    Menjalankan exploit.py dengan monitoring.
    - AUTO-KILL jika tidak ada output selama SILENCE_TIMEOUT detik.
    """
    print(f"{Colors.CYAN}[+] Menjalankan Exploit (REMOTE) & Monitoring Stuck...{Colors.ENDC}")
    print(f"{Colors.BLUE}[INFO] Timeout Hening diset ke: {SILENCE_TIMEOUT} detik.{Colors.ENDC}")
    print(f"{Colors.WARNING}--- OUTPUT START ---{Colors.ENDC}")
    
    if os.path.exists("log_error.txt"):
        os.remove("log_error.txt")

    log_buffer = []
    
    try:
        process = subprocess.Popen(
            ["python3", "exploit.py", "REMOTE"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True,
            bufsize=1, 
            universal_newlines=True
        )

        q = queue.Queue()
        t = threading.Thread(target=enqueue_output, args=(process.stdout, q))
        t.daemon = True
        t.start()

        last_activity = time.time()
        is_stuck = False

        while True:
            try:
                line = q.get(timeout=0.1)
                print(line, end='')
                log_buffer.append(line)
                last_activity = time.time()
            except queue.Empty:
                if time.time() - last_activity > SILENCE_TIMEOUT:
                    print(f"\n{Colors.FAIL}[!!!] STUCK DETECTED (No Output > {SILENCE_TIMEOUT}s) [!!!]{Colors.ENDC}")
                    print(f"{Colors.FAIL}[!!!] Killing process...{Colors.ENDC}")
                    log_buffer.append(f"\n[SYSTEM] PROCESS KILLED DUE TO INACTIVITY ({SILENCE_TIMEOUT}s timeout).")
                    process.kill()
                    is_stuck = True
                    break

            if process.poll() is not None and q.empty():
                break

        print(f"\n{Colors.WARNING}--- OUTPUT END ---{Colors.ENDC}")

        with open("log_error.txt", "w") as f:
            f.writelines(log_buffer)
        
        if is_stuck:
             print(f"\n{Colors.RED}[!] Exploit dihentikan paksa karena macet.{Colors.ENDC}")
             print(f"{Colors.BLUE}[TIP] Gunakan Menu [4] (Fix Exploit) untuk membetulkan ini.{Colors.ENDC}")
        else:
             print(f"\n{Colors.GREEN}[✓] Eksekusi selesai normal. Log disimpan.{Colors.ENDC}")

    except Exception as e:
        print(f"\n{Colors.FAIL}[!] Gagal menjalankan exploit: {e}{Colors.ENDC}")
