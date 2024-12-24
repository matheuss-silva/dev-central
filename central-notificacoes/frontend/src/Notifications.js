import React, { useState, useEffect } from 'react';

function Notifications() {
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${ws_scheme}://localhost:8000/ws/notifications/`); 
    
    socket.onopen = () => {
        console.log("WebSocket conectado para notificações.");
        
        // Enviar ping a cada 30 segundos para manter a conexão viva
        const pingInterval = setInterval(() => {
            if (socket.readyState === WebSocket.OPEN) {
                socket.send(JSON.stringify({ type: 'ping' }));
            }
        }, 30000); // 30 segundos

        // Limpar o intervalo ao desconectar
        socket.onclose = () => {
            clearInterval(pingInterval);
            console.log("WebSocket desconectado para notificações.");
        };
    };

    socket.onmessage = (event) => {
        console.log("Mensagem recebida:", event.data);
        const data = JSON.parse(event.data);
        const newNotification = data.notification;
        setNotifications(prevNotifications => [newNotification, ...prevNotifications]);
    };

    socket.onerror = (error) => {
        console.error("Erro no WebSocket:", error);
    };

    return () => {
        socket.close();
    };
}, []);

  return (
    <div id="notification-container">
      <h3>Notificações em Tempo Real</h3>
      {notifications.length > 0 ? (
        notifications.map((notification, index) => (
          <div key={index} className="notification">
            <p>{notification}</p>
          </div>
        ))
      ) : (
        <p>Sem notificações no momento.</p>
      )}
    </div>
  );
}

export default Notifications;
