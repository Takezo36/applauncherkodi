# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import xbmcgui
import simplejson as json
import subprocess
import os

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID) + "\\"
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

def getAppsWithIcons(additionalDir=""):
  output = subprocess.check_output("powershell $PSVersionTable.PSVersion.Major", creationflags=0x08000000)
  try: 
    version = int(output)
    if version < 3:
      showFailedMsg()
      return {}
  except ValueError:
    showFailedMsg()
    return {}
  output = subprocess.check_output(["powershell", APPREADER_SCRIPT], creationflags=0x08000000)
  result = json.loads(output.decode("ascii","ignore"))
  return result
def showFailedMsg():
  subprocess.call("echo \\\"" + FAIL_URL + "\\\"|clip")
  xbmcgui.Dialog().ok('Error', FAILED_LINE1,FAILED_LINE2,FAILED_LINE3)
if (__name__ == "__main__"):
  xbmc.log("version %s started" % ADDON_VERSION)
  ADDON.openSettings()
  xbmc.log('finished')

