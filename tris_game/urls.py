from django.urls import path
from .views import home_view, game_room_view, history_view

urlpatterns = [
    # URL per la home page
    path('', home_view, name='home'),
    # URL per la stanza di gioco, con codice stanza dinamico
    path('tris/<str:room_code>/', game_room_view, name='game_room'),
    # URL per la cronologia del player
    path('history/', history_view, name='history'),
]
