# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import xbmcgui
import simplejson as json
import subprocess
import os
import platform
import time
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer

CACHE_TIME = 999999

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID) + "\\"
GET_CHANGE_DATE_SCRIPT_LOCATION = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" +os.sep + "lib" + os.sep + "ChangeDate.ps1"
with open(GET_CHANGE_DATE_SCRIPT_LOCATION, 'r') as myfile:
  GET_CHANGE_DATE_SCRIPT=myfile.read()
APPREADER_SCRIPT_LOCATION = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" +os.sep + "lib" + os.sep + "appreader.ps1"
with open(APPREADER_SCRIPT_LOCATION, 'r') as myfile:
  APPREADER_SCRIPT=myfile.read()
APPREADER_SCRIPT = APPREADER_SCRIPT.replace("$args[0]", "\""+ADDON_USER_DATA_FOLDER + "\"")
FAILED_LINE1 = ADDON.getLocalizedString(35020)
FAILED_LINE2 = ADDON.getLocalizedString(35021)
FAIL_URL = "https://docs.microsoft.com/de-de/powershell/scripting/setup/installing-windows-powershell?view=powershell-6" 
FAILED_LINE3 = FAIL_URL + ADDON.getLocalizedString(35022)
if not os.path.exists(ADDON_USER_DATA_FOLDER):
    os.makedirs(ADDON_USER_DATA_FOLDER)
def getLastChange():
  try:
    if int(platform.version().split(".")[0]) >= 11:
      cache = StorageServer.StorageServer(ADDON_ID+ADDON_VERSION, CACHE_TIME)
      cachedInstalledVersions = cache.get("installedstore")
      currentInstalledVersions = str(hash(subprocess.check_output(["powershell", "(Get-AppxPackage).version"], creationflags=0x08000000)))
      if not cachedInstalledVersions or cachedInstalledVersions != currentInstalledVersions:
        cache.set("installedstore", currentInstalledVersions)
        return time.time()
  except:
    xbmc.log("failed to platform version", xbmc.LOGDEBUG)
  return subprocess.check_output(["powershell", GET_CHANGE_DATE_SCRIPT], creationflags=0x08000000)
def getAppsWithIcons(additionalDir=""):
  output = subprocess.check_output("powershell $PSVersionTable.PSVersion.Major", creationflags=0x08000000)
  try: 
    version = int(output)
    if version < 2:
      showFailedMsg()
      return {}
  except ValueError:
    showFailedMsg()
    return {}
  output = subprocess.check_output(["powershell", APPREADER_SCRIPT], creationflags=0x08000000)
  result = json.loads(output.replace("\n","").replace("\r","").decode("ascii","ignore"))
  return result
def showFailedMsg():
  subprocess.call(["echo", FAIL_URL,"|","c:\\windows\\system32\\clip.exe"], shell=True)
  xbmcgui.Dialog().ok('Error', FAILED_LINE1,FAILED_LINE2,FAILED_LINE3)
if (__name__ == "__main__"):
  xbmc.log("version %s started" % ADDON_VERSION)
  ADDON.openSettings()
  xbmc.log('finished')

