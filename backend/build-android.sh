#!/bin/bash
#buildozer appclean
source ../venv/bin/activate
git stash
git pull
pip install buildozer
buildozer distclean
pip install cython
sudo apt install openjdk-21-jdk openjdk-21-jre 
pip install setuptools
pip install python-for-android
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/armeabi-v7a__ndk_target_21/kivy/kivy/weakproxy.pyx
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/arm64-v8a__ndk_target_21/kivy/kivy/weakproxy.pyx
python -m pip install cython django Pillow kivy kivymd mutagen requests buildozer
python -m buildozer android debug
cp bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk /mnt/c/codigo/melodify/melodify.apk