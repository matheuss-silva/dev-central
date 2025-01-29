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
        const eventContainer = document.getElementById("event-container");
        const eventNameElement = document.getElementById("event-name");
        const eventDescriptionElement = document.getElementById("event-description");
        const eventStartElement = document.getElementById("event-start");
        const eventEndElement = document.getElementById("event-end");
        const eventStatusElement = document.getElementById("event-status");
        let eventLogoElement = document.getElementById("event-logo");
    
        eventNameElement.textContent = data.name || "Não disponível";
        eventDescriptionElement.textContent = data.description || "Não disponível";
        eventStartElement.textContent = data.start_date || "Não disponível";
        eventEndElement.textContent = data.end_date || "Não disponível";
        eventStatusElement.textContent = data.status || "Não disponível";
    
        // Se o elemento da logo não existir, criamos um
        if (!eventLogoElement) {
            eventLogoElement = document.createElement("img");
            eventLogoElement.id = "event-logo";
            eventLogoElement.alt = "Logotipo do evento";
            eventLogoElement.style.width = "100px";
            eventLogoElement.style.marginBottom = "10px";
            eventContainer.insertBefore(eventLogoElement, eventContainer.firstChild);
        }
    
        // Atualiza o logotipo apenas se a URL for válida
        if (data.logo_url) {
            eventLogoElement.src = data.logo_url;
            eventLogoElement.style.display = "block";
        } else {
            // Garante que a logo permanece caso já tenha sido carregada antes
            if (!eventLogoElement.src) {
                eventLogoElement.style.display = "none";
            }
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
