// static/js/Melodify.js
function Melodify(user_id=0){
    /* Restore initial melodify state */
    this.user_id            = user_id;    
    this.state              = INITIAL_STATE;
    this.next_page          = 1;
    this.search_timeout     = null;
    this.is_loading         = false;
    this.search_term        = '';
    this.player             = new MelodifyPlayer();
    this.lyrics_editor      = false;
    this.download_queue     = [];
};
Melodify.prototype = {
    toast: function(message, timeout=5, error=false, id=null){
        id = id ? id : Math.floor(Math.random() * 1000000);
        const fadeDuration = 500;
        const toastHTML = `
            <div class="toast ${ error ? 'error' : ''}" id="toast-${id}"">
                ${ error ? '<i class="fas fa-times" style="color: #fd0;"></i>&nbsp;' : '' }
                ${message}
            </div>
        `;
        const toaster = this.node('toaster');
        const node = melodify.node(`toast-${id}`);
        if(node) node.remove();
        toaster.insertAdjacentHTML('beforeend', toastHTML);
        const currentToast = melodify.node(`toast-${id}`);
        setTimeout(() => {
            if (currentToast) {
                currentToast.classList.add('toast-fade');
            }
        }, (timeout*1000) - fadeDuration);
        setTimeout(() => {
            if (currentToast) {
                currentToast.remove();
            }
        }, timeout*1000);
    },
    error: function(error){
        this.toast(`ERROR : ${error}`, 5, true, 'melodify-error');
        console.error(error);
    },
    toggleAnalyzer(){
        melodify.state.enable_analyzer=melodify.node('use-renderer').checked;
        melodify.node('analyzer').style.display = melodify.state.enable_analyzer ? 'flex' : 'none';
        melodify.saveState(); 
    },
    loadState : function(){
        state = localStorage.getItem(`melodify[${ this.user_id }]`);
        if(state) this.state = JSON.parse(state);
        this.loadScheme(this.state.settings.scheme);
        this.player.playlist = this.state.playlist;
    },
    lock: function(){
        melodify.is_loading = true;
        const node = melodify.node('loading-wrapper');
        node.style.display = 'flex';
    },    
    unlock: function(){
        const node = melodify.node('loading-wrapper');
        node.style.display = 'none';
        melodify.is_loading = false;
    },
    loading : function(type='spinner'){
        if( melodify.is_loading )return;
        melodify.lock();
        const content = melodify.node('loading-content');
        content.innerHTML = `<i class="fas fa-${type} spin" style="color:var(--accent-color);"></i>`;
    },
    initialize: function(){
        /*
            // Start fullscreen
            setTimeout(()=>document.documentElement.requestFullscreen().catch((err) => {
                melodify.error(`Cannot enable fullscreen: ${err.message}`);
            }), 3000);
        */
        this.loadState();
        this.node('menu').innerHTML = this.node('navbar-links').innerHTML; //copy entries from normal menu to hover menu
        /* Restore playlist */
        this.player.updatePlaylist(this.state.playlist);
        /* Restore playlist playback index */
        this.player.index = this.state.playlist_index;
        /* Begin playback */
        if(this.state.playlist.length){
            this.player.play(this.state.playlist[this.player.index]);
        }
        window.history.pushState(null, null, window.location.href);
        window.onpopstate = function() {
            // Cuando el usuario pulsa "Atrás", volvemos a empujar el estado actual
            window.history.pushState(null, null, window.location.href);
            if(melodify.state.history.length > 1){
                here = melodify.state.history.pop();
                url = melodify.state.history.pop();
                if(url && url !== null && url != null) {
                    // melodify.toast(`Navigating to ${url}`);
                    melodify.navigate(url, [], false);
                    melodify.state.history.push(url)
                }
            }
            return false;
        };
        resize();
        melodify.player.updateButtons();
        Howler.volume(melodify.state.volume);
        var barWidth = (melodify.state.volume * 90) / 100;
		barFull.style.width = (barWidth * 100) + '%';
		sliderBtn.style.left = (window.innerWidth * barWidth + window.innerWidth * 0.05 - 25) + 'px';
        melodify.node(`section-${ melodify.state.current_section }`).click();
    },
    node : function(id){
        return document.getElementById(id);
    },
    saveState: function() {
        this.state.playlist = this.player.playlist;
        this.state.playlist_index = this.player.index;
        localStorage.setItem(`melodify[${melodify.user_id}]`, JSON.stringify(this.state));
    },
    reset_scroll: function(){
        try{ scrollbox.scrollTop = 0;} catch{}
    },
    emptyQueue : function(){
        this.player.playlist = [];
        this.player.updatePlaylist();
        this.player.index = 0;
        this.saveState();
    },
    getSongDetails: function( buttonElement ){
        const artistName = buttonElement.getAttribute('data-artistname');
        const songName   = buttonElement.getAttribute('data-songname');
        const lyrics     = buttonElement.getAttribute('data-lyrics');
        const audioUrl   = buttonElement.getAttribute('data-src');
        const pictureUrl = buttonElement.getAttribute('data-picture');
        const songId     = buttonElement.getAttribute('data-id');
        const nextSong   = buttonElement.getAttribute('data-next-id');
        // @song instanciation
        return {
            title       : `${artistName} - ${songName}`,
            file        : audioUrl,
            url_picture : pictureUrl,
            url_detalle : `/song/${songId}`,
            id          : songId,
            song_id     : songId,
            lyrics      : lyrics,
            artist_name : artistName,
            song_name   : songName,
            next        : nextSong,
        };
    },
    playSong: function(buttonElement, only_enqueue=false) {
        const nextSong   = buttonElement.getAttribute('data-next-id');
        var song = this.getSongDetails( buttonElement );
        
        if( !only_enqueue) {
            melodify.first_song = song;
        }
        /* check if song is on playlist already */
        for(i in melodify.player.playlist){
            var entry = melodify.player.playlist[i];
            if(entry.id == song.id) {
                if( !only_enqueue ) melodify.player.play(melodify.player.playlist[i]);
                return;
            }
        }
        melodify.player.enqueue( song );
        if( nextSong != "" && (nextSong != melodify.first_song.id) ){
            melodify.playSong( melodify.node(`song-${ nextSong }`) , true );
        }
        if( !only_enqueue ) {
            melodify.player.play(melodify.first_song);
            melodify.saveState();
        }
    },
    enqueueSong: function( buttonElement ){
        var song = this.getSongDetails( buttonElement );  
        song.next = melodify.player.playlist.length ? melodify.player.playlist[ 0 ].id : song.id;
        if(melodify.player.playlist.length)
            melodify.player.playlist[ melodify.player.playlist.length-1 ].next = song.id; 
        melodify.player.playlist.push(song);
        melodify.player.updatePlaylist();
        melodify.saveState();
    },
    navigate: function(url, params=[], register_history=true){
        if( register_history ) this.state.history.push(url);
        target_url = url+'?'
        for(p in params){
            target_url += `&${ params[p]}`;
        }
        fetch(target_url)
        .then(response => response.text())
        .then(data => {
            /* Remove event listeners */
            var search = melodify.node('searchInput');
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
            melodify.saveState();
            content.focus();
            melodify.node('curtain').click();
        })
        .catch(error => {
            melodify.error(`Navigate: Network / Server error: ${error}`);
        });
    },
    getCookie: function(name) {
        var node = document.getElementsByName('csrfmiddlewaretoken')[0];
        return node.value;
    },
    request: function(url, json_data, done_callback, no_csrf=false) { 
        var headers = {
            'Content-Type'      : 'application/json',
        };
        if(!no_csrf) headers['X-CSRFToken'] = this.getCookie('csrftoken');
        if(!no_csrf) headers['X-Requested-With'] = 'XMLHttpRequest';
        fetch(
            url, 
            { 
                method: 'POST',
                headers: headers, 
                body: JSON.stringify(json_data)
            }
        )
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                done_callback(data);
            } else if (data.status === 'login') {
                melodify.node('login-window-wrapper').style.display="flex";
            } else {
                melodify.error(`Request Error: ${ data.message }`);
            }
        })
        .catch(error => {
            if( error == "TypeError: done_callback is not a function"){
                melodify.error("Request: missing success callback")
            } else {
                melodify.error(`Request: Network / Server error: ${error}`);
            }
        })
        .finally(()=>{
            melodify.unlock();
        });
    },
    loadScheme : function(scheme){
        this.request(`/scheme/${ scheme }/`,{}, (data)=>{ 
            melodify.node('scheme').innerHTML = ':root '+JSON.stringify(data.values).replaceAll('"', '').replaceAll(',', ';');
            this.state.settings.scheme = scheme;
            const styles = getComputedStyle(document.documentElement);
            const renderer = styles.getPropertyValue('--renderer');
            melodify.node('playbar').setAttribute('renderer', renderer);
        }, true);
    },
    filter: function(type) {
        const input  = melodify.node('search-Input');
        const filter = input.value.toLowerCase();
        const cards = document.querySelectorAll('.item');
        const noMessage  = melodify.node('no-message');
        
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
    search: function(value) {
        const input  = melodify.node('megasearch');
        const filter = input.value.toLowerCase();
        if(this.search_timeout) clearTimeout( this.search_timeout );
        this.search_timeout = setTimeout(()=>{
            melodify.request(`/search/`, {topic : value}, (data)=>{
                const urls = {
                    'albums'    : '/albums/',
                    'artists'   : '/artist/',
                    'songs'     : '/song/',
                    'genres'    : '/genre/',
                    'tags'      : '/tag/',
                    'lists'     : '/playlist/',
                    'users'     : '/user/',
                };
                const icons = {
                    'albums'    : 'compact-disc',
                    'artists'   : 'users',
                    'songs'     : 'music',
                    'genres'    : 'shapes',
                    'tags'      : 'tag',
                    'lists'     : 'list',
                    'users'     : 'user',
                };
                var html =`<div id="search-results">`;
                for( category in data.results){
                    var items = data.results[ category ];
                    if( items.length == 0 ) continue;
                    html += `<h2 class="section" style="text-transform: capitalize "><i class="fas fa-${ icons[ category ] }" style="color:var(--accent-color);"></i>&nbsp;${ category }&nbsp;<span class="small">(${ items.length })</span></h2>`;
                    html +=`<ul class="sidebar-items">`;
                    for( i in items ){
                        var item = items[i];
                        html += `<li class="sidebar-entry" onclick="melodify.navigate('${ urls[ category ] }${ item.id }')">
                            <div class="sidebar-entry-picture" style="background-image:url('${ item.picture!='' && item.picture!=null  ? category=='artists' ? 'media/'+item.picture : item.picture : '/static/images/'+ category.substring(0, category.length-1) +'.png' }')"></div>
                            <div class="sidebar-entry-content">
                                <p class="sidebar-entry-primary">${ item.name ?? item.title }</p>
                                <p class="sidebar-entry-secondary" style="text-transform: capitalize">${ item.artist__name ?? item.artists__name ?? category.substring(0, category.length-1) }</p>
                            </div>
                        </li>`;
                    }
                    html +=`</ul>`;
                }
                html +=`</div>`;
                melodify.node('main-content').innerHTML = html;
            }, true);
        }, 500);
    },
    downloadSong: function(index, song_url){
        disable(index); 
        node.innerHTML = '<i style="font-size: 17px" class="fas fa-spinner spin"></i>'
        melodify.request(
            '/stealget/', 
            { url : `${ song_url }` }, 
            (data)=>{ 
                melodify.scanSongs(data.songs); 
                melodify.node(`download-${index}`).innerHTML = '<i style="font-size: 17px" class="fas fa-check"></i>'
            }
        ); 
    },
    downloadQueue : function(){
        if( melodify.download_queue.length ){
            const song = melodify.download_queue.pop();
            const node = melodify.node(`download-${ song.id.split('-')[1] }`);
            node.innerHTML = '<i style="font-size: 17px" class="fas fa-spinner spin"></i>'
            melodify.toast(`Descargando ${song.artist} - ${song.title}`);
            melodify.request(
                '/stealget/', 
                { url : song.url }, 
                (data)=>{ 
                    node.innerHTML = '<i style="font-size: 17px" class="fas fa-check"></i>'
                    melodify.scanSongs(data.songs);
                    // melodify.node('song-${}') 
                    return melodify.downloadQueue();
                }
            );                
        } else {
            melodify.unlock();
            melodify.node('download-all').removeAttribute('disabled');
        }
    },
    downloadList: function(){
        melodify.node('download-all').setAttribute('disabled', 'disabled');
        document.querySelectorAll('#results ul li').forEach((e)=>{
            const id = e.getAttribute('id');
            melodify.download_queue[ melodify.download_queue.length ] = {
                id      : id,
                title   : e.getAttribute('title'),
                artist  : e.getAttribute('artist'),
                url     : e.getAttribute('url'),
            }
            disable(id.split('-')[1]);
            melodify.node(`download-${ id.split('-')[1] }`).innerHTML = '<i style="font-size: 17px" class="fas fa-clock"></i>'
        });
        melodify.downloadQueue();
    },
    scanSongs: function(artist_list){
        for(artist in artist_list){
            // melodify.toast(`Scanning ${artist_list[artist]}songs`, 5, 0, "scan-songs");
            melodify.request('/scan/artist/', { artist : artist_list[artist] }, ()=>{});    
        }   
    },
    showResults: function(data){
        container = melodify.node('results');
        container.innerHTML = '';
        if( data.songs.length > 1){
            container.innerHTML += `
                <div style="font-size: 14px; font-weight: bold; width: 100%; align-items: center; justify-content: right; display: flex;">
                    <button 
                        title="Descargar todo" 
                        class="input" 
                        id="download-all"
                        onclick="melodify.downloadList()">
                        <i class="fas fa-download "></i>&nbsp;Descargar Todo
                    </button>
                </div>`;
        }
        container.innerHTML += "<ul>";
        var id=0;
        ul = document.createElement('ul');
        for( d in data.songs ){
            song = data.songs[d];
            ul.innerHTML += `
                <li id="song-${id}" url="${song.url}" title="${song.name}" artist="${song.artist}">
                    <p>${ song.name }</p>
                    <p>${ song.artist }</p>
                    <button title="Descargar" id="download-${d}" class="input accent" onclick="melodify.downloadSong(${d}, '${song.url}');">
                        <i id="download-icon-${d}" class="fas fa-download "></i>
                    </button>
                </li>`;
            id++;
        }
        container.appendChild(ul);
    },
    hidePlaylists : function(){ 
        const div = melodify.node('playlists-window');
        div.style.display = 'none';
    },
    showPlaylists : function( parent, song_id ){
        const div = melodify.node('playlists-window');
        div.style.display = 'inline-block';
        melodify.node('playlists-window').setAttribute('data-song', song_id);
    },       
    addSongToPlaylist : function(playlist_id){
        song_id = melodify.node('playlists-window').getAttribute('data-song');
        this.request('/playlists/populate/', { song : song_id, playlist : playlist_id }, ()=>{ 
            melodify.hidePlaylists();
        });
    },
    remSongFromPlaylist : function(playlist_id, song_id){
        this.request('/playlists/songs/remove/', { song : song_id, playlist : playlist_id }, ()=>{ 
            location.reload(); 
        });
    },
    toggleNewListForm : function() {
        const form = melodify.node('new-list');
        // Muestra u oculta el formulario
        if (form.style.display === 'none' || form.style.display === '') {
            form.style.display = 'flex'; 
            melodify.node('new-list-name').focus();
        } else {
            form.style.display = 'none';
            melodify.node('new-list-name').value = ''; // Limpia el input al ocultar
        }
    },
    createPlaylist : function() {
        const playlistNameInput = melodify.node('new-list-name');
        const playlistName = playlistNameInput.value.trim();
        const container = melodify.node('tileContainer');
        if (!playlistName) {
            melodify.toast("Por favor, introduce un nombre para la lista.");
            return;
        }

        this.request('/playlists/new/', { name : playlistName }, ()=>{ 
            melodify.toggleNewListForm(); 
            melodify.search_term = ''; // Reseteamos el término de búsqueda si es necesario
            melodify.next_page = 1;
            container.innerHTML = '';
            melodify.loadPlaylists(); 
        });
    },
    bookmarkSong: function( song_id, enable ){
        this.request('/song/bookmark/', { song : song_id }, (data)=>{
            melodify.toast(data.message, 5, false, 'bookmark-status'); 
            melodify.node(  `bookmark-song-${ song_id }`).classList.toggle("hidden"),
            melodify.node(`unbookmark-song-${ song_id }`).classList.toggle("hidden")
        });
    },
    handleScroll: function( callback ) {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 200) {
            callback();
        }
    },
    handleAlbumScroll: function( ) {
        melodify.handleScroll( melodify.loadAlbums );
    },
    handlePlaylistScroll: function(){
        melodify.handleScroll( melodify.loadPlaylists );
    },
    triggerSearch: function( handler, callback ) {
        const searchInput   = melodify.node('searchInput'); 
        const container     = melodify.node('tileContainer');
        const scrollbox     = document.getElementsByClassName('main-content')[0];

        const newSearchTerm = searchInput.value.toLowerCase().trim();
    
        if (newSearchTerm !== melodify.search_term) {
            // Reiniciar el estado para una nueva búsqueda
            melodify.search_term = newSearchTerm;
            melodify.next_page = 1;
            albumCount = 0;
            container.innerHTML = '';
            scrollbox.addEventListener('scroll', handler);
            callback();
        }
    },
    handlePlaylistFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => melodify.triggerSearch(melodify.handlePlaylistScroll, melodify.loadPlaylists), 300);
    },
    handleAlbumFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => melodify.triggerSearch(melodify.handleAlbumScroll, melodify.loadAlbums), 300);
    },
    loadAlbums : function() {
        let albumCount = 0;
        const scrollbox     = document.getElementsByClassName('main-content')[0];

        if (melodify.is_loading) return;
        melodify.loading();
        
        var album_container = melodify.node('tileContainer');
        var album_count     = melodify.node('album-count');
        
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
            melodify.unlock();
        })
        .catch(error => {
            melodify.error(`Error fetching albums: ${error}`);
            melodify.unlock();
        });
    },
    loadPlaylists: function() {
        let playlistCount = 0;
        const scrollbox          = document.getElementsByClassName('main-content')[0];
        
        if (melodify.is_loading) return;
        melodify.loading();
        
        const playlist_container = melodify.node('tileContainer');
        const countDisplay       = melodify.node('playlist-count');

        fetch(`playlists/?page=${melodify.next_page}${ melodify.search_term ? '&search=' : ''}${melodify.search_term}&user_id=${melodify.user_id}` , {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            node = document.querySelector('#playlists-window .wrapper ul');
            node.innerHTML = '';
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
                        </a>`;
                    playlist_container.appendChild(div);
                    node.insertAdjacentHTML('beforeend', `
                        <li onclick="melodify.addSongToPlaylist('${ playlist.id }')">
                            <div class="playlist-entry-picture"></div>
                            <div>
                                ${ playlist.nombre }
                            </div>
                            <div>
                            </div>
                        </li>
                    `);
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
            melodify.unlock();

        })
        .catch(error => {
            melodify.error(`Error fetching playlists: ${error}`);
            melodify.unlock();
        });
    },
    saveSrt: function() {
        // 1. Seleccionamos todos los contenedores de edición (edit-item)
        const blocks = document.querySelectorAll('.edit-item');
        let srtResult = '';

        blocks.forEach((block, index) => {
            const id = index + 1;
            
            // 2. Obtenemos los valores de los inputs y textareas específicos
            // Usamos los nombres de clase que definimos en la creación dinámica
            const start = block.querySelector('.start-field').value.trim();
            const end   = block.querySelector('.end-field').value.trim();
            const text  = block.querySelector('.text-field').value.trim();

            // 3. Solo agregamos el bloque si tiene contenido para evitar bloques vacíos
            if (start && end && text) {
                // El formato SRT requiere: ID, Tiempo, Texto y una línea en blanco
                srtResult += `${id}\n${start} --> ${end}\n${text}\n\n`;
            }
        });

        // 4. Verificación de seguridad
        if (srtResult.length === 0) {
            melodify.toast("No hay contenido para exportar.");
            return;
        }

        // 5. Llamamos a la función de descarga que ya tienes
        melodify.request(
            '/lyrics/save/', 
            { 
                song    : melodify.player.playlist[ melodify.player.index ].id, 
                lyrics  : srtResult 
            }, (data)=>{
            melodify.toast('<i class="fas fa-save"></i>&nbsp;Guardado.')
            // editor.downloadFile(srtResult, "subtitulos_editados_2025.srt");
            }
        );
    },
};    

const melodify = new Melodify();