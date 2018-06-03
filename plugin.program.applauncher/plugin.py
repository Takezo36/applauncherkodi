# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen <mail>
# This program is Free Software see LICENSE file for details

import os
import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import simplejson as json
import resources.lib.AppLister as AppLister
import resources.lib.Constants as Constants
import resources.lib.AppRunner as AppRunner
import subprocess
import urllib
from distutils.util import strtobool
try:
   import StorageServer
except:
   import storageserverdummy as StorageServer


ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_ID       = ADDON.getAddonInfo('id')
ADDON_USER_DATA_FOLDER = xbmc.translatePath("special://profile/addon_data/"+ADDON_ID)
APP_LAUNCHER = xbmc.translatePath("special://home")+ "addons" + os.sep + ADDON_ID + os.sep + "resources" + os.sep + "lib" + os.sep + "AppLauncher.py"
ADDON_STORAGE_FILE = ADDON_USER_DATA_FOLDER + os.sep + "store.json"
ACTION = "action"
ACTION_SHOW_DIR = "showdir"
ACTION_ADD_CUSTOM_VARIANT = "addcustomvariant"
ACTION_ADD_CUSTOM_ENTRY = "addcustomentry"
ACTION_ADD_START_TO_CUSTOM = "addtostart"
ACTION_REMOVE_FROM_START = "removetostart"
ACTION_REMOVE_FROM_CUSTOMS = "removefromcustoms"
ACTION_ADD_CUSTOM_FOLDER = "addcustomfolder"
ACTION_SET_CUSTOM_ICON = "setcustomicon"
ACTION_SET_CUSTOM_BACKDROP = "setcustombackdrop"
ACTION_MOVE_TO_FOLDER = "movetofolder"
ACTION_EXEC = "exec"
FORCE_REFRESH = "forcerefresh"
CUSTOM_ENTRIES = "custom"
CUSTOM_ARTS = "arts"
DIR = "dir"
IS_CUSTOM = "iscustom"
handle = -1
PLUGIN_ACTION = "Container.Update(plugin://plugin.program.applauncher?"
DIR_SEP = ")(/&%$"
CREATE_CUSTOM_ENTRY_STRING = "Create custom entry"
CREATE_CUSTOM_FOLDER_STRING = "Create custom folder"
CREATE_CUSTOM_VARIANT_STRING = "Create custom variant"
ADD_START_ENTRY_TO_CUSTOMS_STRING = "Add to custom entries"
REMOVE_CUSTOM_ENTRY_STRING = "Remove from custom entries"
MOVE_TO_FOLDER_STRING = "Move entry to folder"
FORCE_REFRESH_STRING = "Force refresh"
SET_CUSTOM_ICON_STRING = "Set custom icon"
SET_CUSTOM_BACKGROUND_STRING = "Set custom background"
ICON_TITLE_STRING = "Icon"
BACKGROUND_TITLE_STRING = "Background"
CHOSE_TITLE_STRING = "Select "

def addAddCustomEntryButton(handle, path):
  li = xbmcgui.ListItem(CREATE_CUSTOM_ENTRY_STRING)
  li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_ADD_CUSTOM_ENTRY+"&"+DIR+"="+urllib.quote(path))
  xbmcplugin.addDirectoryItem(handle, li.getPath(), li)
def addAddCustomFolderButton(handle, path):
  li = xbmcgui.ListItem(CREATE_CUSTOM_FOLDER_STRING)
  li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_ADD_CUSTOM_FOLDER+"&"+DIR+"="+urllib.quote(path))
  xbmcplugin.addDirectoryItem(handle, li.getPath(), li) 

def addForceRefreshButton(contextMenu, path, isCustom):
  #print PLUGIN_ACTION+ACTION+"="+ACTION_SHOW_DIR+"&"+DIR+"="+urllib.quote(path)+"&"+FORCE_REFRESH+"=1&"+IS_CUSTOM+"="+str(int(isCustom))+")"
  contextMenu.append((FORCE_REFRESH_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_SHOW_DIR+"&"+DIR+"="+urllib.quote(path)+"&"+FORCE_REFRESH+"=1&"+IS_CUSTOM+"="+str(int(isCustom))+")"))
  return contextMenu

def addSideCallEntries(contextMenu, sideCalls):
  for sideCall in sideCalls:
    contextMenu.append((sideCall[Constants.NAME], PLUGIN_ACTION+ACTION+"="+ACTION_EXEC+"&"+ACTION_EXEC+"="+sideCall[Constants.EXEC]+")"))
  return contextMenu

