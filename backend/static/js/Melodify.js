function Melodify(){
    /* Restore initial melodigy state */
    const initial_state = {
        currentSongId   : null,
        currentTime     : 0,
        volume          : 0.5,
        queue           : [],
        current_page    : '',
    };
    state = localStorage.getItem('melodify');
    if(!state) state = initial_state;
    else state = JSON.parse(state);
    
    this.next_page  = 1;
    this.state      = state;
    this.is_loading = false;
    this.search_term = '';
};

Melodify.prototype = {

    saveState : function() {
        localStorage.setItem('melodify', JSON.stringify(this.state));
    },

    reset_scroll : function(){
        try{ scrollbox.scrollTop = 0;} catch{}
    },

    navigate : function(url){
        fetch(`${url}?back=${ melodify.state.current_page.replace('/','') }`)
        .then(response => response.text())
        .then(data => {
            /* Remove event listeners */
            var search = document.getElementById('searchInput');
            if(search){
                search.removeEventListener('input', melodify.handlePlaylistFilter);
                search.removeEventListener('input', melodify.handleAlbumFilter);
            }
            const content = document.getElementsByClassName('main-content')[0];
            content.removeEventListener('scroll', melodify.handleAlbumScroll);
            content.removeEventListener('scroll', melodify.handlePlaylistScroll);
            content.scrollTop = 0;
            content.innerHTML = "";
            content.innerHTML = data;
            content.style="";
            melodify.next_page = 1;
            melodify.search_term = '-';
            var scripts = content.getElementsByTagName('script');
            for(s in scripts){
                eval(scripts[s].innerHTML);
            }
            melodify.state.current_page = url;
        })
        .catch(error => {
            console.error('Navigate: Fetch error:', error);
            alert(`Navigate: Network/Server Error ${error}`);
        });
    },
       
    getCookie : function(name) {
        var node = document.getElementsByName('csrfmiddlewaretoken')[0];
        console.log(node);
        return node.value;
    },

    request : function(url, json_data, done_callback) { 
        fetch(
            url, 
            { 
                method: 'POST',
                headers: {
                    'Content-Type'      : 'application/json',
                    'X-CSRFToken'       : melodify.getCookie('csrftoken'), 
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

    showResults : function(data){
        container = document.getElementById('results');
        container.innerHTML = `<div style="font-size: 14px; font-weight: bold; width: 100%; align-items: center; justify-content: right; display: flex;">Descargar Todo&nbsp;<button title="Descargar todo" class="input" onclick="melodify.request('/stealget/', { url : document.getElementById('searchInput').value}, (data)=>{ melodify.scanSongs(data.songs); })"><i class="fas fa-download "></i></button></div>`;
        container.innerHTML += "<ul>";
        for( d in data.songs ){
            song = data.songs[d];
            console.log(song);
            container.innerHTML += `<li><p>${ song.name }</p><p>${ song.artist }</p><button title="Descargar" id="download-${d}" class="input accent" onclick="disable(${d}); melodify.request('/stealget/', { url : '${ song.url }' }, (data)=>{ melodify.scanSongs(data.songs); enable(${d}); })"><i class="fas fa-download "></i></button></li>`;
        }
        container.innerHTML += "</ul>";
    },
  
    hidePlaylists : function(){ 
        const div = document.getElementById('playlists-window');
        div.style.display = 'none';
    },

    showPlaylists : function( parent, song_id ){
        const div = document.getElementById('playlists-window');
        div.style.display = 'inline-block';
        document.getElementById('playlists-window').setAttribute('data-song', song_id);
    },       

    addSongToPlaylist : function(playlist_id){
        song_id = document.getElementById('playlists-window').getAttribute('data-song');
        this.request('/playlists/populate/', { song : song_id, playlist : playlist_id }, ()=>{ 
            melodify.hidePlaylists();
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
        const container = document.getElementById('tileContainer');
        if (!playlistName) {
            alert("Por favor, introduce un nombre para la lista.");
            return;
        }

        this.request('/playlists/new/', { name : playlistName }, ()=>{ 
            toggleNewListForm(); 
            melodify.search_term = ''; // Reseteamos el término de búsqueda si es necesario
            melodify.next_page = 1;
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
   
    handleScroll : function( callback ) {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 200) {
            callback();
        }
    },
    
    handleAlbumScroll : function( ) {
        melodify.handleScroll( loadAlbums );
    },
    
    handlePlaylistScroll : function(){
        melodify.handleScroll( loadPlaylists );
    },

    handlePlaylistFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => triggerSearch(melodify.handlePlaylistScroll, loadPlaylists), 300);
    },

    handleAlbumFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => triggerSearch(melodify.handleAlbumScroll, loadAlbums), 300);
    },
};    

const melodify = new Melodify();

/* album list stuff */

function truncate(artist, n){
    return  (artist.split(', ').length == 2) ? artist.replace(', ', ' / ') : 
            (artist.split(', ').length  > n) ? 'Various Artists'           : 
            artist;
};

function loadAlbums() {
    let albumCount = 0;
    const loadingIndicator = document.getElementById('loading');
    const scrollbox     = document.getElementsByClassName('main-content')[0];

    if (melodify.isLoading) return;
    melodify.isLoading = true;
    loadingIndicator.style.display = 'block';

    var album_container = document.getElementById('tileContainer');
    var album_count     = document.getElementById('album-count');
    
    
    fetch(`/albums/?page=${melodify.next_page}${ melodify.search_term ? '&search=' : ''}${melodify.search_term}`, {
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
                    <a onclick="melodify.navigate('${album.url_detalle}')"> 
                        <div class="album-art">
                            <div picture="${ album.url_picture }" class="album-image ${ album.url_picture=='None' ? 'nopicture' : ''}" style="${ album.url_picture!="None" ? 'background-image: url(\''+album.url_picture+'\')' : ''}" alt="Album cover"></div>
                        </div>
                        <div class="tile-info">
                            <h3 class="album-name">${album.nombre}</h3>
                            <h6>${truncate(album.artist, 3)}</h6>
                        </div>
                    </a>
                `;
                album_container.appendChild(div);
            });
            melodify.next_page++;
            // Actualizamos el contador total si la respuesta lo incluye
            if (data.total_count !== undefined) {
                    albumCount = data.total_count;
                    album_count.textContent = albumCount;
            }
        } else {
            scrollbox.removeEventListener('scroll', melodify.handleAlbumScroll);
        }            
        melodify.isLoading = false;

        loadingIndicator.style.display = 'none';
    })
    .catch(error => {
        console.error('Error fetching albums:', error);
        melodify.isLoading = false;
        loadingIndicator.style.display = 'none';
    });
}

function loadPlaylists() {
    let playlistCount = 0;
    const playlist_container = document.getElementById('tileContainer');
    const countDisplay       = document.getElementById('playlist-count');
    const scrollbox          = document.getElementsByClassName('main-content')[0];

    if (melodify.is_loading) return;
    melodify.is_loading = true;
    const loadingIndicator  = document.getElementById('loading');

    loadingIndicator.style.display = 'block';

    fetch(`playlists/?page=${melodify.next_page}${ melodify.search_term ? '&search=' : ''}${melodify.search_term}` , {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.playlists.length > 0) {
            data.playlists.forEach(playlist => {
                const div = document.createElement('div');
                div.className = "tile-item playlist-item";
                div.setAttribute('data-playlist-artist', playlist.safeartist); 
                div.setAttribute('data-playlist-name', playlist.safename);
                
                div.innerHTML = `
                    <a onclick="melodify.navigate('${playlist.url_detalle}')"> 
                        <div class="album-art">
                            <div class="album-image" style="{% if playlist.url_picture %}background-image: url('${playlist.url_picture}'){% endif %}" alt="Playlist cover"></div>
                        </div>
                        <div class="tile-info">
                            <h3 class="playlist-name">${playlist.nombre}</h3>
                            <h6 class="playlist-artists">${truncate(playlist.artists, 3)}</h6>
                            <h6 class="playlist-genres">${truncate(playlist.genres, 3)}</h6>
                        </div>
                    </a>
                `;
                playlist_container.appendChild(div);
            });
            melodify.next_page++;
            // Actualizamos el contador total si la respuesta lo incluye
            if (data.total_count !== undefined) {
                    playlistCount = data.total_count;
                    countDisplay.textContent = playlistCount;
            }
        } else {
            scrollbox.removeEventListener('scroll', melodify.handlePlaylistScroll);
        }
        melodify.is_loading = false;
        loadingIndicator.style.display = 'none';
    })
    .catch(error => {
        console.error('Error fetching playlists:', error);
        melodify.is_loading = false;
        loadingIndicator.style.display = 'none';
    });
}

 function toggleNewListForm() {
    const form = document.getElementById('new-list');
    // Muestra u oculta el formulario
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'flex'; // o 'block', dependiendo de tus estilos 'new-list'
        document.getElementById('new-list-name').focus();
    } else {
        form.style.display = 'none';
        document.getElementById('new-list-name').value = ''; // Limpia el input al ocultar
    }
}

function triggerSearch( handler, callback ) {
    const searchInput   = document.getElementById('searchInput'); 
    const container     = document.getElementById('tileContainer');
    const scrollbox     = document.getElementsByClassName('main-content')[0];

    const newSearchTerm = searchInput.value.toLowerCase().trim();
   
    if (newSearchTerm !== melodify.search_term) {
        // Reiniciar el estado para una nueva búsqueda
        melodify.search_term = newSearchTerm;
        melodify.next_page = 1;
        albumCount = 0;
        container.innerHTML = ''; // Limpiar álbumes anteriores
        scrollbox.addEventListener('scroll', handler); // Asegurarse de que el scroll listener esté activo
        callback(); // Cargar la primera página de los resultados de la búsqueda
    }
}

function enable(node_id){
    node = document.getElementById(`download-${node_id}`);
    node.removeAttribute('readonly');
    node.removeAttribute('disabled');
}

function disable(node_id){
    node = document.getElementById(`download-${node_id}`)
    node.setAttribute('readonly', 'readonly');
    node.setAttribute('disabled', 'disabled');        
}
