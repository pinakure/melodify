// static/js/Melodify.js

// Cache references to DOM elements.
var elms = ['track', 'timer', 'duration', 'playBtn', 'pauseBtn', 'prevBtn', 'nextBtn', 'playlistBtn', 'volumeBtn', 'progress', 'bar', 'wave', 'loading', 'playlist', 'list', 'volume', 'barEmpty', 'barFull', 'sliderBtn'];
elms.forEach(function(elm) {
	window[elm] = document.getElementById(elm);
});

// var wave = new SiriWave({
//   container: waveform,
//   width: window.innerWidth,
//   height: 12,
//   cover: true,
//   color: 'f80',
//   speed: 0.03,
//   amplitude: 0.7,
//   frequency: 2
// });
// wave.start();

function MelodifyPlayer() {
    this.playlist       = [];
    this.index          = 0;
    this.howl           = null;
    this.lyrics         = null;
    this.lyrics_index   = 1;
    this.lyrics_last    = 0;
    playBtn.addEventListener    ('click'      , function()      { melodify.player.play();});
    pauseBtn.addEventListener   ('click'      , function()      { melodify.player.pause();});
    prevBtn.addEventListener    ('click'      , function()      { melodify.player.skip('prev');});
    nextBtn.addEventListener    ('click'      , function()      { melodify.player.skip('next');});
    waveform.addEventListener   ('click'      , function(event) { melodify.player.seek(event.clientX / window.innerWidth);});
    volumeBtn.addEventListener  ('click'      , function()      { melodify.player.toggleVolume();});
    volume.addEventListener     ('click'      , function()      { melodify.player.toggleVolume();});
    barEmpty.addEventListener   ('click'      , function(event) { var per = event.layerX / parseFloat(barEmpty.scrollWidth); melodify.player.volume(per);});
    sliderBtn.addEventListener  ('mousedown'  , function()      { window.sliderDown = true;});
    sliderBtn.addEventListener  ('touchstart' , function()      { window.sliderDown = true; });
    volume.addEventListener     ('mouseup'    , function()      { window.sliderDown = false; });
    volume.addEventListener     ('touchend'   , function()      { window.sliderDown = false; });
    volume.addEventListener     ('mousemove', move);
    volume.addEventListener     ('touchmove', move);
    window.addEventListener     ('resize', resize);
}

