#!/usr/bin/env python3
'''
    script to update streamlink for Kodi
'''
import fileinput

text_list = [
    {
        'file': 'resources/lib/streamlink/cache.py',
        'find': 'class Cache(object):',
        'replace': '''import xbmc
import xbmcvfs
from streamlink.compat import is_py2

xdg_cache = xbmc.translatePath('special://profile/addon_data/script.module.streamlink')
temp_dir = xbmc.translatePath('special://temp')

if is_py2:
    xdg_cache = xdg_cache.encode('utf-8')
    temp_dir = temp_dir.encode('utf-8')

cache_dir = os.path.join(xdg_cache, "streamlink")

temp_streamlink = os.path.join(temp_dir, 'script.module.streamlink')
if not xbmcvfs.exists(cache_dir):
    xbmcvfs.mkdirs(cache_dir)
if not xbmcvfs.exists(temp_streamlink):
    xbmcvfs.mkdirs(temp_streamlink)
\n\nclass Cache(object):''',
    },
    {
        'file': 'resources/lib/streamlink/cache.py',
        'find': '        fd, tempname = tempfile.mkstemp()',
        'replace': '        fd, tempname = tempfile.mkstemp(dir=temp_streamlink)',
    },
    {
        'file': 'resources/lib/streamlink/compat.py',
        'find': '    from backports.shutil_which import which',
        'replace': '    from shutil_which.shutil_which import which',
    },
       
]


for data in text_list:
    with fileinput.FileInput(data['file'], inplace=True) as file:
        for line in file:
            print(line.replace(data['find'], data['replace']), end='')

