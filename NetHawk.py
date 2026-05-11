import hashlib
import colorama
from colorama import Fore, Style
import os
import pyfiglet
from termcolor import colored
from bs4 import BeautifulSoup
import requests
import requests.exceptions
import urllib.parse
from collections import deque
import re
import socket
from concurrent.futures import ThreadPoolExecutor
import scapy.all as scapy
from scapy.all import sniff, IP, TCP, UDP, Raw
from mac_vendor_lookup import MacLookup
from scapy.layers.http import HTTPRequest, HTTPResponse 


# ASCII Banner
ascii_banner = pyfiglet.figlet_format("Herab's \t\t Recon \t\t Toolkit")
print(colored(ascii_banner, 'green'))
print(colored("Developed by: Herab Modi", 'yellow'))

# Global variable for the main loop
a = 1

def main_menu():
    print(colored("\n1. Port Scanning Tool", 'cyan'))
    print(colored("2. Network Scanner", 'cyan'))
    print(colored("3. Web Scraper", 'cyan'))
    print(colored("4. Hash Password Cracker", 'cyan'))
    print(colored("5. Scan Network Traffic", 'cyan'))
    print(colored("6. Quit", 'cyan'))
    # Prompt the user for choice
    choice = input(colored("\nChoose a tool (1-6): ", 'yellow'))
    return choice

def port_scanner():
    ascii_banner = pyfiglet.figlet_format("PORT SCANNER")
    print(colored(ascii_banner, 'cyan'))
    print(colored("\n[Port Scanner] Scan for open ports on a target system.", 'green'))

    # Regular Expression Patterns for Validation
    ip_add_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    port_range_pattern = re.compile("([0-9]+)-([0-9]+)")

    open_ports = []

    # Validate IP Address
    while True:
        ip_add_entered = input(colored("\nEnter the IP address to scan: ", 'yellow'))
        if ip_add_pattern.search(ip_add_entered):
            print(colored(f"{ip_add_entered} is a valid IP address.", 'green'))
            break
        else:
            print(colored("Invalid IP address format. Please try again.", 'red'))

    # Validate Port Range
    while True:
        print(colored("Enter the range of ports to scan (e.g., 20-80):", 'cyan'))
        port_range = input(colored("Port Range: ", 'yellow')).replace(" ", "")
        port_range_valid = port_range_pattern.search(port_range)
        if port_range_valid:
            port_min = int(port_range_valid.group(1))
            port_max = int(port_range_valid.group(2))
            break
        else:
            print(colored("Invalid port range format. Please try again.", 'red'))

    # Scan Function with Multithreading
    def scan_port(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip_add_entered, port))
                try:
                    service_name = socket.getservbyport(port)
                except OSError:
                    service_name = "Unknown Service"
                open_ports.append((port, service_name))
        except:
            pass

    print(colored("\nStarting Port Scan...\n", 'cyan'))

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(scan_port, range(port_min, port_max + 1))

    # Display Results
    if open_ports:
        print(colored("\nScan Complete! Open Ports:", 'green'))
        for port, service_name in open_ports:
            print(colored(f"Port {port} ({service_name}) is open on {ip_add_entered}.", 'yellow'))
    else:
        print(colored("\nNo open ports found in the specified range.", 'red'))

    print(colored("\n" + "-" * 120, 'red'))

def network_scanner():
    ascii_banner = pyfiglet.figlet_format("NETWORK SCANNER")
    print(colored(ascii_banner, 'cyan'))
    """Network Device Scanner Tool"""
    print(colored("\n[Network Scanner Tool] Scan the network to identify connected devices.", 'green'))

    def scan_network(ip_range):
        """Scan the network and collect device information."""
        arp_request = scapy.ARP(pdst=ip_range)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast / arp_request
        answered = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
        
        devices = []
        for element in answered:
            device_info = {
                "ip": element[1].psrc,
                "mac": element[1].hwsrc,
                "hostname": get_hostname(element[1].psrc),
                "vendor": get_vendor(element[1].hwsrc)
            }
            devices.append(device_info)
        return devices

    def get_hostname(ip):
        """Resolve hostname from IP address."""
        try:
            return socket.gethostbyaddr(ip)[0]
        except socket.herror:
            return "Unknown"

    def get_vendor(mac):
        """Resolve the vendor from MAC address."""
        try:
            return MacLookup().lookup(mac)
        except:
            return "Unknown"

    def display_results(devices):
        """Display the scan results in a tabular format."""
        print("\nIP Address\t\tMAC Address\t\t\tVendor\t\t\t\t\t\tHostname")
        print("-" * 150)
        for device in devices:
            print(colored(f"{device['ip']}\t\t{device['mac']}\t{device['vendor']}\t\t\t\t\t{device['hostname']}", 'green'))

    # Main execution
    ip_range = input(colored("\nEnter the IP range (e.g., 192.168.1.0/24): ", 'magenta'))
    print(colored("\nScanning the network. Please wait...", 'yellow'))
    devices = scan_network(ip_range)
    print(colored("\nScan Complete. Devices Found:\n", 'cyan'))
    display_results(devices)
    print(colored("\n" + "-" * 150, 'red'))

