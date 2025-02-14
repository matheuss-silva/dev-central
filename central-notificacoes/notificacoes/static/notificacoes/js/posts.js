document.addEventListener('DOMContentLoaded', function() {
    const postsContainer = document.getElementById('post-container');
    const userId = postsContainer.dataset.userId;

    if (!userId) {
        console.error("User ID não encontrado.");
        return;
    }

    console.log('User ID: ', userId);

    const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
    const socket = new WebSocket(ws_scheme + '://' + window.location.host + '/ws/posts/' + userId + '/');

    socket.onopen = function() {
        console.log("WebSocket conectado para postagens.");
    };

    socket.onmessage = function(event) {
        // Recebe mensagens WebSocket para adicionar ou remover posts em tempo real.
        const data = JSON.parse(event.data);
        const action = data['action'];

        if (action === 'add') {
            const post = data['post'];
            console.log('Novo post recebido via WebSocket:', post);
            addPost(post);
        } else if (action === 'delete') {
            const postId = data['post_id'];
            console.log('Post excluído via WebSocket:', postId);
            removePost(postId);
        }
    };

    socket.onclose = function() {
        console.log("WebSocket para postagens desconectado.");
    };

    socket.onerror = function(e) {
        console.error("Erro no WebSocket para postagens:", e);
    };

    function addPost(post) {
        // Cria um novo post e adiciona dinamicamente à interface do usuário.
        const postElement = document.createElement('div');
        postElement.className = 'post';
        postElement.setAttribute('data-post-id', post.id);
        postElement.style.cssText = 'margin-bottom: 20px; border: 1px solid #ccc; padding: 10px; border-radius: 5px;';
        
        const formattedDate = post.created_at && post.created_at !== "Horário não disponível"
            ? post.created_at
            : new Date().toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
    
        postElement.innerHTML = `
            <h2>${post.title}</h2>
            <h4>${post.subtitle}</h4>
            <p><strong>Autor:</strong> ${post.author}</p>
            <p><strong>Publicado em:</strong> ${formattedDate}</p>
            ${post.image_url ? `<img src="${post.image_url}" alt="Imagem do post" class="post-image" style="width: 100px;">` : ''}
        `;
    
        postsContainer.prepend(postElement);
    }
    
    

    function removePost(postId) {
        // Remove um post da interface quando ele é excluído pelo autor.
        const postElement = document.querySelector(`[data-post-id="${postId}"]`);
        if (postElement) {
            postElement.remove();
            console.log(`Post com ID ${postId} removido da interface.`);
        } else {
            console.error(`Post com ID ${postId} não encontrado na interface.`);
        }
    }
    
});
