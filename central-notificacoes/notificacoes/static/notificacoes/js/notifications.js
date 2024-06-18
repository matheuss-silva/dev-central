document.addEventListener('DOMContentLoaded', function() {
    var userIdElement = document.getElementById('user-id');
    var user_id = userIdElement ? userIdElement.textContent : null;

    console.log("UserID: ", user_id);  // Log do UserID para depuração

    if (!user_id || user_id === "null") {
        console.error("UserID não encontrado ou é null.");
        return;
    }
    
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + '/ws/notifications/' + user_id + '/';
    console.log("WebSocket Path: ", ws_path);  // Log do caminho do WebSocket para depuração

    var websocket = new WebSocket(ws_path);

    websocket.onopen = function() {
        console.log("WebSocket aberto com sucesso.");
    };

    websocket.onclose = function(e) {
        console.error('WebSocket closed unexpectedly');
    };

    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const notificationArea = document.getElementById('notification-area');
        const messageDiv = document.createElement('div');
        messageDiv.textContent = data.message;
        notificationArea.appendChild(messageDiv);
    };
      
});
