# explorador_funcional.py - Versión funcional garantizada
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import os
import socket
import webbrowser
from urllib.parse import urljoin, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import subprocess
import re

class ExploradorServidores:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 Explorador de Servidores de Archivos")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.servidores_encontrados = []
        self.servidor_actual = None
        self.ruta_actual = "/"
        self.historial_rutas = ["/"]
        self.indice_historial = 0
        
        # Configurar estilo
        self.configurar_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Iniciar búsqueda automática
        self.buscar_servidores()
    
    def configurar_estilo(self):
        """Configurar tema oscuro para la interfaz."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colores del tema oscuro
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
        style.configure('TButton', background='#404040', foreground='#ffffff')
        style.map('TButton', background=[('active', '#505050')])
        
        # Configurar Entry con tema oscuro
        style.configure('TEntry', 
                       background='#404040', 
                       foreground='#ffffff',
                       fieldbackground='#404040',
                       bordercolor='#606060',
                       lightcolor='#606060',
                       darkcolor='#606060',
                       insertcolor='#ffffff')
        style.map('TEntry',
                 focuscolor=[('focus', '#707070')],
                 bordercolor=[('focus', '#707070')])
        
        # Configurar Combobox con tema oscuro
        style.configure('TCombobox', 
                       background='#404040', 
                       foreground='#ffffff',
                       fieldbackground='#404040',
                       bordercolor='#606060',
                       arrowcolor='#ffffff',
                       lightcolor='#606060',
                       darkcolor='#606060',
                       insertcolor='#ffffff',
                       selectbackground='#505050',
                       selectforeground='#ffffff')
        style.map('TCombobox',
                 focuscolor=[('focus', '#707070')],
                 bordercolor=[('focus', '#707070')],
                 selectbackground=[('focus', '#505050')],
                 fieldbackground=[('readonly', '#404040')],
                 background=[('readonly', '#404040')])
        
        # Configurar el dropdown del Combobox
        style.configure('TCombobox*Listbox',
                       background='#404040',
                       foreground='#ffffff',
                       selectbackground='#505050',
                       selectforeground='#ffffff',
                       bordercolor='#606060')
        
        # Configurar Treeview
        style.configure('Treeview', 
                       background='#353535', 
                       foreground='#ffffff',
                       fieldbackground='#353535',
                       bordercolor='#606060')
        style.configure('Treeview.Heading', 
                       background='#404040', 
                       foreground='#ffffff',
                       bordercolor='#606060')
        style.map('Treeview',
                 selected=[('focus', '#505050')])
        
        # Configurar LabelFrame
        style.configure('TLabelframe', 
                       background='#2b2b2b',
                       foreground='#ffffff',
                       bordercolor='#606060')
        style.configure('TLabelframe.Label', 
                       background='#2b2b2b',
                       foreground='#ffffff')
    
    def crear_interfaz(self):
        """Crear toda la interfaz gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ===== PANEL SUPERIOR: SERVIDORES =====
        servidor_frame = ttk.LabelFrame(main_frame, text="🌐 Servidores Detectados", padding=10)
        servidor_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Combo de servidores
        ttk.Label(servidor_frame, text="Servidor:").pack(side=tk.LEFT, padx=(0, 5))
        self.combo_servidores = ttk.Combobox(servidor_frame, width=50, state="readonly")
        self.combo_servidores.pack(side=tk.LEFT, padx=(0, 10))
        self.combo_servidores.bind('<<ComboboxSelected>>', self.cambiar_servidor)
        
        # Botones de servidor
        ttk.Button(servidor_frame, text="🔄 Buscar", command=self.buscar_servidores).pack(side=tk.LEFT, padx=2)
        ttk.Button(servidor_frame, text="➕ Añadir manual", command=self.añadir_servidor_manual).pack(side=tk.LEFT, padx=2)
        ttk.Button(servidor_frame, text="🌐 Abrir en navegador", command=self.abrir_navegador).pack(side=tk.LEFT, padx=2)
        
        # Status
        self.label_status = ttk.Label(servidor_frame, text="🔍 Buscando servidores...")
        self.label_status.pack(side=tk.RIGHT)
        
        # ===== PANEL NAVEGACIÓN =====
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botones de navegación
        ttk.Button(nav_frame, text="⬅️ Atrás", command=self.navegar_atras).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="➡️ Adelante", command=self.navegar_adelante).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="🏠 Inicio", command=self.ir_inicio).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="⬆️ Subir", command=self.subir_directorio).pack(side=tk.LEFT, padx=2)
        ttk.Button(nav_frame, text="🔄 Actualizar", command=self.actualizar).pack(side=tk.LEFT, padx=2)
        
        # Barra de dirección
        ttk.Label(nav_frame, text="📁 Ruta:").pack(side=tk.LEFT, padx=(20, 5))
        self.entry_ruta = ttk.Entry(nav_frame, width=50)
        self.entry_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_ruta.bind('<Return>', self.navegar_ruta_manual)
        
        # ===== PANEL PRINCIPAL: EXPLORADOR =====
        explorador_frame = ttk.LabelFrame(main_frame, text="📁 Explorador de Archivos", padding=10)
        explorador_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para archivos
        columns = ("nombre", "tipo", "tamaño", "modificado")
        self.tree = ttk.Treeview(explorador_frame, columns=columns, show="tree headings", height=20)
        
        # Configurar columnas
        self.tree.heading("#0", text="📄 Archivo/Carpeta")
        self.tree.heading("tipo", text="🏷️ Tipo")
        self.tree.heading("tamaño", text="📏 Tamaño")
        self.tree.heading("modificado", text="🕒 Modificado")
        
        self.tree.column("#0", width=400)
        self.tree.column("tipo", width=100)
        self.tree.column("tamaño", width=100)
        self.tree.column("modificado", width=150)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(explorador_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(explorador_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # Pack del treeview y scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_v.grid(row=0, column=1, sticky='ns')
        scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        explorador_frame.grid_rowconfigure(0, weight=1)
        explorador_frame.grid_columnconfigure(0, weight=1)
        
        # Eventos del treeview
        self.tree.bind('<Double-1>', self.doble_click)
        self.tree.bind('<Button-3>', self.menu_contextual)
        
        # ===== PANEL INFERIOR: ACCIONES =====
        acciones_frame = ttk.Frame(main_frame)
        acciones_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(acciones_frame, text="⬇️ Descargar", command=self.descargar_seleccionado).pack(side=tk.LEFT, padx=2)
        ttk.Button(acciones_frame, text="📂 Abrir carpeta destino", command=self.abrir_carpeta_descargas).pack(side=tk.LEFT, padx=2)
        
        # Info del archivo seleccionado
        self.label_info = ttk.Label(acciones_frame, text="Selecciona un archivo para ver información")
        self.label_info.pack(side=tk.RIGHT)
        
        # Bind para mostrar info
        self.tree.bind('<<TreeviewSelect>>', self.mostrar_info_archivo)
    
    def obtener_interfaces_red(self):
        """Obtener todas las interfaces de red disponibles."""
        interfaces = []
        
        try:
            # Método 1: IP principal usando socket
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_principal = s.getsockname()[0]
            s.close()
            
            interfaces.append({
                'ip': ip_principal,
                'tipo': self.detectar_tipo_ip(ip_principal)
            })
            
            # Método 2: Usar ipconfig para obtener más interfaces
            try:
                result = subprocess.run(['ipconfig'], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    for linea in result.stdout.split('\n'):
                        if 'IPv4' in linea or 'IP Address' in linea:
                            ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', linea)
                            if ip_match:
                                ip = ip_match.group(1)
                                if (ip != '127.0.0.1' and 
                                    not ip.startswith('169.254') and
                                    not any(i['ip'] == ip for i in interfaces)):
                                    interfaces.append({
                                        'ip': ip,
                                        'tipo': self.detectar_tipo_ip(ip)
                                    })
            except:
                pass
            
            # Método 3: Probar IPs comunes de VPN
            vpn_tests = ['26.', '25.', '10.147.', '10.244.', '172.']
            for prefix in vpn_tests:
                try:
                    test_ip = f"{prefix}1.1"
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.settimeout(0.2)
                    s.connect((test_ip, 80))
                    local_ip = s.getsockname()[0]
                    s.close()
                    
                    if (local_ip.startswith(prefix.split('.')[0]) and
                        not any(i['ip'] == local_ip for i in interfaces)):
                        interfaces.append({
                            'ip': local_ip,
                            'tipo': 'VPN'
                        })
                except:
                    continue
                    
        except Exception as e:
            print(f"Error obteniendo interfaces: {e}")
        
        return interfaces
    
    def detectar_tipo_ip(self, ip):
        """Detectar tipo de red basado en la IP."""
        if ip.startswith('192.168.'):
            return 'LAN'
        elif ip.startswith('10.'):
            return 'VPN'
        elif ip.startswith('172.'):
            return 'VPN'
        elif ip.startswith('26.') or ip.startswith('25.'):
            return 'VPN-Hamachi'
        else:
            return 'Otra'
    
    def generar_ips_para_escanear(self, interfaces):
        """Generar lista de IPs para escanear basado en las interfaces."""
        ips_para_escanear = set()
        
        for interface in interfaces:
            ip = interface['ip']
            tipo = interface['tipo']
            
            # Agregar la IP propia
            ips_para_escanear.add(ip)
            
            # Generar rango según el tipo
            partes = ip.split('.')
            
            if tipo == 'LAN':
                # Para LAN, escanear toda la subred
                base = f"{partes[0]}.{partes[1]}.{partes[2]}"
                for i in range(1, 255):
                    ips_para_escanear.add(f"{base}.{i}")
            
            elif 'VPN' in tipo:
                # Para VPN, escanear rango más específico
                if ip.startswith('26.') or ip.startswith('25.'):
                    # Hamachi
                    base = f"{partes[0]}.{partes[1]}.{partes[2]}"
                    for i in range(1, 255):
                        ips_para_escanear.add(f"{base}.{i}")
                elif ip.startswith('10.'):
                    # ZeroTier u otras VPN
                    base = f"{partes[0]}.{partes[1]}.{partes[2]}"
                    for i in range(1, 255):
                        ips_para_escanear.add(f"{base}.{i}")
                else:
                    # Otras VPNs
                    base = f"{partes[0]}.{partes[1]}.{partes[2]}"
                    for i in range(max(1, int(partes[3])-50), min(255, int(partes[3])+51)):
                        ips_para_escanear.add(f"{base}.{i}")
        
        return list(ips_para_escanear)
    
    def buscar_servidores(self):
        """Buscar servidores en la red en un hilo separado."""
        self.actualizar_status("🔍 Buscando servidores...")
        self.combo_servidores.set("")
        
        def buscar():
            servidores = self.escanear_red()
            self.root.after(0, lambda: self.actualizar_lista_servidores(servidores))
        
        threading.Thread(target=buscar, daemon=True).start()
    
    def escanear_red(self):
        """Escanear la red en busca de servidores HTTP."""
        # Obtener interfaces de red
        interfaces = self.obtener_interfaces_red()
        self.root.after(0, lambda: self.actualizar_status(f"🔍 Detectadas {len(interfaces)} interfaces"))
        
        # Generar IPs para escanear
        ips_para_escanear = self.generar_ips_para_escanear(interfaces)
        puertos = [8000, 8001, 8080, 8765, 9000]
        
        total_combinaciones = len(ips_para_escanear) * len(puertos)
        self.root.after(0, lambda: self.actualizar_status(f"🌐 Escaneando {len(ips_para_escanear)} IPs"))
        
        servidores_encontrados = []
        
        def probar_servidor(ip, puerto):
            try:
                url = f"http://{ip}:{puerto}/"
                response = requests.get(url, timeout=2.0)
                if response.status_code == 200:
                    return (ip, puerto)
            except:
                pass
            return None
        
        # Escanear con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=100) as executor:
            tareas = []
            
            for ip in ips_para_escanear:
                for puerto in puertos:
                    tarea = executor.submit(probar_servidor, ip, puerto)
                    tareas.append(tarea)
            
            completadas = 0
            for tarea in as_completed(tareas):
                completadas += 1
                
                if completadas % 200 == 0:
                    progreso = (completadas / total_combinaciones) * 100
                    self.root.after(0, lambda p=progreso: self.actualizar_status(f"🔍 Progreso: {p:.1f}%"))
                
                resultado = tarea.result()
                if resultado:
                    servidores_encontrados.append(resultado)
        
        return servidores_encontrados
    
    def añadir_servidor_manual(self):
        """Mostrar diálogo para añadir servidor manualmente."""
        # Crear ventana de diálogo
        dialogo = tk.Toplevel(self.root)
        dialogo.title("➕ Añadir Servidor Manual")
        dialogo.geometry("450x350")
        dialogo.configure(bg='#2b2b2b')
        dialogo.resizable(False, False)
        
        # Centrar ventana
        dialogo.transient(self.root)
        dialogo.grab_set()
        
        # Variables para los campos
        ip_var = tk.StringVar()
        puerto_var = tk.StringVar(value="8000")
        
        # Frame principal del diálogo
        main_frame = ttk.Frame(dialogo)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = ttk.Label(main_frame, text="🌐 Añadir Servidor Manual", 
                          font=('Arial', 14, 'bold'),
                          background='#2b2b2b',
                          foreground='#ffffff')
        titulo.pack(pady=(0, 20))
        
        # Frame para IP
        ip_frame = ttk.Frame(main_frame)
        ip_frame.pack(fill=tk.X, pady=10)
        
        ip_label = ttk.Label(ip_frame, text="🌍 Dirección IP:", 
                            width=15,
                            background='#2b2b2b',
                            foreground='#ffffff')
        ip_label.pack(side=tk.LEFT)
        
        ip_entry = ttk.Entry(ip_frame, textvariable=ip_var, width=25, font=('Arial', 10))
        ip_entry.pack(side=tk.LEFT, padx=(10, 0))
        ip_entry.focus()
        
        # Frame para Puerto
        puerto_frame = ttk.Frame(main_frame)
        puerto_frame.pack(fill=tk.X, pady=10)
        
        puerto_label = ttk.Label(puerto_frame, text="🔌 Puerto:", 
                                width=15,
                                background='#2b2b2b',
                                foreground='#ffffff')
        puerto_label.pack(side=tk.LEFT)
        
        puerto_entry = ttk.Entry(puerto_frame, textvariable=puerto_var, width=25, font=('Arial', 10))
        puerto_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Ejemplos con mejor formato
        ejemplos_frame = ttk.LabelFrame(main_frame, text="💡 Ejemplos", padding=15)
        ejemplos_frame.pack(fill=tk.X, pady=20)
        
        # Crear etiquetas individuales para mejor control de color
        ejemplo_label1 = ttk.Label(ejemplos_frame, text="• IP Local: 192.168.1.100", 
                                  background='#2b2b2b', foreground='#00ff00', font=('Arial', 9))
        ejemplo_label1.pack(anchor='w', pady=2)
        
        ejemplo_label2 = ttk.Label(ejemplos_frame, text="• VPN Hamachi: 26.80.123.45", 
                                  background='#2b2b2b', foreground='#ffaa00', font=('Arial', 9))
        ejemplo_label2.pack(anchor='w', pady=2)
        
        ejemplo_label3 = ttk.Label(ejemplos_frame, text="• VPN ZeroTier: 10.147.17.200", 
                                  background='#2b2b2b', foreground='#00aaff', font=('Arial', 9))
        ejemplo_label3.pack(anchor='w', pady=2)
        
        ejemplo_label4 = ttk.Label(ejemplos_frame, text="• Puerto común: 8000, 8080, 8001", 
                                  background='#2b2b2b', foreground='#ff6600', font=('Arial', 9))
        ejemplo_label4.pack(anchor='w', pady=2)
        
        # Frame para botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=(25, 0))
        
        def probar_y_añadir():
            """Probar conexión y añadir servidor si funciona."""
            ip = ip_var.get().strip()
            puerto_str = puerto_var.get().strip()
            
            # Validaciones
            if not ip:
                messagebox.showerror("Error", "Ingresa una dirección IP")
                return
            
            if not puerto_str:
                messagebox.showerror("Error", "Ingresa un puerto")
                return
            
            try:
                puerto = int(puerto_str)
                if puerto < 1 or puerto > 65535:
                    raise ValueError("Puerto fuera de rango")
            except ValueError:
                messagebox.showerror("Error", "El puerto debe ser un número entre 1 y 65535")
                return
            
            # Validar formato IP básico
            partes_ip = ip.split('.')
            if len(partes_ip) != 4:
                messagebox.showerror("Error", "Formato de IP inválido")
                return
            
            try:
                for parte in partes_ip:
                    num = int(parte)
                    if num < 0 or num > 255:
                        raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Formato de IP inválido")
                return
            
            # Probar conexión
            def probar_conexion():
                try:
                    url = f"http://{ip}:{puerto}/"
                    response = requests.get(url, timeout=5.0)
                    
                    if response.status_code == 200:
                        # Conexión exitosa
                        dialogo.after(0, lambda: conexion_exitosa(ip, puerto))
                    else:
                        dialogo.after(0, lambda: conexion_fallida(f"Servidor respondió con código {response.status_code}"))
                        
                except requests.exceptions.Timeout:
                    dialogo.after(0, lambda: conexion_fallida("Tiempo de espera agotado"))
                except requests.exceptions.ConnectionError:
                    dialogo.after(0, lambda: conexion_fallida("No se pudo conectar al servidor"))
                except Exception as e:
                    dialogo.after(0, lambda: conexion_fallida(f"Error: {str(e)}"))
            
            # Deshabilitar botones durante la prueba
            btn_probar.configure(state='disabled', text="🔄 Probando...")
            btn_cancelar.configure(state='disabled')
            
            # Ejecutar prueba en hilo separado
            threading.Thread(target=probar_conexion, daemon=True).start()
        
        def conexion_exitosa(ip, puerto):
            """Manejar conexión exitosa."""
            # Añadir servidor a la lista
            nuevo_servidor = (ip, puerto)
            if nuevo_servidor not in self.servidores_encontrados:
                self.servidores_encontrados.append(nuevo_servidor)
                
                # Actualizar combo
                valores = [f"http://{ip}:{puerto}" for ip, puerto in self.servidores_encontrados]
                self.combo_servidores['values'] = valores
                self.combo_servidores.set(f"http://{ip}:{puerto}")
                
                # Actualizar status
                self.actualizar_status(f"✅ Servidor añadido: {ip}:{puerto}")
                
                # Cambiar al nuevo servidor
                self.cambiar_servidor()
                
                messagebox.showinfo("Éxito", f"Servidor añadido correctamente:\nhttp://{ip}:{puerto}")
                dialogo.destroy()
            else:
                messagebox.showinfo("Información", "Este servidor ya está en la lista")
                dialogo.destroy()
        
        def conexion_fallida(mensaje):
            """Manejar conexión fallida."""
            # Rehabilitar botones
            btn_probar.configure(state='normal', text="🔗 Probar y Añadir")
            btn_cancelar.configure(state='normal')
            
            # Preguntar si quiere añadirlo de todas formas
            respuesta = messagebox.askyesno(
                "Conexión fallida", 
                f"{mensaje}\n\n¿Quieres añadir el servidor de todas formas?\n(Útil si el servidor está temporalmente apagado)"
            )
            
            if respuesta:
                ip = ip_var.get().strip()
                puerto = int(puerto_var.get().strip())
                conexion_exitosa(ip, puerto)
        
        def cancelar():
            """Cerrar diálogo sin hacer nada."""
            dialogo.destroy()
        
        # Botones con mejor estilo
        btn_probar = ttk.Button(botones_frame, text="🔗 Probar y Añadir", command=probar_y_añadir)
        btn_probar.pack(side=tk.LEFT, padx=(0, 15))
        
        btn_cancelar = ttk.Button(botones_frame, text="❌ Cancelar", command=cancelar)
        btn_cancelar.pack(side=tk.LEFT)
        
        # Bind Enter para probar
        dialogo.bind('<Return>', lambda e: probar_y_añadir())
        dialogo.bind('<Escape>', lambda e: cancelar())
        
        # Centrar diálogo en la pantalla
        dialogo.update_idletasks()
        x = (dialogo.winfo_screenwidth() // 2) - (dialogo.winfo_width() // 2)
        y = (dialogo.winfo_screenheight() // 2) - (dialogo.winfo_height() // 2)
        dialogo.geometry(f"+{x}+{y}")
        
        # Foco en el campo IP
        ip_entry.focus_set()
    
    def actualizar_status(self, mensaje):
        """Actualizar el mensaje de status."""
        self.label_status.config(text=mensaje)
    
    def actualizar_lista_servidores(self, servidores):
        """Actualizar la lista de servidores encontrados."""
        self.servidores_encontrados = servidores
        
        if servidores:
            valores = [f"http://{ip}:{puerto}" for ip, puerto in servidores]
            self.combo_servidores['values'] = valores
            self.combo_servidores.set(valores[0])
            self.actualizar_status(f"✅ {len(servidores)} servidor(es) encontrado(s)")
            self.cambiar_servidor()
        else:
            self.combo_servidores['values'] = []
            self.actualizar_status("❌ No se encontraron servidores")
    
    def cambiar_servidor(self, event=None):
        """Cambiar al servidor seleccionado."""
        servidor = self.combo_servidores.get()
        if servidor:
            self.servidor_actual = servidor
            self.ir_inicio()
    
    def ir_inicio(self):
        """Navegar al directorio raíz."""
        self.navegar_a("/")
    
    def navegar_a(self, ruta):
        """Navegar a una ruta específica."""
        if not self.servidor_actual:
            messagebox.showwarning("Advertencia", "Selecciona un servidor primero")
            return
        
        self.ruta_actual = ruta
        self.entry_ruta.delete(0, tk.END)
        self.entry_ruta.insert(0, ruta)
        
        # Actualizar historial
        if len(self.historial_rutas) > self.indice_historial + 1:
            self.historial_rutas = self.historial_rutas[:self.indice_historial + 1]
        
        if not self.historial_rutas or self.historial_rutas[-1] != ruta:
            self.historial_rutas.append(ruta)
            self.indice_historial = len(self.historial_rutas) - 1
        
        self.cargar_directorio()
    
    def cargar_directorio(self):
        """Cargar el contenido del directorio actual."""
        def cargar():
            try:
                url = urljoin(self.servidor_actual, self.ruta_actual)
                response = requests.get(url, timeout=5.0)
                
                if response.status_code == 200:
                    archivos = self.parsear_listado_html(response.text)
                    self.root.after(0, lambda: self.mostrar_archivos(archivos))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", f"Error {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando directorio: {e}"))
        
        threading.Thread(target=cargar, daemon=True).start()
    
    def parsear_listado_html(self, html):
        """Parsear el HTML del listado de archivos."""
        archivos = []
        lineas = html.split('\n')
        
        for linea in lineas:
            if '<a href="' in linea:
                try:
                    # Extraer nombre del archivo/carpeta
                    inicio = linea.find('<a href="') + 9
                    fin = linea.find('"', inicio)
                    href = linea[inicio:fin]
                    
                    if href and href not in ['..', '/']:
                        # Extraer nombre visible
                        inicio_nombre = linea.find('>', linea.find('<a href=')) + 1
                        fin_nombre = linea.find('</a>', inicio_nombre)
                        nombre = linea[inicio_nombre:fin_nombre].strip()
                        
                        if nombre:
                            es_directorio = href.endswith('/')
                            archivos.append({
                                'nombre': unquote(nombre),
                                'href': href,
                                'es_directorio': es_directorio,
                                'tipo': '📁 Carpeta' if es_directorio else '📄 Archivo',
                                'tamaño': '-' if es_directorio else 'N/A',
                                'modificado': 'N/A'
                            })
                except:
                    continue
        
        return archivos
    
    def mostrar_archivos(self, archivos):
        """Mostrar archivos en el treeview."""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar carpeta padre si no estamos en raíz
        if self.ruta_actual != "/":
            self.tree.insert("", "end", values=("📁 Subir", "Directorio", "-", "-"), 
                           tags=("directorio_padre",))
        
        # Ordenar: carpetas primero, luego archivos
        archivos.sort(key=lambda x: (not x['es_directorio'], x['nombre'].lower()))
        
        # Agregar archivos
        for archivo in archivos:
            icono = "📁" if archivo['es_directorio'] else "📄"
            self.tree.insert("", "end", text=f"{icono} {archivo['nombre']}", 
                           values=(archivo['tipo'], archivo['tamaño'], archivo['modificado']),
                           tags=("directorio" if archivo['es_directorio'] else "archivo",))
    
    def doble_click(self, event):
        """Manejar doble clic en archivo/carpeta."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        valores = self.tree.item(item, 'values')
        nombre = self.tree.item(item, 'text')
        
        if "📁 Subir" in valores[0]:
            self.subir_directorio()
        elif "📁" in nombre:  # Es carpeta
            nombre_carpeta = nombre.replace("📁 ", "")
            nueva_ruta = self.ruta_actual.rstrip('/') + '/' + nombre_carpeta + '/'
            self.navegar_a(nueva_ruta)
        else:  # Es archivo
            self.descargar_archivo(nombre.replace("📄 ", ""))
    
    def descargar_archivo(self, nombre_archivo):
        """Descargar un archivo específico."""
        try:
            url_archivo = urljoin(self.servidor_actual, self.ruta_actual + nombre_archivo)
            
            # Obtener carpeta de descargas por defecto
            try:
                downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(downloads_path):
                    downloads_path = os.path.expanduser("~")
            except:
                downloads_path = os.getcwd()
            
            # Pedir ubicación de descarga
            archivo_destino = filedialog.asksaveasfilename(
                title="Guardar archivo como",
                initialdir=downloads_path,
                initialfile=nombre_archivo,
                filetypes=[("Todos los archivos", "*.*")]
            )
            
            if archivo_destino:
                def descargar():
                    try:
                        self.root.after(0, lambda: self.actualizar_status("⬇️ Descargando archivo..."))
                        
                        response = requests.get(url_archivo, stream=True, timeout=30)
                        if response.status_code == 200:
                            with open(archivo_destino, 'wb') as f:
                                for chunk in response.iter_content(chunk_size=8192):
                                    if chunk:
                                        f.write(chunk)
                            
                            self.root.after(0, lambda: self.actualizar_status("✅ Descarga completada"))
                            self.root.after(0, lambda: messagebox.showinfo("Descarga completada", 
                                f"Archivo descargado exitosamente:\n{archivo_destino}"))
                        else:
                            self.root.after(0, lambda: self.actualizar_status("❌ Error en descarga"))
                            self.root.after(0, lambda: messagebox.showerror("Error", f"Error {response.status_code}"))
                    except Exception as e:
                        self.root.after(0, lambda: self.actualizar_status("❌ Error de descarga"))
                        self.root.after(0, lambda: messagebox.showerror("Error", f"Error: {e}"))
                
                threading.Thread(target=descargar, daemon=True).start()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error preparando descarga: {e}")
    
    def descargar_seleccionado(self):
        """Descargar el archivo seleccionado."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            messagebox.showwarning("Advertencia", "Selecciona un archivo para descargar")
            return
        
        nombre = self.tree.item(item, 'text')
        if "📁" in nombre:
            messagebox.showwarning("Advertencia", "No se pueden descargar carpetas")
            return
        
        self.descargar_archivo(nombre.replace("📄 ", ""))
    
    def navegar_atras(self):
        """Navegar hacia atrás en el historial."""
        if self.indice_historial > 0:
            self.indice_historial -= 1
            ruta = self.historial_rutas[self.indice_historial]
            self.ruta_actual = ruta
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, ruta)
            self.cargar_directorio()
    
    def navegar_adelante(self):
        """Navegar hacia adelante en el historial."""
        if self.indice_historial < len(self.historial_rutas) - 1:
            self.indice_historial += 1
            ruta = self.historial_rutas[self.indice_historial]
            self.ruta_actual = ruta
            self.entry_ruta.delete(0, tk.END)
            self.entry_ruta.insert(0, ruta)
            self.cargar_directorio()
    
    def subir_directorio(self):
        """Subir un nivel en el directorio."""
        if self.ruta_actual != "/":
            partes = self.ruta_actual.rstrip('/').split('/')
            nueva_ruta = '/'.join(partes[:-1]) + '/' if len(partes) > 1 else "/"
            self.navegar_a(nueva_ruta)
    
    def navegar_ruta_manual(self, event):
        """Navegar a ruta ingresada manualmente."""
        ruta = self.entry_ruta.get().strip()
        if ruta:
            if not ruta.startswith('/'):
                ruta = '/' + ruta
            if not ruta.endswith('/') and ruta != '/':
                ruta += '/'
            self.navegar_a(ruta)
    
    def actualizar(self):
        """Actualizar el directorio actual."""
        self.cargar_directorio()
    
    def abrir_navegador(self):
        """Abrir el servidor actual en el navegador web."""
        if self.servidor_actual:
            webbrowser.open(self.servidor_actual)
        else:
            messagebox.showwarning("Advertencia", "Selecciona un servidor primero")
    
    def abrir_carpeta_descargas(self):
        """Abrir la carpeta de descargas del sistema."""
        try:
            downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
            os.startfile(downloads_path)
        except:
            messagebox.showwarning("Advertencia", "No se pudo abrir la carpeta de descargas")
    
    def mostrar_info_archivo(self, event):
        """Mostrar información del archivo seleccionado."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            nombre = self.tree.item(item, 'text')
            valores = self.tree.item(item, 'values')
            tipo = valores[0] if valores else "N/A"
            self.label_info.config(text=f"📄 {nombre.replace('📄 ', '').replace('📁 ', '')} | {tipo}")
        else:
            self.label_info.config(text="Selecciona un archivo para ver información")
    
    def menu_contextual(self, event):
        """Mostrar menú contextual con clic derecho."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            menu = tk.Menu(self.root, tearoff=0)
            nombre = self.tree.item(item, 'text')
            
            if "📁" in nombre:
                menu.add_command(label="📂 Abrir carpeta", command=lambda: self.doble_click(None))
            else:
                menu.add_command(label="⬇️ Descargar", command=self.descargar_seleccionado)
            
            menu.add_separator()
            menu.add_command(label="🔄 Actualizar", command=self.actualizar)
            
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

def main():
    root = tk.Tk()
    app = ExploradorServidores(root)
    root.mainloop()

if __name__ == "__main__":
    main()