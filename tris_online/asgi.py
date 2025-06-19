"""
ASGI config for tris_online project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import tris_game.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tris_online.settings')

# Importa l'applicazione HTTP di Django dopo aver impostato l'ambiente
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # Gestisce le richieste HTTP tradizionali
    "http": django_asgi_app,

    # Gestisce le connessioni WebSocket
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            tris_game.routing.websocket_urlpatterns
        )
    ),
})
