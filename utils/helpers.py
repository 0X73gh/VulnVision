import os
import sys
from colorama import Fore, init

init(autoreset=True)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def welcome_message():
    clear_terminal()
    print(Fore.GREEN + "="*50)
    print(Fore.CYAN + "    Welcome to VulnVision - The Security Scanner")
    print(Fore.GREEN + "="*50)
    print(Fore.YELLOW + "    Please wait, initializing...\n")

def ask_user():
    url = input(Fore.CYAN + "Enter the URL to scan (e.g., http://example.com): ").strip()
    permission = input(Fore.CYAN + "Do you have permission to scan this website? (yes/no): ").strip().lower()
    
    if permission not in ["yes", "y"]:
        print(Fore.RED + "[!] You need permission to scan this website. Exiting.")
        sys.exit(1)
    
    scan_type = input(Fore.CYAN + "Enter scan type (e, m, d, s, h): ").strip().lower()
    if scan_type not in ["e", "m", "d", "s", "h"]:
        print(Fore.RED + "[!] Invalid scan type. Exiting.")
        sys.exit(1)
    
    return url, scan_type
