import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Partita
from asgiref.sync import sync_to_async

class TrisConsumer(AsyncWebsocketConsumer):
    #Gestisce la logica di gioco in tempo reale.
    async def connect(self):
        self.codice_stanza = self.scope['url_route']['kwargs']['codice_stanza']
        self.gruppo_stanza = f'tris_{self.codice_stanza}'

        await self.channel_layer.group_add(self.gruppo_stanza, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.gruppo_stanza, self.channel_name)

    async def receive(self, text_data):
        dati_json = json.loads(text_data)
        tipo_messaggio = dati_json.get('tipo')

        if tipo_messaggio == 'ingresso_giocatore':
            await self.gestisci_ingresso_giocatore(dati_json)
        elif tipo_messaggio == 'mossa':
            await self.gestisci_mossa(dati_json)

    # --- Gestori di eventi ---

    async def gestisci_ingresso_giocatore(self, dati):
        nickname = dati['nickname']
        partita = await self.get_partita()

        # Assegna il giocatore solo se la modalità è PvP e c'è un posto libero
        if partita.modalita_gioco == 'player':
            if partita.giocatore1 is None:
                partita.giocatore1 = nickname
            elif partita.giocatore2 is None and partita.giocatore1 != nickname:
                partita.giocatore2 = nickname

            # Se entrambi i giocatori sono presenti, inizia la partita
            if partita.giocatore1 and partita.giocatore2:
                partita.stato_partita = 'in_corso'
        
        await self.save_partita(partita)
        await self.invia_stato_partita_a_tutti()

    async def gestisci_mossa(self, dati):
        nickname = dati['nickname']
        indice_cella = int(dati['indice_cella'])
        
        partita = await self.get_partita()

        if not self.is_mossa_valida(partita, nickname, indice_cella):
            return

        partita = self.applica_mossa(partita, indice_cella, partita.prossimo_turno)
        partita = self.aggiorna_stato_post_mossa(partita)
        await self.save_partita(partita)

        if partita.stato_partita == 'in_corso' and partita.prossimo_turno == 'O' and partita.giocatore2 == 'BOT':
            await self.esegui_mossa_bot()
        else:
            await self.invia_stato_partita_a_tutti()

    async def esegui_mossa_bot(self):
        partita = await self.get_partita()
        
        mosse_disponibili = [i for i, v in enumerate(partita.scacchiera) if v == '_']
        if not mosse_disponibili: return

        if partita.modalita_gioco == 'bot_easy':
            mossa_bot = random.choice(mosse_disponibili)
        else: # bot_hard
            mossa_bot = self.calcola_mossa_difficile(partita.scacchiera, 'O', 'X')

        partita = self.applica_mossa(partita, mossa_bot, 'O')
        partita = self.aggiorna_stato_post_mossa(partita)
        await self.save_partita(partita)
        await self.invia_stato_partita_a_tutti()

    # --- Logica di Gioco e Validazione (invariata ma fondamentale) ---
    def is_mossa_valida(self, partita, nickname, indice):
        if partita.stato_partita != 'in_corso': return False
        giocatore_simbolo = 'X' if nickname == partita.giocatore1 else 'O'
        if giocatore_simbolo != partita.prossimo_turno: return False
        if not (0 <= indice < 9) or partita.scacchiera[indice] != '_': return False
        return True

    def applica_mossa(self, partita, indice, simbolo):
        lista_scacchiera = list(partita.scacchiera)
        lista_scacchiera[indice] = simbolo
        partita.scacchiera = "".join(lista_scacchiera)
        return partita

    def aggiorna_stato_post_mossa(self, partita):
        simbolo_vincitore = self.controlla_vincitore(partita.scacchiera)
        if simbolo_vincitore:
            partita.stato_partita = 'finita'
            partita.vincitore = partita.giocatore1 if simbolo_vincitore == 'X' else partita.giocatore2
        elif '_' not in partita.scacchiera:
            partita.stato_partita = 'finita'
            partita.vincitore = 'Pareggio'
        else:
            partita.prossimo_turno = 'O' if partita.prossimo_turno == 'X' else 'X'
        return partita

    def controlla_vincitore(self, s):
        linee = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        for l in linee:
            if s[l[0]] == s[l[1]] == s[l[2]] and s[l[0]] != '_': return s[l[0]]
        return None

    def calcola_mossa_difficile(self, scacchiera, simbolo_bot, simbolo_player):
        mosse_disponibili = [i for i, v in enumerate(scacchiera) if v == '_']
        for simbolo in [simbolo_bot, simbolo_player]:
            for mossa in mosse_disponibili:
                test = list(scacchiera); test[mossa] = simbolo
                if self.controlla_vincitore("".join(test)) == simbolo: return mossa
        if 4 in mosse_disponibili: return 4
        angoli = [i for i in [0,2,6,8] if i in mosse_disponibili]
        if angoli: return random.choice(angoli)
        return random.choice(mosse_disponibili)

    # --- Comunicazione e invio dati ---
    async def invia_stato_partita_a_tutti(self):
        partita = await self.get_partita()
        messaggio, classe_info = self.crea_messaggio_info(partita)
        await self.channel_layer.group_send(
            self.gruppo_stanza,
            {
                'type': 'broadcast_stato',
                'scacchiera': partita.scacchiera,
                'messaggio': messaggio,
                'classe_info': classe_info
            }
        )

    def crea_messaggio_info(self, partita):
        if partita.stato_partita == 'attesa':
            return f"In attesa del 2° giocatore... Codice: {partita.codice_stanza}", "info-attesa"
        if partita.stato_partita == 'in_corso':
            giocatore_di_turno = partita.giocatore1 if partita.prossimo_turno == 'X' else partita.giocatore2
            return f"Turno di: {giocatore_di_turno} ({partita.prossimo_turno})", "info-corso"
        if partita.stato_partita == 'finita':
            return (f"Partita finita in pareggio!", "info-finita") if partita.vincitore == 'Pareggio' else (f"Ha vinto {partita.vincitore}!", "info-finita")
        return "", ""

    async def broadcast_stato(self, event):
        await self.send(text_data=json.dumps(event))

    # --- Interazioni DB ---
    @sync_to_async
    def get_partita(self):
        return Partita.objects.get(codice_stanza=self.codice_stanza)

    @sync_to_async
    def save_partita(self, partita):
        partita.save()