def addRemoveCustomFolder(contextMenu, path):
  contextMenu.append((MOVE_TO_FOLDER_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_MOVE_TO_FOLDER+"&"+DIR+"="+path+")"))
  return contextMenu

def addRemoveCustomEntry(contextMenu, path):
  contextMenu.append((REMOVE_CUSTOM_ENTRY_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_REMOVE_FROM_CUSTOMS+"&"+DIR+"="+path+")"))
  return contextMenu
def addAddStartToCustomEntries(contextMenu, path):
  contextMenu.append((ADD_START_ENTRY_TO_CUSTOMS_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_ADD_START_TO_CUSTOM+"&"+DIR+"="+path+")"))
  return contextMenu
def addCustomVariantEntry(contextMenu, path):
  contextMenu.append((CREATE_CUSTOM_VARIANT_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_ADD_CUSTOM_VARIANT+"&"+DIR+"="+path+")"))
  return contextMenu
def addSetCustomIconEntry(contextMenu, path):
  contextMenu.appen((SET_CUSTOM_ICON_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_SET_CUSTOM_ICON+"&"+DIR+"="+path+")"))
  return contextMenu
def addSetCustomBackgroundEntry(contextMenu, path):
  contextMenu.appen((SET_CUSTOM_BACKGROUND_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_SET_CUSTOM_BACKGROUND+"&"+DIR+"="+path+")"))
  return contextMenu

def createEntries(folderToShow = "", folderIsInCustoms = True):
  customeEntries = None
  startEntries = None
  folderToShow = urllib.unquote(folderToShow)
  isRoot = False
  if folderToShow == "":
    isRoot = True
  if folderIsInCustoms or isRoot:
    addCustomEntries(folderToShow, isRoot)
  if not folderIsInCustoms or folderToShow == "":
    if not strtobool(ADDON.getSetting("dontshowstart")):
      addStartEntries(folderToShow, isRoot)
  if folderIsInCustoms or isRoot:
    addAddCustomEntryButton(handle, folderToShow)
    #addAddCustomFolderButton(handle, folderToShow)
  xbmcplugin.endOfDirectory(handle, cacheToDisc=False)  

def getFolder(entries, folderToShow):
  if folderToShow == "":
    return entries
  for folder in folderToShow.split(DIR_SEP):
      entries = entries[folder]
  return entries

def addEntries(entries, folderToShow, isCustom, isRoot):
  for key in entries.keys():#sorted(entries, key=lambda k: k[Constants.NAME]):
    if key == Constants.TYPE or key == Constants.NAME:
      continue
    entry = entries[key]
    if entry[Constants.TYPE] == Constants.TYPE_APP:
      li = createAppEntry(entry, folderToShow+DIR_SEP+key, isCustom)
      xbmcplugin.addDirectoryItem(handle, li.getPath(), li)
    elif entry[Constants.TYPE] == Constants.TYPE_FOLDER:
      if not isRoot:
        folderLink = folderToShow + DIR_SEP + key
      else:
        folderLink = key
      kodiAction = "plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_SHOW_DIR+"&"+DIR+"="+urllib.quote(folderLink)+"&"+IS_CUSTOM+"="+str(int(isCustom))
      li = createFolder(key, kodiAction, folderLink, isCustom)
      xbmcplugin.addDirectoryItem(handle, li.getPath(), li, isFolder=True)
  

def getAppList():
  apps = cache.get("apps")
  ##print "APPS LOOK: " + apps
  if not apps:
    apps = AppLister.getAppsWithIcons()
    cache.set("apps", json.dumps(apps))
    #apps2 = cache.get("apps")
    ##print "APPS LOOK: " + apps2
  else:
    apps = json.loads(apps)
  return apps
  
def addStartEntries(folderToShow, isRoot):
  entries = getAppList()
  #entries = AppLister.getAppsWithIcons()
  ##print "LOOOOOK"
  ##print entries
  entries = getFolder(entries, folderToShow)
  addEntries(entries, folderToShow, False, isRoot)



def createFolder(name, target, path, isCustom):
  ##print target
  li = xbmcgui.ListItem(name)
  li.setPath(path=target)
  #li.setIsFolder(True)
  contextMenu = []
  addBaseContextMenu(contextMenu, path, isCustom, True)
  li.addContextMenuItems(contextMenu)
  return li

