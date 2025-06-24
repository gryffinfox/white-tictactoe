from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('room_code', 'player1', 'player2', 'game_state', 'game_mode', 'winner', 'current_turn')
    list_filter = ('game_state', 'game_mode')
    search_fields = ('room_code', 'player1', 'player2')
    readonly_fields = ('board',)