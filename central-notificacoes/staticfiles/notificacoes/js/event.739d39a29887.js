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

        // 🚀 Agendar um refresh 2 segundos após o horário de início do evento
        if (data.start_date && data.status === "Aguardando Início") {
            const eventStartTime = convertTimeToDate(data.start_date);
            const now = new Date();
            
            // Se o evento deveria ter iniciado, forçar a atualização
            if (now >= eventStartTime) {
                console.log("⏳ Evento iniciou! Agendando atualização...");
                setTimeout(() => {
                    console.log("🔄 Forçando atualização do status do evento...");
                    eventSocket.send(JSON.stringify({ action: "refresh" }));
                }, 2000); // Espera 2 segundos
            }
        }
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
            eventContainer.setAttribute("data-event-id", data.id);

            document.getElementById("event-name").textContent = data.name || "Não disponível";
            document.getElementById("event-description").textContent = data.description || "Não disponível";
            document.getElementById("event-start").textContent = data.start_date || "Não disponível";
            document.getElementById("event-end").textContent = data.end_date || "Não disponível";
            document.getElementById("event-status").textContent = data.status || "Não disponível";

            const eventLogoElement = document.getElementById("event-logo");
            if (eventLogoElement) {
                if (data.logo_url) {
                    eventLogoElement.src = data.logo_url;
                    eventLogoElement.style.display = "block";  // Mostra a logo se existir
                } else {
                    eventLogoElement.style.display = "none";  // Oculta se não houver logo
                }
            }

            // Atualizar cor do status dinamicamente
            const statusElement = document.getElementById("event-status");
            if (statusElement) {
                const statusColors = {
                    "Ativo": "green",
                    "Aguardando Início": "blue",
                    "Encerrado (dia)": "gray",
                    "Finalizado": "red"
                };
                statusElement.style.color = statusColors[data.status] || "black";
            }
        } else {
            console.error("⚠️ Elemento 'event-container' não encontrado na página.");
        }
    }

    function convertTimeToDate(timeString) {
        const [hours, minutes] = timeString.split(":").map(Number);
        const now = new Date();
        now.setHours(hours, minutes, 0, 0); // Define o horário baseado no start_date do evento
        return now;
    }
});
