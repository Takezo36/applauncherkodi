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

def runLinuxDemon(kodiExe, command):
  subprocess.Popen((sys.executable + " " + APP_LAUNCHER + " " + command + " " + kodiExe).split(" "))

def runWindowsDemon(kodiExe, command):
  subprocess.Popen(["powershell", 'Start-Process \"' + command + '\" -Wait;Start-Process \"' + kodiExe + '\"'], creationflags=0x08000000)

def executeApp(command, killKodi, minimize, killAfterAppClose):
  if myOS == "Windows":
    command = command.replace("/","\\")
  if killKodi:
    kodiExe = xbmc.translatePath("special://xbmc") + "kodi"
    if myOS == "Linux":
      runLinuxDemon(kodiExe, command)
    elif myOS == "Windows":
      runWindowsDemon(kodiExe, command)
#elif myOS == "Darwin":
#  import AppListerOSX as MyAppLister
    else:
      runLinuxDemon()
    xbmc.executebuiltin("Quit")
  else:
    print command
    if minimize:
      xbmc.executebuiltin("Minimize")
    if command[:15] == "explorer shell:":
      print "store app"
      subprocess.call(command)
    else:
      subprocess.call(command.strip().split(" "))
    if killAfterAppClose:
      xbmc.executebuiltin("Quit")


