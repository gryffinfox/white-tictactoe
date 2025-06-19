from django.db import models
import json

class Partita(models.Model):
    codice_stanza = models.CharField(max_length=100, unique=True)
    giocatore1 = models.CharField(max_length=100, blank=True, null=True) # Nickname giocatore X
    giocatore2 = models.CharField(max_length=100, blank=True, null=True) # Nickname giocatore O o 'BOT'
    
    # Stato della scacchiera: 9 caratteri, '_' per vuoto, 'X', 'O'
    # Esempio: "X_O___O_X"
    scacchiera = models.CharField(max_length=9, default='_________') 
    
    # 'X' o 'O'
    prossimo_turno = models.CharField(max_length=1, default='X')
    
    # 'attesa', 'in_corso', 'finita'
    stato_partita = models.CharField(max_length=10, default='attesa', choices=[('attesa', 'In attesa'), ('in_corso', 'In Corso'), ('finita', 'Finita')]) 
    
    # 'player' o 'bot_easy' o 'bot_hard'
    modalita_gioco = models.CharField(max_length=10, default='player',choices=[('player', 'Player vs Player'), ('bot_easy', 'Player vs Bot Facile'), ('bot_hard', 'Player vs Bot Difficile')])
    
    vincitore = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Partita {self.codice_stanza} ({self.stato_partita})"
