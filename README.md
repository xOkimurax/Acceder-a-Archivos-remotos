🌐 Acceder a Archivos Remotos

Descripción del Proyecto
Este es un software beta que permite compartir y acceder a archivos de forma remota a través de una red local. El proyecto consiste en un sistema cliente-servidor que facilita el intercambio de archivos entre computadoras conectadas a la misma red.

¿Para qué sirve?
Compartir archivos entre computadoras en la misma red local
Explorar directorios remotos de forma gráfica e intuitiva
Detectar automáticamente servidores de archivos en la red
Descargar archivos desde servidores remotos
Navegar por el sistema de archivos remoto como si fuera local
Componentes del Sistema
1.
Servidor de Archivos (servidor_archivos.py) - Comparte archivos desde el disco C:\
2.
Cliente Detector (cliente_detector.py) - Busca servidores activos en la red
3.
Explorador GUI (explorador_gui.py) - Interfaz gráfica para navegar y descargar archivos
4.
Cliente de Búsqueda (cliente_busqueda.py) - Herramienta de línea de comandos para encontrar servidores
⚠️ Software Beta
IMPORTANTE: Este es un software en versión beta, lo que significa:

Puede contener errores o comportamientos inesperados
Las funcionalidades están en desarrollo y pueden cambiar
Se recomienda usar solo en redes confiables
No está optimizado para uso en producción
Úsalo bajo tu propia responsabilidad
📋 Requisitos del Sistema
Software Necesario
Python 3.7+ instalado en el sistema
Bibliotecas Python requeridas:
requests
tkinter (incluido con Python)
concurrent.futures (incluido con Python)
socket (incluido con Python)
threading (incluido con Python)
Instalación de Dependencias
Bash



Run
pip install requests
Sistema Operativo
Windows (optimizado para Windows)
Puede funcionar en Linux/macOS con modificaciones menores
🚀 Cómo Ejecutar el Proyecto
Opción 1: Usar Archivos Ejecutables (Recomendado)
En la carpeta Version en .exe y ordenado/ encontrarás archivos .exe listos para usar:

Bash



Run
# Iniciar el servidorservidor_noconsola.exe# Abrir el explorador gráficoexplorador_gui.exe# Detectar servidores en la redcliente_detector.exe# Detener el servidorDetener servidor.bat
Opción 2: Ejecutar desde Código Fuente
1. Iniciar el Servidor
Bash



Run
python servidor_archivos.py
Esto iniciará el servidor en el puerto 8000 y compartirá el contenido del disco C:\

2. Detectar Servidores en la Red
Bash



Run
python cliente_detector.py
Escanea la red local buscando servidores de archivos activos.

3. Usar el Explorador Gráfico
Bash



Run
python explorador_gui.py
Abre una interfaz gráfica para navegar y descargar archivos de servidores remotos.

4. Búsqueda Simple de Servidores
Bash



Run
python cliente_busqueda.py
Herramienta de línea de comandos para encontrar servidores activos.

🔧 Configuración
Cambiar Puerto del Servidor
Edita la variable PORT en servidor_archivos.py:

Python



PORT = 8000  # Cambia por el puerto deseado
Cambiar Directorio Compartido
Edita la variable RUTA_A_COMPARTIR en servidor_archivos.py:

Python



RUTA_A_COMPARTIR = r"C:\\"  # Cambia por la ruta deseada
📁 Estructura del Proyecto
PlainText



compartirarchivos/├── Version en .exe y ordenado/     # Ejecutables compilados├── build/                          # Archivos de compilación├── dist/                          # Distribución de ejecutables├── servidor_archivos.py           # Servidor HTTP de archivos├── cliente_detector.py            # Detector de servidores├── explorador_gui.py             # Interfaz gráfica├── cliente_busqueda.py           # Cliente de búsqueda└── *.spec                        # Archivos de configuración PyInstaller
🔒 Consideraciones de Seguridad
Solo usar en redes confiables: El servidor no tiene autenticación
Firewall: Asegúrate de que el puerto 8000 esté abierto
Contenido compartido: Ten cuidado con qué archivos compartes
Red local únicamente: No expongas el servidor a Internet
🐛 Solución de Problemas
El servidor no inicia
Verifica que el puerto 8000 no esté en uso
Ejecuta como administrador si es necesario
Revisa el archivo servidor_status.txt para logs
No se detectan servidores
Asegúrate de estar en la misma red
Verifica que el firewall no bloquee las conexiones
Prueba con diferentes puertos
Errores de descarga
Verifica la conexión de red
Asegúrate de tener permisos de escritura en la carpeta de destino
📞 Soporte
Este es un proyecto beta en desarrollo. Para reportar errores o sugerir mejoras, puedes crear un issue en el repositorio de GitHub.
