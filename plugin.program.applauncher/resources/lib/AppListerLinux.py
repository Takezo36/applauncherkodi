# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import xbmc
import xbmcaddon
import os
import Constants
import subprocess


ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
IGNORE_CATEGORIES = ["GNOME", "GTK", "Application", "Core"]
MAX_FOLDER_DEPTH = 1
def discoverIcon(dirName, icon):
  allowedIconType = [".jpg", ".png"]
  if os.path.isfile("/usr/share/pixmaps/"+icon+".png"):
    return "/usr/share/pixmaps/"+icon+".png"
  if os.path.isdir(dirName):
    themeList = os.listdir(dirName)
    #moving hicolor to front
    if "hicolor" in themeList:
      themeList.remove("hicolor")
      themeList.insert(0, "hicolor")
    for theme in themeList:
      if os.path.isdir(dirName+theme):
        for iconfolder in sorted(os.listdir(dirName+theme), reverse=True):
          if os.path.isfile(dirName+theme+os.sep+iconfolder+os.sep+"apps"+os.sep+icon+".png"):
            return dirName+theme+os.sep+iconfolder+os.sep+"apps"+os.sep+icon+".png"
          if os.path.isfile(dirName+theme+os.sep+iconfolder+os.sep+"actions"+os.sep+icon+".png"):
            return dirName+theme+os.sep+iconfolder+os.sep+"actions"+os.sep+icon+".png"
  return None
#this is fucking slow find better way to look up the icons  
#  if os.path.isfile(dirName) and dirName[-4:] in allowedIconType and icon in dirName:
   # return dirName
  #if os.path.isdir(dirName):
 #   for entry in sorted(os.listdir(dirName), reverse=True):
#      if os.path.isdir(dirName+entry):
     #   discovered = discoverIcon(dirName+entry+os.sep, icon)
    #  else:
   #     discovered = discoverIcon(dirName+entry, icon)
  #    if discovered is not None:
 #       return discovered
#  return None

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
              if desktopEntry:
                entry[Constants.EXEC]=line.split("=")[1][:-1]
                if "%" in entry[Constants.EXEC]:
                  entry[Constants.EXEC] = entry[Constants.EXEC][:entry[Constants.EXEC].find("%")]
                entry[Constants.EXEC] = getFullExecPath(entry[Constants.EXEC])
              else:
                sideCall[Constants.EXEC]=line.split("=")[1][:-1]
                if "%" in sideCall[Constants.EXEC]:
                  sideCall[Constants.EXEC] = sideCall[Constants.EXEC][:sideCall[Constants.EXEC].find("%")]
            elif line.startswith("Name"):
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
              #print line
              #print categories
          if Constants.ICON in entry:
            entry[Constants.ICON]=getBestIcon(entry[Constants.ICON])
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
#  print result
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
  #print parent

def addFolder(entry, name, parent):
  entry[Constants.TYPE] = Constants.TYPE_FOLDER
  parent[name] = entry

if (__name__ == "__main__"):
  xbmc.log("version %s started" % ADDON_VERSION)
  ADDON.openSettings()
  xbmc.log('finished')

