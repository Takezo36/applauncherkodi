# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import platform
import sys
import xbmc
import xbmcaddon
import subprocess
import os
myOS = platform.system()


ADDON = xbmcaddon.Addon()
ADDON_ID       = ADDON.getAddonInfo('id')
LINUX_DEMON_PATH = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" + os.sep + "lib" + os.sep + "LinuxRestartDemon.py"
def getAppsWithIcons(additionalDir=""):
  return MyAppLister.getAppsWithIcons()

def runLinuxDemon():
  subprocess.Popen((sys.executable + " " + APP_LAUNCHER + " " + command + " " + kodiExe).split(" "))


def executeApp(command, killKodi, minimize, killAfterAppClose):
  if killKodi:
    kodiExe = xbmc.translatePath("special://xbmc") + "kodi"
    if myOS == "Linux":
      runLinuxDemon(kodiExe)
    elif myOS == "Windows":
      runWindowsDemon(kodiExe)
#elif myOS == "Darwin":
#  import AppListerOSX as MyAppLister
    else:
      runLinuxDemon()
    xbmc.executebuiltin("Quit")
  else:
    if minimize:
      xbmc.executebuiltin("Minimize")
    subprocess.call(command.strip().split(" "))
    if killAfterAppClose:
      xbmc.executebuiltin("Quit")


