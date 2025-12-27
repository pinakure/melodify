// static/js/Melodify.js

// Cache references to DOM elements.
var elms = ['track', 'timer', 'duration', 'repBtn', 'shufBtn', 'playBtn', 'pauseBtn', 'prevBtn', 'nextBtn', 'playlistBtn', 'volumeBtn', 'progress', 'bar', 'wave', 'loading', 'playlist', 'list', 'volume', 'barEmpty', 'barFull', 'sliderBtn'];
elms.forEach(function(elm) {
	window[elm] = document.getElementById(elm);
});

const INITIAL_STATE = {
    currentSongId   : null,
    currentTime     : 0,
    volume          : 1.0,
    playlist        : [],
    playlist_index  : 0,
    repeat_mode     : 1,
    shuffle         : false,
    history         : [],
    settings        : {
        background_blend_style  : 'soft-light',
        scheme                  : 'default',
    },
    current_page    : '',
    first_song      : null,
};

const REPEAT_MODES = {
    0 : 'NO-REPEAT',
    1 : 'REPEAT',
    2 : 'REPEAT-ONE',
};

function MelodifyPlayer() {
    this.playlist       = [];
    this.index          = 0;
    this.howl           = null;
    this.lyrics         = null;
    this.lyrics_index   = 1;
    this.lyrics_last    = 0;
    repBtn      .addEventListener   ('click'      , function()      { melodify.player.cycleRepeatMode();});
    shufBtn     .addEventListener   ('click'      , function()      { melodify.player.toggleShuffle();});
    playBtn     .addEventListener   ('click'      , function()      { melodify.player.play();});
    pauseBtn    .addEventListener   ('click'      , function()      { melodify.player.pause();});
    prevBtn     .addEventListener   ('click'      , function()      { melodify.player.skip('prev');});
    nextBtn     .addEventListener   ('click'      , function()      { melodify.player.skip('next');});
    waveform    .addEventListener   ('click'      , function(event) { melodify.player.seek(event.clientX / window.innerWidth);});
    volumeBtn   .addEventListener   ('click'      , function()      { melodify.player.toggleVolume();});
    volume      .addEventListener   ('click'      , function()      { melodify.player.toggleVolume();});
    barEmpty    .addEventListener   ('click'      , function(event) { var per = event.layerX / parseFloat(barEmpty.scrollWidth); melodify.player.volume(per);});
    sliderBtn   .addEventListener   ('mousedown'  , function()      { window.sliderDown = true;});
    sliderBtn   .addEventListener   ('touchstart' , function()      { window.sliderDown = true; });
    volume      .addEventListener   ('mouseup'    , function()      { window.sliderDown = false; });
    volume      .addEventListener   ('touchend'   , function()      { window.sliderDown = false; });
    volume      .addEventListener   ('mousemove', move);
    volume      .addEventListener   ('touchmove', move);
    window      .addEventListener   ('resize', resize);
}

