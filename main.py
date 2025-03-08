import sys
import os
import time
import threading
import random
from datetime import datetime, timedelta

from utils.helpers import welcome_message, ask_user
from scanner import (security_headers, outdated_software, cors, xss, 
                    sql_injection, port_scanner, nmap_scanner, 
                    gobuster_scanner, exploit_db_scanner)
from reports.report_generator import generate_report

# Terminal colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Store scan status for display
scan_status = {}

# Estimated time for each scan type (in seconds)
# These values should be adjusted based on actual performance
SCAN_TIMES = {
    "Security Headers": {"e": 5, "m": 5, "d": 5, "s": 5},
    "Outdated Software": {"e": 10, "m": 10, "d": 10, "s": 10},
    "CORS Check": {"e": 8, "m": 8, "d": 8, "s": 8},
    "XSS Check": {"m": 20, "d": 20, "s": 20},
    "SQL Injection": {"m": 25, "d": 25, "s": 25},
    "Port Scan": {"d": 30, "s": 30},
    "Nmap Scan": {"e": 40, "m": 40, "d": 60, "s": 60},
    "Directory Enum": {"s": 45},
    "Exploit DB": {"s": 15}
}

def clear_screen():
    """Clear terminal screen based on operating system"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    """Print a simple ASCII banner for VulnVision"""
    banner = f"""
{Colors.BLUE}{Colors.BOLD}╔═══════════════════════════════════════════════════════╗{Colors.ENDC}
{Colors.BLUE}{Colors.BOLD}║                    VULNVISION                         ║{Colors.ENDC}
{Colors.BLUE}{Colors.BOLD}║               Security Scanner Tool                   ║{Colors.ENDC}
{Colors.BLUE}{Colors.BOLD}╚═══════════════════════════════════════════════════════╝{Colors.ENDC}
 Version 1.0.0
 {Colors.CYAN}Created by: 0X73{Colors.ENDC}
 {Colors.CYAN}https://github.com/0X73gh{Colors.ENDC}
