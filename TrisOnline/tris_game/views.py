from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models import Partita
import uuid # Libreria per generare codici random
from django.db.models import Q # Gestire query

def home_view(request):
    # Gestisce la pagina iniziale con logica separata per creare, unirsi o giocare vs BOT.
    if request.method == 'POST':
        nickname = request.POST.get('nickname', '').strip() # strip rimuove spazi iniziali e finali nella stringa
        azione = request.POST.get('azione') # Nuovo campo per distinguere l'azione

        if not nickname:
            return render(request, 'tris_game/home.html', {'errore': 'Il Nickname è obbligatorio.'})

        request.session['nickname'] = nickname

        # --- AZIONE: CREA UNA NUOVA PARTITA PVP ---
        if azione == 'crea_pvp':
            # Genera un codice stanza unico che non sia già in uso per una partita non finita
            while True:
                codice_stanza = str(uuid.uuid4().hex[:6].upper()) # Codice più corto e leggibile
                # Cerca solo partite 'in_corso' o 'attesa'.
                if not Partita.objects.filter(codice_stanza=codice_stanza, stato_partita__in=['attesa', 'in_corso']).exists():
                    break
            
            # Crea la nuova partita
            Partita.objects.create(
                codice_stanza=codice_stanza,
                giocatore1=nickname,
                modalita_gioco='player',
                stato_partita='attesa' # In attesa del secondo giocatore
            )
            return redirect('stanza_gioco', codice_stanza=codice_stanza)

        # --- AZIONE: UNISCITI A PARTITA PVP ESISTENTE ---
        elif azione == 'unisciti_pvp':
            codice_stanza = request.POST.get('codice_stanza', '').strip().upper()
            if not codice_stanza:
                return render(request, 'tris_game/home.html', {'errore': 'Il Codice Stanza è obbligatorio per unirsi.'})

            try:
                # Cerca una partita in attesa con quel codice
                partita = Partita.objects.get(codice_stanza=codice_stanza, stato_partita='attesa')
                
                # Controlla che il giocatore che si unisce non sia lo stesso che ha creato la stanza
                if partita.giocatore1 == nickname:
                    return render(request, 'tris_game/home.html', {'errore': 'Sei già in questa stanza. Attendi un altro giocatore.'})

                return redirect('stanza_gioco', codice_stanza=codice_stanza)

            except Partita.DoesNotExist:
                return render(request, 'tris_game/home.html', {'errore': 'Stanza non trovata o già in corso. Controlla il codice.'})

        # --- AZIONE: GIOCA CONTRO IL BOT ---
        elif azione in ['bot_easy', 'bot_hard']:
            codice_stanza = str(uuid.uuid4().hex[:8])
            Partita.objects.create(
                codice_stanza=codice_stanza,
                giocatore1=nickname,
                giocatore2='BOT',
                modalita_gioco=azione,
                stato_partita='in_corso'
            )
            return redirect('stanza_gioco', codice_stanza=codice_stanza)

    return render(request, 'tris_game/home.html')


def stanza_gioco_view(request, codice_stanza):
    # Renderizza la pagina della stanza di gioco con la scacchiera.
    nickname = request.session.get('nickname')
    if not nickname:
        return redirect('home')

    context = {
        'codice_stanza': codice_stanza,
        'nickname': nickname,
    }
    return render(request, 'tris_game/stanza_gioco.html', context)



def cronologia_view(request):
    # Mostra la cronologia delle partite finite per il giocatore corrente.
    nickname = request.session.get('nickname')
    if not nickname:
        # Se l'utente non ha un nickname in sessione, non può avere una cronologia
        return redirect('home')

    # Filtra le partite in cui il nickname appare come giocatore1 O giocatore2
    # e che sono finite. Le ordina dalla più recente alla più vecchia.
    partite_giocate = Partita.objects.filter(
        Q(giocatore1=nickname) | Q(giocatore2=nickname),
        stato_partita='finita'
    ).order_by('-id')

    context = {
        'nickname': nickname,
        'partite': partite_giocate
    }
    return render(request, 'tris_game/cronologia.html', context)