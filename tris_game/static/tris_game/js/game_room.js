const roomCode = JSON.parse(document.getElementById('json-room-code').textContent);
const nickname = JSON.parse(document.getElementById('json-nickname').textContent);
const gameInfoEl = document.getElementById('game-info');
const gameBoardEl = document.getElementById('game-board');

const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
const socket = new WebSocket(
    `${protocol}://${window.location.host}/ws/tris/${roomCode}/`
);

socket.onopen = function(e) {
    console.log("WebSocket connection opened.");
    socket.send(JSON.stringify({ 'type': 'player_join', 'nickname': nickname }));
};

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Data received:", data);

    // Aggiorna messaggio e stile
    gameInfoEl.textContent = data.message;
    gameInfoEl.className = 'info-base'; // Rimuove tutte le classi di stato
    gameInfoEl.classList.add(data.info_class);

    // Aggiorna scacchiera
    const board = data.board;
    for (let i = 0; i < board.length; i++) {
        const cell = document.getElementById(`cell-${i}`);
        const symbol = board[i];
        cell.textContent = symbol === '_' ? '' : symbol;

        cell.classList.remove('X', 'O');
        if (symbol === 'X') cell.classList.add('X');
        if (symbol === 'O') cell.classList.add('O');
    }
};

socket.onclose = function(e) {
    console.error('WebSocket connection closed unexpectedly.');
    gameInfoEl.textContent = 'Connection lost. Please reload the page.';
    gameInfoEl.className = 'info-base info-waiting';
};

gameBoardEl.addEventListener('click', function(e) {
    if (e.target.classList.contains('cell')) {
        const cellIndex = e.target.getAttribute('data-index');
        socket.send(JSON.stringify({
            'type': 'move',
            'cell_index': cellIndex,
            'nickname': nickname
        }));
    }
});