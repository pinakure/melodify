import threading
import time
from pathlib import Path
import sys
import os
import toga
from toga.style import Pack
from django.core.management import execute_from_command_line

def run_django():
    """Función para arrancar Django en un hilo separado."""
    app_dir = Path(__file__).resolve().parent
    backend_dir = app_dir / "backend"
    for path in [str(app_dir), str(backend_dir)]:
        if path not in sys.path:
            sys.path.insert(0, path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
    try:
        # Forzamos a Django a correr en localhost puerto 8000
        # Usamos --noreload porque el auto-reloader no funciona bien en Android
        manage_py_path = str(app_dir / "backend" / "manage.py")
        execute_from_command_line([manage_py_path, 'runserver', '127.0.0.1:8000', '--noreload'])
    except Exception as e:
        print(f"Error arrancando Django: {e}")

class Melodify(toga.App):
    def startup(self):
        if hasattr(toga.App.app, "_impl"):
            try:
                from org.beeware.android import MainActivity
                activity = MainActivity.singletonThis
                # Ocultamos la barra de soporte (AppCompat ActionBar)
                action_bar = activity.getSupportActionBar()
                if action_bar:
                    action_bar.hide()
            except ImportError:
                pass # No estamos en Android
        # 1. Lanzar Django en el hilo de fondo
        self.django_thread = threading.Thread(target=run_django)
        self.django_thread.daemon = True  # Para que el hilo muera al cerrar la app
        self.django_thread.start()

        # 2. Configurar la interfaz de Toga
        main_box = toga.Box()
        time.sleep(5)
        # En Android, si el servidor corre internamente, usamos 127.0.0.1
        self.webview = toga.WebView(
            url="http://127.0.0.1:8000",
            style=Pack(flex=1)
        )

        main_box.add(self.webview)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

def main():
    return Melodify()
