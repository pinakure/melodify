function PlaylistManager(){

}

function hidePlaylists( ){
    const div = document.getElementById('playlists-window');
    div.style.display = 'none';
}

function showPlaylists( parent, song_id ){
    const div = document.getElementById('playlists-window');
    div.style.display = 'inline-block';

    /* Do stuff */
    document.getElementById('playlists-window').setAttribute('data-song', song_id);
}

function enqueueSong( artist, title, filename, node_id, song_id ){
    alert(`Enqueue ${title}...`);
    var song = {
        title   : `${artist}`,
        file    : filename,
        howl    : null,
        next    : melodify_player.playlist[ melodify_player.index ].next ?? null,
    };
    melodify_player.enqueue(song); 
    melodify_player.playlist[ melodify_player.playlist.count-2 ].next = melodify_player.playlist[ melodify_player.playlist.count-2 ].next; 
    
    melodify_player.playlist[ melodify_player.index ].next = song; ç
}

PlaylistManager.prototype.addSongToPlaylist = function(playlist_id){
    song_id = document.getElementById('playlists-window').getAttribute('data-song');
    // Enviar datos al endpoint de Django usando AJAX POST
    fetch('/playlists/populate/', { // Usaremos este nombre de URL en urls.py
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Importante: Necesitas el CSRF token para peticiones POST en Django
            'X-CSRFToken': getCookie('csrftoken'), 
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ song: song_id, playlist: playlist_id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // loadPlaylists(); 
            hidePlaylists();
        } else {
            alert('Error al asociar la pista a la lista: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ocurrió un error de red o del servidor.');
    });

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const playlistmgr = new PlaylistManager();