// Constante de escala (debe ser la misma que usaste antes)
const PIXELS_PER_SECOND = 60;

function timeToSeconds(timeStr) {
    // Convierte "00:00:02,500" a 2.5 segundos
    const [hours, minutes, seconds] = timeStr.split(':');
    const [secs, ms] = seconds.split(',');
    return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(secs) + parseInt(ms) / 1000;
}

// Convierte segundos (ej: 125.5) a formato SRT (00:02:05,500)
function secondsToSrtTime(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = Math.floor(totalSeconds % 60);
    const milliseconds = Math.floor((totalSeconds % 1) * 1000);

    return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')},${String(milliseconds).padStart(3, '0')}`;
}

// Inicializa el comportamiento de arrastre
function initDraggableAndResizable() {
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
                updateInputsFromTimeline(target, index);
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

                updateInputsFromTimeline(target, index);
            }
        }
    });
}

// Función unificada para calcular y actualizar los inputs
function updateInputsFromTimeline(target, index) {
    const xOffset = parseFloat(target.getAttribute('data-x')) || 0;
    const currentWidth = target.offsetWidth;
    const originalStart = parseFloat(target.getAttribute('data-original-start'));

    // Calcular nuevos tiempos en segundos
    const newStartSecs = originalStart + (xOffset / PIXELS_PER_SECOND);
    const newDurationSecs = currentWidth / PIXELS_PER_SECOND;
    const newEndSecs = newStartSecs + newDurationSecs;

    // Actualizar el input de tiempo en el editor
    const timeInput = document.querySelector(`#edit-block-${index} .time-field`);
    if (timeInput) {
        timeInput.value = `${secondsToSrtTime(newStartSecs)} --> ${secondsToSrtTime(newEndSecs)}`;
    }
}

function processSRT(data) {
    melodify.node('srtFileInput').style.display = 'none';
    melodify.lyrics_editor = true;
    const timelineTrack = document.getElementById('timelineTrack');
    const editorContainer = document.getElementById('subtitleEditor');
    
    timelineTrack.innerHTML = `<div id="songShape"></div>`;
    editorContainer.innerHTML = ''; 
    
    const blocks = data.replace(/\r\n/g, '\n').split('\n\n');
    let maxEndTime = 0;

    blocks.forEach((block, index) => {
            const lines = block.split('\n');
            if (lines.length >= 3) {
                const times = lines[1].split(' --&gt; ');
                const start = timeToSeconds(times[0]);
                const end = timeToSeconds(times[1]);
                const duration = end - start;
                const text = lines.slice(2).join(' ');

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
                visualBlock.onclick = () => scrollToEditor(index);
                timelineTrack.appendChild(visualBlock);

                // --- 2. Crear bloque de edición ---
                const editDiv = document.createElement('div');
                editDiv.id = `edit-block-${index}`;
                editDiv.className = 'edit-item';
                editDiv.style.padding = '10px';
                
                // Usamos un template string con el evento oninput
                editDiv.innerHTML = `
                    <div style="font-weight: bold; color: var(--tile-info-text);">#${index + 1}</div>
                    <input type="text" class="time-field" value="${lines[1]}" style="width: 280px; margin-bottom: 5px;">
                    <textarea class="text-field" style="width: 100%; height: 40px; display: block;">${text}</textarea>
                `;

                // EVENTO EN TIEMPO REAL: Actualizar bloque visual al escribir
                const textarea = editDiv.querySelector('.text-field');
                textarea.addEventListener('input', (e) => {
                    visualBlock.innerText = e.target.value;
                });

                // OPCIONAL: Resaltar bloque azul cuando el textarea recibe foco
                textarea.addEventListener('focus', () => {
                    highlightTimelineBlock(index);
                });

                editorContainer.appendChild(editDiv);
            }
    });
    

    timelineTrack.innerHTML += `
    <div id="songPositionWrapper">
        <div id="songPosition"></div>
    </div>`;
    var time = melodify.player.howl ? melodify.player.howl.duration() : maxEndTime;
    timelineTrack.style.width = `${time * PIXELS_PER_SECOND}px`;
    // timelineTrack.style.width = `${(maxEndTime + 10) * PIXELS_PER_SECOND}px`;
    melodify.node('songPositionWrapper').style.width = timelineTrack.style.width;
    initDraggableAndResizable();
}

// Resalta el bloque azul en la línea de tiempo
function highlightTimelineBlock(index) {
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
}

function scrollToEditor(index) {
    const target = document.getElementById(`edit-block-${index}`);
    document.querySelectorAll('.edit-item').forEach(el => el.style.backgroundColor = 'transparent');
    
    // target.style.backgroundColor = 'var(--secondary-color)';
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    target.querySelector('textarea').focus();
}
function downloadFile(content, fileName) {
    const blob = new Blob([content], { type: 'text/srt' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    window.URL.revokeObjectURL(url);
}
