from django.core.management.base import BaseCommand
from main.models import Scheme
from .scan import saferead
import platform
import shutil
import os 

APP_NAME        = f'melodify'
PATH            = f'/src/{APP_NAME}'
BASE_PATH       = f'{PATH}/backend'
USER            = f'{APP_NAME}'
GROUP           = f'www-data'
VENV            = f'{PATH}/venv'
PYTHON          = f'{VENV}/bin/python'
APP_CMD         = f'{PYTHON} manage.py'
ROOT            = f'admin'
ROOT_PASSWORD   = f'Melodify777!'
SERVER_SECURE   = False

APT_PACKAGES    = [
    'ffmpeg'                        ,
    'nginx'                         ,
    'openjdk-17-jdk'                ,
    'openjdk-17-jre'                ,
    'cmake'                         ,
    'pkg-config'                    ,
    'automake'                      ,
    'autoconf'                      ,
    'libtool'                       ,
    'libffi-dev'                    ,
    'libssl-dev'                    ,
    'python3-dev'                   ,
    'libltdl-dev'                   ,
    'libsqlite3-dev'                ,    
]

PIP_PACKAGES    = [
    'spotdl'                        ,
    'stable-ts'                     ,
    '"cython<3.0.0"'                ,
    'python-for-android'            ,
    'django'                        ,
    'kivy'                          ,
    'kivymd'                        ,
    'asgiref'                       ,
    'sqlparse'                      ,
    'Pillow'                        ,
    'mutagen'                       ,
    'requests'                      ,
    'django-fontawesome_5'          ,
    'setuptools'                    ,
    'nostr-sdk'                     ,
    'gunicorn'                      ,
    'buildozer'                     ,
]

DIRECTORIES     = [
    f'/static/${APP_NAME}'          ,
    f'/library'                     ,
    f'/library/.artists'            ,
    f'{BASE_PATH}/media/artists'    ,
    f'{BASE_PATH}/media/albums'     ,
    f'{BASE_PATH}/media/songs'      ,
]

COMMANDS        = [
    f'{APP_CMD} makemigrations'     ,
    f'{APP_CMD} makemigrations main',
    f'{APP_CMD} migrate'            ,
    f'{APP_CMD} migrate main'       ,
    f'{APP_CMD} collectstatic'      ,
]

SERVICES = [
    'nginx',
    f'{ APP_NAME }',
]

LINK = {
    f'/etc/nginx/sites-available/{APP_NAME}' : f'/etc/nginx/sites-enabled/{APP_NAME}',
}

COPY = {
    f'{BASE_PATH}/config/etc/systemd/system/{APP_NAME}.service'  : f'/etc/systemd/system/{APP_NAME}.service', 
}

if SERVER_SECURE:
    COPY[f'{BASE_PATH}/config/etc/nginx/sites-available/{APP_NAME}-secure'] = f'/etc/nginx/sites-available/{APP_NAME}'
else:
    COPY[f'{BASE_PATH}/config/etc/nginx/sites-available/{APP_NAME}'] = f'/etc/nginx/sites-available/{APP_NAME}'
    

SERVICES = [
    f'nginx',
    f'{APP_NAME}',
]

LOG_FILE = f'/var/log/{APP_NAME}.log'

class Command(BaseCommand):
    help = "Install Required dependencies"

    def add_arguments(self, parser):
        pass

    def section(self, text):
        print('-'*80)
        print(text)
        print('-'*80)

    def handle(self, *args, **options):
        if platform.system() == 'Windows':
            print("This command is intended to run only on linux servers.")
            exit()
        os.system('clear')
        self.section('Install System Packages')
        os.system(f'sudo apt install {" ".join(APT_PACKAGES)}')
        self.section('Install Python Packages')
        os.system(f'pip install {" ".join(PIP_PACKAGES)}')
        self.section('Copy Required Files')
        for source,dest in COPY.items():
            os.system(f'sudo cp {source} {dest}')
        self.section('Make Symbolic Links')
        for source,dest in LINK.items():
            os.system(f'sudo ln -s {source} {dest}')
        self.section('Reload Service Files')
        os.system('sudo systemctl daemon-reload')
        for service in SERVICES:
            self.section(f"Enable / Start Service {service}")
            os.system(f'sudo systemctl enable {service}')
            os.system(f'sudo systemctl stop {service}')
            os.system(f'sudo systemctl start {service}')
            os.system(f'sudo systemctl status {service}')
        self.section('Create Required Directories')
        for dir in DIRECTORIES:
            os.system(f'sudo mkdir -p {dir}')
            os.system(f'sudo chown -R {USER}:{GROUP} {dir}')
            os.system(f'sudo chmod -R 775 {dir}')
        self.section('Create Log File')
        os.system(f'sudo touch {LOG_FILE}')
        os.system(f'sudo chown -R {USER}:{GROUP} {LOG_FILE}')
        os.system(f'sudo chmod -R 775 {LOG_FILE}')
        self.section('Setup Library Root')
        os.system(f'echo /library > {BASE_PATH}/config/library-root.cfg')
        self.section('Prepare Settings')
        os.system(f'echo "DEBUG=True"               >  backend/settings.py')
        os.system(f'echo "SECURE={SERVER_SECURE}"   >> backend/settings.py')
        os.system(f'cat backend.settings-master.py  >> backend/settings.py')
        os.system(f'echo "DEBUG=False"              >  backend/settings-server.py')
        os.system(f'echo "SECURE={SERVER_SECURE}"   >> backend/settings-server.py')
        os.system(f'cat backend.settings-master.py  >> backend/settings-server.py')
        self.section('Initialize django application database')
        os.system(f'{APP_CMD} makemigrations')
        os.system(f'{APP_CMD} makemigrations main')
        os.system(f'{APP_CMD} migrate')
        os.system(f'{APP_CMD} migrate main')
        os.system(f'{APP_CMD} collectstatic --noinput')