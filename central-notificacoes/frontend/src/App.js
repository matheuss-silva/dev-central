import React, { useState, useEffect } from 'react';
import Notifications from './Notifications';
import Posts from './Posts';

function App() {
  const [userId] = useState(null);  // Inicialmente nulo
  const [posts, setPosts] = useState([]);      // Estado para as postagens
  const [notifications, setNotifications] = useState([]);  // Estado para as notificações

  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/posts/')
      .then(response => response.json())
      .then(data => setPosts(data))
      .catch(error => console.error("Erro ao buscar postagens:", error));
    
    fetch('http://127.0.0.1:8000/api/notifications/')
      .then(response => response.json())
      .then(data => setNotifications(data))
      .catch(error => console.error("Erro ao buscar notificações:", error));
  }, []);

  return (
    <div className="App">
      <Notifications userId={userId} notifications={notifications} />  {/* Passa as notificações */}
      <Posts posts={posts} />  {/* Passa as postagens para o componente Posts */}
    </div>
  );
}

export default App;
