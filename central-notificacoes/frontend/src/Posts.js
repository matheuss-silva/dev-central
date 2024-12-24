import React, { useState, useEffect } from 'react';

function Posts() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(`${ws_scheme}://localhost:8000/ws/posts/`); 

    const ping = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }));
        }
    }, 30000); // Ping a cada 30 segundos

    socket.onopen = () => {
        console.log("WebSocket conectado para postagens.");
    };

    socket.onmessage = (event) => {
        console.log("Mensagem recebida:", event.data);
        const data = JSON.parse(event.data);
        const newPost = data.post;
        setPosts(prevPosts => [newPost, ...prevPosts]);
    };

    socket.onerror = (error) => {
        console.error("Erro no WebSocket:", error);
    };

    socket.onclose = (e) => {
        console.log("WebSocket desconectado para postagens:", e);
        clearInterval(ping); // Limpa o ping quando o WebSocket for fechado
    };

    return () => {
        clearInterval(ping);
        socket.close();
    };
}, []);



  return (
    <div id="post-container">
      <h3>Postagens em Tempo Real</h3>
      {posts.length > 0 ? (
        posts.map((post, index) => (
          <div key={index} className="post">
            <h2>{post.title}</h2>
            <h4>{post.subtitle}</h4>
            {post.image_url && <img src={post.image_url} alt="Imagem do post" style={{ width: '100px' }} />}
          </div>
        ))
      ) : (
        <p>Sem postagens no momento.</p>
      )}
    </div>
  );
}

export default Posts;