"""
    print(banner)

def print_menu():
    """Print scan type menu"""
    menu = f"""
{Colors.BOLD}AVAILABLE SCAN TYPES:{Colors.ENDC}
{Colors.CYAN}[e]{Colors.ENDC} Essential - Basic security headers and configuration checks
{Colors.CYAN}[m]{Colors.ENDC} Medium    - Essential + Common web vulnerabilities (XSS, SQLi)
{Colors.CYAN}[d]{Colors.ENDC} Deep      - Medium + Port scanning and network analysis 
{Colors.CYAN}[s]{Colors.ENDC} Stealth   - Deep + Directory enumeration and exploit matching
"""
    print(menu)

def get_user_input():
    """Get URL and scan type with simple validation"""
    print(f"{Colors.BOLD}Enter target URL (including http:// or https://): {Colors.ENDC}", end='')
    url = input().strip()
    
    while not (url.startswith('http://') or url.startswith('https://')):
        print(f"{Colors.RED}Error: URL must start with http:// or https://{Colors.ENDC}")
        print(f"{Colors.BOLD}Enter target URL: {Colors.ENDC}", end='')
        url = input().strip()
    
    valid_options = ['e', 'm', 'd', 's']
    print(f"{Colors.BOLD}Select scan type [{'/'.join(valid_options)}] (default: m): {Colors.ENDC}", end='')
    scan_type = input().strip().lower()
    
    if not scan_type:
        scan_type = 'm'
    
    while scan_type not in valid_options:
        print(f"{Colors.RED}Error: Invalid option. Please choose from {', '.join(valid_options)}{Colors.ENDC}")
        print(f"{Colors.BOLD}Select scan type [{'/'.join(valid_options)}]: {Colors.ENDC}", end='')
        scan_type = input().strip().lower()
    
    # Confirm before proceeding with invasive scans
    if scan_type in ['d', 's']:
        scan_name = 'Deep' if scan_type == 'd' else 'Stealth'
        print(f"\n{Colors.YELLOW}WARNING: You've selected a {scan_name} scan.{Colors.ENDC}")
        print(f"{Colors.YELLOW}This may generate significant traffic to the target.{Colors.ENDC}")
        print(f"{Colors.BOLD}Do you want to proceed? [y/n]: {Colors.ENDC}", end='')
        confirm = input().strip().lower()
        
        if confirm != 'y':
            return get_user_input()
    
    return url, scan_type

def create_progress_bar(percentage, width=40):
    """Create a progress bar string based on percentage"""
    completed = int(width * percentage / 100)
    remaining = width - completed
    bar = f"[{Colors.GREEN}{'█' * completed}{Colors.YELLOW}{'▒' * remaining}{Colors.ENDC}]"
    return f"{bar} {percentage:3.0f}%"

def format_time_remaining(seconds):
    """Format seconds into mm:ss format"""
    if seconds < 0:
        return "00:00"
    
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def update_scan_status(scan_name, status, progress=0, total_time=0, result=None):
    """Update scan status dictionary with progress information"""
    if scan_name not in scan_status:
        # Initialize if first time
        scan_status[scan_name] = {
            'status': status,
            'progress': progress,
            'start_time': datetime.now(),
            'total_time': total_time,
            'result': result,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        }
    else:
        # Update existing entry
        scan_status[scan_name].update({
            'status': status,
            'progress': progress,
            'result': result,
            'timestamp': datetime.now().strftime("%H:%M:%S")
        })
        
        # If completed, update total_time to actual time
        if status == 'Complete' and progress == 100:
            elapsed = (datetime.now() - scan_status[scan_name]['start_time']).total_seconds()
            scan_status[scan_name]['total_time'] = elapsed

def print_scan_status():
    """Print current scan status with progress bars"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.BOLD}SCAN STATUS:{Colors.ENDC}")
    print("-" * 76)
    
    # Calculate overall progress
    total_scans = len(scan_status)
    if total_scans > 0:
        completed_scans = sum(1 for details in scan_status.values() if details['status'] == 'Complete')
        running_progress = sum(details['progress'] for details in scan_status.values()) / total_scans
        
        # Calculate overall ETA based on remaining scans
        running_scans = [s for s in scan_status.values() if s['status'] == 'Running']
        eta_seconds = 0
        for scan in running_scans:
            if scan['progress'] > 0:
                remaining_pct = 100 - scan['progress']
                time_elapsed = (datetime.now() - scan['start_time']).total_seconds()
                time_per_percent = time_elapsed / scan['progress'] if scan['progress'] > 0 else 0
                scan_eta = remaining_pct * time_per_percent
                eta_seconds = max(eta_seconds, scan_eta)
        
        # Add time for pending scans
        pending_scans = [s for s in scan_status.values() if s['status'] == 'Pending']
        eta_seconds += sum(s['total_time'] for s in pending_scans)
        
        # Print overall progress
        overall_bar = create_progress_bar(running_progress)
        eta_str = format_time_remaining(eta_seconds)
        print(f"{Colors.BOLD}Overall Progress: {overall_bar} ETA: {eta_str}{Colors.ENDC}")
        print(f"Completed: {completed_scans}/{total_scans} scans")
        print("-" * 76)
    
    # Print table header
    print(f"{'Scan Type':<20} {'Status':<10} {'Progress':<44}")
    print("-" * 76)
    
    # Print scan details with progress bars
    for scan_name, details in scan_status.items():
        status_color = Colors.GREEN if details['status'] == 'Complete' else Colors.YELLOW
        status_text = f"{status_color}{details['status']}{Colors.ENDC}"
        
        # Progress bar
        if details['status'] == 'Complete':
            progress_bar = create_progress_bar(100)
        elif details['status'] == 'Running':
            progress_bar = create_progress_bar(details['progress'])
        else:  # Pending
            progress_bar = create_progress_bar(0)
        
        print(f"{scan_name:<20} {status_text:<16} {progress_bar}")
        
        # For running scans, show estimated time remaining
        if details['status'] == 'Running' and details['progress'] > 0:
            elapsed = (datetime.now() - details['start_time']).total_seconds()
            time_per_percent = elapsed / details['progress']
            remaining = (100 - details['progress']) * time_per_percent
            remaining_str = format_time_remaining(remaining)
            print(f"{' ' * 30}Est. remaining: {remaining_str}")
    
    print("-" * 76)