MelodifyPlayer.prototype = {

    updateButtons: function(){
        repBtn .setAttribute('data-mode', REPEAT_MODES[ melodify.state.repeat_mode ]);
        shufBtn.setAttribute('data-mode', melodify.state.shuffle ? 'SHUFFLE' : 'NO-SHUFFLE');
        playBtn.setAttribute('data-enabled', 'true');
        if(( melodify.player.playlist.length > 0 && melodify.player.index           > 0) 
        || ( melodify.state.repeat_mode      > 0 && melodify.player.playlist.length > 1)
        || ( melodify.state.shuffle              && melodify.player.playlist.length > 1)
        ){
            prevBtn.setAttribute('data-enabled', 'true');
        } else {
            prevBtn.setAttribute('data-enabled', 'false');
        }
        if(( melodify.player.playlist.length > 0 && melodify.player.index           < (melodify.player.playlist.length-1)) 
        || ( melodify.state.repeat_mode      > 0 && melodify.player.playlist.length > 1                                  ) 
        || ( melodify.state.shuffle              && melodify.player.playlist.length > 1                                  )
        ){
            nextBtn.setAttribute('data-enabled', 'true');
        } else {
            nextBtn.setAttribute('data-enabled', 'false');
        }
    },

    cycleRepeatMode: function(){
        melodify.state.repeat_mode++;
        melodify.state.repeat_mode%=3;
        melodify.player.updateButtons();
        melodify.saveState();
    },
    
    toggleShuffle: function(){
        melodify.state.shuffle ^= 1;
        if(melodify.state.shuffle) melodify.state.repeat_mode = 1;
        melodify.player.updateButtons();
        melodify.saveState();
    },

    loadLyrics: function(lyrics){
        this.lyrics = {};
        if(lyrics.length > 0){
            lyrics = lyrics.split('\n\n');
            try{
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
                        start : (get_start_time()*1000)+parseInt(start.split(',')[1]),
                        end   : (get_end_time()  *1000)+parseInt(end.split(',')[1]),
                        text  : text, 
                    };
                }
            } catch {}
        }
        this.lyrics_index = 1;
        this.lyrics_last  = 0;
    },

    enqueue : function(song){
        this.playlist.push(song);
        this.index = this.playlist.length-1;
    },

    play: function(song) {
        if(song==undefined){
            this.howl.play();
            playBtn.style.display = 'none';
            return;
        }
        document.title = song.title;
        melodify.player.pause();
		var self = this;
        index = this.playlist.indexOf(song);
        var data = self.playlist[index];
		if(!data)return;
		this.howl = new Howl({
            src: [ data.file ],
            html5: false, 
            onplay: function() {
                duration.innerHTML = self.formatTime(Math.round(melodify.player.howl.duration()));
                
                requestAnimationFrame(self.step.bind(self));
                
                // Sync lyrics bar size with song duration
                node = melodify.node('timelineTrack');
                if(node) {
                    node.style.width = `${melodify.player.howl.duration() * PIXELS_PER_SECOND}px`;
                    melodify.node('songPositionWrapper').style.width = node.style.width;
                }
                pauseBtn.style.display = 'flex';
            },
            onload: function() {
                melodify.node('loading-audio').style.display = 'none';
                melodify.player.updateButtons();
            },
            onloaderror: function(id, error) {
                melodify.toast(`Error loading audio: ${error}`, 5, true);
                console.error(`Error loading audio: ${error}`);
                melodify.node('loading-audio').style.display = 'none';
            },
            onend: function() {
                self.skip('next');
            },
            onnext : function(){
                alert('hello');
            },
            onprev : function(){
                alert('hello');
            },
            onpause: function() {
            },
            onstop: function() {
            },
            onseek: function() {
                requestAnimationFrame(self.step.bind(self));
            }
        });
    
		this.howl.play();

		track.innerHTML = data.title;
		track.setAttribute('data-song-id', data.song_id);

		if (this.howl.state() === 'loaded') {
			playBtn.style.display = 'none';
			pauseBtn.style.display = 'flex';
		} else {
			melodify.node('loading-audio').style.display = 'flex';
			playBtn.style.display = 'none';
			pauseBtn.style.display = 'none';
		}
    
        this.loadLyrics( song.lyrics );

		self.index = index;
        melodify.player.updatePlaylist(this.playlist);
	},

    pause: function() {
		// Get the Howl we want to manipulate.
		if(!melodify.player.howl)return;
		// Puase the howl object.
		melodify.player.howl.pause();

		// Show the play button.
		playBtn.style.display = 'flex';
		pauseBtn.style.display = 'none';
	},

    /* updates entries drawn at si ar playlist */
    updatePlaylist : function(){
		list.innerHTML = "";
        var index = 1;
		this.playlist.forEach(function(song) {
			var div = document.createElement('div');
			div.className = 'list-song';
			div.innerHTML = `<li onclick="melodify.navigate('${ song.url_detalle }')" class="sidebar-entry ${melodify.player.index == melodify.player.playlist.indexOf(song) ?'active':''}">
                                <div class="sidebar-entry-picture" style="background-image:url('${ song.url_picture!='' && song.url_picture!=null && song.url_picture!='None' ? song.url_picture : '/static/images/song.png' }')"></div>
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
            if( melodify.state.shuffle ){

            } else {
                if( melodify.state.repeat_mode == 2){
                    index = this.index;
                    this.index = -1;
                } else {

                    index = this.index-1;
                    if( melodify.state.repeat_mode == 1){
                        if(index < 0) index = melodify.player.playlist.length-1;
                    } else {
                        index = this.index;
                        this.index = -1;
                    }
                }
            }
		} else {
            if( melodify.state.shuffle ){
                
            } else {
                if( melodify.state.repeat_mode == 2){
                    index = this.index;
                    this.index = -1;
                } else {
                    index = this.index+1;
                    if( melodify.state.repeat_mode == 1){
                        index %= melodify.player.playlist.length;
                    } else if( index == melodify.player.playlist.length - 1 ){
                        this.pause();
                        return;
                    }
                }
            }
		}
		this.skipTo(index);
        if(melodify.state.current_page.split('/')[1] == 'player'){
            melodify.navigate(`/player/?song=${ melodify.player.playlist[index].id }&`);
        }
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
        var percent = (((seek / this.howl.duration()) * 100) || 0);
        var pc = `${percent}%`;
		progress.style.width = pc;
        
        // If the howl is still playing, continue stepping.
		if (this.howl.playing()) {
			requestAnimationFrame(self.step.bind(self));

            if(melodify.lyrics_editor){
                
                var song_position = melodify.node('songPosition');
                if(!song_position) melodify.lyrics_editor = false;
                else {
                    song_position.style.width = pc;
                    wrapper = melodify.node('timelineContainer');
                    wrapper.scrollTo({ left: (wrapper.scrollWidth - wrapper.clientWidth) * (percent/100), behavior:'smooth'}); 
                    index = 0;
                    for (const [i, block] of editor.blocks.entries()) {
                        if (seek >= block.start && seek < block.end) {
                            editor.highlightTimelineBlock(index);
                            // auto-select node 
                            if( editor.auto_select) 
                                editor.scrollToEditor(index);
                            break;
                        }
                        index++;
                    }
                }
            } else if(melodify.player.lyrics){
                
                var lyric = melodify.player.lyrics[ melodify.player.lyrics_index ];
                if( lyric == undefined ) return;
                var next  = melodify.player.lyrics[ melodify.player.lyrics_index+1 ]==undefined ? '' : melodify.player.lyrics[ melodify.player.lyrics_index+1 ];
                var now   = parseInt(seek*1000);// parseInt(seek+0.5);
                if( (now >= lyric.start) && (now <= lyric.end)){
                    // melodify.node('debug').innerHTML=`${now} - ${lyric.start} - ${lyric.end}`;
                    if( melodify.player.lyrics_last != lyric.start){
                        try {
                                melodify.node('lyrics').innerHTML = `
                                <div class="lyric-wrapper" style="position: relative;height: 32px;">
                                    <p class="lyric">${ lyric.text }</p>
                                    <p class="lyric-animation" style="color: var(--accent-color); animation-duration:${ lyric.end - lyric.start }ms;">${ lyric.text }</p>
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

function Melodify(user_id=0){
    console.log(`new Melodify(${user_id})`);
    /* Restore initial melodify state */
    this.user_id            = user_id;    
    this.state              = INITIAL_STATE;
    this.next_page          = 1;
    this.search_timeout     = null;
    this.is_loading         = false;
    this.search_term        = '';
    this.player             = new MelodifyPlayer();
    this.lyrics_editor      = false;
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
            console.log("Navegación atrás bloqueada");
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
    },
    node : function(id){
        return document.getElementById(id);
    },
    saveState: function() {
        console.log(`melodify.saveState(${melodify.user_id})`);
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
        if( !only_enqueue ) melodify.player.play(melodify.first_song);
    },
    enqueueSong: function( buttonElement ){
        var song = this.getSongDetails( buttonElement );  
        song.next = melodify.player.playlist.length ? melodify.player.playlist[ 0 ].id : song.id;
        if(melodify.player.playlist.length)
            melodify.player.playlist[ melodify.player.playlist.length-1 ].next = song.id; 
        melodify.player.playlist.push(song);
        melodify.player.updatePlaylist();
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
            console.error('Navigate: Fetch error:', error);
            melodify.toast(`Navigate: Network/Server Error ${error}`);
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
            console.log("BEACON");
            if (data.status === 'success') {
                done_callback(data);
            } else if (data.status === 'login') {
                melodify.node('login-window-wrapper').style.display="flex";
            } else {
                melodify.toast('Error: ' + data.message, 5, true);
            }
        })
        .catch(error => {
            if( error == "TypeError: done_callback is not a function"){
                melodify.toast("You forgot to write the done callback.", 5, true)
            } else {
                console.error('Fetch error:', error);
                melodify.toast('Ocurrió un error de red o del servidor.', 5, true);
            }
        });
    },
    loadScheme : function(scheme){
        this.request(`/scheme/${ scheme }/`,{}, (data)=>{ 
            melodify.node('scheme').innerHTML = data.values;
        }, true);
        this.state.settings.scheme = scheme;
    },
    /* Callback functions */
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
    scanSongs : function(artist_list){
        melodify.toast("Scanning songs");
        for(artist in artist_list){
            this.request('/scan/artist/', { artist : artist_list[artist] }, ()=>{});    
        }   
    },
    showResults : function(data){
        container = melodify.node('results');
        container.innerHTML = `<div style="font-size: 14px; font-weight: bold; width: 100%; align-items: center; justify-content: right; display: flex;">Descargar Todo&nbsp;<button title="Descargar todo" class="input" onclick="melodify.request('/stealget/', { url : melodify.node('searchInput').value}, (data)=>{ melodify.scanSongs(data.songs); })"><i class="fas fa-download "></i></button></div>`;
        container.innerHTML += "<ul>";
        for( d in data.songs ){
            song = data.songs[d];
            container.innerHTML += `<li><p>${ song.name }</p><p>${ song.artist }</p><button title="Descargar" id="download-${d}" class="input accent" onclick="disable(${d}); melodify.request('/stealget/', { url : '${ song.url }' }, (data)=>{ melodify.scanSongs(data.songs); enable(${d}); })"><i class="fas fa-download "></i></button></li>`;
        }
        container.innerHTML += "</ul>";
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
    createPlaylist : function() {
        const playlistNameInput = melodify.node('new-list-name');
        const playlistName = playlistNameInput.value.trim();
        const container = melodify.node('tileContainer');
        if (!playlistName) {
            melodify.toast("Por favor, introduce un nombre para la lista.");
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
        this.request('/song/bookmark/', { song : song_id }, (data)=>{
            melodify.toast(data.message, 5, false, 'bookmark-status'); 
            melodify.node(  `bookmark-song-${ song_id }`).classList.toggle("hidden"),
            melodify.node(`unbookmark-song-${ song_id }`).classList.toggle("hidden")
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
            console.error('Error fetching albums:', error);
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
            melodify.toast(`Error fetching playlists: ${error}`, 5, true);
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

/* album list stuff */

function toggleNewListForm() {
    const form = melodify.node('new-list');
    // Muestra u oculta el formulario
    if (form.style.display === 'none' || form.style.display === '') {
        form.style.display = 'flex'; 
        melodify.node('new-list-name').focus();
    } else {
        form.style.display = 'none';
        melodify.node('new-list-name').value = ''; // Limpia el input al ocultar
    }
}
function triggerSearch( handler, callback ) {
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
}
