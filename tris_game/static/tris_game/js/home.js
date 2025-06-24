document.addEventListener('DOMContentLoaded', () => {
    const roomCodeContainer = document.getElementById('room-code-container');
    const actionRadios = document.querySelectorAll('input[name="action"]');
    const actionButton = document.getElementById('action-button');

    function updateFormDisplay() {
        const selectedAction = document.querySelector('input[name="action"]:checked').value;

        if (selectedAction === 'join_pvp') {
            roomCodeContainer.classList.add('show');
            actionButton.textContent = 'Join Room';
        } else {
            roomCodeContainer.classList.remove('show');
            if (selectedAction === 'create_pvp') {
                actionButton.textContent = 'Create Room';
            } else if (selectedAction === 'bot_easy') {
                actionButton.textContent = 'Play vs. BOT (Easy)';
            } else {
                actionButton.textContent = 'Play vs. BOT (Hard)';
            }
        }
    }

    actionRadios.forEach(radio => radio.addEventListener('change', updateFormDisplay));
    
    // Inizializza lo stato corretto al caricamento della pagina
    updateFormDisplay();
});