def simulate_scan_progress(scan_name, scan_time, stop_event):
    """Simulate progress updates for a scan to give visual feedback"""
    start_time = time.time()
    total_time = scan_time  # seconds
    
    # Update progress every 0.5 seconds
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        if elapsed >= total_time:
            update_scan_status(scan_name, "Complete", 100)
            break
            
        # Calculate progress percentage (0-100)
        progress = min(99, (elapsed / total_time) * 100)
        update_scan_status(scan_name, "Running", progress)
        
        time.sleep(0.5)

def run_scan_with_progress(url, scan_type):
    """Run scans with progress bars and estimated time"""
    host = url.replace("http://", "").replace("https://", "").split("/")[0]
    
    # Dictionary to hold simulation threads and their stop events
    sim_threads = {}
    
    # Calculate and display estimated total scan time
    total_est_time = 0
    active_scans = []
    
    # Add essential scans
    if scan_type in ["e", "m", "d", "s"]:
        active_scans.extend(["Security Headers", "Outdated Software", "CORS Check"])
        total_est_time += SCAN_TIMES["Security Headers"][scan_type]
        total_est_time += SCAN_TIMES["Outdated Software"][scan_type]
        total_est_time += SCAN_TIMES["CORS Check"][scan_type]
    
    # Add medium scans
    if scan_type in ["m", "d", "s"]:
        active_scans.extend(["XSS Check", "SQL Injection"])
        total_est_time += SCAN_TIMES["XSS Check"][scan_type]
        total_est_time += SCAN_TIMES["SQL Injection"][scan_type]
    
    # Add deep scans
    if scan_type in ["d", "s"]:
        active_scans.append("Port Scan")
        total_est_time += SCAN_TIMES["Port Scan"][scan_type]
    
    # Always add nmap scan
    active_scans.append("Nmap Scan")
    total_est_time += SCAN_TIMES["Nmap Scan"][scan_type]
    
    # Add stealth scans
    if scan_type in ["s"]:
        active_scans.extend(["Directory Enum", "Exploit DB"])
        total_est_time += SCAN_TIMES["Directory Enum"][scan_type]
        total_est_time += SCAN_TIMES["Exploit DB"][scan_type]
    
    # Initialize all scans as pending with their estimated times
    for scan_name in active_scans:
        update_scan_status(scan_name, "Pending", 0, SCAN_TIMES[scan_name][scan_type])
    
    # Display initial status
    print_scan_status()
    
    # Status updater thread
    stop_status_update = threading.Event()
    
    def status_updater():
        while not stop_status_update.is_set():
            print_scan_status()
            time.sleep(0.5)
    
    status_thread = threading.Thread(target=status_updater)
    status_thread.daemon = True
    status_thread.start()
    
    try:
        # Run essential scans
        if scan_type in ["e", "m", "d", "s"]:
            # Security Headers
            update_scan_status("Security Headers", "Running", 0)
            sec_headers_stop = threading.Event()
            sec_headers_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("Security Headers", SCAN_TIMES["Security Headers"][scan_type], sec_headers_stop)
            )
            sec_headers_thread.start()
            sim_threads["Security Headers"] = (sec_headers_thread, sec_headers_stop)
            
            # Actually run the scan
            result = security_headers.check_security_headers(url)
            
            # Stop simulation and mark as complete
            sec_headers_stop.set()
            sec_headers_thread.join()
            update_scan_status("Security Headers", "Complete", 100, result="See report")
            
            # Outdated Software
            update_scan_status("Outdated Software", "Running", 0)
            outdated_stop = threading.Event()
            outdated_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("Outdated Software", SCAN_TIMES["Outdated Software"][scan_type], outdated_stop)
            )
            outdated_thread.start()
            sim_threads["Outdated Software"] = (outdated_thread, outdated_stop)
            
            # Actually run the scan
            result = outdated_software.check_outdated_software(url)
            
            # Stop simulation and mark as complete
            outdated_stop.set()
            outdated_thread.join()
            update_scan_status("Outdated Software", "Complete", 100, result="See report")
            
            # CORS Check
            update_scan_status("CORS Check", "Running", 0)
            cors_stop = threading.Event()
            cors_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("CORS Check", SCAN_TIMES["CORS Check"][scan_type], cors_stop)
            )
            cors_thread.start()
            sim_threads["CORS Check"] = (cors_thread, cors_stop)
            
            # Actually run the scan
            result = cors.check_cors(url)
            
            # Stop simulation and mark as complete
            cors_stop.set()
            cors_thread.join()
            update_scan_status("CORS Check", "Complete", 100, result="See report")
        
        # Run medium scans
        if scan_type in ["m", "d", "s"]:
            # XSS Check
            update_scan_status("XSS Check", "Running", 0)
            xss_stop = threading.Event()
            xss_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("XSS Check", SCAN_TIMES["XSS Check"][scan_type], xss_stop)
            )
            xss_thread.start()
            sim_threads["XSS Check"] = (xss_thread, xss_stop)
            
            # Actually run the scan
            result = xss.check_xss(url)
            
            # Stop simulation and mark as complete
            xss_stop.set()
            xss_thread.join()
            update_scan_status("XSS Check", "Complete", 100, result="See report")
            
            # SQL Injection
            update_scan_status("SQL Injection", "Running", 0)
            sql_stop = threading.Event()
            sql_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("SQL Injection", SCAN_TIMES["SQL Injection"][scan_type], sql_stop)
            )
            sql_thread.start()
            sim_threads["SQL Injection"] = (sql_thread, sql_stop)
            
            # Actually run the scan
            result = sql_injection.check_sql_injection(url)
            
            # Stop simulation and mark as complete
            sql_stop.set()
            sql_thread.join()
            update_scan_status("SQL Injection", "Complete", 100, result="See report")
        
        # Run deep scans
        if scan_type in ["d", "s"]:
            # Port Scan
            update_scan_status("Port Scan", "Running", 0)
            port_stop = threading.Event()
            port_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("Port Scan", SCAN_TIMES["Port Scan"][scan_type], port_stop)
            )
            port_thread.start()
            sim_threads["Port Scan"] = (port_thread, port_stop)
            
            # Actually run the scan
            result = port_scanner.scan_ports(host)
            
            # Stop simulation and mark as complete
            port_stop.set()
            port_thread.join()
            update_scan_status("Port Scan", "Complete", 100, result="See report")
        
        # Run nmap scan
        update_scan_status("Nmap Scan", "Running", 0)
        nmap_stop = threading.Event()
        nmap_sim_thread = threading.Thread(
            target=simulate_scan_progress,
            args=("Nmap Scan", SCAN_TIMES["Nmap Scan"][scan_type], nmap_stop)
        )
        nmap_sim_thread.start()
        sim_threads["Nmap Scan"] = (nmap_sim_thread, nmap_stop)
        
        # Actually run the nmap scan
        nmap_thread = nmap_scanner.nmap_scan(host)
        
        # Run stealth scans
        if scan_type in ["s"]:
            # Directory Enum
            update_scan_status("Directory Enum", "Running", 0)
            dir_stop = threading.Event()
            dir_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("Directory Enum", SCAN_TIMES["Directory Enum"][scan_type], dir_stop)
            )
            dir_thread.start()
            sim_threads["Directory Enum"] = (dir_thread, dir_stop)
            
            # Actually run the scan
            result = gobuster_scanner.gobuster_scan(url)
            
            # Stop simulation and mark as complete
            dir_stop.set()
            dir_thread.join()
            update_scan_status("Directory Enum", "Complete", 100, result="See report")
            
            # Exploit DB
            update_scan_status("Exploit DB", "Running", 0)
            exploit_stop = threading.Event()
            exploit_thread = threading.Thread(
                target=simulate_scan_progress,
                args=("Exploit DB", SCAN_TIMES["Exploit DB"][scan_type], exploit_stop)
            )
            exploit_thread.start()
            sim_threads["Exploit DB"] = (exploit_thread, exploit_stop)
            
            # Actually run the scan
            result = exploit_db_scanner.exploit_db_scan(host)
            
            # Stop simulation and mark as complete
            exploit_stop.set()
            exploit_thread.join()
            update_scan_status("Exploit DB", "Complete", 100, result="See report")
        
        # Wait for nmap to finish
        nmap_thread.join()
        
        # Stop simulation and mark as complete
        nmap_stop.set()
        nmap_sim_thread.join()
        update_scan_status("Nmap Scan", "Complete", 100, result="See report")
        
        # Generate report
        print_scan_status()
        print(f"\n{Colors.GREEN}All scans completed! Generating report...{Colors.ENDC}")
        generate_report(url)
        
    except Exception as e:
        # Stop all simulation threads
        for thread_name, (thread, stop_event) in sim_threads.items():
            stop_event.set()
            
        raise e
        
    finally:
        # Stop status updater thread
        stop_status_update.set()
        status_thread.join()

