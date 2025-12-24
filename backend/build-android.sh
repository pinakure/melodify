#!/bin/bash
rm -rf bin
source ../venv/bin/activate
source ./install.sh
git stash
git pull
rm -rf ./buildozer
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_conversion.pxi
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/armeabi-v7a__ndk_target_21/kivy/kivy/weakproxy.pyx
git checkout HEAD -- .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/kivy/arm64-v8a__ndk_target_21/kivy/kivy/weakproxy.pyx
python -m buildozer android debug
source ./debug-apk.sh
