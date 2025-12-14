#!/bin/bash
#buildozer appclean
git stash
git pull
source ../venv/bin/activate
python -m pip install cython django Pillow kivy kivymd mutagen requests buildozer
python -m buildozer android debug
cp bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk /mnt/c/codigo/melodify/melodify.apk