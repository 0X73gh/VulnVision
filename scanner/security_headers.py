import requests
from colorama import Fore

def check_security_headers(url):
    try:
        response = requests.get(url, timeout=5)
        headers = response.headers

        missing_headers = [h for h in ["Permissions-Policy", "Content-Security-Policy", "Strict-Transport-Security"] if h not in headers]

        if missing_headers:
            print(Fore.YELLOW + f"[!] Missing security headers: {', '.join(missing_headers)}")
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[!] Failed to check security headers: {e}")