def addBaseContextMenu(contextMenu, path, isCustom, isFolder):
  if isCustom:
    if not isFolder:
      addRemoveCustomEntry(contextMenu, path)
  else:
    if not isFolder:
      addCustomVariantEntry(contextMenu, path)
      addAddStartToCustomEntries(contextMenu, path)
      addSetCustomIconEntry(contextMenu, path)
      addSetCustomBackgroundEntry(contextMenu, path)

  i = path.rfind(DIR_SEP)
  if i != 0:
    refreshPath = path[:i]
  else:
    refreshPath = ""
  if refreshPath.find(DIR_SEP) == -1:
    refreshPath = ""
  addForceRefreshButton(contextMenu, refreshPath, isCustom)

def createAppEntry(entry, addToStartPath, isCustom = False):
  li = xbmcgui.ListItem(entry[Constants.NAME])
  arts = loadData()[CUSTOM_ARTS]
  try:
    for key in arts.split(DIR_SEP):
      arts = arts[key]
  except:
    arts = None

  if arts and Constants.ICON in arts.keys():
    icon = arts[Constants.ICON]
  elif Constants.ICON in entry:
    icon = entry[Constants.ICON]
  else:
    icon = ""

  if arts and Constants.BACKGROUND in arts.keys():
    background = arts[Constants.BACKGROUND]
  elif Constants.BACKGROUND in entry:
    background = entry[Constants.BACKGROUND]
  else:
    background = icon
  li.setArt({'icon' : icon,
             'thumb':icon,
             'poster':icon,
             'banner':icon,
             'fanart':background,
             'clearart':icon,
             'clearlogo':icon,
             'landscape':icon})
  contextMenu = []
  if Constants.SIDECALLS in entry.keys():
    addSideCallEntries(contextMenu, entry[Constants.SIDECALLS])
  addBaseContextMenu(contextMenu, addToStartPath, isCustom, False)
  li.addContextMenuItems(contextMenu)
  li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_EXEC+"&"+ACTION_EXEC+"="+entry[Constants.EXEC])
  return li
def addStartEntryAsCustom(path):
  entry = getAppList()
  for key in path.split(DIR_SEP):
    entry = entry[key]
  storeEntry(entry[Constants.EXEC], entry[Constants.ICON], entry[Constants.NAME])

def addCustomEntry(exe="/", icon="/", background="/", name="", path=""):
  dialog = xbmcgui.Dialog()
  fileName = dialog.browseSingle(1, 'Select Execution File', 'files', '', False, False, exe)
  if fileName == "":
    return
  params = dialog.input("Add parameters")
  icon = dialog.browseSingle(1, 'Select Icon', 'files', '', False, False, icon)
  if icon == "":
    return
  background = dialog.browseSingle(1, 'Select Background', 'files', '', False, False, icon)
  if background == "":
    return
  name = dialog.input("Set name", name)
  if name == "":
    return
  storeEntry(fileName + " " + params, icon, background, name)

def setCustomArtDialog(path, isBackground):
  dialog = xbmcgui.Dialog()
  entry = getApplist()
  for key in path.split(DIR_SEP):
    entry = entry[key]
  default = "/"
  if isBackground:
    entryKey = Constants.BACKGROUND
    title = CHOSE_TITLE_STRING + BACKGROUND_TITLE_STRING
    if Constants.BACKGROUND in entry.keys():
      default = entry[Constants.BACKGROUND]
  else:
    entryKey = Constants.ICON
    title = CHOSE_TITLE_STRING + ICON_TITLE_STRING
    if Constants.ICON in entry.keys():
      default = entry[Constants.ICON]

  art = dialog.browseSingle(1, title, 'files', '', False, False, default)
  if art == "":
    return
  data = loadData()
  storepoint = data[CUSTOM_ARTS]
  for key in path.split(DIR_SEP):
    if key in storepoint.keys():
      storepoint = storepoint[key]
    else:
      storepoint[key] = {}
      storepoint = storepoint[key]
  storepoint[entryKey] = art
  writeData(data)

def storeEntry(exe="/", icon="/", background="/", name="", path=""):
  entry = {}
  entry[Constants.NAME] = name
  entry[Constants.EXEC] = exe
  entry[Constants.ICON] = icon
  entry[Constants.BACKGROUND] = background
  entry[Constants.TYPE] = Constants.TYPE_APP
