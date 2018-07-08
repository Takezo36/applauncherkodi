# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import platform
import simplejson as json
import xbmcaddon
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

CACHE_TIME = 999999
ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID = ADDON.getAddonInfo('id')

myOS = platform.system()
print myOS
if myOS == "Linux":
  import AppListerLinux as MyAppLister
elif myOS == "Windows":
  import AppListerWindows as MyAppLister
else:
  import AppListerLinux as MyAppLister

def getAppsWithIcons():
  cache = StorageServer.StorageServer(ADDON_ID+ADDON_VERSION, CACHE_TIME)
  lastChange = cache.get("lastchange")
  newLastChange = MyAppLister.getLastChange()
  if lastChange != newLastChange:
    apps = MyAppLister.getAppsWithIcons()
    cache.set("apps", json.dumps(apps))
    cache.set("lastchange", str(newLastChange))
  else:
    apps = json.loads(cache.get("apps"))
  return apps

