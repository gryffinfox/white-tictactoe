import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Game
from . import game_logic

# Gestisce la connessione WebSocket e la logica di gioco in tempo reale.
class TicTacToeConsumer(AsyncWebsocketConsumer):

    # Chiamato alla connessione di un client.
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'tris_{self.room_code}'
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    # Chiamato alla disconnessione di un client.
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Chiamato quando si riceve un messaggio dal client.
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'player_join':
            await self.handle_player_join(data)
        elif message_type == 'move':
            await self.handle_move(data)

    # Gestisce l'ingresso di un giocatore nella stanza.
    async def handle_player_join(self, data):
        nickname = data['nickname']
        game = await self._get_game()

        if game.game_mode == Game.GameMode.PLAYER:
            if game.player1 is None:
                game.player1 = nickname
            elif game.player2 is None and game.player1 != nickname:
                game.player2 = nickname
                game.game_state = Game.GameState.IN_PROGRESS
        
        await self._save_game(game)
        await self._broadcast_game_state()

    # Gestisce una mossa inviata da un giocatore.
    async def handle_move(self, data):
        nickname = data['nickname']
        cell_index = int(data['cell_index'])
        game = await self._get_game()

        if not self._is_move_valid(game, nickname, cell_index):
            return

        # Applica la mossa e aggiorna lo stato.
        game = self._apply_move(game, cell_index, game.current_turn)
        game = self._update_status_after_move(game)
        await self._save_game(game)

        # Se è il turno del BOT, esegue la sua mossa.
        is_bot_turn = (game.game_state == Game.GameState.IN_PROGRESS and 
                       game.current_turn == 'O' and game.player2 == 'BOT')
        
        if is_bot_turn:
            await self.execute_bot_move()
        else:
            await self._broadcast_game_state()
    
    # Esegue la mossa del BOT in base alla difficoltà.
    async def execute_bot_move(self):
        game = await self._get_game()
        
        bot_move = -1
        if game.game_mode == Game.GameMode.BOT_EASY:
            bot_move = game_logic.calculate_easy_bot_move(game.board, 'O', 'X')
        elif game.game_mode == Game.GameMode.BOT_HARD:
            bot_move = game_logic.calculate_minimax_move(game.board, 'O')['index']

        if bot_move != -1:
            game = self._apply_move(game, bot_move, 'O')
            game = self._update_status_after_move(game)
            await self._save_game(game)
        
        await self._broadcast_game_state()

    # Controlla se una mossa è valida.
    def _is_move_valid(self, game, nickname, index):
        if game.game_state != Game.GameState.IN_PROGRESS: return False
        player_symbol = 'X' if nickname == game.player1 else 'O'
        if player_symbol != game.current_turn: return False
        if not (0 <= index < 9) or game.board[index] != '_': return False
        return True

    # Applica una mossa sulla scacchiera.
    def _apply_move(self, game, index, symbol):
        board_list = list(game.board)
        board_list[index] = symbol
        game.board = "".join(board_list)
        return game

    # Aggiorna lo stato della partita dopo una mossa (vittoria, pareggio, ecc.).
    def _update_status_after_move(self, game):
        winner_symbol = game_logic.check_winner(game.board)
        if winner_symbol:
            game.game_state = Game.GameState.FINISHED
            game.winner = game.player1 if winner_symbol == 'X' else game.player2
        elif '_' not in game.board:
            game.game_state = Game.GameState.FINISHED
            game.winner = 'Draw'
        else:
            game.current_turn = 'O' if game.current_turn == 'X' else 'X'
        return game

    # Invia lo stato aggiornato della partita a tutti i client nel gruppo.
    async def _broadcast_game_state(self):
        game = await self._get_game()
        message, info_class = self._create_info_message(game)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'broadcast.state', # Nome del gestore per l'evento
                'board': game.board,
                'message': message,
                'info_class': info_class
            }
        )

    # Prepara il messaggio di stato da visualizzare sul client.
    def _create_info_message(self, game):
        if game.game_state == Game.GameState.WAITING:
            return f"Waiting for Player 2... Code: {game.room_code}", "info-waiting"
        if game.game_state == Game.GameState.IN_PROGRESS:
            turn_player = game.player1 if game.current_turn == 'X' else game.player2
            return f"Turn: {turn_player} ({game.current_turn})", "info-progress"
        if game.game_state == Game.GameState.FINISHED:
            if game.winner == 'Draw':
                return "Game ended in a draw!", "info-finished"
            return f"{game.winner} has won!", "info-finished"
        return "", ""

    # Invia i dati al singolo client WebSocket. (Nota: il nome del metodo deve corrispondere al 'type' in group_send)
    async def broadcast_state(self, event):
        await self.send(text_data=json.dumps(event))

    # Recupera la partita dal DB in modo asincrono.
    @sync_to_async
    def _get_game(self):
        return Game.objects.get(room_code=self.room_code)

    # Salva la partita nel DB in modo asincrono.
    @sync_to_async
    def _save_game(self, game):
        game.save()