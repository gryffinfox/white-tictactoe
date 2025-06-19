from django.urls import path
from .views import home_view, stanza_gioco_view, cronologia_view

urlpatterns = [
    # URL per la home page
    path('', home_view, name='home'),
    # URL per la stanza di gioco, con codice stanza dinamico
    path('tris/<str:codice_stanza>/', stanza_gioco_view, name='stanza_gioco'),
    # URL per la cronologia del player
    path('cronologia/', cronologia_view, name='cronologia'),
]
