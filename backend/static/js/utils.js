// static/js/utils.js

var move = function(event) {
	if (window.sliderDown) {
		var x = event.clientX || event.touches[0].clientX;
		var startX = window.innerWidth * 0.05;
		var layerX = x - startX;
		var per = Math.min(1, Math.max(0, layerX / parseFloat(barEmpty.scrollWidth)));
		melodify.player.volume(per);
	}
};

function truncate(artist, n){
    return  (artist.split(', ').length == 2) ? artist.replace(', ', ' / ') : 
            (artist.split(', ').length  > n) ? 'Various Artists'           : 
            artist;
};

function enable(node_id){
    node = melodify.node(`download-${node_id}`);
    node.removeAttribute('readonly');
    node.removeAttribute('disabled');
}

function disable(node_id){
    node = melodify.node(`download-${node_id}`)
    node.setAttribute('readonly', 'readonly');
    node.setAttribute('disabled', 'disabled');        
}

var resize = function() {
	// Update the position of the slider.
	var sound = melodify.player.playlist.length > 0 ? melodify.player.playlist[melodify.player.index].howl : null;
	if (sound) {
		var vol = sound.volume();
		var barWidth = (vol * 0.9);
		sliderBtn.style.left = (window.innerWidth * barWidth + window.innerWidth * 0.05 - 25) + 'px';
	}
};