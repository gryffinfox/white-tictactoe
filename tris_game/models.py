from django.db import models

class Game(models.Model):
    class GameState(models.TextChoices):
        WAITING = 'waiting', 'Waiting for Player'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FINISHED = 'finished', 'Finished'

    class GameMode(models.TextChoices):
        PLAYER = 'player', 'Player vs Player'
        BOT_EASY = 'bot_easy', 'Player vs Bot (Easy)'
        BOT_HARD = 'bot_hard', 'Player vs Bot (Hard)'

    room_code = models.CharField(max_length=100, unique=True)
    player1 = models.CharField(max_length=100, blank=True, null=True) # Nickname del giocatore X
    player2 = models.CharField(max_length=100, blank=True, null=True) # Nickname del giocatore O o 'BOT'
    
    # Stato della scacchiera: 9 caratteri, '_' per vuoto, 'X', 'O'.
    board = models.CharField(max_length=9, default='_________') 
    
    # Simbolo del prossimo turno: 'X' o 'O'.
    current_turn = models.CharField(max_length=1, default='X')
    
    # Stato della partita, con scelte predefinite.
    game_state = models.CharField(max_length=20, default=GameState.WAITING, choices=GameState.choices) 
    
    # Modalità di gioco, con scelte predefinite.
    game_mode = models.CharField(max_length=20, default=GameMode.PLAYER, choices=GameMode.choices)
    
    # Nickname del vincitore o 'Pareggio'.
    winner = models.CharField(max_length=100, blank=True, null=True)

    # Rappresentazione testuale del modello nell'admin di Django.
    def __str__(self):
        return f"Game {self.room_code} ({self.get_game_state_display()})"