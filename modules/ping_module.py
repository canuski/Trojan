import subprocess

def run():
    """Voer een ping uit naar een doelwit."""
    target = "8.8.8.8"  # Google DNS
    try:
        result = subprocess.check_output(["ping", "-n", "4", target], text=True)
        return result
    except subprocess.CalledProcessError as e:
        return f"Ping mislukt: {e}"
