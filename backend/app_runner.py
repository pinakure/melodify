import os
import threading
import time
import webview
from django.core.management import execute_from_command_line

# --- CONFIGURACIÓN IMPORTANTE ---
# Reemplaza 'nombre_de_tu_proyecto.settings' con la ruta real a tu settings.py
DJANGO_SETTINGS_MODULE = "backend.settings" 
HOST_IP = "127.0.0.1"
PORT = "8000"
APP_TITLE = "Melodify"
# --------------------------------

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

def run_django_server():
    """
    Función que inicia el servidor Django.
    Se ejecuta en un hilo separado.
    """
    # Usamos --noreload porque PyInstaller no funciona bien con el recargador automático
    print(f"Iniciando servidor Django en http://{HOST_IP}:{PORT}...")
    execute_from_command_line([
        "manage.py", 
        "runserver", 
        "--noreload", 
        f"{HOST_IP}:{PORT}"
    ])

def create_webview_window():
    """
    Función que crea y abre la ventana de la aplicación de escritorio.
    """
    url = f"http://{HOST_IP}:{PORT}"
    
    # Esperamos un momento para asegurarnos de que el servidor esté activo
    time.sleep(1.5) 
    print(f"Abriendo interfaz gráfica: {url}")

    # Crea la ventana usando pywebview
    webview.create_window(
        title=APP_TITLE, 
        url=url, 
        width=1024, 
        height=768,
        # Puedes añadir más opciones aquí, como fullscreen=True
    )
    
    # Inicia el bucle principal de la GUI. Esto bloquea la ejecución.
    webview.start()

if __name__ == "__main__":
    # 1. Inicia el servidor Django en un hilo secundario
    django_thread = threading.Thread(target=run_django_server, daemon=True)
    django_thread.start()

    # 2. Inicia la interfaz gráfica (la ventana del navegador web nativo)
    create_webview_window()

    # Cuando la ventana de pywebview.start() se cierra, el programa termina.
    print("Aplicación cerrada.")

    