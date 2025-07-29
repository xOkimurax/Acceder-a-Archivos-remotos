# servidor_noconsola_fix.py
import sys
import os

# CRÍTICO: Redirigir streams ANTES de importar otras librerías
if hasattr(sys, 'frozen'):  # Detecta si está compilado como .exe
    # Redirigir stdout y stderr a archivos o /dev/null
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Ahora sí, importar el resto
import http.server
import socketserver
import socket
import threading

PORT = 8000
RUTA_A_COMPARTIR = r"C:\\"

def main():
    try:
        # Crear archivo de log para confirmar que se ejecuta
        with open("servidor_status.txt", "w") as log:
            log.write(f"Servidor iniciado en puerto {PORT}\n")
        
        os.chdir(RUTA_A_COMPARTIR)

        def obtener_ip_local():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
            except Exception:
                ip = "127.0.0.1"
            finally:
                s.close()
            return ip

        ip_lan = obtener_ip_local()
        
        # Guardar IP en archivo para que sepas dónde conectarte
        with open("servidor_ip.txt", "w") as ip_file:
            ip_file.write(f"http://{ip_lan}:{PORT}\n")
            ip_file.write(f"http://127.0.0.1:{PORT}\n")

        Handler = http.server.SimpleHTTPRequestHandler
        
        # Usar 0.0.0.0 para escuchar en todas las interfaces
        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            # Log de éxito
            with open("servidor_status.txt", "a") as log:
                log.write(f"Servidor activo en {ip_lan}:{PORT}\n")
            
            httpd.serve_forever()

    except Exception as e:
        # Guardar cualquier error en archivo
        with open("servidor_error.txt", "w") as error_file:
            error_file.write(f"Error: {str(e)}\n")
            error_file.write(f"Tipo: {type(e).__name__}\n")

if __name__ == "__main__":
    main()