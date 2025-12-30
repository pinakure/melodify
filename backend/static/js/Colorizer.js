function Colorizer(){};
    
Colorizer.prototype = {
    color       : '--bg-main',

    hex_value   : '#00000000',
    
    input       : {
        r : null,
        g : null,
        b : null,
        a : null,
    },
    
    value       : {
        r : null, 
        g : null, 
        b : null, 
        a : null, 
    },

    modified : false,

    elements : [
        'bg-main',
        'bg-nav',
        'bg-sidebar',
        'bg-sidebar-selection',
        'bg-sidebar-hover',
        'bg-content-blend',
        'bg-content',
        'text-color',
        'secondary-color',
        'link-color',
        'section-color',
        'confirm-color',
        'accent-color',
        'bg-player-title',
        'shadow-color',
        'tile-placeholder',
        'tile-info',
        'tile-info-text',
        'gradient-begin',
        'gradient-end',
    ],
    
    properties : {
        '--nav-height'            : '60px',
        '--sidebar-width'         : '432px',
        '--default-font'          : "'lunchtype-regular'",
        '--player-font'           : "'lunchtype-regular'",
        '--player-font-size'      : '24px',
        '--renderer'              : 'themed',
    },
    
    colors      : {},

    initializeSwatches : function(){
        colorizer.colors = {};
        melodify.node('swatches').innerHTML = '';
        
        for( i in colorizer.elements){
            const element = colorizer.elements[i];
            document.getElementById('swatches').innerHTML += `<div 
            title="${ element }" 
            id="${ element }" 
            class="swatch" 
            onclick="colorizer.pick('${element}')" 
            style="background-color: var(--${element})"
            ></div>`;
        }

        for( i in colorizer.elements){
            const element = colorizer.elements[i];
            colorizer.colors[ colorizer.cssvar(element) ] = getComputedStyle(document.getElementById( element )).getPropertyValue(colorizer.cssvar(element)).trim();
        }
    },
   
    initialize: function(){
        this.input = {
            r : melodify.node('r-range'),
            g : melodify.node('g-range'),
            b : melodify.node('b-range'),
            a : melodify.node('a-range'),
        };
        this.value = {
            r : melodify.node('r-val'), 
            g : melodify.node('g-val'), 
            b : melodify.node('b-val'), 
            a : melodify.node('a-val'), 
        };
        [ this.input.r, this.input.g, this.input.b, this.input.a ].forEach(input => { input.addEventListener('input', colorizer.update);});
        this.setValue('--bg-main');
        this.initializeSwatches();
        melodify.node('bg-main').click();
        this.update();
    },
    
    clear : function(){
        const styles = getComputedStyle(document.documentElement);
        colorizer.elements.forEach((color)=>{
            document.documentElement.style.removeProperty(colorizer.cssvar(color));
        });
    },

    cssvar : function(varname){
        return `--${varname.replaceAll('_', '-')}`;
    },
    
    pick: function(name){
        document.getElementsByClassName('swatch').forEach((swatch)=>swatch.className = 'swatch'); 
        melodify.node(name).className='swatch active';
        colorizer.setValue(colorizer.cssvar(name));
    },

    setScheme: function(scheme){
        colorizer.clear();
        melodify.loadScheme( scheme ); 
        melodify.saveState();
        melodify.node('bg-main').click();
        colorizer.modified = false;
    },

    saveScheme: function(){
        melodify.node('save-scheme' ).style.display='none';
        melodify.node('swatch-tweak').style.display='none';
        melodify.node('clone-scheme').style.display='block';
        payload = ':root {\n';
        for( color in colorizer.colors){
            payload += `\t${color} : ${colorizer.colors[color]};\n`;
        }
        for( property in colorizer.properties){
            payload += `\t${property} : ${colorizer.properties[property]};\n`;
        }
        payload += '}';
        console.log(payload);
    },
    
    customizeScheme: function(){
        melodify.node('save-scheme' ).style.display='block';
        melodify.node('swatch-tweak').style.display='block';
        melodify.node('clone-scheme').style.display='none';
    },  

    setValue: function(color){
        colorizer.color = color;
        const styles = getComputedStyle(document.documentElement);
        const value = styles.getPropertyValue(color).replaceAll('#', '');
        colorizer.value.r.textContent = parseInt(value.substring(0,2), 16);
        colorizer.value.g.textContent = parseInt(value.substring(2,4), 16);
        colorizer.value.b.textContent = parseInt(value.substring(4,6), 16);
        if(value.length>6)
            colorizer.value.a.textContent = parseInt(value.substring(6,8), 16)??255;
        else 
            colorizer.value.a.textContent = 255
        colorizer.input.r.value = colorizer.value.r.textContent;
        colorizer.input.g.value = colorizer.value.g.textContent;
        colorizer.input.b.value = colorizer.value.b.textContent;
        colorizer.input.a.value = colorizer.value.a.textContent;
        colorizer.modified = true;
    },

    update: function(){
        const r = colorizer.input.r.value;
        const g = colorizer.input.g.value;
        const b = colorizer.input.b.value;
        const a = colorizer.input.a.value;

        // Actualizar etiquetas de texto
        colorizer.value.r.textContent = r;
        colorizer.value.g.textContent = g;
        colorizer.value.b.textContent = b;
        colorizer.value.a.textContent = a;

        // Convertir a HEX para mostrarlo
        const hex = "#" + [r, g, b, a].map(x => {
            const h = parseInt(x).toString(16);
            return h.length === 1 ? '0' + h : h;
        }).join('');
        
        colorizer.hex_value = hex;
        colorizer.colors[colorizer.color]=hex;

        // APLICAR AL CSS: Actualiza la variable para que el fondo cambie
        document.documentElement.style.setProperty(colorizer.color, hex);
    },
};
const colorizer = new Colorizer();
    