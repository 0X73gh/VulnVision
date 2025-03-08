import requests
from colorama import Fore

def check_leaked_data(email):
    """Checks if an email appears in data breaches."""
    print(Fore.CYAN + f"[*] Checking leaks for {email}...")
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"User-Agent": "VulnScanner"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print(Fore.YELLOW + "[!] This email has been found in data breaches.")
    else:
        print(Fore.GREEN + "[+] No leaks found.")
