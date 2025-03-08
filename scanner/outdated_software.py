import requests
from colorama import Fore

def check_outdated_software(url):
    try:
        response = requests.get(url, timeout=5)
        server_header = response.headers.get("Server", "Unknown")
        powered_by = response.headers.get("X-Powered-By", "Unknown")

        if "apache" in server_header.lower() or "nginx" in server_header.lower():
            print(Fore.YELLOW + f"[!] Server software detected: {server_header}")

        if powered_by != "Unknown":
            print(Fore.YELLOW + f"[!] X-Powered-By detected: {powered_by}")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[!] Failed to check software versions: {e}")
