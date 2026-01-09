/* static/js/MelodifyAdmin.js */
function MelodifyAdmin(){
    console.warn("Admin Plugin Loaded");
}

MelodifyAdmin.prototype = {

    request : function(section, payload, callback=(data)=>console.log(data)){
        melodify.request(`/management/${section}/`, payload, callback);
    },

    db : {
        export : function(){
            melodify.admin.request('admin', { action : 'db-export' }, 
                (data)=>{

                }
            );
        },
        import : function(){
            melodify.admin.request('admin', { action : 'db-import' });
        },
        drop : function(){
            melodify.admin.request('admin', { action : 'db-drop' });
        },
    },
    library : {
        forceScan : function(){
            melodify.admin.request('admin', { action : 'library-scan' });
        },
        generateLyrics : function(){
            melodify.admin.request('admin', { action : 'library-lyrics' });
        },
        scrapMetadata : function(){
            melodify.admin.request('admin', { action : 'library-scrape' });
        },
    },
    log : {

        update_rate : 1000,
        auto_update : true,
        timeout     : null,

        clear : function(){
            melodify.admin.request('log', { clear : true })
        },
        setAutoupdate : function(){
            if( melodify.admin.log.timeout ) {
                clearTimeout( melodify.admin.log.timeout ); 
                melodify.admin.log.timeout = null;
            }
            value = melodify.node('log-autoupdate').checked;
            melodify.admin.log.auto_update = value;
            if( value ) melodify.admin.log.update();
        },
        setRate : function(){
            node = melodify.node('log-rate');
            melodify.admin.log.update_rate = node.value*1000;
            if(( melodify.admin.log.update_rate < 1000) || ( isNaN(melodify.admin.log.update_rate))){
                melodify.admin.log.update_rate = 1000;
            }
        },
        update : function(){
            melodify.admin.request('log', {}, 
                (data)=>{ 
                    try{
                        node = melodify.node('log');
                        node.innerHTML = data.response;
                        node.scrollTop = node.scrollHeight;
                        if( melodify.admin.log.auto_update ) {
                            melodify.admin.log.timeout = setTimeout( melodify.admin.log.update, melodify.admin.log.update_rate);
                        }
                    } catch {
                        melodify.admin.log.timeout = null;
                    }
                } 
            );
        },    
    },
    init : function(){
        melodify.admin.log.timeout = setTimeout( melodify.admin.log.update, melodify.admin.log.UPDATE_FREQUENCY);
    },
};

const MELODIFY_ADMIN = true;