document.addEventListener('DOMContentLoaded', function () {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(ws_scheme + '://' + window.location.host + '/ws/event/');

    socket.onopen = function () {
        console.log("WebSocket conectado para eventos.");
    };

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        if (data.status) {
            const statusElement = document.querySelector('#event-container span');
            statusElement.textContent = data.status;
            statusElement.style.color = data.status === "Ativo" ? "green" : (data.status === "Pausado" ? "yellow" : "red");
        }
    };

    socket.onclose = function () {
        console.log("WebSocket desconectado.");
    };
});
