import requests
from colorama import Fore

ADMIN_PATHS = ["/admin", "/admin/login", "/login", "/dashboard", "/wp-admin"]

def find_admin_panel(url):
    """Attempts to find an admin panel."""
    print(Fore.CYAN + "[*] Searching for admin panel...")
    for path in ADMIN_PATHS:
        full_url = f"{url}{path}"
        response = requests.get(full_url)
        if response.status_code == 200:
            print(Fore.YELLOW + f"  [+] Possible admin panel: {full_url}")