def web_scraper():
    ascii_banner = pyfiglet.figlet_format("WEB SCRAPER")
    print(colored(ascii_banner, 'cyan'))

    print(colored("\n[Web Scraper Tool] Search for all the emails in a website.", 'green'))

    # Prompt the user for the target URL
    user_url = input(colored("Enter the target URL to scan: ", 'magenta'))
    urls = deque([user_url])
    scrapped_urls = set()  # To avoid revisiting URLs
    emails = set()         # To collect unique email addresses
    count = 0              # Limit the number of URLs to scrape

    try:
        while len(urls):
            count += 1
            if count > 100:  # Stop after processing 100 URLs
                print(colored("\n[!] URL processing limit reached.", 'yellow'))
                break

            # Get the next URL from the queue
            url = urls.popleft()
            scrapped_urls.add(url)

            # Parse the URL to extract its base and path
            parts = urllib.parse.urlsplit(url)
            base_url = f"{parts.scheme}://{parts.netloc}"
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            print(colored(f"\n[{count}] Processing: {url}", 'yellow'))

            try:
                response = requests.get(url)
            except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
                print(colored("[!] Failed to fetch the URL. Skipping...", 'red'))
                continue

            # Extract emails from the page
            new_emails = set(re.findall(r'[a-zA-Z0-9.\-+_]+@[a-zA-Z0-9.\-+_]+\.[a-zA-Z]+', response.text))
            emails.update(new_emails)

            # Parse HTML and extract links
            soup = BeautifulSoup(response.text, "lxml")
            for anchor in soup.find_all("a"):
                link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
                if link.startswith('/'):
                    link = base_url + link  # Convert relative URL to absolute
                elif not link.startswith('http'):
                    link = path + link     # Handle partial URLs
                if link not in urls and link not in scrapped_urls:
                    urls.append(link)

    except KeyboardInterrupt:
        print(colored("\n[!] User interrupted the process.", 'red'))

    # Display all collected emails
    print(colored("\n[+] Collected Emails:", 'green'))
    for email in emails:
        print(colored(email, 'light_green'))

    print(colored("\n[!] Web Scraper finished.", 'green'))
    print(colored("\n" + "-" * 120, 'red'))

def hash_cracker():
    print(colored("\n[Hash Cracker Tool] Converts a hash password into a readable password", 'green'))

    ascii_banner = pyfiglet.figlet_format("HASH CRACKER")
    print(colored(ascii_banner, 'cyan'))

    def crack_hash(hash_func, target_hash, hash_type):
        pass_found = False
        try:
            with open("password.txt", "r") as file:
                for guess in file:
                    guess = guess.strip()
                    hashed_guess = hash_func(bytes(guess, 'utf-8')).hexdigest()
                    if hashed_guess.upper() == target_hash.upper():
                        print(colored(f"\nThe password for {hash_type} hash is: {guess}", 'green'))
                        pass_found = True
                        break
                    else:
                        print(colored(f"Password guess {guess} does not match, trying next...", 'yellow'))
        except FileNotFoundError:
            print(colored("\nError: Password file 'file.txt' not found. Make sure the file exists.", 'red'))
            return

        if not pass_found:
            print(colored(f"\nPassword for {hash_type} hash not found in the database.", 'red'))

        print(colored("\n" + "-" * 120, 'red'))

    while True:
        print(colored("\nEnter the type of hash to crack (Select 3 to quit):", 'blue'))
        print(colored("1. SHA1 Hash", 'blue'))
        print(colored("2. MD5 Hash",'blue'))
        print(colored("3. Quit to Main Menu",'blue'))
        choice = input("> ")

        if choice == "1":
            sha1hash = input(colored("Enter the SHA1 hash to crack: ",'magenta'))
            crack_hash(hashlib.sha1, sha1hash, "SHA1")
        elif choice == "2":
            md5hash = input(colored("Enter the MD5 hash to crack: ",'magenta'))
            crack_hash(hashlib.md5, md5hash, "MD5")
        elif choice == "3":
            break
        else:
            print(colored("Invalid choice! Please select a valid option.", 'red'))

    print(colored("\n" + "-" * 120, 'red'))


