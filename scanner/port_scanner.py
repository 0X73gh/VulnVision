import socket
import threading
from tqdm import tqdm
from colorama import Fore

def check_port(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((host, port)) == 0:
            print(Fore.YELLOW + f"[!] Port {port} is open!")
        s.close()
    except socket.gaierror:
        print(Fore.RED + f"[!] Could not resolve {host}. Skipping port scan.")

def scan_ports(host):
    common_ports = [21, 22, 23, 25, 53, 80, 443, 3306, 5432, 8080, 110]
    threads = []

    for port in tqdm(common_ports, desc="Scanning Ports", unit="port"):
        thread = threading.Thread(target=check_port, args=(host, port))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
