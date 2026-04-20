[app]
title = IA Tributaria
package.name = superia
package.domain = com.superia
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,urllib3,certifi,idna,charset-normalizer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,ACCESS_NETWORK_STATE
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
