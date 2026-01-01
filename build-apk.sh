#!/bin/bash
clear
echo "Updating source files"
cp -rf backend/main 		melodify.apk/src/melodify/backend/main
cp -rf backend/templates 	melodify.apk/src/melodify/backend/templates
cp -rf backend/static 		melodify.apk/src/melodify/backend/static
cp -rf /static/melodify		melodify.apk/src/melodify/backend/static
cp -rf backend/media 		melodify.apk/src/melodify/backend/media
cp -rf backend/scripts 		melodify.apk/src/melodify/backend/scripts
cp -rf backend/config 		melodify.apk/src/melodify/backend/config
cp -rf backend/manage.py	melodify.apk/src/melodify/backend/manage.py
cp -rf backend/db.sqlite3	melodify.apk/src/melodify/backend/db.sqlite3
cp -rf backend/backend		melodify.apk/src/melodify/backend/backend
echo "Setting up Settings file"
echo "DEBUG=True" > melodify.apk/src/melodify/backend/backend/settings.py
echo "SECURE=False" >> melodify.apk/src/melodify/backend/backend/settings.py
echo "ANDROID=True" >> melodify.apk/src/melodify/backend/backend/settings.py
cat  backend/backend/settings-master.py >> melodify.apk/src/melodify/backend/backend/settings.py
cd melodify.apk
briefcase create android
briefcase update android
briefcase run android -d '@beePhone'
cd ..