def print_summary():
    """Print scan summary"""
    clear_screen()
    print_banner()
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}VULNVISION SCAN COMPLETED{Colors.ENDC}")
    print("-" * 70)
    
    # Calculate total elapsed time
    start_times = [details['start_time'] for details in scan_status.values()]
    if start_times:
        first_scan = min(start_times)
        total_elapsed = (datetime.now() - first_scan).total_seconds()
        mins, secs = divmod(int(total_elapsed), 60)
        elapsed_str = f"{mins:02d}:{secs:02d}"
    else:
        elapsed_str = "00:00"
    
    # Count findings (this is a placeholder - you would extract real data)
    total_findings = 0
    for scan_name, details in scan_status.items():
        if details['status'] == 'Complete':
            # Increment total (in a real implementation, you'd get actual counts)
            total_findings += 1
    
    print(f"Target: {Colors.BOLD}{list(scan_status.values())[0]['target'] if scan_status else 'Unknown'}{Colors.ENDC}")
    print(f"Scan date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total scan time: {elapsed_str}")
    print(f"Total scans completed: {len(scan_status)}")
    print(f"Potential security issues found: {total_findings}")
    print(f"Report generated: {Colors.CYAN}vulnvision_report.html{Colors.ENDC}")
    print("-" * 70)

def main():
    """Main function to run VulnVision with progress bars"""
    try:
        clear_screen()
        print_banner()
        print_menu()
        
        url, scan_type = get_user_input()
        
        print(f"\n{Colors.BOLD}Starting {scan_type.upper()} scan on: {url}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Press Ctrl+C to abort the scan at any time.{Colors.ENDC}")
        time.sleep(2)  # Give user time to read
        
        run_scan_with_progress(url, scan_type)
        
        print_summary()
        
        print(f"\n{Colors.BOLD}Would you like to run another scan? [y/n]: {Colors.ENDC}", end='')
        another = input().strip().lower()
        if another == 'y':
            main()
        else:
            print(f"\n{Colors.BLUE}Thank you for using VulnVision!{Colors.ENDC}")
            
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Scan aborted by user.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {str(e)}{Colors.ENDC}")
        sys.exit(1)

if __name__ == "__main__":
    main()
