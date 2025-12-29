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

LINK = {
    f'/etc/nginx/sites-available/{APP_NAME}' : f'/etc/nginx/sites-enabled/{APP_NAME}',
}

COPY = {
    f'{BASE_PATH}/config/etc/nginx/sites-available/{APP_NAME}'   : f'/etc/nginx/sites-available/{APP_NAME}',
    f'{BASE_PATH}/config/etc/systemd/system/{APP_NAME}.service'  : f'/etc/systemd/system/{APP_NAME}.service', 
}

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
        os.system(f'sudo apt install {" ".join(APT_PACKAGES)}')
        os.system(f'pip install {" ".join(PIP_PACKAGES)}')



"""
#!/bin/bash
USER=$(whoami)
PYTHON=/src/melodify/venv/bin/python3
MELODIFY=$PYTHON manage.py
echo "----------------------------------------------------------------------------------------"
echo "Activating VirtualEnv..."
echo "----------------------------------------------------------------------------------------"
source ../venv/bin/activate
echo "----------------------------------------------------------------------------------------"
echo "Installing system dependencies..."
echo "----------------------------------------------------------------------------------------"
sudo apt install            \
    ffmpeg                  \
    nginx                   \
    openjdk-17-jdk          \
    openjdk-17-jre          \
    cmake                   \
    pkg-config              \
    automake                \
    autoconf                \
    libtool                 \
    libffi-dev              \
    libssl-dev              \
    python3-dev             \
    libltdl-dev             \
    libsqlite3-dev
echo "----------------------------------------------------------------------------------------"
echo "Installing python dependencies..."
echo "----------------------------------------------------------------------------------------"
pip install                 \
    spotdl                  \
    stable-ts               \
    "cython<3.0.0"          \
    python-for-android      \
    django                  \
    kivy                    \
    kivymd                  \
    asgiref                 \
    sqlparse                \
    Pillow                  \
    mutagen                 \
    requests                \
    django-fontawesome_5    \
    setuptools              \
    gunicorn                \
    buildozer               
echo "----------------------------------------------------------------------------------------"
echo "Installing Nginx & Gunicorn config files..."
echo "----------------------------------------------------------------------------------------"
sudo cp config/etc/nginx/sites-available/melodify /etc/nginx/sites-available/melodify 
sudo ln -s /etc/nginx/sites-available/melodify /etc/nginx/sites-enabled/melodify 
sudo cp config/etc/systemd/system/melodify.service /etc/systemd/system/melodify.service 
echo "----------------------------------------------------------------------------------------"
echo "Enabling / Starting Nginx service..."
echo "----------------------------------------------------------------------------------------"
sudo systemctl daemon-reload
sudo systemctl enable nginx
sudo systemctl stop nginx
sudo systemctl start nginx
sudo systemctl status nginx
echo "----------------------------------------------------------------------------------------"
echo "Enabling / Starting Gunicorn-Melodify service..."
echo "----------------------------------------------------------------------------------------"
sudo systemctl enable melodify
sudo systemctl stop melodify
sudo systemctl start melodify
sudo systemctl status melodify
echo "----------------------------------------------------------------------------------------"
echo "Initializing django application database..."
echo "----------------------------------------------------------------------------------------"
$MELODIFY makemigrations 
$MELODIFY makemigrations main
$MELODIFY migrate
$MELODIFY migrate main
echo "----------------------------------------------------------------------------------------"
echo "Creating required working directories..."
echo "----------------------------------------------------------------------------------------"
sudo mkdir -p /library/.artists
sudo chown -R $USER:www-data /library
sudo chmod -R 755 /static
sudo mkdir -p /static/melodify
sudo chown -R $USER:www-data /static
sudo chmod -R 755 /static
sudo mkdir -p ./media/artists
sudo mkdir -p ./media/albums
sudo mkdir -p ./media/songs
sudo chown -R $USER:www-data ./media
sudo chmod -R 755 ./media
echo "----------------------------------------------------------------------------------------"
echo "Initializing Log File..."
echo "----------------------------------------------------------------------------------------"
sudo touch /var/log/melodify.log
sudo chown -R melodify:www-data /var/log/melodify.log
sudo chmod -R 755 /var/log/melodify.log
echo "----------------------------------------------------------------------------------------"
echo "Collecting static files..."
echo "----------------------------------------------------------------------------------------"
$MELODIFY collectstatic --noinput
echo "----------------------------------------------------------------------------------------"
echo "Setting up library root (temporary fix)"
echo "----------------------------------------------------------------------------------------"
echo /library > /src/melodify/backend/config/library-root.cfg
$MELODIFY 

"""