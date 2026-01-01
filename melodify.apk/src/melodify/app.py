"""
Melodify
"""

import toga
from toga.style.pack import COLUMN, ROW


class Melodify(toga.App):
    def startup(self):
        # 1. Definimos la URL. 
        # Usa 'http://10.0.2.2:8000' para conectar al Django de tu PC desde el emulador.
        # Usa 'http://127.0.0.1:8000' solo si el servidor corre dentro del mismo dispositivo.
        server_url = "http://127.0.0.1:8000"

        # 2. Creamos el contenedor principal
        main_box = toga.Box(style=Pack(direction=COLUMN))

        # 3. Creamos el WebView que apuntará a tu Django
        self.webview = toga.WebView(
            url=server_url,
            style=Pack(flex=1) # El flex=1 hace que ocupe toda la pantalla
        )

        # 4. Agregamos el webview al box
        main_box.add(self.webview)
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()


def main():
    return Melodify()
