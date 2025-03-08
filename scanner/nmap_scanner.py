import subprocess
import threading
from colorama import Fore

def run_nmap_scan(host):
    """Runs an Nmap scan on the target host."""
    try:
        print(Fore.CYAN + "[*] Running Nmap scan...")
        result = subprocess.run(["nmap", "-sV", host], capture_output=True, text=True)
        print(Fore.YELLOW + result.stdout)
    except Exception as e:
        print(Fore.RED + f"[!] Nmap scan failed: {e}")

def nmap_scan(host):
    """Runs Nmap in a separate thread to avoid blocking execution."""
    thread = threading.Thread(target=run_nmap_scan, args=(host,))
    thread.start()
    return thread
