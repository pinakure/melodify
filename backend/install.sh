#!/bin/bash
USER=$(whoami)
source ../venv/bin/activate
echo "Installing dependencies..."
sudo apt install ffmpeg nginx openjdk-17-jdk openjdk-17-jre cmake pkg-config automake autoconf libtool libffi-dev libssl-dev python3-dev libltdl-dev libsqlite3-dev
pip install spotdl "cython<3.0.0" python-for-android django kivy kivymd asgiref sqlparse Pillow mutagen requests django-fontawesome_5 setuptools gunicorn buildozer
echo "Installing server config files..."
sudo cp config/etc/nginx/sites-available/melodify /etc/nginx/sites-available/melodify 
sudo cp config/etc/systemd/system/gunicorn.service /etc/systemd/system/gunicorn.service 
sudo systemctl daemon-reload
sudo systemctl restart nginx
sudo systemctl status nginx
echo "Creating django application database..."
python3 manage.py makemigrations 
python3 manage.py makemigrations main
python3 manage.py migrate
python3 manage.py migrate main
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
python3 manage.py collectstatic --noinput
sudo touch /var/log/melodify.log
sudo chown -R melodify:www-data /var/log/melodify.log
sudo chmod -R 755 /var/log/melodify.log