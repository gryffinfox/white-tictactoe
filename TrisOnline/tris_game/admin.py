from django.contrib import admin
from .models import Partita

@admin.register(Partita)
class PartitaAdmin(admin.ModelAdmin):
    list_display = ('codice_stanza', 'giocatore1', 'giocatore2', 'stato_partita', 'modalita_gioco', 'vincitore', 'prossimo_turno')
    list_filter = ('stato_partita', 'modalita_gioco')
    search_fields = ('codice_stanza', 'giocatore1', 'giocatore2')
    readonly_fields = ('scacchiera',)