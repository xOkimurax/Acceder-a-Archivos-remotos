# cliente_detector.py
import socket
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración
PUERTOS = [8000, 8001, 8080, 8765, 9000]  # Puertos comunes a probar
TIMEOUT = 1.0  # Tiempo de espera por conexión
MAX_WORKERS = 100  # Hilos concurrentes para escaneo rápido

def obtener_ip_local():
    """Obtiene la IP local de esta máquina."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def generar_ips_subred(ip_local):
    """Genera todas las IPs de la subred (clase C)."""
    base = ".".join(ip_local.split(".")[:-1])
    return [f"{base}.{i}" for i in range(1, 255)]

def probar_servidor_http(ip, puerto):
    """Intenta conectarse a un servidor HTTP y verificar si responde."""
    url = f"http://{ip}:{puerto}/"
    try:
        response = requests.get(url, timeout=TIMEOUT)
        if response.status_code == 200:
            # Verificar si realmente es un servidor de archivos
            if "Index of" in response.text or "Directory listing" in response.text or len(response.text) > 100:
                return (ip, puerto, "HTTP File Server")
    except:
        pass
    return None

def mostrar_progreso():
    """Muestra puntos de progreso mientras escanea."""
    for i in range(30):  # Máximo 30 segundos
        print(".", end="", flush=True)
        time.sleep(1)

def main():
    print("🔍 Cliente Detector de Servidor de Archivos")
    print("=" * 50)
    
    ip_local = obtener_ip_local()
    print(f"📍 IP local detectada: {ip_local}")
    
    ips = generar_ips_subred(ip_local)
    total_combinaciones = len(ips) * len(PUERTOS)
    
    print(f"🌐 Escaneando {len(ips)} IPs en {len(PUERTOS)} puertos ({total_combinaciones} combinaciones)")
    print("⏳ Buscando servidores", end="")
    
    # Hilo para mostrar progreso
    progreso_thread = threading.Thread(target=mostrar_progreso, daemon=True)
    progreso_thread.start()
    
    servidores_encontrados = []
    
    # Escaneo concurrente
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tareas = []
        
        # Crear tareas para todas las combinaciones IP:Puerto
        for ip in ips:
            for puerto in PUERTOS:
                tarea = executor.submit(probar_servidor_http, ip, puerto)
                tareas.append(tarea)
        
        # Procesar resultados conforme van completándose
        for tarea in as_completed(tareas):
            resultado = tarea.result()
            if resultado:
                servidores_encontrados.append(resultado)
                # Mostrar inmediatamente cuando encuentre uno
                ip, puerto, tipo = resultado
                print(f"\n✅ ¡ENCONTRADO! {tipo} en http://{ip}:{puerto}")
    
    print("\n" + "=" * 50)
    
    if servidores_encontrados:
        print(f"🎯 Resumen: {len(servidores_encontrados)} servidor(es) encontrado(s):")
        print()
        for i, (ip, puerto, tipo) in enumerate(servidores_encontrados, 1):
            print(f"  {i}. {tipo}")
            print(f"     🌐 URL: http://{ip}:{puerto}")
            print(f"     📱 IP: {ip} | Puerto: {puerto}")
            print()
        
        # Abrir automáticamente el primero en el navegador
        if len(servidores_encontrados) == 1:
            ip, puerto, _ = servidores_encontrados[0]
            try:
                import webbrowser
                webbrowser.open(f"http://{ip}:{puerto}")
                print("🌐 Abriendo automáticamente en el navegador...")
            except:
                pass
    else:
        print("❌ No se encontraron servidores de archivos en la red.")
        print("💡 Asegúrate de que:")
        print("   • El servidor esté ejecutándose")
        print("   • Ambas máquinas estén en la misma red")
        print("   • El firewall permita las conexiones")
    
    input("\n⏸️ Presiona Enter para salir...")

if __name__ == "__main__":
    main()