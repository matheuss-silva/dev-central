document.addEventListener("DOMContentLoaded", () => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const eventSocket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/event/");

    eventSocket.onopen = () => {
        console.log("WebSocket para evento conectado.");
    };

    eventSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("Atualização do evento recebida:", data);
        updateEvent(data);
    };

    eventSocket.onclose = () => {
        console.log("WebSocket de evento desconectado.");
    };

    eventSocket.onerror = (error) => {
        console.error("Erro no WebSocket de evento:", error);
    };

    function updateEvent(data) {
        document.getElementById("event-name").textContent = data.name || "Não disponível";
        document.getElementById("event-description").textContent = data.description || "Não disponível";
        document.getElementById("event-status").textContent = data.status || "Não disponível";

        const eventLogoElement = document.getElementById("event-logo");
        if (data.logo_url) {
            eventLogoElement.src = data.logo_url;
            eventLogoElement.style.display = "block";
        } else {
            eventLogoElement.style.display = "none";
        }

        // Muda cor do status
        const statusElement = document.getElementById("event-status");
        switch (data.status) {
            case "Ativo":
                statusElement.style.color = "green";
                break;
            case "Pausado":
                statusElement.style.color = "orange";
                break;
            case "Finalizado":
                statusElement.style.color = "red";
                break;
            default:
                statusElement.style.color = "black";
        }
    }
});
