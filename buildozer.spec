[app]
title = SmartGloveApp
package.name = smartgloveapp
package.domain = org.smartglove

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,tflite

version = 0.1

requirements = python3,kivy==2.2.1,requests,pillow,numpy,tflite-runtime,pyjnius==1.5.0

orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a
android.allow_backup = True 
