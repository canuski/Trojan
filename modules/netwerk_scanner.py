import nmap
import netifaces
import ipaddress
import platform

def get_local_subnet():
    """Berekent het subnet op basis van het lokale IP-adres en subnetmasker, controleert eerst Ethernet, dan Wi-Fi."""
    try:
        # Log alle beschikbare netwerkinterfaces
        print("Beschikbare netwerkinterfaces:")
        interfaces_to_check = netifaces.interfaces()
        print(interfaces_to_check)

        # Eerst proberen we 'Ethernet', daarna 'Wi-Fi' voor Windows
        interfaces_to_check = ['Ethernet', 'Wi-Fi']
        
        for iface in interfaces_to_check:
            if iface in interfaces_to_check:
                try:
                    # Verkrijg het IP-adres en subnetmasker van de interface
                    ip_address = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
                    netmask = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['netmask']
                    
                    # Bereken het subnet
                    network = ipaddress.IPv4Network(f'{ip_address}/{netmask}', strict=False)
                    print(f"Subnet gevonden op {iface}: {network.network_address}/24")
                    return str(network.network_address) + "/24"  # Subnet in /24-formaat (bijvoorbeeld 192.168.1.0/24)
                except KeyError:
                    # Als de interface geen IP-adres heeft, gaan we naar de volgende
                    print(f"Geen IP-adres voor interface: {iface}")
                    continue
        
        # Als we hier komen, is geen van de interfaces geschikt
        print("Geen geldig subnet gevonden op Ethernet of Wi-Fi.")
        return None

    except Exception as e:
        print(f"Fout bij ophalen subnet: {e}")
        return None

def run():
    """
    Voert een netwerk scan uit op het dynamisch berekende subnet.
    Retourneert een string met de resultaten van de scan.
    """
    # Verkrijg dynamisch het lokale subnet
    subnet = get_local_subnet()
    if not subnet:
        return "Fout bij het bepalen van het subnet."

    scanner = nmap.PortScanner()
    scan_results = []

    print(f"Start netwerk scan op subnet: {subnet}")
    
    try:
        scanner.scan(hosts=subnet, arguments='-sP')  # Ping scan
        for host in scanner.all_hosts():
            if scanner[host].state() == "up":
                host_info = f"Host: {host} ({scanner[host].hostname()}) is actief."
                scan_results.append(host_info)

                # Zoek open poorten
                print(f"Scan poorten op host: {host}")
                scanner.scan(host, arguments='-p 1-1024 -sS')
                for port in scanner[host]['tcp']:
                    port_info = f"    Poort {port}: {scanner[host]['tcp'][port]['state']}"
                    scan_results.append(port_info)
    except Exception as e:
        print(f"Fout tijdens netwerk scan: {e}")
        return f"Scan mislukt: {e}"

    return "\n".join(scan_results)
