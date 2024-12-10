import netifaces
import ipaddress
import nmap

def get_local_subnets():
    """Berekent de subnetten van alle netwerkinterfaces die een geldig IP-adres hebben."""
    subnets = []
    try:
        # Verkrijg de netwerkinterfaces
        interfaces = netifaces.interfaces()
        print("Beschikbare netwerkinterfaces:", interfaces)

        for iface in interfaces:
            try:
                # Verkrijg het IP-adres en subnetmasker van de interface
                ip_address = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                netmask = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['netmask']

                # Exclude loopback and link-local networks
                if ip_address.startswith("127.") or ip_address.startswith("169.254."):
                    print(f"Special-purpose network {ip_address} wordt overgeslagen.")
                    continue

                # Bereken het subnet
                network = ipaddress.IPv4Network(f'{ip_address}/{netmask}', strict=False)
                print(f"Subnet gevonden op interface {iface}: {network.network_address}/24")
                subnets.append(str(network.network_address) + "/24")  # Voeg het subnet toe in /24-formaat
            except (KeyError, IndexError):
                print(f"Geen geldig IP-adres voor interface {iface}.")
                continue

        if not subnets:
            print("Geen geldig subnet gevonden op een van de interfaces.")
            return None

        return subnets

    except Exception as e:
        print(f"Fout bij ophalen subnet: {e}")
        return None

def scan_network_with_nmap(subnet):
    """Gebruik Nmap om een netwerk te scannen met besturingssysteemdetectie en een stille scan."""
    nm = nmap.PortScanner()

    try:
        print(f"Start netwerkscan op {subnet} met Nmap...")
        nm.scan(hosts=subnet, arguments='-p 22-1024 -O -T4')  # Scan poorten 22-1024, OS-detectie en stille scan
        print(f"Scanresultaten voor {subnet}:")

        results = []
        for host in nm.all_hosts():
            result = f"Host: {host} ({nm[host].hostname()})"
            result += f"\n  - Poorten: {nm[host].all_tcp()}"
            result += f"\n  - Status: {nm[host].state()}"

            # Check for OS information
            if 'osmatch' in nm[host] and nm[host]['osmatch']:
                result += f"\n  - OS: {nm[host]['osmatch'][0]['name']}"
            else:
                result += "\n  - OS: Niet gedetecteerd"

            results.append(result)

        if results:
            return "\n".join(results)
        else:
            return f"Geen actieve hosts gevonden op {subnet}."

    except Exception as e:
        return f"Fout bij uitvoeren van Nmap-scan op {subnet}: {e}"

def run():
    """Netwerkscan uitvoeren voor alle interfaces."""
    subnets = get_local_subnets()

    if subnets:
        scan_results = []
        for subnet in subnets:
            result = scan_network_with_nmap(subnet)
            scan_results.append(result)
        return "\n".join(scan_results)
    else:
        return "Geen geldige subnetten gevonden, kan geen scan uitvoeren."
