import json
import os
import shutil
import tempfile
from time import time, mktime


import xbmc
import xbmcvfs
from streamlink.compat import is_py2

try:
    xdg_cache = xbmc.translatePath('special://profile/addon_data/script.module.streamlink')
except:
    xdg_cache = xbmcvfs.translatePath('special://profile/addon_data/script.module.streamlink')
try:
    temp_dir = xbmc.translatePath('special://temp')
except:
    temp_dir = xbmcvfs.translatePath('special://temp')

if is_py2:
    xdg_cache = xdg_cache.encode('utf-8')
    temp_dir = temp_dir.encode('utf-8')

cache_dir = os.path.join(xdg_cache, "streamlink")

temp_streamlink = os.path.join(temp_dir, 'script.module.streamlink')
if not xbmcvfs.exists(cache_dir):
    xbmcvfs.mkdirs(cache_dir)
if not xbmcvfs.exists(temp_streamlink):
    xbmcvfs.mkdirs(temp_streamlink)



class Cache(object):
    """Caches Python values as JSON and prunes expired entries."""

    def __init__(self, filename, key_prefix=""):
        self.key_prefix = key_prefix
        self.filename = os.path.join(cache_dir, filename)

        self._cache = {}

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as fd:
                    self._cache = json.load(fd)
            except Exception:
                self._cache = {}
        else:
            self._cache = {}

    def _prune(self):
        now = time()
        pruned = []

        for key, value in self._cache.items():
            expires = value.get("expires", time())
            if expires <= now:
                pruned.append(key)

        for key in pruned:
            self._cache.pop(key, None)

        return len(pruned) > 0

    def _save(self):
        fd, tempname = tempfile.mkstemp()
        fd = os.fdopen(fd, "w")
        json.dump(self._cache, fd, indent=2, separators=(",", ": "))
        fd.close()

        # Silently ignore errors
        try:
            if not os.path.exists(os.path.dirname(self.filename)):
                os.makedirs(os.path.dirname(self.filename))

            shutil.move(tempname, self.filename)
        except (IOError, OSError):
            os.remove(tempname)

    def set(self, key, value, expires=60 * 60 * 24 * 7, expires_at=None):
        self._load()
        self._prune()

        if self.key_prefix:
            key = "{0}:{1}".format(self.key_prefix, key)

        expires += time()

        if expires_at:
            expires = mktime(expires_at.timetuple())

        self._cache[key] = dict(value=value, expires=expires)
        self._save()

    def get(self, key, default=None):
        self._load()

        if self._prune():
            self._save()

        if self.key_prefix:
            key = "{0}:{1}".format(self.key_prefix, key)

        if key in self._cache and "value" in self._cache[key]:
            return self._cache[key]["value"]
        else:
            return default

    def get_all(self):
        ret = {}
        self._load()

        if self._prune():
            self._save()

        for key, value in self._cache.items():
            if self.key_prefix:
                prefix = self.key_prefix + ":"
            else:
                prefix = ""
            if key.startswith(prefix):
                okey = key[len(prefix):]
                ret[okey] = value["value"]

        return ret


__all__ = ["Cache"]
