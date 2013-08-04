#!/bin/bash -ex
DIR="$1"
find "$DIR" -name "*.mp3" > music_files
echoprint-codegen -s < music_files > music_files.json
python fastingest.py music_files.json

# Cleanup
rm music_files 
rm music_files.json

