# servidor_descargas.py
import sys
import os

# CRÍTICO: Redirigir streams ANTES de importar otras librerías
if hasattr(sys, 'frozen'):  # Detecta si está compilado como .exe
    # Redirigir stdout y stderr a /dev/null para evitar errores silenciosos
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Ahora sí, importar el resto
import http.server
import socketserver
import urllib.parse
import mimetypes

PORT = 8000
RUTA_A_COMPARTIR = r"C:\\"

class DownloadHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler personalizado que permite descargas directas de archivos."""
    
    def guess_type(self, path):
        """Mejorar detección de tipos MIME para descargas."""
        mimetype, encoding = mimetypes.guess_type(path)
        
        # Para archivos ejecutables y otros tipos específicos
        if path.lower().endswith(('.exe', '.msi', '.bat', '.cmd')):
            return 'application/octet-stream', encoding
        elif path.lower().endswith(('.zip', '.rar', '.7z')):
            return 'application/zip', encoding
        elif path.lower().endswith(('.pdf')):
            return 'application/pdf', encoding
        elif path.lower().endswith(('.doc', '.docx')):
            return 'application/msword', encoding
        elif path.lower().endswith(('.xls', '.xlsx')):
            return 'application/vnd.ms-excel', encoding
        
        return mimetype, encoding

    def end_headers(self):
        """Agregar headers para permitir descargas desde el navegador."""
        # Permitir descargas desde cualquier origen (CORS)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        
        # Mejorar compatibilidad con navegadores
        self.send_header('Accept-Ranges', 'bytes')
        
        super().end_headers()

    def do_GET(self):
        """Manejar peticiones GET con descarga forzada para TODOS los archivos."""
        # Decodificar la URL
        path = urllib.parse.unquote(self.path)
        
        # Obtener ruta completa del archivo
        full_path = self.translate_path(path)
        
        # Si es un archivo (no directorio), SIEMPRE forzar descarga
        if os.path.isfile(full_path):
            # Forzar descarga para TODOS los archivos sin excepción
            filename = os.path.basename(full_path)
            
            try:
                file_size = os.path.getsize(full_path)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(file_size))
                self.end_headers()
                
                # Enviar el archivo en chunks para archivos grandes
                with open(full_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)  # 8KB chunks
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except:
                # Si hay error, enviar 404
                self.send_error(404, "File not found")
            return
        
        # Para directorios, usar el comportamiento normal (mostrar listado)
        super().do_GET()

    def translate_path(self, path):
        """Traducir path URL a path del sistema de archivos."""
        # Remover parámetros de query
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Decodificar URL encoding
        path = urllib.parse.unquote(path)
        
        # Normalizar separadores de directorio
        path = path.replace('/', os.sep)
        
        # Construir path completo desde la raíz compartida
        if path.startswith(os.sep):
            path = path[1:]
        
        return os.path.join(RUTA_A_COMPARTIR, path)

def main():
    try:
        os.chdir(RUTA_A_COMPARTIR)
        
        # Usar nuestro handler personalizado en lugar del SimpleHTTPRequestHandler
        Handler = DownloadHTTPRequestHandler
        
        # Usar 0.0.0.0 para escuchar en todas las interfaces
        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            httpd.serve_forever()
    except:
        pass  # Fallar silenciosamente si hay errores

if __name__ == "__main__":
    main()