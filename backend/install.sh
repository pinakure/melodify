#!/bin/bash
source ../venv/bin/activate
pip install django mutagen Pillow
../venv/bin/python manage.py install --settings=backend.settings-install
