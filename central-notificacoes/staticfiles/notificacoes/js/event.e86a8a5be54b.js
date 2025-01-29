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
        updateEvent(data);
    };

    eventSocket.onclose = () => {
        console.log("WebSocket de evento desconectado.");
    };

    eventSocket.onerror = (error) => {
        console.error("Erro no WebSocket de evento:", error);
    };

    function updateEvent(data) {
        const eventNameElement = document.getElementById("event-name");
        const eventDescriptionElement = document.getElementById("event-description");
        const eventStartElement = document.getElementById("event-start");
        const eventEndElement = document.getElementById("event-end");
        const eventStatusElement = document.getElementById("event-status");
        const eventLogoElement = document.getElementById("event-logo");
    
        eventNameElement.textContent = data.name || "Não disponível";
        eventDescriptionElement.textContent = data.description || "Não disponível";
        eventStartElement.textContent = data.start_date || "Não disponível";
        eventEndElement.textContent = data.end_date || "Não disponível";
        eventStatusElement.textContent = data.status || "Não disponível";
    
        // Atualiza o logotipo apenas se existir
        if (data.logo_url) {
            eventLogoElement.src = data.logo_url;
            eventLogoElement.style.display = "block";
        } else {
            eventLogoElement.style.display = "none";
        }
    
        // Altera a cor do status
        if (data.status === "Ativo") {
            eventStatusElement.style.color = "green";
        } else if (data.status === "Pausado") {
            eventStatusElement.style.color = "orange";
        } else {
            eventStatusElement.style.color = "red";
        }
    }
    
    
});
