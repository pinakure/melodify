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


PlaylistManager.prototype.request = function(url, json_data, done_callback) { 
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
            window.location = `/accounts/login/?next=${window.location}`;
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ocurrió un error de red o del servidor.');
    });
}

PlaylistManager.prototype.addSongToPlaylist = function(playlist_id){
    song_id = document.getElementById('playlists-window').getAttribute('data-song');
    this.request('/playlists/populate/', { song : song_id, playlist : playlist_id }, ()=>{ 
        hidePlaylists();
        location.reload(); 
    });
}

PlaylistManager.prototype.remSongFromPlaylist = function(playlist_id, song_id){
    this.request('/playlists/songs/remove/', { song : song_id, playlist : playlist_id }, ()=>{ 
        location.reload(); 
    });
}

PlaylistManager.prototype.createPlaylist = function() {
    const playlistNameInput = document.getElementById('new-list-name');
    const playlistName = playlistNameInput.value.trim();

    if (!playlistName) {
        alert("Por favor, introduce un nombre para la lista.");
        return;
    }

    this.request('/playlists/new/', { name : playlistName }, ()=>{ 
        toggleNewListForm(); 
        currentSearchTerm = ''; // Reseteamos el término de búsqueda si es necesario
        nextPage = 1;
        container.innerHTML = '';
        loadPlaylists(); 
     });
}
        

function getCookie(name) {
    var node = document.getElementsByName('csrfmiddlewaretoken')[0];
    console.log(node);
    return node.value;
}

const playlistmgr = new PlaylistManager();