def scan_network(ip_range):                                     #USE THIS:- http://zero.webappsecurity.com/login.html?login_error=true
    """Scan the network and collect device information."""
    arp_request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for element in answered:
        device_info = {
            "ip": element[1].psrc,
            "mac": element[1].hwsrc,
            "hostname": get_hostname(element[1].psrc),
            "vendor": get_vendor(element[1].hwsrc)
        }
        devices.append(device_info)
    return devices

def get_hostname(ip):
    """Resolve hostname from IP address."""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "Unknown"

def get_vendor(mac):
    """Resolve the vendor from MAC address."""
    try:
        return MacLookup().lookup(mac)
    except:
        return "Unknown"

def display_results(devices):
    """Display the scan results in a tabular format."""
    print("\nIP Address\t\tMAC Address\t\t\tVendor\t\t\tHostname")
    print("-" * 100)
    for idx, device in enumerate(devices):
        print(colored(f"{idx + 1}. {device['ip']}\t{device['mac']}\t{device['vendor']}\t{device['hostname']}", 'green'))

def process_packet(packet):
    """Processes sniffed packets to extract relevant information."""
    if packet.haslayer(scapy.IP):
        src_ip = packet[scapy.IP].src
        dst_ip = packet[scapy.IP].dst
        protocol = "Unknown"

        if packet.haslayer(scapy.TCP):
            protocol = "TCP"
        elif packet.haslayer(scapy.UDP):
            protocol = "UDP"

        print(colored(f"[+] Packet: {src_ip} -> {dst_ip} | Protocol: {protocol}", 'yellow'))

    # Extract HTTP Data
    if packet.haslayer(HTTPRequest):
        http_layer = packet[HTTPRequest]
        url = f"http://{http_layer.Host.decode()}{http_layer.Path.decode()}"
        print(colored(f"[HTTP] {url}", 'blue'))

    if packet.haslayer(scapy.Raw):
        payload = packet[scapy.Raw].load.decode(errors='ignore')

        # 🔥 FIXED: Improved credential extraction (captures both username & password)
        credentials = re.findall(r'(?i)(username|user|email|login|userid|pass|password)=([^&\s]+)', payload)

        if credentials:
            cred_dict = {}
            for key, value in credentials:
                cred_dict[key.lower()] = value  # Normalize keys to lowercase

            print(colored(f"[!] Possible Credentials Captured: {cred_dict}", 'red'))


def sniff_packets(target_ip):
    """Sniff packets and filter only those related to the target IP."""
    print(colored(f"\n[*] Starting packet sniffing for {target_ip}. Press Ctrl+C to stop.\n", 'cyan'))
    scapy.sniff(filter=f"host {target_ip}", prn=process_packet, store=False)

def network_sniffer():
    """Main function to scan network and allow sniffing."""
    ascii_banner = pyfiglet.figlet_format("Traffic Scanner")
    print(colored(ascii_banner, 'cyan'))
    ip_range = input(colored("\nEnter the IP range (e.g., 192.168.1.0/24): ", 'magenta'))
    print(colored("\nScanning the network. Please wait...", 'yellow'))
    devices = scan_network(ip_range)
    
    if not devices:
        print(colored("\nNo devices found on the network!", 'red'))
        return

    print(colored("\nScan Complete. Devices Found:\n", 'cyan'))
    display_results(devices)

    # Allow user to select a device for sniffing
    while True:
        try:
            choice = int(input(colored("\nEnter the number of the device to sniff packets from (0 to exit): ", 'yellow')))
            if choice == 0:
                return
            if 1 <= choice <= len(devices):
                selected_ip = devices[choice - 1]["ip"]
                print(colored(f"\nStarting packet sniffing for {selected_ip}...\n", 'green'))
                sniff_packets(selected_ip)
                break
            else:
                print(colored("\nInvalid selection! Please choose a valid number.", 'red'))
        except ValueError:
            print(colored("\nInvalid input! Please enter a number.", 'red'))

# Run the network sniffer
#network_sniffer()

def quit_tool():
    global a  # Use the global 'a' variable
    a = 0

def main():
    while a == 1:
        choice = main_menu()
        if choice == '1':
            port_scanner()
        elif choice == '2':
            network_scanner()
        elif choice == '3':
            web_scraper()
        elif choice == '4':
            hash_cracker()
        elif choice == '5':
            network_sniffer()
        elif choice == '6':
            quit_tool()
        else:
            print(colored("\nInvalid choice! Please select a valid option.", 'red'))

if __name__ == "__main__":
    main()