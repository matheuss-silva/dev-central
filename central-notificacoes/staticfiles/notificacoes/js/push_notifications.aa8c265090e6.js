document.addEventListener('DOMContentLoaded', function() {
    var userIdElement = document.getElementById('user-id');
    var user_id = userIdElement ? userIdElement.textContent : null;

    if (!user_id || user_id === "null") {
        console.error("UserID não encontrado ou é null.");
        return;
    }
    
    var ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + '/ws/notifications/' + user_id + '/';

    var websocket = new WebSocket(ws_path);

    websocket.onopen = function() {
        console.log("WebSocket conectado.");
    };

    websocket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const pushNotificationArea = document.getElementById('push-notification-area');  

        if (pushNotificationArea) {
            const notificationDiv = document.createElement('div');
            notificationDiv.classList.add('push-notification');
            notificationDiv.textContent = data.message;
            pushNotificationArea.appendChild(notificationDiv);

            console.log("Notificação adicionada:", notificationDiv.textContent);

            // Remover notificação após 5 segundos
            setTimeout(() => {
                console.log("Removendo notificação:", notificationDiv.textContent);
                notificationDiv.remove();
            }, 5000);  // 5 segundos
        } else {
            console.error("Elemento 'push-notification-area' não encontrado.");
        }
    };

    websocket.onclose = function(e) {
        console.error('WebSocket fechado inesperadamente');
    };
});
