import json
import time
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from nostr_sdk import Event, PublicKey
from main.models import NostrProfile

"""
Metadatos de Nostr (NIP-01): 
    Opcionalmente, tras el registro, puedes usar el nostr-sdk en el backend para consultar los 
    relays y traer el nombre de usuario (name) o el avatar (picture) que el usuario ya tenga configurado 
    en Nostr y rellenar su perfil de Django.
Vincular cuentas existentes: 
    Si un usuario ya tiene una cuenta con contraseña y quiere "activar" el login con Nostr, 
    crea una vista donde, estando logueado, firme un evento. 
    En esa vista simplemente guardas su pubkey en el modelo NostrProfile vinculado a su request.user.
"""

class NostrAuthBackend(ModelBackend):
    """
    Backend de autenticación híbrido. 
    Permite login tradicional y autenticación mediante firmas Nostr (NIP-98).
    """

    def authenticate(self, request, username=None, password=None, signed_event_json=None, **kwargs):
        # 1. Si hay username y password, usar la lógica estándar de Django
        if username and password:
            return super().authenticate(request, username=username, password=password, **kwargs)

        # 2. Si no hay contraseña pero hay un evento de Nostr, validar firma
        if signed_event_json:
            return self._authenticate_nostr(request, signed_event_json)

        return None

    def _authenticate_nostr(self, request, signed_event_json):
        try:
            # Parsear el evento desde el JSON recibido del frontend
            if isinstance(signed_event_json, str):
                event = Event.from_json(signed_event_json)
            else:
                event = Event.from_json(json.dumps(signed_event_json))

            # A. Verificación Criptográfica (Firma y Hash)
            event.verify()

            # B. Validación NIP-98 (Seguridad de Identidad)
            # 1. Verificar el Kind (27235 es para autenticación HTTP)
            if event.kind().as_u64() != 27235:
                return None

            # 2. Verificar Timestamp (Evitar ataques de repetición)
            # El evento no debe tener más de 60 segundos de antigüedad
            now = int(time.time())
            event_time = event.created_at().as_secs()
            if event_time < (now - 60) or event_time > (now + 10):
                return None

            # 3. Verificar URL (El tag 'u' debe coincidir con la URL del servidor)
            # Esto evita que una firma de 'Sitio A' se use en 'Sitio B'
            request_url = request.build_absolute_uri()
            url_verified = False
            for tag in event.tags().to_vec():
                tag_list = tag.as_vec()
                if len(tag_list) >= 2 and tag_list[0] == "u":
                    # Comprobamos si la URL del evento está contenida en nuestra URL
                    if tag_list[1] in request_url:
                        url_verified = True
                        break
            
            if not url_verified:
                return None

            # C. Identificación del Usuario
            pubkey_hex = event.author().to_hex()

            try:
                # Caso: Usuario ya vinculado
                profile = NostrProfile.objects.get(pubkey=pubkey_hex)
                return profile.user
            except NostrProfile.DoesNotExist:
                # Caso: Registro Automático
                # Creamos un username único basado en el pubkey
                username = f"nostr_{pubkey_hex[:12]}"
                
                # Crear usuario sin contraseña (password usable = False)
                user = User.objects.create_user(username=username)
                user.set_unusable_password()
                user.save()

                # Crear el vínculo con Nostr
                NostrProfile.objects.create(user=user, pubkey=pubkey_hex)
                return user

        except Exception as e:
            # En producción, loguear el error: print(f"Error Nostr Auth: {e}")
            return None

    def get_user(self, user_id):
        """Requerido para que la sesión de Django persista."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None