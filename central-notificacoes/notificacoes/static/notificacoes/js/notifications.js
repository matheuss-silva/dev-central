document.addEventListener('DOMContentLoaded', function() {
    var userIdElement = document.getElementById('user-id');
    var user_id = userIdElement ? userIdElement.textContent : null;

    console.log("UserID: ", user_id);

    if (!user_id || user_id === "null") {
        console.error("UserID não encontrado ou é null.");
        return;
    }
    
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + '/ws/notifications/' + user_id + '/';
    console.log("WebSocket Path: ", ws_path);

    function connectWebSocket() {
        var websocket = new WebSocket(ws_path);

        websocket.onopen = function() {
            console.log("WebSocket aberto com sucesso.");
        };

        websocket.onclose = function(e) {
            console.error('WebSocket closed unexpectedly. Tentando reconectar...');
            setTimeout(connectWebSocket, 1000);  // Tenta reconectar após 1 segundo
        };

        websocket.onmessage = function(event) {
            try {
                const data = JSON.parse(event.data);
                const notificationArea = document.getElementById('notification-area');
                
                if (notificationArea) {
                    const messageDiv = document.createElement('div');
                    messageDiv.textContent = data.message;
                    notificationArea.appendChild(messageDiv);
                } else {
                    console.error("Elemento com ID 'notification-area' não encontrado.");
                }
            } catch (e) {
                console.error('Erro ao processar mensagem WebSocket: ', e);
            }
        };
    }

    connectWebSocket();
});
