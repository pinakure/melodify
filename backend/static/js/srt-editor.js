const PIXELS_PER_SECOND = 60; // Constante de escala

function SrtEditor( lyrics ){
    this.lyrics             = "";
    this.serialized_blocks  = [];
    this.blocks             = this.deserializeBlocks( lyrics );
    this.container          = melodify.node('subtitleEditor');
    this.timelineTrack      = melodify.node('timelineTrack');
    this.timelineTrack.addEventListener('dblclick'   , this.newBlock     );
    melodify.node('srtFileInput'    ).addEventListener('change'     , this.getFile  );
    melodify.node('downloadBtn'     ).addEventListener('click'      , melodify.saveSrt  );
    if( lyrics.length > 0 ) melodify.node('srtFileInput'    ).style.display = 'none';
    this.processSRT();
    
    melodify.lyrics_editor  = this;
}

SrtEditor.prototype = {
    deserializeBlocks : function( lyrics ){
        this.lyrics = lyrics;
        this.serialized_blocks = lyrics.replace(/\r\n/g, '\n').split('\n\n');
        var payload = [];
        var self = this;
        this.serialized_blocks.forEach((block, index)=> {
            const lines = block.split('\n');
            if (lines.length >= 3) {
                const times     = lines[1].replace(' --> ', ' --&gt; ').split(' --&gt; ');
                const start     = self.timeToSeconds(times[0]);
                const end       = self.timeToSeconds(times[1]);
                const duration  = end - start;
                const text      = lines.slice(2).join(' ');
                payload[ index ] = {
                    start       : start,
                    end         : end,
                    duration    : end-start,
                    text        : text,
                };
            }
        });
        return payload;
    },
    deleteBlock: function(index){
        this.blocks.splice(index, 1);
        this.processSRT();
    },
    processSRT: function() {
        this.timelineTrack.innerHTML = `<div id="songShape"></div>`;
        this.container.innerHTML = ''; 
        let maxEndTime = 0;
        var self = this;
        this.blocks.forEach((block, index) => {
            const start     = block.start;
            const end       = block.end;
            const duration  = block.duration;
            const text      = block.text;
            
            if (end > maxEndTime) maxEndTime = end;

            // --- 1. Crear bloque visual ---
            const visualBlock = document.createElement('div');
            visualBlock.className = 'timeline-segment';
            visualBlock.id = `segment-${index}`;
            // Guardar metadatos para el arrastre
            visualBlock.setAttribute('data-original-start', start);
            visualBlock.setAttribute('data-duration', duration);
            visualBlock.setAttribute('data-x', 0); // Offset inicial del drag
            // Dentro de processSRT, al crear el visualBlock:
            visualBlock.style.cssText = `
                position: absolute; 
                left: ${start * PIXELS_PER_SECOND}px;
                width: ${duration * PIXELS_PER_SECOND}px; 
                height: 60px;
                top: 0px;
                background: var(--section-color);
                color: white;
                cursor: grab; /* Indica que se puede mover */
                border: 1px solid #2c3e50;
                padding: 5px;
                border-radius: 4px;
                font-size: 11px;
                overflow: hidden;
                touch-action: none; 
                box-sizing: border-box; /* Importante para cálculos de ancho exactos */
            `;
            visualBlock.innerText = text;
            visualBlock.onclick = () => editor.scrollToEditor(index);
            self.timelineTrack.appendChild(visualBlock);

            // --- 2. Crear bloque de edición ---
            const editDiv = document.createElement('div');
            editDiv.id = `edit-block-${index}`;
            editDiv.className = 'edit-item';
            editDiv.style.padding = '10px';
            
            // Usamos un template string con el evento oninput
            editDiv.innerHTML = `
                <div style="font-weight: bold; color: var(--tile-info-text);">#${index + 1}</div>
                    <input type="text" style="display:none" class="time-field" value="${start} --&gt; ${end}" style="width: 280px; margin-bottom: 5px;">
                    <div style="display: flex;justify-content: space-between;">
                        <input readonly="readonly"  type="text" class="start-field" value="${self.secondsToSrtTime(start)}" style="pointer-events: none; width: 280px; margin-bottom: 5px;"/>
                        <div> --&gt; </div>
                        <input readonly="readonly" type="text" class="end-field" value="${self.secondsToSrtTime(end)}" style="pointer-events: none; width: 280px; margin-bottom: 5px;"/>
                        <button class="input secondary" onclick="editor.deleteBlock(${index});"><i class="fas fa-trash"></i></button>
                    </div>
                <textarea class="text-field" style="width: 100%; height: 40px; display: block;">${text}</textarea>
            `;

            // EVENTO EN TIEMPO REAL: Actualizar bloque visual al escribir
            const textarea = editDiv.querySelector('.text-field');
            textarea.addEventListener('input', (e) => {
                visualBlock.innerText = e.target.value;
            });

            // OPCIONAL: Resaltar bloque azul cuando el textarea recibe foco
            textarea.addEventListener('focus', () => {
                editor.highlightTimelineBlock(index);
            });

            self.container.appendChild(editDiv);
        });    
        var pos_wrapper = document.createElement('div');
        pos_wrapper.id = 'songPositionWrapper';
        var pos = document.createElement('div');
        pos.id = 'songPosition';
        pos_wrapper.appendChild(pos);
        self.timelineTrack.appendChild(pos_wrapper);
        var time = melodify.player.howl ? melodify.player.howl.duration() : maxEndTime;
        self.timelineTrack.style.width = `${time * PIXELS_PER_SECOND}px`;
        // timelineTrack.style.width = `${(maxEndTime + 10) * PIXELS_PER_SECOND}px`;
        melodify.node('songPositionWrapper').style.width = self.timelineTrack.style.width;
        this.initDraggableAndResizable();
    },
    // Convierte "00:00:02,500" a 2.5 segundos
    timeToSeconds: function(timeStr) {
        const [hours, minutes, seconds] = timeStr.split(':');
        const [secs, ms] = seconds.split(',');
        return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(secs) + parseInt(ms) / 1000;
    },
    // Convierte segundos (ej: 125.5) a formato SRT (00:02:05,500)
    secondsToSrtTime: function(totalSeconds) {
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = Math.floor(totalSeconds % 60);
        const milliseconds = Math.floor((totalSeconds % 1) * 1000);
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')},${String(milliseconds).padStart(3, '0')}`;
    },
    // Inicializa el comportamiento de arrastre
    initDraggableAndResizable: function() {
        interact('.timeline-segment').resizable({
            // Permitir redimensionar desde los bordes izquierdo y derecho
            edges: { left: true, right: true, bottom: false, top: false },
            listeners: {
                move(event) {
                    const target = event.target;
                    const index = target.id.split('-')[1];
                    
                    // 1. Obtener posición X y ancho actual
                    let x = (parseFloat(target.getAttribute('data-x')) || 0);
                    let w = event.rect.width;

                    // 2. Actualizar posición si se estira desde la izquierda
                    x += event.deltaRect.left;

                    // 3. Aplicar cambios visuales
                    target.style.width = `${w}px`;
                    target.style.transform = `translateX(${x}px)`;
                    target.setAttribute('data-x', x);

                    // 4. Sincronizar con los campos de tiempo
                    editor.updateInputsFromTimeline(target, index);
                }
            },
            modifiers: [
                // No permitir que el bloque sea más pequeño que 0.1 segundos
                interact.modifiers.restrictSize({
                    min: { width: 0.1 * PIXELS_PER_SECOND, height: 60 }
                })
            ]
        }).draggable({
            // Mantener la lógica de arrastre que ya teníamos
            listeners: {
                move(event) {
                    const target = event.target;
                    const index = target.id.split('-')[1];
                    let x = (parseFloat(target.getAttribute('data-x')) || 0) + event.dx;

                    target.style.transform = `translateX(${x}px)`;
                    target.setAttribute('data-x', x);

                    editor.updateInputsFromTimeline(target, index);
                }
            }
        });
    },
    // Función unificada para calcular y actualizar los inputs
    updateInputsFromTimeline: function(target, index) {
        const xOffset = parseFloat(target.getAttribute('data-x')) || 0;
        const currentWidth = target.offsetWidth;
        const originalStart = parseFloat(target.getAttribute('data-original-start'));

        // Calcular nuevos tiempos en segundos
        const newStartSecs      = originalStart + (xOffset / PIXELS_PER_SECOND);
        const newDurationSecs   = currentWidth / PIXELS_PER_SECOND;
        const newEndSecs        = newStartSecs + newDurationSecs;

        // Actualizar el input de tiempo en el editor
        document.querySelector(`#edit-block-${index} .start-field`  ).value = `${editor.secondsToSrtTime(newStartSecs)}`;
        document.querySelector(`#edit-block-${index} .end-field`    ).value = `${editor.secondsToSrtTime(newEndSecs)}`;
    },
    // Resalta el bloque azul en la línea de tiempo
    highlightTimelineBlock: function(index) {
        document.querySelectorAll('.timeline-segment').forEach(el => {
            el.style.background = 'var(--section-color)';
            el.style.color = 'var(--text-color)';
            el.style.boxShadow = 'none';
        });
        
        const activeBlock = document.getElementById(`segment-${index}`);
        activeBlock.style.background = 'var(--accent-color)'; 
        activeBlock.style.boxShadow = '0 0 10px rgba(0,0,0,0.5)';
        
        // Hacer scroll en la línea de tiempo si el bloque está fuera de vista
        activeBlock.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    },
    scrollToEditor: function(index) {
        const target = document.getElementById(`edit-block-${index}`);
        document.querySelectorAll('.edit-item').forEach(el => el.style.backgroundColor = 'transparent');
        
        // target.style.backgroundColor = 'var(--secondary-color)';
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });
        target.querySelector('textarea').focus();
    },
    downloadFile: function(content, fileName) {
        const blob = new Blob([content], { type: 'text/srt' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        a.click();
        window.URL.revokeObjectURL(url);
    },
    getFile: function(e){
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(e) {
            editor.blocks = editor.deserializeBlocks(e.target.result);
            editor.processSRT();
            melodify.node('srtFileInput').style.display = 'none';
        };
        reader.readAsText(file);
    },
    newBlock: function(e){
        // Calcular la posición X relativa al track
        const rect = this.getBoundingClientRect();
        const x = parseInt(e.clientX - rect.left);
        
        // Crear nuevo block
        const new_block     = {
            start    : x / PIXELS_PER_SECOND,
            end      : (x / PIXELS_PER_SECOND) + 2,
            text     : "Nuevo Subtitulo",
            duration : 2,
        };

        console.log(new_block);
        var found = false;
        // Insertar en array de blocks
        editor.blocks.forEach((block, index)=> {
            const start     = block.start;
            const end       = block.end;

            if( !found && ( new_block.end < start ) || ( new_block.start > end ) ){
                //editor.blocks = [ editor.blocks.slice( 0, index), new_block , editor.blocks.slice(index) ];
                editor.blocks.splice( index, 0,  new_block);
                found=true;
            }
        });

        // Refrescar la interfaz
        editor.processSRT();
        melodify.toast(`Nuevo bloque añadido en el segundo ${ parseInt(new_block.start) }`);
    },
};

var editor = null;