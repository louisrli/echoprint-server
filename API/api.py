#!/usr/bin/env python
# encoding: utf-8
"""
api.py

Created by Brian Whitman on 2010-06-16.
Copyright (c) 2010 The Echo Nest Corporation. All rights reserved.
"""
from __future__ import with_statement

import web
import fp
import re
import youtube as yt

try:
    import json
except ImportError:
    import simplejson as json


# Very simple web facing API for FP dist

urls = (
    '/query', 'query',
    '/query?(.*)', 'query',
    '/youtube', 'youtube'
)


CODEVER = 4.21

class youtube:
    def POST(self):
        params = web.input(youtube_url=None, start=None, stop=None)

        if not (params.youtube_url and params.start and params.stop):
            return web.webapi.BadRequest()

        # Extract the fingerprints from the videos
        tag = yt.fingerprint_youtube(params.youtube_url, 
                int(params.start), int(params.stop))

        # Query the tag in the database
        best_match = _query_tag(tag['code'], tag)
        return best_match

class query:
    def POST(self):
        params = web.input(mp3={})
        if 'mp3' in params:
            filename = _save_file(params.mp3, "audio")
            tag = yt.generate_tag(filename)

            print tag['code']
            return _query_tag(tag['code'])
        else:
            return web.webapi.BadRequest()

def _save_file(webfile, output_dir):
    """
    Saves a POSTed file to output_dir.

    Args:
        webfile: A web.py file object

    Returns:
        The path to the output file
    """
    filepath = webfile.filename.replace('\\','/') 
    filename = filepath.split('/')[-1] 

    o = output_dir +'/'+ filename

    fout = open(o, 'w') 

    try:
        fout.write(webfile.file.read()) 
    finally:
        fout.close() 

    return o


def _query_tag(fp_code, query_obj=None):
    """
    Queries the database for given fingerprint

    Args:
        fp_code: A fingerprint string
        query_obj: An optional dict of echoprint-codegen

    """
    response = fp.best_match_for_query(fp_code)
    if response:
        return json.dumps({
            "ok":True, 
            "message":response.message(),
            "match":response.match(),
            "score":response.score,
            "qtime":response.qtime, 
            "track_id":response.TRID, 
            "total_time":response.total_time
            })


application = web.application(urls, globals())#.wsgifunc()
        
if __name__ == "__main__":
    application.run()

