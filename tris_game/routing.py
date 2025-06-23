from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Prendere il codice stanza dall'URL WebSocket
    re_path(r'ws/tris/(?P<room_code>\w+)/$', consumers.TicTacToeConsumer.as_asgi()),
]
