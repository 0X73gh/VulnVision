import requests
from colorama import Fore

def check_sql_injection(url):
    try:
        test_url = url + "?id=1' OR '1'='1"
        response = requests.get(test_url, timeout=5)

        if "syntax error" in response.text.lower() or "mysql" in response.text.lower():
            print(Fore.YELLOW + "[!] Potential SQL Injection vulnerability detected!")
        else:
            print(Fore.GREEN + "[*] No SQL Injection detected.")

    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"[!] Failed to check SQL Injection: {e}")
