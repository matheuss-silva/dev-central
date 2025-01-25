document.addEventListener("DOMContentLoaded", () => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const eventSocket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/event/");

    eventSocket.onopen = () => {
        console.log("WebSocket para evento conectado.");
    };

    eventSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Atualização do evento recebida:", data);

        // Atualiza os campos do evento na página
        document.getElementById("event-name").textContent = data.name;
        document.getElementById("event-description").textContent = data.description;
        document.getElementById("event-start").textContent = data.start_date;
        document.getElementById("event-end").textContent = data.end_date;
        const statusElement = document.getElementById("event-status");
        statusElement.textContent = data.status;

        // Alterar cor do status com base no estado
        if (data.status === "Ativo") {
            statusElement.style.color = "green";
        } else if (data.status === "Pausado") {
            statusElement.style.color = "orange";
        } else {
            statusElement.style.color = "red";
        }
    };

    eventSocket.onclose = () => {
        console.log("WebSocket de evento desconectado.");
    };

    eventSocket.onerror = (error) => {
        console.error("Erro no WebSocket de evento:", error);
    };
});
