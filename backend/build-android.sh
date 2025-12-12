#!/bin/bash
source ../venv/bin/activate
python -m pip install cython django Pillow kivy kivymd mutagen requests buildozer
python -m buildozer android debug