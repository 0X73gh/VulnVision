import requests
from colorama import Fore

def subdomain_scan(domain):
    """Finds subdomains using a public API."""
    print(Fore.CYAN + "[*] Searching for subdomains...")
    try:
        response = requests.get(f"https://crt.sh/?q={domain}&output=json")
        if response.status_code == 200:
            subdomains = set(entry["name_value"] for entry in response.json())
            for sub in subdomains:
                print(Fore.YELLOW + f"  - {sub}")
    except Exception as e:
        print(Fore.RED + f"[!] Error scanning subdomains: {e}")
