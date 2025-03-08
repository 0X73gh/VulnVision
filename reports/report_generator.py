import datetime
from colorama import Fore

def generate_report(url):
    """Generates a basic vulnerability report."""
    report_name = f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_name, "w") as file:
        file.write(f"Vulnerability Report for: {url}\n")
        file.write("=" * 50 + "\n")
        file.write("This is a summary of detected vulnerabilities.\n")
    
    print(Fore.GREEN + f"[+] Report saved as {report_name}")
