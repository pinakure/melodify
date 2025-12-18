function Melodify(){
    const initial_state = {
        currentSongId   : null,
        currentTime     : 0,
        volume          : 0.5,
        queue           : []
    };
    state = localStorage.getItem('player_activity');
    if(!state) state = initial_state;
    else state = JSON.parse(state);
    this.state = state;
};

function hidePlaylists( ){ 
    const div = document.getElementById('playlists-window');
    div.style.display = 'none';
}

function showPlaylists( parent, song_id ){
    const div = document.getElementById('playlists-window');
    div.style.display = 'inline-block';
    document.getElementById('playlists-window').setAttribute('data-song', song_id);
}

    
function getCookie(name) {
    var node = document.getElementsByName('csrfmiddlewaretoken')[0];
    console.log(node);
    return node.value;
}




Melodify.prototype = {

    saveState : function() {
        localStorage.setItem('player_activity', JSON.stringify(this.state));
    },

    navigate : function(url){
        fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementsByClassName('main-content')[0].innerHTML = data;
        })
        .catch(error => {
            console.error('Navigate: Fetch error:', error);
            alert(`Navigate: Network/Server Error ${error}`);
        });
    },

    request : function(url, json_data, done_callback) { 
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
            if( error == "TypeError: done_callback is not a function"){
                alert("You forgot to write the done callback.")
            } else {
                console.error('Fetch error:', error);
                alert('Ocurrió un error de red o del servidor.');
            }
        });
    },
    
    /* DEPRECATED */
    enqueueSong : function( artist, title, filename, node_id, song_id ){
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
    },

    filter : function(type) {
        const input  = document.getElementById('search-Input');
        const filter = input.value.toLowerCase();
        const cards = document.querySelectorAll('.item');
        const noMessage  = document.getElementById('no-message');
        
        let found = false;

        cards.forEach(card => {
            const name = card.getAttribute('data-name');
            
            if (name.includes(filter)) {
                card.style.display = ""; 
                found = true;
            } else {
                card.style.display = "none"; 
            }
        });
        if (noMessage) {
            noMessage.style.display = found ? "none" : "";
        }
    },

    scanSongs : function(artist_list){
        console.log("Scanning songs");
        console.log(artist_list);
        for(artist in artist_list){
            this.request('/scan/artist/', { artist : artist_list[artist] }, ()=>{});    
        }   
    },

    addSongToPlaylist : function(playlist_id){
        song_id = document.getElementById('playlists-window').getAttribute('data-song');
        this.request('/playlists/populate/', { song : song_id, playlist : playlist_id }, ()=>{ 
            hidePlaylists();
            location.reload(); 
        });
    },

    remSongFromPlaylist : function(playlist_id, song_id){
        this.request('/playlists/songs/remove/', { song : song_id, playlist : playlist_id }, ()=>{ 
            location.reload(); 
        });
    },

    createPlaylist : function() {
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
    },

    bookmarkSong : function( song_id, enable ){
        this.request('/song/bookmark/', { song : song_id }, ()=>{ 
            document.getElementById(  `bookmark-song-${ song_id }`).classList.toggle("hidden"),
            document.getElementById(`unbookmark-song-${ song_id }`).classList.toggle("hidden")
        });
    },

};    

const melodify = new Melodify();

/* album list stuff */
let nextPage = 1;
let isLoading = false;
let albumCount = 0;
let currentSearchTerm = '-';

function truncate(artist, n){
    return  (artist.split(', ').length == 2) ? artist.replace(', ', ' / ') : 
            (artist.split(', ').length  > n) ? 'Various Artists'           : 
            artist;
};

function loadAlbums() {
    if (isLoading) return;
    isLoading = true;
    loadingIndicator.style.display = 'block';

    const url = new URL(`/albums/`, window.location.origin);
    url.searchParams.set('page', nextPage);
    if (currentSearchTerm) {
        url.searchParams.set('search', currentSearchTerm);
    }

    fetch(url.toString(), {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.albums.length > 0) {
            data.albums.forEach(album => {
                const div = document.createElement('div');
                div.className = "tile-item album-item";
                div.setAttribute('data-album-artist', album.safeartist); 
                div.setAttribute('data-album-name', album.safename);
                
                div.innerHTML = `
                    <a href="${album.url_detalle}"> 
                        <div class="album-art">
                            <div class="album-image" style="background-image: url('${album.url_picture ? album.url_picture : ''}')" alt="Album cover"></div>
                        </div>
                        <div class="tile-info">
                            <h3 class="album-name">${album.nombre}</h3>
                            <h6>${truncate(album.artist, 3)}</h6>
                        </div>
                    </a>
                `;
                container.appendChild(div);
            });
            nextPage++;
            isLoading = false;
            // Actualizamos el contador total si la respuesta lo incluye
            if (data.total_count !== undefined) {
                    albumCount = data.total_count;
                    countDisplay.textContent = albumCount;
            }
        } else {
            scrollbox.removeEventListener('scroll', handleScroll);
        }
        loadingIndicator.style.display = 'none';
    })
    .catch(error => {
        console.error('Error fetching albums:', error);
        isLoading = false;
        loadingIndicator.style.display = 'none';
    });
}

function handleScroll() {
    console.log("HANDLING SCROLL");
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    if (scrollTop + clientHeight >= scrollHeight - 200) {
        loadAlbums();
    }
}

function triggerSearch() {
    const searchInput = document.getElementById('searchInput'); 
    const newSearchTerm = searchInput.value.toLowerCase().trim();
    
    if (newSearchTerm !== currentSearchTerm) {
        // Reiniciar el estado para una nueva búsqueda
        currentSearchTerm = newSearchTerm;
        nextPage = 1;
        albumCount = 0;
        container.innerHTML = ''; // Limpiar álbumes anteriores
        scrollbox.addEventListener('scroll', handleScroll); // Asegurarse de que el scroll listener esté activo
        loadAlbums(); // Cargar la primera página de los resultados de la búsqueda
    }
}