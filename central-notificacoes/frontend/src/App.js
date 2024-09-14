import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  // Definir um estado para armazenar os posts
  const [posts, setPosts] = useState([]);

  // Função para buscar os posts da API
  useEffect(() => {
    fetch('/api/posts/')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Erro ao buscar postagens');
        }
        return response.json();
      })
      .then((data) => {
        setPosts(data); // Armazenar os posts no estado
      })
      .catch((error) => {
        console.error('Erro ao buscar postagens:', error);
      });
  }, []);

  return (
    <div className="App">
      <h1>Postagens em Tempo Reaaal</h1>
      <div id="post-container">
        {posts.length > 0 ? (
          posts.map((post, index) => (
            <div key={index} className="post">
              <h2>{post.title}</h2>
              <h4>{post.subtitle}</h4>
              {post.image_url && (
                <img src={post.image_url} alt="Imagem do Post" className="post-image" style={{ width: '100px' }} />
              )}
              <p>Autor: {post.author}</p>
            </div>
          ))
        ) : (
          <p>Sem postagens no momento.</p>
        )}
      </div>
    </div>
  );
}

export default App;
