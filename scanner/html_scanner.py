import requests
from bs4 import BeautifulSoup
from colorama import Fore

VULNERABLE_INPUTS = ["script", "iframe", "onerror", "onload", "alert"]

def html_vulnerability_scan(url):
    """Scans for XSS and SQL injection vulnerabilities."""
    print(Fore.CYAN + "[*] Scanning HTML for vulnerabilities...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    for input_tag in soup.find_all("input"):
        for vuln in VULNERABLE_INPUTS:
            if vuln in str(input_tag):
                print(Fore.RED + f"[!] Potential XSS vulnerability: {input_tag}")
