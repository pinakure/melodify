#!/bin/bash
#buildozer appclean
source ../venv/bin/activate
git stash
git pull
sudo apt install nginx openjdk-17-jdk openjdk-17-jre cmake pkg-config automake autoconf libtool libffi-dev libssl-dev python3-dev libltdl-dev libsqlite3-dev
pip install "cython<3.0.0" python3 hostpython3 python-for-android django kivy kivymd asgiref sqlparse Pillow mutagen requests django-fontawesome_5 setuptools gunicorn buildozer
rm -rf ./buildozer
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/armeabi-v7a__ndk_target_21/kivy/kivy/weakproxy.pyx
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/arm64-v8a__ndk_target_21/kivy/kivy/weakproxy.pyx
python -m buildozer android debug
source ./debug-apk
