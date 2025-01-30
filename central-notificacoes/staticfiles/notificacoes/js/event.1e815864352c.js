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
        console.log("WebSocket de evento desconectado. Tentando reconectar...");
        setTimeout(() => {
            window.location.reload(); // Recarregar página se a conexão for perdida
        }, 5000);
    };

    eventSocket.onerror = (error) => {
        console.error("Erro no WebSocket de evento:", error);
    };

    function updateEvent(data) {
        const eventContainer = document.getElementById("event-container");

        // Verifica se o evento é o mesmo antes de atualizar
        if (eventContainer.getAttribute("data-event-id") !== data.id) {
            eventContainer.setAttribute("data-event-id", data.id);
        }

        document.getElementById("event-name").textContent = data.name || "Não disponível";
        document.getElementById("event-description").textContent = data.description || "Não disponível";
        document.getElementById("event-start").textContent = data.start_date || "Não disponível";
        document.getElementById("event-end").textContent = data.end_date || "Não disponível";
        document.getElementById("event-status").textContent = data.status || "Não disponível";

        const eventLogoElement = document.getElementById("event-logo");
        if (data.logo_url) {
            eventLogoElement.src = data.logo_url;
            eventLogoElement.style.display = "block";
        } else {
            eventLogoElement.style.display = "none";
        }

        // Atualizar cor do status dinamicamente
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
