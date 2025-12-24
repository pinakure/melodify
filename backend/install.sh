#!/bin/bash
USER=$(whoami)
source ../venv/bin/activate
echo "Installing dependencies..."
sudo apt install nginx openjdk-17-jdk openjdk-17-jre cmake pkg-config automake autoconf libtool libffi-dev libssl-dev python3-dev libltdl-dev libsqlite3-dev
pip install "cython<3.0.0" python-for-android "django==6.0" kivy kivymd asgiref sqlparse Pillow mutagen requests django-fontawesome_5 setuptools gunicorn buildozer
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
python3 manage.py collectstatic --noinput