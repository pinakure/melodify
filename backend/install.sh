#!/bin/bash
source ../venv/bin/activate
sudo apt install nginx openjdk-17-jdk openjdk-17-jre cmake pkg-config automake autoconf libtool libffi-dev libssl-dev python3-dev libltdl-dev libsqlite3-dev
pip install "cython<3.0.0" python-for-android "django==6.0" kivy kivymd asgiref sqlparse Pillow mutagen requests django-fontawesome_5 setuptools gunicorn buildozer

