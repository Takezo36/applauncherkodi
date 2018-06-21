# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import os
import Constants
import subprocess
import xbmcgui
import hashlib
from distutils.util import strtobool



ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID)
IGNORE_CATEGORIES = ["GNOME", "GTK", "Application", "Core"]
MAX_FOLDER_DEPTH = 1
FAILED_LINE1 = ADDON.getLocalizedString(35023)
FAILED_LINE2 = ADDON.getLocalizedString(35024)
FAILED_LINE3 = ADDON.getLocalizedString(35025)

def showSVGMissingDialog():
  xbmcgui.Dialog().ok('Error', FAILED_LINE1,FAILED_LINE2,FAILED_LINE3)

def discoverIcon(dirName, icon):
  allowedIconTypes = [".jpg", ".png", ".ico", ".svg"]
  for allowedIconType in allowedIconTypes:
    if os.path.isfile("/usr/share/pixmaps/"+icon+allowedIconType):
      return "/usr/share/pixmaps/"+icon+allowedIconType
  if os.path.isdir(dirName):
    themeList = os.listdir(dirName)
    #moving hicolor to front
    if "hicolor" in themeList:
      themeList.remove("hicolor")
      themeList.insert(0, "hicolor")
    for theme in themeList:
      for allowedIconType in allowedIconTypes:
        for subfolder in sorted(os.listdir(dirName+theme), reverse=True):
          if os.path.isdir(dirName+theme+os.sep+subfolder):
            for iconfolder in sorted(os.listdir(dirName+theme+os.sep+subfolder), reverse=True):
              if os.path.isfile(dirName+theme+os.sep+subfolder+os.sep+iconfolder+os.sep+icon+allowedIconType):
                return dirName+theme+os.sep+subfolder+os.sep+iconfolder+os.sep+icon+allowedIconType
  return None

def svg2png(svg):
  hash_object = hashlib.md5(svg.encode())
  outname = ADDON_USER_DATA_FOLDER + "/" + hash_object.hexdigest() + ".png"
  if not os.path.isfile(outname):
    executable = ADDON.getSetting("svgpath").replace("%output",outname)
    executable.replace("%input",svg)
    try:
      subprocess.call(executable.split(" "))
    except:
      return None
  return outname

def getBestIcon(icon):
  if os.path.isfile(icon):
    return icon
  return discoverIcon("/usr/share/icons/", icon)

def getAppsWithIcons(additionalDir=""):
  result = {}
  allApps = {}
  language = xbmc.getLanguage(xbmc.ISO_639_1)
  defaultDirs = ["/usr/share/applications/", "~/.local/share/applications/"]
  ignoreCategories = ["GNOME", "GTK"]
  if additionalDir and additionalDir[-1:]!="/":
    additionalDir += "/"
  if additionalDir:
    defaultDirs.append(additionalDir)
  for appDir in defaultDirs:
    if os.path.isdir(appDir):
      for file in sorted(os.listdir(appDir)):
        if file.endswith(".desktop"):
          entry = {}
          desktopEntry = False
          sideCalls = []
          sideCall = {}
          entry[Constants.SIDECALLS] = sideCalls
          entry[Constants.TYPE] = Constants.TYPE_APP
          for line in open(appDir+os.sep+file):
            
            if line.startswith("[Desktop Entry"):
              #main entry entrance
              desktopEntry = True
            if line.startswith("[Desktop Action"):
              sideCall = {}
              desktopEntry = False
              sideCalls.append(sideCall)
            if line.startswith("Exec"):
              tempExec=line.split("=")[1][:-1]
              if "%" in tempExec:
                tempExec = tempExec[:tempExec.find("%")]
                tempExecSplit = tempExec.split(" ")
              if desktopEntry:
                entry[Constants.ARGS] = tempExecSplit[1:]
                entry[Constants.EXEC] = tempExecSplit[0]  
                entry[Constants.EXEC] = getFullExecPath(entry[Constants.EXEC])
              else:
                sideCall[Constants.ARGS] = tempExecSplit[1:]
                sideCall[Constants.EXEC] = tempExecSplit[0]  
                sideCall[Constants.EXEC] = getFullExecPath(entry[Constants.EXEC])
            elif line.startswith("Name="):
              if desktopEntry:
                if Constants.NAME not in entry:
                  entry[Constants.NAME]=line.split("=")[1][:-1]
              else:
                if Constants.NAME not in sideCall:
                  sideCall[Constants.NAME]=line.split("=")[1][:-1]
            elif line.startswith("Name["+language+"]"):
              if desktopEntry:
                entry[Constants.NAME]=line.split("=")[1][:-1]
              else:
                sideCall[Constants.NAME]=line.split("=")[1][:-1]
            elif line.startswith("Icon"):
              if desktopEntry:
                entry[Constants.ICON]=line.split("=")[1][:-1]
              else:
                sideCall[Constants.ICON]=line.split("=")[1][:-1]
            elif line.startswith("Categories"):
              categories = line.split("=")[1][:-1].split(";")
          if Constants.ICON in entry:
            icon = getBestIcon(entry[Constants.ICON])
            if icon and icon[-4:] == ".svg":
              icon = svg2png(icon)
            entry[Constants.ICON] = icon
          if entry[Constants.SIDECALLS]:
            for sideCall in entry[Constants.SIDECALLS]:
              if Constants.ICON in sideCall:
                sideCall[Constants.ICON]=getBestIcon(sideCall[Constants.ICON])
          allApps[entry[Constants.NAME]] = entry
          if categories:
            i = 0
            for category in categories:
              if category and category not in ignoreCategories and category[:8] != "X-GNOME-" and category[:8] != "X-Unity-":
                addItemToFolder(entry, category, result)
                i=i+1
                if i >= MAX_FOLDER_DEPTH:
                  break
  addFolder(allApps, Constants.ALL_APPS_FOLDER, result)
  return result

def getFullExecPath(target):
  if "/" in target:
    return target
  else:
    myTarget = target.split(" ")
  cmd = "whereis " + myTarget[0]
  whereis = subprocess.check_output(cmd.split(" ")).split(" ")
  if len(whereis) > 1:
    target = whereis[1]
  if len(myTarget) > 1:
    for i in range(1, len(myTarget)):
      target = target + " " + myTarget[i]
  return target

def addItemToFolder(entry, folderName, parent):
  if folderName in parent:
    folder = parent[folderName]
  else:
    folder = {}
    addFolder(folder, folderName, parent)
  folder[entry[Constants.NAME]] = entry

def addFolder(entry, name, parent):
  entry[Constants.TYPE] = Constants.TYPE_FOLDER
  parent[name] = entry

if (__name__ == "__main__"):
  xbmc.log("version %s started" % ADDON_VERSION)
  ADDON.openSettings()
  xbmc.log('finished')
if strtobool(ADDON.getSetting("showsvgmsg")):
  try:
    subprocess.call([ADDON.getSetting("svgpath").split(" ")[0],"--help"])
  except:
    showSVGMissingDialog()
  ADDON.setSetting("showsvgmsg","false")