MelodifyPlayer.prototype = {

    loadLyrics : function(lyrics){
        this.lyrics = {};
        if(lyrics.length > 0){
            lyrics = lyrics.split('\n\n');
            for(l in lyrics){
                var lyric = lyrics[l].split('\n');
                var index = lyric[0];
                var time  = lyric[1].split(' --> ');
                var start = time[0];
                var end   = time[1];
                var text  = lyric[2];
                var get_start_time = (hms = start.split(',')[0])=>{ const [hours, minutes, seconds] = hms.split(':'); return parseInt(hours) * 60 * 60 + parseInt(minutes) * 60 + parseInt(seconds); }; 
                var get_end_time   = (hms = end.split(',')[0]  )=>{ const [hours, minutes, seconds] = hms.split(':'); return parseInt(hours) * 60 * 60 + parseInt(minutes) * 60 + parseInt(seconds); }; 
                this.lyrics[ index ] = {
                    start : get_start_time(),
                    end   : get_end_time(),
                    text  : text, 
                };
            }
        }
        this.lyrics_index = 1;
        this.lyrics_last  = 0;
    },
    enqueue : function(song){
        this.playlist.push(song);
        this.index = this.playlist.length-1;
        // console.table(this.playlist);
    },
    play: function(song) {
        if(song==undefined){
            this.howl.play();
            playBtn.style.display = 'none';
            return;
        }
        document.title = song.title;
        // this.enqueue(song);
        melodify.player.pause();
		var self = this;
        index = this.playlist.indexOf(song);
        var data = self.playlist[index];
		if(!data)return;
		this.howl = new Howl({
            src: [ data.file ],
            html5: false, // Force to HTML5 so that the audio can stream in (best for large files).
            onplay: function() {
                // Display the duration.
                duration.innerHTML = self.formatTime(Math.round(melodify.player.howl.duration()));

                // Start updating the progress of the track.
                requestAnimationFrame(self.step.bind(self));

                // Start the wave animation if we have already loaded
                // wave.container.style.display = 'block';
                bar.style.display = 'none';
                pauseBtn.style.display = 'block';
            },
            onload: function() {
                // Start the wave animation.
                // wave.container.style.display = 'block';
                bar.style.display = 'none';
                loading.style.display = 'none';
            },
            onloaderror: function(id, error) {
                console.log(`Error loading audio: ${error}`);
                bar.style.display = 'none';
                loading.style.display = 'none';
            },
            onend: function() {
                // Stop the wave animation.
                // wave.container.style.display = 'none';
                bar.style.display = 'block';
                self.skip('next');
            },
            onpause: function() {
                // Stop the wave animation.
                // wave.container.style.display = 'none';
                bar.style.display = 'block';
            },
            onstop: function() {
                // Stop the wave animation.
                // wave.container.style.display = 'none';
                bar.style.display = 'block';
            },
            onseek: function() {
                // Start updating the progress of the track.
                requestAnimationFrame(self.step.bind(self));
            }
        });
    
		// Begin playing the howl object.
		this.howl.play();

		// Update the track display.
		track.innerHTML = data.title;
		track.setAttribute('data-song-id', data.song_id);

		// Show the pause button.
		if (this.howl.state() === 'loaded') {
			playBtn.style.display = 'none';
			pauseBtn.style.display = 'block';
		} else {
			loading.style.display = 'block';
			playBtn.style.display = 'none';
			pauseBtn.style.display = 'none';
		}
    
        this.loadLyrics( song.lyrics );

		// Keep track of the index we are currently playing.
		self.index = index;
        melodify.player.updatePlaylist(this.playlist);
	},
    pause: function() {
		// Get the Howl we want to manipulate.
		if(!melodify.player.howl)return;
		// Puase the howl object.
		melodify.player.howl.pause();

		// Show the play button.
		playBtn.style.display = 'block';
		pauseBtn.style.display = 'none';
	},
    /* updates entries drawn at sidebar playlist */
    updatePlaylist : function(){
		list.innerHTML = "";
        var index = 1;
		this.playlist.forEach(function(song) {
			var div = document.createElement('div');
			div.className = 'list-song';
			div.innerHTML = `<li onclick="melodify.navigate('${ song.url_detalle }')" class="sidebar-entry ${melodify.player.index == melodify.player.playlist.indexOf(song) ?'active':''}">
                                <div class="sidebar-entry-picture" style="background-image:url('${ song.url_picture }')"></div>
                                <div class="sidebar-entry-content">
                                    <p class="sidebar-entry-primary">${ index } - ${ song.song_name }</p>
                                    <p class="sidebar-entry-secondary">${ song.artist_name }</p>
                                </div>
                            </li>`;
            div.onclick = function() {
				melodify.player.skipTo(melodify.player.playlist.indexOf(song));
			};
			list.appendChild(div);
            index++;
		});
	},
    skip: function(direction) {
		// Get the next track based on the direction of the track.
		var index = 0;
		if (direction === 'prev') {
			index = this.index-1;
		} else {
            index = this.index+1;
		}
        index %= this.playlist.length;
		this.skipTo(index);
	},
    skipTo: function(index) {
		var self = this;

        if( this.index == index ){
            return;
        }

		// Stop the current track.
		if (self.howl) {
			self.howl.stop();
		}

		// Reset progress.
		progress.style.width = '0%';

		// Play the new track.
		self.play(self.playlist[index]);
	},
    volume: function(val) {
		var self = this;

		// Update the global volume (affecting all Howls).
		Howler.volume(val);

		// Update the display on the slider.
		var barWidth = (val * 90) / 100;
		barFull.style.width = (barWidth * 100) + '%';
		sliderBtn.style.left = (window.innerWidth * barWidth + window.innerWidth * 0.05 - 25) + 'px';
	},
    seek: function(per) {
		var self = this;
		// Convert the percent into a seek position.
		if (this.howl.playing()) {
			this.howl.seek(this.howl.duration() * per);
		}
        this.lyrics_index=1;
        this.lyrics_last =0;
	},
    step: function() {
		var self = this;

		// Determine our current seek position.
		var seek = this.howl.seek() || 0;
		timer.innerHTML = self.formatTime(Math.round(seek));
		progress.style.width = (((seek / this.howl.duration()) * 100) || 0) + '%';

		// If the howl is still playing, continue stepping.
		if (this.howl.playing()) {
			requestAnimationFrame(self.step.bind(self));

            if(melodify.player.lyrics){
                var lyric = melodify.player.lyrics[ melodify.player.lyrics_index ];
                if( lyric == undefined ) return;
                var next  = melodify.player.lyrics[ melodify.player.lyrics_index+1 ]==undefined ? '' : melodify.player.lyrics[ melodify.player.lyrics_index+1 ];
                var now   = parseInt(seek+0.5);
                if( (now >= lyric.start) && (now <= lyric.end)){
                    // document.getElementById('debug').innerHTML=`${now} - ${lyric.start} - ${lyric.end}`;
                    if( melodify.player.lyrics_last != lyric.start){
                        try {
                                document.getElementById('lyrics').innerHTML = `
                                <div class="lyric-wrapper" style="position: relative;height: 32px;">
                                    <p class="lyric">${ lyric.text }</p>
                                    <p class="lyric-animation" style="color: var(--accent-color); animation-duration:${ lyric.end - lyric.start }s;">${ lyric.text }</p>
                                </div>
                                <p class="blend-50">${ next.text ?? ''}</p>
                            `;
                            melodify.player.lyrics_last = lyric.start;
                        } catch{

                        }
                    }
                }
                if( (now > lyric.end)){
                    melodify.player.lyrics_index++;
                }
            }

		}
	},
    toggleVolume: function() {
		var self = this;
		var display = (volume.style.display === 'block') ? 'none' : 'block';

		setTimeout(function() {
			volume.style.display = display;
		}, (display === 'block') ? 0 : 500);
		volume.className = (display === 'block') ? 'fadein' : 'fadeout';
	},
    formatTime: function(secs) {
		var minutes = Math.floor(secs / 60) || 0;
		var seconds = (secs - minutes * 60) || 0;

		return minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
	}
};

