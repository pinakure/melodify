// static/js/MelodifyPlayer.js

var analyzer_bars = [];
for(var i=0, index=0; i<1024; i+=32, index++){
    analyzer_bars[ index ] = document.getElementById(`analyzer-bar-${index}`);
}

function MelodifyPlayer() {
    this.playlist       = [];
    this.index          = 0;
    this.howl           = null;
    this.karaoke        = false;
    this.lyrics         = null;
    this.current_lyric  = "";
    this.current_lyric_index = 0;
    this.lyrics_interrupt = null;
    this.lyrics_index   = 1;
    this.lyrics_last    = 0;
    this.buffer         = null;
    this.analyzer       = null;
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
        // melodify.saveState();
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
                melodify.saveState();
                // Initialize analyzer
                melodify.player.analyzer = Howler.ctx.createAnalyser();
                Howler.masterGain.connect( melodify.player.analyzer );
                melodify.player.buffer = new Uint8Array( melodify.player.analyzer.frequencyBinCount );
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

        this.loadLyrics( melodify.player.karaoke ? song.karaoke : song.lyrics );

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
                index = parseInt(Math.random() * melodify.player.playlist.length);
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
                index = parseInt(Math.random() * melodify.player.playlist.length);
            } else {
                if( melodify.state.repeat_mode == 2){
                    index = this.index;
                    this.index = -1;
                } else {
                    index = this.index+1;
                    if( melodify.state.repeat_mode == 1){
                        index %= melodify.player.playlist.length;
                    } else if( index == melodify.player.playlist.length ){
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
        melodify.state.volume = val;
        melodify.saveState();
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

    updateAnalyzer : function(){
        if(!melodify.state.enable_analyzer) return;
        melodify.player.analyzer.getByteFrequencyData( melodify.player.buffer );
        analyzer_bars.forEach((bar, i) => {
            const value = melodify.player.buffer[i];
            // Usamos Math.floor para un mejor rendimiento que parseInt
            const heightPercentage = Math.floor((value / 255) * 100);
            bar.style.height = `${heightPercentage}%`;
        });
    },

    updateCurrentLyric : function(){
        // melodify.node('debug').innerHTML=`
        //     <ul>
        //     <li>${melodify.player.current_lyric}</li>
        //     <li>${melodify.player.current_lyric_rate}</li>
        //     <li>${melodify.player.current_lyric_rate}</li>
        //     <li>${melodify.player.current_lyric_index}/${melodify.player.current_lyric.length}</li>
        //     </ul>
        // `;
        node = document.getElementsByClassName('lyric-animation')[0];
        if(node){
            node.innerHTML=melodify.player.current_lyric.substring(0, melodify.player.current_lyric_index );
            if( melodify.player.current_lyric_index < melodify.player.current_lyric.length ){
                melodify.player.current_lyric_index++;
            } else {
                clearInterval(melodify.player.lyrics_interrupt);
            }
        }
    },

    updateLyrics : function(percent, pc, seek){
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
                        if( !melodify.player.karaoke ){
                            melodify.node('lyrics').innerHTML = `
                                <div class="lyric-wrapper">
                                    <p class="lyric">${ lyric.text }</p>
                                    <p class="lyric-animation"></p>
                                </div>
                                <p class="blend-50">${ next.text ?? ''}</p>
                            `;
                            melodify.player.current_lyric       = lyric.text;
                            melodify.player.current_lyric_index = 1;
                            melodify.player.current_lyric_rate  = ( lyric.end - lyric.start ) / lyric.text.length;
                            clearInterval(melodify.player.lyrics_interrupt);
                            melodify.player.lyrics_interrupt = setInterval(melodify.player.updateCurrentLyric, melodify.player.current_lyric_rate);
                            melodify.player.updateCurrentLyric();
                            melodify.player.lyrics_last = lyric.start;
                        } else {
                            melodify.node('lyrics').innerHTML = `
                                <div class="lyric-wrapper">
                                    <p class="lyric">${ lyric.text }</p>
                                </div>
                                <p class="blend-50">${ next.text ?? ''}</p>
                            `;
                        }
                    } catch{

                    }
                }
            }
            if( (now > lyric.end)){
                melodify.player.lyrics_index++;
            }
        }
    },

    step: function() {
		var self = this;

		// Determine our current seek position.
		var seek                = this.howl.seek() || 0;
		timer.innerHTML         = self.formatTime(Math.round(seek));
        var percent             = (((seek / this.howl.duration()) * 100) || 0);
        var pc                  = `${percent}%`;
		progress.style.width    = pc;

        // If the howl is still playing, continue stepping.
		if (this.howl.playing()) {
			requestAnimationFrame(self.step.bind(self));
            this.updateLyrics(percent, pc, seek);
            this.updateAnalyzer();
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