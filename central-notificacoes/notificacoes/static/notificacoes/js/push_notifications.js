document.addEventListener('DOMContentLoaded', function() {
    const userId = "{{ user_id_json|escapejs }}";  // Certifique-se de que o user_id está correto
    const notificationsContainer = document.getElementById('push-notification-area');  // Certifique-se de que existe essa área

    console.log('User ID: ', userId);

    // Conectar ao WebSocket
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
        console.error('WebSocket erro:', e);
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
