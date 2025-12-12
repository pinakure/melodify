import threading
import time
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivymd.app import MDApp
import os
import sys
try:
    from kivymd.uix.webview import MDWebView
except ImportError:
    # Una clase de reserva simple para que el desarrollo en PC no falle
    class MDWebView(BoxLayout):
        def __init__(self, url, **kwargs):
            super().__init__(**kwargs)
            self.add_widget(Label(text=f"WebView no disponible en PC. Cargando {url}"))
        def reload(self):
            pass

# Importaciones adicionales para el servidor WSGI
from wsgiref.simple_server import make_server
# Ya no importamos WSGIHandler directamente aquí arriba

# --- Lógica para Iniciar Django en Hilo Separado Programáticamente ---

def start_django_server_programmatic():
    # Asegúrate de que el path y las variables de entorno estén configuradas ANTES de importar CUALQUIER COSA de Django
    sys.path.append(os.getcwd()) 
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    
    try:
        # AHORA importamos lo necesario, después de configurar las variables de entorno
        import django
        django.setup() # <--- ESTO ES CRUCIAL

        from django.core.handlers.wsgi import WSGIHandler
        
        # Crea la aplicación WSGI de Django
        application = WSGIHandler()
        # Inicia el servidor WSGI localmente en el puerto 8000
        httpd = make_server('127.0.0.1', 8000, application)
        print("Servidor Django WSGI iniciado en http://127.0.0.1:8000")
        httpd.serve_forever()
        
    except Exception as e:
        print(f"Error starting Django server programmatically: {e}")

class ClientLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Usa el MDWebView para cargar tu URL local
        self.webview = MDWebView(url="http://127.0.0.1:8000")
        self.add_widget(self.webview)

    # Puedes añadir un botón o lógica para recargar la página si el servidor tarda en arrancar
    def reload_page(self):
        self.webview.reload()


class MyApp(MDApp): # <--- Ahora hereda de MDApp, no de App
    def build(self):
        # 1. Iniciar el servidor Django programático en un hilo secundario
        django_thread = threading.Thread(target=start_django_server_programmatic, daemon=True)
        django_thread.start()

        # Espera inicial para el servidor
        time.sleep(3) 

        layout = ClientLayout()
        layout.reload_page() # Intenta cargar la URL después de la espera
        return layout

if __name__ == '__main__':
    # Asegúrate de usar 'backend.settings' como en tu ejemplo anterior
    # sys.path y os.environ se configuran dentro del hilo del servidor.
    MyApp().run()