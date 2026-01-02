#!/bin/bash
clear
echo "Fixing Owner"
	sudo chown -R melodify:www-data .
echo "Installing Dependencies"
	sudo apt-get install libxcb-cursor0
echo "Authorizing X11 Host"
	sudo xhost +local:
echo "Updating source files"
	mkdir -p src/melodify/backend/main 2>NUL
	mkdir -p src/melodify/backend/static 2>NUL
	mkdir -p src/melodify/backend/templates 2>NUL
	mkdir -p src/melodify/backend/media 2>NUL
	mkdir -p src/melodify/backend/scripts 2>NUL
	mkdir -p src/melodify/backend/config 2>NUL
	cp -rf ../backend/main/* 	src/melodify/backend/main/
	cp -rf ../backend/templates/*	src/melodify/backend/templates/
	cp -rf ../backend/media/* 	src/melodify/backend/media/
	cp -rf ../backend/scripts/*	src/melodify/backend/scripts/
	cp -rf ../backend/config/* 	src/melodify/backend/config/
	cp -rf ../backend/manage.py	src/melodify/backend/manage.py
	cp -rf ../backend/db.sqlite3	src/melodify/backend/db.sqlite3
	cp -rf ../backend/backend/*	src/melodify/backend/backend
	cp -rf ../backend/static/* 	src/melodify/backend/static/
	cp -rf /static/melodify/*	src/melodify/backend/static/
echo "Setting up Settings file"
	echo "DEBUG=True"    > src/melodify/backend/backend/settings.py
	echo "SECURE=False" >> src/melodify/backend/backend/settings.py
	echo "ANDROID=True" >> src/melodify/backend/backend/settings.py
	cat  ../backend/backend/settings-master.py >> src/melodify/backend/backend/settings.py
briefcase create android  2> ../error.log
briefcase update android 2>> ../error.log
briefcase run android 2>> ../error.log

