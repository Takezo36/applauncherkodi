# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import platform
import sys
import xbmc
import xbmcaddon
import subprocess
import os
import ast
myOS = platform.system()


ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID) + "\\"
LINUX_DEMON_PATH = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" + os.sep + "lib" + os.sep + "LinuxRestartDemon.py"
def getAppsWithIcons(additionalDir=""):
  return MyAppLister.getAppsWithIcons()

def runLinuxDemon(command, args):
  args.insert(0, (sys.executable + " " + LINUX_DEMON_PATH + " " + command).split(" "))
  subprocess.Popen(args)
def runLinux(command, args):
  args.insert(0, command)
  subprocess.Popen(args)
def runLinuxMinimize(command, args):
  from ewmh import EWMH
  ewmh = EWMH()
  win = ewmh.getActiveWindow()
  args.insert(0, command)
  subprocess.call(args)
  ewmh.setActiveWindow(win)
  ewmh.display.flush()

def runWindowsDemon(kodiExe, command, args):
  WINDOWS_DAEMON_SCRIPT_LOCATION = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" +os.sep + "lib" + os.sep + "WindowsDaemon.ps1"
  with open(WINDOWS_DAEMON_SCRIPT_LOCATION, 'r') as myfile:
    WINDOWS_DAEMON_SCRIPT=myfile.read()
  WINDOWS_DAEMON_SCRIPT = WINDOWS_DAEMON_SCRIPT.replace("%kodiexe%", kodiExe).replace("%exec%", command).replace("%waittime%", ADDON.getSetting("waittimeuwp"));
  if args:
    sargs = "\""+"\",\"".join(args)+"\""
  else:
    sargs = ""
  WINDOWS_DAEMON_SCRIPT = WINDOWS_DAEMON_SCRIPT.replace("%args%", sargs)
  call = ["powershell", WINDOWS_DAEMON_SCRIPT]
  subprocess.Popen(call, creationflags=0x08000000)
def runWindows(command, args):
  if args:
    call = ["powershell", "Start-Process \"" + command + "\" -ArgumentList @(\""+"\",\"".join(args)+"\");"]
  else:
    call = ["powershell", "Start-Process \"" + command + "\";"]
  subprocess.Popen(call, creationflags=0x08000000)

  

def executeApp(command, sargs, killKodi, minimize):
  if sargs == "":
    args = []
  else:
    args = sargs.split(",")
  if killKodi:
    if myOS == "Linux":
      runLinuxDemon(command, args)
    elif myOS == "Windows":
      runWindowsDemon(xbmc.translatePath("special://xbmc") + "kodi", command, args)
    xbmc.executebuiltin("Quit")  
  elif minimize:
    xbmc.executebuiltin("Minimize")
    if myOS == "Linux":
      runLinuxMinimize(command, args)
    elif myOS == "Windows":
      runWindowsDemon(xbmc.translatePath("special://xbmc") + "kodi", command, args)
  else:
    if myOS == "Linux":
      runLinux(command, args)
    elif myOS == "Windows":
      runWindows(command, args)

    
      


