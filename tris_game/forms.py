from django import forms

# Definisce il form di ingresso per la home page.
class EntryForm(forms.Form):
    nickname = forms.CharField(
        label="Enter your nickname", 
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your nickname'})
    )
    action = forms.ChoiceField(
        choices=[
            ('create_pvp', 'Create Room'),
            ('join_pvp', 'Join Room'),
            ('bot_easy', 'Play vs. BOT (Easy)'),
            ('bot_hard', 'Play vs. BOT (Hard)'),
        ],
        widget=forms.RadioSelect,
        initial='create_pvp'
    )
    room_code = forms.CharField(
        label="Room Code", 
        max_length=10, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Room Code', 'style': 'text-transform: uppercase;'})
    )

    # Validazione custom per rendere il room_code obbligatorio solo per l'azione 'join_pvp'.
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        room_code = cleaned_data.get('room_code')

        if action == 'join_pvp' and not room_code:
            self.add_error('room_code', "Room code is required to join a game.")
        
        # Pulisce e formatta i dati prima di restituirli.
        if room_code:
            cleaned_data['room_code'] = room_code.upper().strip()
        if cleaned_data.get('nickname'):
            cleaned_data['nickname'] = cleaned_data['nickname'].strip()

        return cleaned_data