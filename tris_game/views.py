from django.shortcuts import render, redirect
from django.db.models import Q
import uuid
from .models import Game
from .forms import EntryForm

# Gestisce la home page, la creazione e l'unione a partite.
def home_view(request):
    if request.method == 'POST':
        form = EntryForm(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data['nickname']
            action = form.cleaned_data['action']
            room_code = form.cleaned_data.get('room_code')

            request.session['nickname'] = nickname

            # Crea una nuova partita PvP.
            if action == 'create_pvp':
                new_code = str(uuid.uuid4().hex[:6].upper())
                Game.objects.create(
                    room_code=new_code, player1=nickname, 
                    game_mode=Game.GameMode.PLAYER, game_state=Game.GameState.WAITING
                )
                return redirect('game_room', room_code=new_code)

            # Unisciti a una partita PvP.
            elif action == 'join_pvp':
                try:
                    game = Game.objects.get(room_code=room_code, game_state=Game.GameState.WAITING)
                    if game.player1 == nickname:
                        form.add_error(None, 'You are already in this room. Wait for a friend.')
                    else:
                        return redirect('game_room', room_code=room_code)
                except Game.DoesNotExist:
                    form.add_error('room_code', 'Room not found or is already full.')

            # Gioca contro il BOT.
            elif action in [Game.GameMode.BOT_EASY, Game.GameMode.BOT_HARD]:
                new_code = str(uuid.uuid4().hex[:8].upper())
                Game.objects.create(
                    room_code=new_code, player1=nickname, player2='BOT',
                    game_mode=action, game_state=Game.GameState.IN_PROGRESS
                )
                return redirect('game_room', room_code=new_code)
    else:
        form = EntryForm(initial={'nickname': request.session.get('nickname', '')})

    return render(request, 'tris_game/home.html', {'form': form})

# Renderizza la pagina della stanza di gioco.
def game_room_view(request, room_code):
    nickname = request.session.get('nickname')
    if not nickname: return redirect('home')
    
    context = {'room_code': room_code, 'nickname': nickname}
    return render(request, 'tris_game/game_room.html', context)

# Mostra la cronologia delle partite giocate.
def history_view(request):
    nickname = request.session.get('nickname')
    if not nickname: return redirect('home')

    played_games = Game.objects.filter(
        Q(player1=nickname) | Q(player2=nickname),
        game_state=Game.GameState.FINISHED
    ).order_by('-id')

    context = {'nickname': nickname, 'games': played_games}
    return render(request, 'tris_game/history.html', context)