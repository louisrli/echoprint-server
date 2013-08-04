#!/usr/bin/env python
import subprocess
import pyechonest as pye
import os
import logging
from pyechonest import config
from pyechonest import song

# EchoNest API configuation
config.ECHO_NEST_API_KEY = "VVCRHMDOSJTUONGDQ"
config.CODEGEN_BINARY_OVERRIDE = subprocess.check_output(["which", "echoprint-codegen"]).strip()
config.TRACE_API_CALLS = True

def fingerprint_youtube(url, start, stop, whole_video=False):
    # Validate YouTube URL

    mp3file = _download_audio(url)

    tag = generate_tag(mp3file, start, stop)

    if whole_video:
        full_tag = generate_tag(mp3file)
        return tag, full_tag
    else:
        return tag

def _download_audio(url):
    prog = "youtube-dl"
    audio_dir = "audio"
    flags = ["--extract-audio", 
            "--max-quality", "5", 
            "-o", audio_dir + "/" + "%(id)s.%(ext)s",
            "--newline",  # progress bar on newlines
            url] 

    # Get the id for validation
    id = subprocess.check_output([prog, "--get-id", url]).strip()
    filename = "%s/%s.mp3" % (audio_dir, id)

    if os.path.exists(filename):
        logging.info("Already have the file: %s" % filename)
        return filename

    # Extract the mp3 file
    p = subprocess.Popen([prog] + flags,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)

    for line in iter(p.stdout.readline, b''):
        print(">>> " + line.rstrip())

    # Process the .mp3 file
    return filename

def generate_tag(filename, start=-1, stop=-1):
    """
    Note that these default arguments are due to the undocumented
    way that the pyechonest library calls codegen, which checks
    if start / duration are >= 0.

    Args:
        filename: The name of the input audio file to be identified
        start: The start time, in seconds
        stop: The stop time, in seconds
    Returns:
        A dict resulting from the echonest JSON
    """
    if (start > 0 and stop > 0) and not stop > start:
        raise "TODO error"

    duration = stop - start
    codegen = pye.util.codegen(filename, start, duration)

    if any(('error' in c) for c in codegen):
        print codegen
        raise Exception("Couldn't decode file")

    # Only return the first result
    return codegen[0]

def identify_song(tag):
    """
    Uses the Echonest API to try identifying a song
    Returns:
        None if no results were found from any hosts
        Returns a list of artist + title names if successful
    """
    result = song.identify(query_obj=tag)
    if result:
        return [{
            'artist': r.artist_name,
            'title': r.title
            } for r in result]
    else: 
        return None

if __name__ == '__main__':
    main()
