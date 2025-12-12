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
    
    melodify_player.playlist[ melodify_player.index ].next = song;
}

PlaylistManager.prototype.addSongToPlaylist = function(playlist_id){
    song_id = document.getElementById('playlists-window').getAttribute('data-song');
    // Enviar datos al endpoint de Django usando AJAX POST
    fetch('/playlists/populate/', { // Usaremos este nombre de URL en urls.py
        method: 'POST',
        headers: {
            'Content-Type'      : 'application/json',
            'X-CSRFToken'       : getCookie('csrftoken'), 
            'X-Requested-With'  : 'XMLHttpRequest'
        },
        body: JSON.stringify({ song: song_id, playlist: playlist_id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // loadPlaylists(); 
            hidePlaylists();
        } else if (data.status === 'login') {
            window.location = '/accounts/login/?next=/';
        } else {
            alert('Error al asociar la pista a la lista: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ocurrió un error de red o del servidor.');
    });

}

PlaylistManager.prototype.request = function(json_data, url, done_callback) { 
    fetch(
        url, 
        { 
            method: 'POST',
            headers: {
                'Content-Type'      : 'application/json',
                'X-CSRFToken'       : getCookie('csrftoken'), 
                'X-Requested-With'  : 'XMLHttpRequest'
            }, body: JSON.stringify(json_data)
        }
    )
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            done_callback(data);
        } else if (data.status === 'login') {
            window.location = '/accounts/login/?next=/';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ocurrió un error de red o del servidor.');
    });
}

PlaylistManager.prototype.remSongToPlaylist = function(playlist_id, song_id){
    // Enviar datos al endpoint de Django usando AJAX POST
    fetch('/playlists/removefrom/', { 
        method: 'POST',
        headers: {
            'Content-Type'      : 'application/json',
            'X-CSRFToken'       : getCookie('csrftoken'), 
            'X-Requested-With'  : 'XMLHttpRequest'
        },
        body: JSON.stringify({ song: song_id, playlist: playlist_id })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // loadPlaylists(); 
            hidePlaylists();
        } else if (data.status === 'login') {
            window.location = '/accounts/login/?next=/';
        } else {
            alert('Error al asociar la pista a la lista: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ocurrió un error de red o del servidor.');
    });
}

PlaylistManager.prototype.createPlaylist = function() {
    const playlistNameInput = document.getElementById('new-list-name');
    const playlistName = playlistNameInput.value.trim();

    if (!playlistName) {
        alert("Por favor, introduce un nombre para la lista.");
        return;
    }

    this.request('/playlist/new/', { name : playlistName }, ()=>{ 
        toggleNewListForm(); 
        currentSearchTerm = ''; // Reseteamos el término de búsqueda si es necesario
        nextPage = 1;
        container.innerHTML = '';
        loadPlaylists(); 
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