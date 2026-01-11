/* static/js/MelodifyDownloadQueue.js */

function MelodifyDownloadQueue( debug=false ){
    this.queue = [];
    this.downloading = null;
}

MelodifyDownloadQueue.prototype = {
    remove: function(id){
        const index = melodify.downloader.queue.indexOf(id);
        var new_queue = [];
        melodify.downloader.queue.forEach((item)=>{
            if( item.id == id) return;
            new_queue[new_queue.length] = item;
        });
        melodify.downloader.queue = new_queue;
        melodify.downloader.update();
    },
    enqueue: function( list ){
        melodify.echo('enqueue');
        list.forEach(( item )=>{
            melodify.downloader.queue.push(item);
        });
        if( !melodify.downloader.downloading )
            melodify.downloader.run();
        melodify.downloader.update();
    },    
    update: function(){
        const node = melodify.node('queue-contents');
        var html = melodify.downloader.downloading ? melodify.downloader.entry( melodify.downloader.downloading, true) : ''; 
        melodify.downloader.queue.forEach((item)=>{
            html += melodify.downloader.entry(item);
        })
        node.innerHTML = html;
    },    
    run: function(){
        melodify.echo('run');
        if( melodify.downloader.queue.length ){
            if(melodify.downloader.downloading) return;
            melodify.downloader.downloading = melodify.downloader.queue.pop();
            melodify.downloader.update();
            melodify.toast(`Descargando ${melodify.downloader.downloading.artist} - ${melodify.downloader.downloading.title}`);
            melodify.request(
                '/stealget/', 
                { url : melodify.downloader.downloading.url }, 
                (data)=>{ 
                    melodify.scanSongs(data.songs);
                    melodify.downloader.downloading = null; 
                    return melodify.downloader.run();
                }
            );                
        } else {
            try{
                melodify.unlock();
                melodify.downloader.downloading = null;
                melodify.node('download-all').removeAttribute('disabled');
            } catch { /* Will fail if not in DeepSearch page */ }
            melodify.downloader.update();
        }
    },
    entry: function(item, active=false){
        return `
            <div class="list-song${active?' active':''}" id="queue-${item.id}" style="display:flex;align-items:center;position:relative;">
                <i class="fas fa-${active?'spinner spin':'clock'}" id="download-icon-${item.id}" style="line-height: 32px; margin-right: 8px; margin-left: 8px;"></i>
                <div style="width: calc(100% - 16px);">
                    <div style="width: 100%; height: 16px;">${item.title}</div>
                    <div class="small blend-50">${item.artist}</div>
                </div>
                ${ active ? '':'<button type="button" class="" style="border: none; background: none; display: inline-block; width: 24px !important; height: 24px !important;overflow: hidden; position:absolute; right: 16px; top:0px;font-size: 16px; font-weight: 800;" title="Eliminar de laz cola" onclick="melodify.downloader.remove(\''+item.id+'\')"><i class="fas fa-times" style="color: var(--text-color)"></i></button>' }
            </div>
        `;
    },
    result_entry: function(order, index, song){
        return `
            <li id="song-${order}" url="${song.url}" title="${song.name}" artist="${song.artist}">
                <p>${ song.name }</p>
                <p>${ song.artist }</p>
                <button title="Descargar" id="download-${index}" class="input accent" onclick="melodify.downloadSong(${index}, '${song.url}');">
                    <i id="icon-${index}" class="fas fa-download "></i>
                </button>
            </li>
        `;
    },
    results: function(data){
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
                </div>
            `;
        }
        container.innerHTML += "<ul>";
        var order=0;
        ul = document.createElement('ul');
        for( index in data.songs ){
            var song = data.songs[index];
            ul.innerHTML += melodify.downloader.result_entry(order, index, song);
            order++;
        }
        container.appendChild(ul);
    },
};