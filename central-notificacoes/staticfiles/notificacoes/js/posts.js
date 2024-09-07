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
        const post = data['post'];
        console.log('Novo post recebido via WebSocket:', post);
        addPost(post);
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

        postElement.innerHTML = `
            <h2>${post.title}</h2>
            <h4>${post.subtitle}</h4>
            <img src="${post.image_url}" alt="Imagem do post" class="post-image" style="width: 100px;">
        `;

        postsContainer.prepend(postElement);
    }
});
