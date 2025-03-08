import requests
from colorama import Fore

def check_xss(url):
    try:
        test_url = url + "?q=<script>alert(1)</script>"
        response = requests.get(test_url, timeout=5)

        if "<script>alert(1)</script>" in response.text:
            print(Fore.YELLOW + "[!] Potential XSS vulnerability detected!")
        else:
            print(Fore.GREEN + "[*] No XSS detected.")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[!] Failed to check XSS: {e}")
