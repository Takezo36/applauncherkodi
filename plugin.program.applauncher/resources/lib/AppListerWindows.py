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
ADDON_ID       = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID)
APPREADER_SCRIPT = xbmc.translatePath("special://home")+ os.sep + "addons" + os.sep + ADDON_ID + os.sep + "lib" + os.sep + "appreader.ps1"
FAILED_LINE1 = "You need to have PowerShell installed at least version 3.0"
FAILED_LINE2 = "Please download and install it. For more info go to"
FAIL_URL = "https://docs.microsoft.com/de-de/powershell/scripting/setup/installing-windows-powershell?view=powershell-6" 
FAILED_LINE3 = FAIL_URL + " (this should be in your clipboard now)"
if not os.path.exists(ADDON_USER_DATA_FOLDER):
    os.makedirs(ADDON_USER_DATA_FOLDER)

def getAppsWithIcons(additionalDir=""):
  output = subprocess.check_output("powershell $PSVersionTable.PSVersion.Major")
  try: 
    version = int(output)
    if version < 3:
      showFailedMsg()
      return {}
    except ValueError:
      showFailedMsg()
      return {}
  output = subprocess.check_output([APPREADER_SCRIPT, ADDON_USER_DATA_FOLDER])
  result = json.loads(output)
  return result
def showFailedMsg():
  subprocess.call("echo \\\"" + FAIL_URL + "\\\"|clip")
  xbmcgui.Dialog().ok('Error', FAILED_LINE1,FAILED_LINE2,FAILED_LINE3)
if (__name__ == "__main__"):
  xbmc.log("version %s started" % ADDON_VERSION)
  ADDON.openSettings()
  xbmc.log('finished')