function Melodify(){
    /* Restore initial melodify state */
    const initial_state = {
        currentSongId   : null,
        currentTime     : 0,
        volume          : 0.5,
        queue           : [],
        history         : [],
        current_page    : '',
        first_song      : null,
        skin            : 'default',
    };
    state = localStorage.getItem('melodify');
    if(!state) state = initial_state;
    else state = JSON.parse(state);
    
    this.next_page  = 1;
    this.state      = state;
    this.is_loading = false;
    this.search_term = '';
    this.player = new MelodifyPlayer();
};
Melodify.prototype = {
    saveState : function() {
        localStorage.setItem('melodify', JSON.stringify(this.state));
    },
    reset_scroll : function(){
        try{ scrollbox.scrollTop = 0;} catch{}
    },
    getSongDetails : function( buttonElement ){
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
    playSong : function(buttonElement, only_enqueue=false) {
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
            melodify.playSong( document.getElementById(`song-${ nextSong }`) , true );
        }
        if( !only_enqueue ) melodify.player.play(melodify.first_song);
    },
    enqueueSong : function( buttonElement ){
        var song = this.getSongDetails( buttonElement );  
        song.next = melodify.player.playlist[ 0 ].id;
        melodify.player.playlist[ melodify.player.playlist.length-1 ].next = song.id; 
        melodify.player.playlist.push(song);
        melodify.player.updatePlaylist();
    },
    navigate : function(url, params=[], register_history=true){
        if( register_history ) this.state.history.push(url);
        target_url = url+'?'
        for(p in params){
            target_url += `&${ params[p]}`;
        }
        fetch(target_url)
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
            melodify.saveState();
            content.focus();
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
    loadScheme : function(scheme){
        this.request(`/scheme/${ scheme }/`,{}, (data)=>{ 
            document.getElementById('scheme').innerHTML = data.values;
        });
    },
    /* Callback functions */
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
            melodify.loadPlaylists(); 
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
        melodify.handleScroll( melodify.loadAlbums );
    },
    handlePlaylistScroll : function(){
        melodify.handleScroll( melodify.loadPlaylists );
    },
    handlePlaylistFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => triggerSearch(melodify.handlePlaylistScroll, melodify.loadPlaylists), 300);
    },
    handleAlbumFilter : function(){
        clearTimeout(melodify.searchTimeout);
        melodify.searchTimeout = setTimeout(() => triggerSearch(melodify.handleAlbumScroll, melodify.loadAlbums), 300);
    },
    loadAlbums : function() {
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
    },
    loadPlaylists : function() {
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
    },
};    

const melodify = new Melodify();
resize();
/* album list stuff */

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
        container.innerHTML = '';
        scrollbox.addEventListener('scroll', handler);
        callback();
    }
}
