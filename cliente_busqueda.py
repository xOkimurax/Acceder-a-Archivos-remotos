import socket
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Rango de puertos a probar donde puede estar el servidor
PUERTOS = range(8000, 8011)  # Por ejemplo, del 8000 al 8010

# Tiempo máximo de espera por respuesta
TIMEOUT = 0.5

def obtener_ip_local():
    """Obtiene la IP local de la máquina."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # No necesita conexión real, solo IP local
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generar_ips_subred(ip_local):
    """Genera lista de IPs en la misma subred (clase C)"""
    base = ".".join(ip_local.split(".")[:-1])
    return [f"{base}.{i}" for i in range(1, 255)]

def probar_servidor(ip, puerto):
    """Intenta conectarse a servidor HTTP en ip:puerto y devuelve info si responde."""
    url = f"http://{ip}:{puerto}/"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return (ip, puerto)
    except:
        pass
    return None

def main():
    ip_local = obtener_ip_local()
    print(f"[+] IP local: {ip_local}")
    ips = generar_ips_subred(ip_local)

    print("[*] Escaneando la red en busca del servidor...")

    resultados = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        tareas = []
        for ip in ips:
            for puerto in PUERTOS:
                tareas.append(executor.submit(probar_servidor, ip, puerto))
        for tarea in as_completed(tareas):
            resultado = tarea.result()
            if resultado:
                resultados.append(resultado)
                print(f"[✔] Servidor detectado en {resultado[0]}:{resultado[1]}")
                # Opcional: si querés parar al primer resultado encontrado, descomenta
                # break

    if not resultados:
        print("[!] No se detectó ningún servidor en la red y puertos indicados.")

if __name__ == "__main__":
    main()
