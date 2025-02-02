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
        const postElement = document.createElement('div');
        postElement.className = 'post';
        postElement.setAttribute('data-post-id', post.id);
        postElement.style.cssText = 'margin-bottom: 20px; border: 1px solid #ccc; padding: 10px; border-radius: 5px;';
    
        postElement.innerHTML = `
            <h2>${post.title}</h2>
            <h4>${post.subtitle}</h4>
            <p><strong>Autor:</strong> ${post.author}</p>
            <p><strong>Publicado em:</strong> ${post.created_at}</p> <!-- ✅ Exibe a data corretamente -->
            ${post.image_url ? `<img src="${post.image_url}" alt="Imagem do post" class="post-image" style="width: 100px;">` : ''}
        `;
    
        postsContainer.prepend(postElement);
    }
    

    function removePost(postId) {
        const postElement = document.querySelector(`[data-post-id="${postId}"]`);
        if (postElement) {
            postElement.remove();
            console.log(`Post com ID ${postId} removido da interface.`);
        } else {
            console.error(`Post com ID ${postId} não encontrado na interface.`);
        }
    }
    
});
