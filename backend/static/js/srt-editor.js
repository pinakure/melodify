// Función para convertir el texto SRT en campos editables

function timeToSeconds(timeStr) {
    // Convierte "00:00:02,500" a 2.5 segundos
    const [hours, minutes, seconds] = timeStr.split(':');
    const [secs, ms] = seconds.split(',');
    return parseInt(hours) * 3600 + parseInt(minutes) * 60 + parseInt(secs) + parseInt(ms) / 1000;
}

const PIXELS_PER_SECOND = 60; // 1 segundo = 60px para mayor precisión

function processSRT(data) {
    const timelineTrack = document.getElementById('timelineTrack');
    const editorContainer = document.getElementById('subtitleEditor');
    
    timelineTrack.innerHTML = ''; 
    editorContainer.innerHTML = ''; 
    
    const blocks = data.replace(/\r\n/g, '\n').split('\n\n');
    let maxEndTime = 0;

    blocks.forEach((block, index) => {
        const lines = block.split('\n');
        if (lines.length >= 3) {
            const times = lines[1].split(' --> ');
            const start = timeToSeconds(times[0]);
            const end = timeToSeconds(times[1]);
            const duration = end - start;
            const text = lines.slice(2).join(' ');

            if (end > maxEndTime) maxEndTime = end;

            // --- 1. Crear bloque visual en la Línea de Tiempo ---
            const visualBlock = document.createElement('div');
            visualBlock.className = 'timeline-segment';
            visualBlock.id = `segment-${index}`; // ID para referencia
            visualBlock.style.cssText = `
                position: absolute;
                left: ${start * PIXELS_PER_SECOND}px;
                width: ${duration * PIXELS_PER_SECOND}px;
                height: 60px;
                top: 20px;
                background: #4A90E2;
                color: white;
                cursor: pointer;
                border: 1px solid #2c3e50;
                padding: 5px;
                border-radius: 4px;
                font-size: 11px;
                overflow: hidden;
            `;
            visualBlock.innerText = text;

            // EVENTO CLICK: Sincronizar con el editor
            visualBlock.onclick = () => scrollToEditor(index);
            
            timelineTrack.appendChild(visualBlock);

            // --- 2. Crear bloque de edición ---
            const editDiv = document.createElement('div');
            editDiv.id = `edit-block-${index}`; // ID para encontrarlo
            editDiv.className = 'edit-item';
            editDiv.style.padding = '10px';
            editDiv.style.borderBottom = '1px solid #ccc';
            editDiv.innerHTML = `
                <div style="font-weight: bold; color: #666;">#${index + 1}</div>
                <input type="text" class="time-field" value="${lines[1]}" style="width: 280px; margin-bottom: 5px;">
                <textarea class="text-field" style="width: 100%; height: 40px; display: block;">${text}</textarea>
            `;
            editorContainer.appendChild(editDiv);
        }
    });

    timelineTrack.style.width = `${(maxEndTime + 10) * PIXELS_PER_SECOND}px`;
}

function scrollToEditor(index) {
    const target = document.getElementById(`edit-block-${index}`);
    
    // 1. Quitar resaltado previo de otros bloques
    document.querySelectorAll('.edit-item').forEach(el => {
        el.style.backgroundColor = 'transparent';
    });

    // 2. Resaltar el bloque seleccionado
    target.style.backgroundColor = '#fff9c4'; // Color crema/amarillo suave
    
    // 3. Hacer scroll suave hasta el elemento
    target.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // 4. Opcional: poner el foco en el textarea
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
