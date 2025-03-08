import requests
from colorama import Fore

def check_cors(url):
    try:
        response = requests.get(url, timeout=5)
        cors_header = response.headers.get("Access-Control-Allow-Origin", "")

        if "*" in cors_header or "null" in cors_header:
            print(Fore.YELLOW + f"[!] Potential CORS issue: {cors_header}")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[!] Failed to check CORS: {e}")
