# analyzer.py
import re

def detect_vulnerabilities(all_data):
    vuln = []

    # --- STACK BUFFER OVERFLOW ---
    bof_patterns = [
        r"gets", r"strcpy", r"strcat", r"sprintf",
        r"strncpy", r"memcpy", r"read\(.*\,.*\, [1-9][0-9]{3,}\)"
    ]
    if any(re.search(p, all_data) for p in bof_patterns):
        vuln.append("🟥 Possible Stack Buffer Overflow")

    # --- FORMAT STRING ---
    if re.search(r"printf\s*\(\s*[a-zA-Z0-9_]+\s*\)", all_data):
        vuln.append("🟥 Possible Format String Vulnerability")

    # --- WIN / BACKDOOR ---
    if "win" in all_data or "/bin/sh" in all_data or "system" in all_data:
        vuln.append("🟧 Suspicious backdoor function (win/system/binsh)")

    # --- HEAP ---
    if "malloc" in all_data or "free" in all_data:
        vuln.append("🟨 Possible Heap Exploitation (malloc/free used)")

    # --- RELRO / GOT ---
    if "No RELRO" in all_data:
        vuln.append("🟧 GOT Overwrite possible (No RELRO)")

    # --- CANARY ---
    if "Canary: No" in all_data or "Canary                                  : No" in all_data:
        vuln.append("🟧 No Canary – Overflow easier")

    # --- NX ---
    if "NX: ENABLED" in all_data or "NX                                      : Yes" in all_data:
        vuln.append("🟦 NX Enabled – ROP or ret2libc required")

    # --- PIE ---
    if "PIE: No" in all_data or "PIE                                     : No" in all_data:
        vuln.append("🟩 PIE disabled – Static addresses → ret2win/ROP easier")

    # --- FORMAT STRING SPECIFIC ---
    if re.search(r"%[0-9]*\$[sdxpn]", all_data):
        vuln.append("🟥 Format String specifiers detected")

    # --- DOUBLE FREE / UAF ---
    if re.search(r"free\s*\(.*\)\s*free\s*\(.*\)", all_data):
        vuln.append("🟥 Potential Double-Free")

    return vuln
