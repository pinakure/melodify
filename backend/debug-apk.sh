#!/bin/bash
if [ -f "./bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk" ]; then
    echo "APK found: ./bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk"
    cp ./bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk /mnt/c/codigo/melodify/melodify.apk
    adb install -s ./bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk 
    adb shell monkey -p com.melodify.melodify -c android.intent.category.LAUNCHER 1
    adb logcat -s python
else
    echo "APK not found: ./bin/melodify-0.1-arm64-v8a_armeabi-v7a-debug.apk" >&2
fi
source ./debug-apk.sh