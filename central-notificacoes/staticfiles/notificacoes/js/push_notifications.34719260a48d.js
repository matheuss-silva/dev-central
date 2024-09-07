document.addEventListener('DOMContentLoaded', function() {
    const notificationsContainer = document.getElementById('push-notification-area');
    const userId = notificationsContainer.dataset.userId;  // Pega o valor de user_id_json do data-attribute

    console.log('User ID: ', userId);

    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(ws_scheme + '://' + window.location.host + '/ws/notifications/' + userId + '/');

    socket.onopen = function() {
        console.log('WebSocket conectado.');
    };

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        const message = data['message'];
        console.log('Mensagem recebida via WebSocket:', message);

        // Adiciona a notificação
        addNotification(message);
    };

    socket.onclose = function() {
        console.log('WebSocket desconectado.');
    };

    socket.onerror = function(e) {
        console.error('Erro no WebSocket:', e);
    };

    function addNotification(message) {
        const notificationElement = document.createElement('div');
        notificationElement.className = 'notification';
        notificationElement.textContent = message;
        notificationsContainer.prepend(notificationElement);

        // Remover notificação após 5 segundos
        setTimeout(() => {
            console.log("Removendo notificação:", notificationElement.textContent);
            notificationElement.remove();
        }, 5000);  // 5 segundos para remover a notificação
    }
});
