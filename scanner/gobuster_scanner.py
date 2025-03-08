import subprocess
from colorama import Fore

def gobuster_scan(url):
    """Runs Gobuster to discover hidden directories."""
    try:
        print(Fore.CYAN + "[*] Running Gobuster scan...")
        result = subprocess.run(["gobuster", "dir", "-u", url, "-w", "/usr/share/wordlists/dirb/common.txt"],
                                capture_output=True, text=True)
        print(Fore.YELLOW + result.stdout)
    except Exception as e:
        print(Fore.RED + f"[!] Gobuster scan failed: {e}")
