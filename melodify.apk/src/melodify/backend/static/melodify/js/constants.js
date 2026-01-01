// static/js/constants.js

const INITIAL_STATE = {
    current_section : 0,
    volume          : 1.0,
    playlist        : [],
    playlist_index  : 0,
    enable_analyzer : true,
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

[
    'track', 
    'timer', 
    'duration', 
    'repBtn', 
    'shufBtn', 
    'playBtn', 
    'pauseBtn', 
    'prevBtn', 
    'nextBtn', 
    'playlistBtn', 
    'volumeBtn', 
    'progress', 
    'bar', 
    'wave', 
    'loading', 
    'playlist', 
    'list', 
    'volume', 
    'barEmpty', 
    'barFull', 
    'sliderBtn'
].forEach(function(elm) {
	window[elm] = document.getElementById(elm);
});
