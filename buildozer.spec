[app]

# App info
title = AASAA Booking
package.name = aasaa
package.domain = com.aasaa.jarrar

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Version
version = 1.1.11.1

# Requirements
requirements = python3,kivy==2.3.0,pillow,plyer,pyjnius,certifi

# Splash and icon
presplash.filename = %(source.dir)s/presplash.png
icon.filename = %(source.dir)s/icon.png

# Orientation
orientation = portrait

# Fullscreen
fullscreen = 0

# Android
android.archs = arm64-v8a

android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_PHONE_STATE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,ACCESS_NETWORK_STATE,RECEIVE_BOOT_COMPLETED,FOREGROUND_SERVICE

android.api = 33
android.minapi = 21
android.ndk = 25b
# android.ndk_path = /Users/abdulmajeed/Library/Android/sdk/ndk/25.1.8937393

android.accept_sdk_license = True
android.enable_androidx = True

# Keep the service alive
android.services =

# Copy libs
android.copy_libs = 1

# Logcat
android.logcat_filters = *:S python:D

# Allow backup
android.allow_backup = True

# P4A
p4a.branch = master

# Whitelist
android.whitelist =

# Gradle
android.gradle_dependencies =
android.add_jars =
android.add_aars =

[buildozer]

# Build log level (0=error, 1=info, 2=debug)
log_level = 2

# Warn on root
warn_on_root = 1

# Build directory
build_dir = ./.buildozer

# Bin directory
bin_dir = ./bin
