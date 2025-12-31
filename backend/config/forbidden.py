from main.utils import load_array

FORBIDDEN_FOLDERS                   = [
    '$RECYCLE.BIN'                  ,
    '.android_secure'               ,                       
    '.album'                        ,               
    '.artist'                       ,               
    '.binaural'                     ,               
    '.casette-eps'                  ,                   
    '.chiptune'                     ,               
    '.genre'                        ,               
    '.mini_vinyls'                  ,                   
    '.ost'                          ,           
    '.podcast'                      ,               
    '.rip'                          ,           
    '.scripts'                      ,               
    '.sessions'                     ,               
    '.source'                       ,               
    '.trash'                        ,               
    '.video'                        ,               
    '_Serato_'                      ,               
    '_Serato_Backup'                ,                       
    'Android'                       ,               
    'LOST_DIR'                      ,               
    'System Volume Information'     ,                               
    'sorted'                        ,               
    'unsorted'                      ,               
    '#.sorted'                      ,               
    '.unsorted'                     ,               
    '.backup'                       ,               
]

FORBIDDEN_TAGS                      = [
    '?'                             ,    
    '??'                            ,        
]

FORBIDDEN_PREFIXES                  = [
    'https://'                      ,            
    'http://'                       ,            
    'www.'                          ,        
    '.'                             ,    
    '?'                             ,    
    '??'                            ,        
    '__'                            ,        
    'by  '                          ,        
    'encoded '                      ,            
    'recopiled '                    ,                
    'ripped '                       ,        
    '['                             ,
    '('                             ,
    '{'                             ,
    '<'                             ,
]

FORBIDDEN_SUFFIXES                  = [
    '.com'                          ,
    '.COM'                          ,
] 

CODENAME_PREFIXES                   = [
    'LSDJ'                          ,              
    'MOD'                           ,              
    'FT'                            ,          
    'HF'                            ,          
    'MWS'                           ,              
    'CWEP'                          ,              
    'BMEP'                          ,              
] 
