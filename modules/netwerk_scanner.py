import time
import requests
import nmap
import ipaddress
import psutil

def run():
    """Netwerkscan uitvoeren op alle beschikbare interfaces."""
    # Verkrijg de lokale netwerkinterfaces en hun subnetten
    
    interfaces = psutil.net_if_addrs()
    
    print("Beschikbare netwerkinterfaces:")
    for interface_name, interface_addresses in interfaces.items():
        print(f"{interface_name}:")
        for address in interface_addresses:
            if address.family == psutil.AF_INET:
                subnet = ipaddress.IPv4Network(address.netmask, strict=False)
                print(f"  - IP: {address.address}, Subnet: {subnet}")
                scan_network(subnet)

def scan_network(subnet):
    """Voer een Nmap scan uit voor een specifiek subnet."""
    print(f"Start netwerkscan op {subnet} met Nmap...")
    nm = nmap.PortScanner()
    nm.scan(hosts=str(subnet), arguments='-p 22,80,443')

    # Verwerk de resultaten
    results = []
    for host in nm.all_hosts():
        if nm[host].state() == "up":
            result = f"Host: {host} ({nm[host].hostname()})"
            for proto in nm[host].all_protocols():
                lport = nm[host][proto].keys()
                for port in lport:
                    result += f"  - Poort: {port} (Status: {nm[host][proto][port]['state']})"
            results.append(result)

    if results:
        return "\n".join(results)
    else:
        return f"Geen actieve hosts gevonden op {subnet}."