#  entry[REMOVE_START] = path+name
  data = loadData()
  storepoint = data[CUSTOM_ENTRIES]
  if path != "":
    for key in path.split(DIR_SEP):
      if key in storepoint.keys() and storepoint[key][Constants.TYPE] == Constants.TYPE_FOLDER:
        storepoint = storepoint[key]
      else:
        storepoint[key] = {}
        storepoint[key][Constants.TYPE] = Constants.TYPE_FOLDER
        storepoint[key][Constants.NAME] = key
        storepoint = storepoint[key]
  storepoint[name] = entry
  writeData(data)

def addCustomVariant(path):
  entry = getAppList()
  for key in path.split(DIR_SEP):
    entry = entry[key]
  addCustomEntry(entry[Constants.EXEC], entry[Constants.ICON], entry[Constants.BACKGROUND], entry[Constants.NAME], path)

def executeApp(command):
  killKodi = strtobool(ADDON.getSetting("killkodi"))
  minimize = strtobool(ADDON.getSetting("minimize"))
  killAfterAppClose = strtobool(ADDON.getSetting("killafterappclose"))    
  AppRunner.executeApp(command, killKodi, minimize, killAfterAppClose)
    

def addSortingMethods():
  xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_LABEL)

def addCustomEntries(folderToShow, isRoot):
  data = loadData()
  if data[CUSTOM_ENTRIES]:
    entries = getFolder(data[CUSTOM_ENTRIES], folderToShow)
    addEntries(entries, folderToShow, True, isRoot)
  
def writeData(data):
  with open(ADDON_STORAGE_FILE, 'w') as fp:  
    json.dump(data, fp)

def loadData():
  if os.path.isfile(ADDON_STORAGE_FILE):
    with open(ADDON_STORAGE_FILE, 'r') as fp:
      data = json.load(fp)
  if not "data" in locals():
    data = {}
  if CUSTOM_ENTRIES not in data:
    data[CUSTOM_ENTRIES] = {}
  if CUSTOM_ARTS not in data:
    data[CUSTOM_ARTS] = {}
  return data

def removeFromCustoms(path):
  data = loadData()
#  #print "path " + path
  if path[0] == DIR_SEP:
    path = path[1:]
 # #print "path " + path
  deleteName = path.split(DIR_SEP)[-1]
  entries = data[CUSTOM_ENTRIES]
  ##print entries
  ##print "deletename " + str(deleteName)
  for key in path.split(DIR_SEP):
    #print "key " + key
    if key == deleteName:
   #   #print "removing"
      entries.pop(key, None)
    else:
      entries = entries[key]
  ##print entries
  ##print data
  writeData(data)
def addCustomFolder():
  pass
def moveItemToFolder(path):
  pass

def parseArgs():
  global handle
  handle = int(sys.argv[1])
  params = {}
  args = sys.argv[2][1:]
  if args:
    for argPair in args.split("&"):
      temp = argPair.split("=")
      params[temp[0]] = temp[1]
  return params
if (__name__ == "__main__"):
  params = parseArgs()
  addSortingMethods()
  xbmc.executebuiltin("Container.SetViewMode(icons)")
  cache = StorageServer.StorageServer(ADDON_ID, 24)
  if FORCE_REFRESH in params:
    ##print "force refresh"
    cache.delete("apps")
  if not os.path.exists(ADDON_USER_DATA_FOLDER):
    os.makedirs(ADDON_USER_DATA_FOLDER)
  if ACTION in params:
    action = params[ACTION]
    if action == ACTION_EXEC:
      executeApp(params[ACTION_EXEC])
    elif action == ACTION_ADD_START_TO_CUSTOM:
      addStartEntryAsCustom(params[DIR])      
    elif action == ACTION_ADD_CUSTOM_ENTRY:
      addCustomEntry(path = params[DIR])
    elif action == ACTION_ADD_CUSTOM_VARIANT:
      addCustomVariant(params[DIR])
    elif action == ACTION_SET_CUSTOM_ICON:
     setCustomArtDialog(params[DIR], False)
    elif action == ACTION_SET_CUSTOM_BACKGROUND:
     setCustomArtDialog(params[DIR], True)
    elif action == ACTION_REMOVE_FROM_CUSTOMS:
      removeFromCustoms(params[DIR])
    elif action == ACTION_SHOW_DIR:
      createEntries(params[DIR], strtobool(params[IS_CUSTOM]))
     # addSortingMethods()
    elif action == ACTION_ADD_CUSTOM_FOLDER:
      addCustomFolder()
    elif action == ACTION_MOVE_TO_FOLDER:
      moveItemToFolder(params[DIR])
      
  else:
    createEntries()
    
    xbmc.log('finished')

