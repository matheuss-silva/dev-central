document.addEventListener("DOMContentLoaded", () => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const eventSocket = new WebSocket(ws_scheme + "://" + window.location.host + "/ws/event/");

    eventSocket.onopen = () => {
        console.log("✅ WebSocket para evento conectado.");
        eventSocket.send(JSON.stringify({ action: "refresh" }));
    };

    eventSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("🔄 Atualização do evento recebida:", data);
        updateEvent(data);
    };

    eventSocket.onclose = () => {
        console.log("⚠️ WebSocket de evento desconectado. Tentando reconectar...");
        setTimeout(() => {
            window.location.reload();
        }, 5000);
    };

    eventSocket.onerror = (error) => {
        console.error("❌ Erro no WebSocket de evento:", error);
    };

    function updateEvent(data) {
        const eventContainer = document.getElementById("event-container");

        if (eventContainer) {
            if (eventContainer.getAttribute("data-event-id") !== String(data.id)) {
                eventContainer.setAttribute("data-event-id", data.id);
            }

            document.getElementById("event-name").textContent = data.name || "Não disponível";
            document.getElementById("event-description").textContent = data.description || "Não disponível";
            document.getElementById("event-start").textContent = data.start_date || "Não disponível";
            document.getElementById("event-end").textContent = data.end_date || "Não disponível";
            document.getElementById("event-status").textContent = data.status || "Não disponível";

            const eventLogoElement = document.getElementById("event-logo");
            if (eventLogoElement) {
                if (data.logo_url) {
                    eventLogoElement.src = data.logo_url;
                    eventLogoElement.style.display = "block";
                } else {
                    eventLogoElement.style.display = "none";
                }
            }

            const statusElement = document.getElementById("event-status");
            if (statusElement) {
                statusElement.style.color = {
                    "Ativo": "green",
                    "Aguardando Início": "blue",
                    "Encerrado (dia)": "gray",
                    "Finalizado": "red"
                }[data.status] || "black";
            }
        }
    }
});
