# -*- coding: utf-8 -*-

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
ADDON_ID = ADDON.getAddonInfo('id')
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
ACTION_SET_CUSTOM_BACKGROUND = "setcustombackground"
ACTION_UNSET_CUSTOM_ICON = "unsetcustomicon"
ACTION_UNSET_CUSTOM_BACKGROUND = "unsetcustombackground"
ACTION_MOVE_TO_FOLDER = "movetofolder"
ACTION_EXEC = "exec"
ACTION_FORCE_REFRESH = "forcerefresh"
ARGS_PARAM = "args"
CUSTOM_ENTRIES = "custom"
CUSTOM_ARTS = "arts"
DIR = "dir"
IS_CUSTOM = "iscustom"
handle = -1
skindir = xbmc.getSkinDir()
PLUGIN_ACTION = "Container.Update(plugin://plugin.program.applauncher?"
DIR_SEP = ADDON.getSetting("dirsep")
CACHE_TIME = int(ADDON.getSetting("cachetime"))
if(skindir.upper() == "SKIN.XONE"):
  CREATE_CUSTOM_ENTRY_STRING = ADDON.getLocalizedString(35000)
else:
  CREATE_CUSTOM_ENTRY_STRING = ADDON.getLocalizedString(35000)
CREATE_CUSTOM_FOLDER_STRING = ADDON.getLocalizedString(35001)
CREATE_CUSTOM_VARIANT_STRING = ADDON.getLocalizedString(35002)
ADD_START_ENTRY_TO_CUSTOMS_STRING = ADDON.getLocalizedString(35003)
REMOVE_CUSTOM_ENTRY_STRING = ADDON.getLocalizedString(35004)
MOVE_TO_FOLDER_STRING = ADDON.getLocalizedString(35005)
FORCE_REFRESH_STRING = ADDON.getLocalizedString(35006)
SET_CUSTOM_ICON_STRING = ADDON.getLocalizedString(35007)
SET_CUSTOM_BACKGROUND_STRING = ADDON.getLocalizedString(35008)
UNSET_CUSTOM_ICON_STRING = ADDON.getLocalizedString(35009)
UNSET_CUSTOM_BACKGROUND_STRING = ADDON.getLocalizedString(35010)
ICON_TITLE_STRING = ADDON.getLocalizedString(35011)
BACKGROUND_TITLE_STRING = ADDON.getLocalizedString(35012)
SELECT_EXECUTION_FILE_STRING = ADDON.getLocalizedString(35013)
ADD_PARAMETERS_STRING = ADDON.getLocalizedString(35014)
SET_NAME_STRING = ADDON.getLocalizedString(35015)
ADD_FOLDER_STRING = ADDON.getLocalizedString(35016)
MOVE_ENTRY_TO_FOLDER_STRING = ADDON.getLocalizedString(35017)
HEADER_FAIL_CUSTOM_ENTRY_STRING = ADDON.getLocalizedString(35018)
CUSTOM_FOLDER_CREATION_FAIL_STRING = ADDON.getLocalizedString(35019)
def addAddCustomEntryButton(handle, path):
  li = xbmcgui.ListItem(CREATE_CUSTOM_ENTRY_STRING)
  li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_ADD_CUSTOM_ENTRY+"&"+DIR+"="+urllib.quote(path))
  xbmcplugin.addDirectoryItem(handle, li.getPath(), li)
def addAddCustomFolderButton(handle, path):
  li = xbmcgui.ListItem(CREATE_CUSTOM_FOLDER_STRING)
  li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_ADD_CUSTOM_FOLDER+"&"+DIR+"="+urllib.quote(path))
  xbmcplugin.addDirectoryItem(handle, li.getPath(), li) 

def addForceRefreshButton(contextMenu):
  contextMenu.append((FORCE_REFRESH_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_FORCE_REFRESH+")"))
  return contextMenu

def addSideCallEntries(contextMenu, sideCalls):
  for sideCall in sideCalls:
    contextMenu.append((sideCall[Constants.NAME], PLUGIN_ACTION+ACTION+"="+ACTION_EXEC+"&"+ACTION_EXEC+"="+sideCall[Constants.EXEC]+"&"+ARGS_PARAM+"="+",".join(sideCall[Constants.ARGS])+")"))
  return contextMenu

def addMoveEntryToFolderEntry(contextMenu, path):
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
def addUnsetCustomIconEntry(contextMenu, path):
  contextMenu.append((UNSET_CUSTOM_ICON_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_UNSET_CUSTOM_ICON+"&"+DIR+"="+path+")"))
  return contextMenu
def addUnsetCustomBackgroundEntry(contextMenu, path):
  contextMenu.append((UNSET_CUSTOM_BACKGROUND_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_UNSET_CUSTOM_BACKGROUND+"&"+DIR+"="+path+")"))
  return contextMenu
def addSetCustomIconEntry(contextMenu, path, isCustom):
  contextMenu.append((SET_CUSTOM_ICON_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_SET_CUSTOM_ICON+"&"+DIR+"="+path+"&"+IS_CUSTOM+"="+str(int(isCustom))+")"))
  return contextMenu
def addSetCustomBackgroundEntry(contextMenu, path, isCustom):
  contextMenu.append((SET_CUSTOM_BACKGROUND_STRING, PLUGIN_ACTION+ACTION+"="+ACTION_SET_CUSTOM_BACKGROUND+"&"+DIR+"="+path+"&"+IS_CUSTOM+"="+str(int(isCustom))+")"))
  return contextMenu

def createEntries(folderToShow = "", folderIsInCustoms = True):
  customeEntries = None
  startEntries = None
  isRoot = False
  if folderToShow == "":
    isRoot = True
  if folderIsInCustoms or isRoot:
    addCustomEntries(folderToShow, isRoot)
  if not folderIsInCustoms or isRoot:
    if not strtobool(ADDON.getSetting("dontshowstart")):
      if strtobool(ADDON.getSetting("flattenapps")):
        folderToShow = "all apps"
        isRoot = False
      addStartEntries(folderToShow, isRoot)
  if folderIsInCustoms or isRoot:
    addAddCustomEntryButton(handle, folderToShow)
  if not strtobool(ADDON.getSetting("dontshowcustomfolders")):
    addAddCustomFolderButton(handle, folderToShow)
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
    if not isRoot:
      path = folderToShow + DIR_SEP + key
    else:
      path = key
    if entry[Constants.TYPE] == Constants.TYPE_APP:
      li = createAppEntry(entry, path, isCustom)
      xbmcplugin.addDirectoryItem(handle, li.getPath(), li)
    elif entry[Constants.TYPE] == Constants.TYPE_FOLDER:
      kodiAction = "plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_SHOW_DIR+"&"+DIR+"="+urllib.quote(path)+"&"+IS_CUSTOM+"="+str(int(isCustom))
      li = createFolder(key, kodiAction, path, isCustom)
      xbmcplugin.addDirectoryItem(handle, li.getPath(), li, isFolder=True)
  

def getAppList():
  apps = cache.get("apps")
  if not apps:
    apps = AppLister.getAppsWithIcons()
    cache.set("apps", json.dumps(apps))
  else:
    apps = json.loads(apps)
  return apps
  
def addStartEntries(folderToShow, isRoot):
  entries = getAppList()
  entries = getFolder(entries, folderToShow)
  addEntries(entries, folderToShow, False, isRoot)



def createFolder(name, target, path, isCustom):
  li = xbmcgui.ListItem(name)
  li.setPath(path=target)
  contextMenu = []
  addBaseContextMenu(contextMenu, path, isCustom, True)
  li.addContextMenuItems(contextMenu)
  return li

def addBaseContextMenu(contextMenu, path, isCustom, isFolder, hasCustomIcon=True, hasCustomBackground=True):
  if isCustom:
    if not isFolder:
      addMoveEntryToFolderEntry(contextMenu, path)
    addRemoveCustomEntry(contextMenu, path)
  else:
    if not isFolder:
      addCustomVariantEntry(contextMenu, path)
      addAddStartToCustomEntries(contextMenu, path)
  if not isFolder:
    if hasCustomIcon:
      addUnsetCustomIconEntry(contextMenu, path)
    else:
      addSetCustomIconEntry(contextMenu, path, isCustom)
    if hasCustomBackground:
      addUnsetCustomBackgroundEntry(contextMenu, path)
    else:
      addSetCustomBackgroundEntry(contextMenu, path, isCustom)


  addForceRefreshButton(contextMenu)

def createAppEntry(entry, addToStartPath, isCustom = False):
  li = xbmcgui.ListItem(entry[Constants.NAME])
  arts = loadData()[CUSTOM_ARTS]
  try:
    for key in addToStartPath.split(DIR_SEP):
      arts = arts[key]
  except:
    arts = None
  hasCustomIcon = False
  hasCustomBackground = False
  if arts and Constants.ICON in arts.keys():
    icon = arts[Constants.ICON]
    hasCustomIcon = True
  elif Constants.ICON in entry:
    icon = entry[Constants.ICON]
  else:
    icon = ""
  #this is a stupid bugfix for a strange serialization bug in powershell
  if type(icon) is list:
    icon = icon[1]
  if arts and Constants.BACKGROUND in arts.keys():
    background = arts[Constants.BACKGROUND]
    hasCustomBackground = True
  elif Constants.BACKGROUND in entry:
    background = entry[Constants.BACKGROUND]
  else:
    background = icon
  try:
    li.setArt({'icon' : icon,
               'thumb':icon,
               'poster':icon,
               'banner':icon,
               'fanart':background,
               'clearart':icon,
               'clearlogo':icon,
               'landscape':icon})
  except:
    xbmc.log("Failed to load icon " + str(icon), xbmc.LOGDEBUG)
  contextMenu = []
  if Constants.SIDECALLS in entry.keys():
    addSideCallEntries(contextMenu, entry[Constants.SIDECALLS])
  addBaseContextMenu(contextMenu, addToStartPath, isCustom, False, hasCustomIcon, hasCustomBackground)
  li.addContextMenuItems(contextMenu)
  try:
    li.setPath(path="plugin://plugin.program.applauncher?"+ACTION+"="+ACTION_EXEC+"&"+ACTION_EXEC+"="+entry[Constants.EXEC]+"&"+ARGS_PARAM+"="+urllib.quote(",".join(entry[Constants.ARGS])))
  except:
    xbmc.log("Failed to load entry", xbmc.LOGDEBUG)
  return li
def addStartEntryAsCustom(path):
  entry = getAppList()
  for key in path.split(DIR_SEP):
    entry = entry[key]
  storeEntry(entry[Constants.EXEC], entry[Constants.ARGS], entry[Constants.ICON], "", entry[Constants.NAME])

def addCustomEntry(exe="/", args="", icon="/", background="/", name="", path=""):
  dialog = xbmcgui.Dialog()

  fileName = dialog.browseSingle(1, SELECT_EXECUTION_FILE_STRING, 'files', '', False, False, exe)
  if fileName == "":
    return
  params = dialog.input(ADD_PARAMETERS_STRING, " ".join(args)).split(" ")
  if type(icon) is list:
    icon = icon[1]
  icon = dialog.browseSingle(1, ICON_TITLE_STRING, 'files', '', False, False, icon)
  if icon == "":
    return
  if type(background) is list:
    background = background[1]
  background = dialog.browseSingle(1, BACKGROUND_TITLE_STRING, 'files', '', False, False, background)
  if background == "":
    return
  name = dialog.input(SET_NAME_STRING, name)
  if name == "":
    return
  storeEntry(fileName, params, icon, background, name, path)

def unsetCustomArtDialog(path, isBackground):
  if isBackground:
    entryKey = Constants.BACKGROUND
  else:
    entryKey = Constants.ICON
  data = loadData()
  storepoint = data[CUSTOM_ARTS]
  for key in path.split(DIR_SEP):
    storepoint = storepoint[key]
  del storepoint[entryKey]
  writeData(data)

def setCustomArtDialog(path, isBackground, isCustom):
  dialog = xbmcgui.Dialog()
  data = loadData()
  if isCustom:
    entry = data[CUSTOM_ENTRIES]
  else:
    entry = getAppList()
  
  for key in path.split(DIR_SEP):
    entry = entry[key]
  default = "/"
  if isBackground:
    entryKey = Constants.BACKGROUND
    title = BACKGROUND_TITLE_STRING
    if Constants.BACKGROUND in entry.keys():
      default = entry[Constants.BACKGROUND]
  else:
    entryKey = Constants.ICON
    title = ICON_TITLE_STRING
    if Constants.ICON in entry.keys():
      default = entry[Constants.ICON]

  art = dialog.browseSingle(1, title, 'files', '', False, False, default)
  if art == "":
    return

  storepoint = data[CUSTOM_ARTS]
  for key in path.split(DIR_SEP):
    if key in storepoint.keys():
      storepoint = storepoint[key]
    else:
      storepoint[key] = {}
      storepoint = storepoint[key]
  storepoint[entryKey] = art
  writeData(data)

def storeEntry(exe="/", args="", icon="/", background="/", name="", path=""):
  entry = {}
  entry[Constants.NAME] = name
  entry[Constants.EXEC] = exe
  entry[Constants.ARGS] = args
  entry[Constants.ICON] = icon
  entry[Constants.BACKGROUND] = background
  entry[Constants.TYPE] = Constants.TYPE_APP
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
  if not Constants.BACKGROUND in entry.keys():
    entry[Constants.BACKGROUND] = entry[Constants.ICON]
  addCustomEntry(entry[Constants.EXEC], entry[Constants.ARGS], entry[Constants.ICON], entry[Constants.BACKGROUND], entry[Constants.NAME], "")

def executeApp(command, args):
  killKodi = strtobool(ADDON.getSetting("killkodi"))
  minimize = strtobool(ADDON.getSetting("minimize"))
  AppRunner.executeApp(command, args, killKodi, minimize)
    

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
  deleteName = path.split(DIR_SEP)[-1]
  entries = data[CUSTOM_ENTRIES]
  for key in path.split(DIR_SEP):
    if key == deleteName:
      entries.pop(key, None)
    else:
      entries = entries[key]
  writeData(data)
def addCustomFolder(path):
  dialog = xbmcgui.Dialog()
  userInput = dialog.input(ADD_FOLDER_STRING)
  if userInput == "":
    return
  userPath = userInput.split(DIR_SEP)

  if userPath[0] == "":
    #add from root
    createPath = userPath[1:]
  else:
    if path == "":
      createPath = userPath
    else:
      createPath = path.split(DIR_SEP) + userPath
  data = loadData()
  getCustomFolder(data, createPath)
  writeData(data)



def getCustomFolder(data, createPath):
  customEntries = data[CUSTOM_ENTRIES]
  for folder in createPath:
    if folder in customEntries.keys():
      if not customEntries[folder][Constants.TYPE] == Constants.TYPE_FOLDER:
        dialog.ok(HEADER_FAIL_CUSTOM_ENTRY_STRING, CUSTOM_FOLDER_CREATION_FAIL_STRING)
        return None
    else:
      customEntries[folder] = {}
      customEntries[folder][Constants.TYPE] = Constants.TYPE_FOLDER
      customEntries[folder][Constants.NAME] = folder
    customEntries = customEntries[folder]
  return customEntries

def moveItemToFolder(path):
  dialog = xbmcgui.Dialog()
  newPath = dialog.input(MOVE_ENTRY_TO_FOLDER_STRING).split(DIR_SEP)
  temp = path.split(DIR_SEP)
  entry = temp[-1]
  entryPath = temp[:-1]
  
  if newPath == None:
    return
  if newPath[0] == "":
    #add from root
    newPath = newPath[1:]
  else:
    newPath = entryPath + newPath
  data = loadData()
  folder = getCustomFolder(data, newPath)
  originalPath = data[CUSTOM_ENTRIES]
  for d in entryPath:
    originalPath = originalPath[d]
  folder[entry] = originalPath[entry]
  del originalPath[entry]
  writeData(data)

def parseArgs():
  global handle
  handle = int(sys.argv[1])
  params = {}
  args = sys.argv[2][1:]
  if args:
    for argPair in args.split("&"):
      temp = argPair.split("=")
      params[temp[0]] = urllib.unquote(temp[1])
  return params
if (__name__ == "__main__"):
  params = parseArgs()
  addSortingMethods()
  xbmc.executebuiltin("Container.SetViewMode(Icons)")
  cache = StorageServer.StorageServer(ADDON_ID+"v2", CACHE_TIME)
  if not os.path.exists(ADDON_USER_DATA_FOLDER):
    os.makedirs(ADDON_USER_DATA_FOLDER)
  if ACTION in params:
    action = params[ACTION]
    if action == ACTION_EXEC:
      executeApp(params[ACTION_EXEC],params[ARGS_PARAM])
    elif action == ACTION_ADD_START_TO_CUSTOM:
      addStartEntryAsCustom(params[DIR])      
    elif action == ACTION_FORCE_REFRESH:
      cache.delete("apps")      
    elif action == ACTION_ADD_CUSTOM_ENTRY:
      addCustomEntry(path = params[DIR])
    elif action == ACTION_ADD_CUSTOM_VARIANT:
      addCustomVariant(params[DIR])
    elif action == ACTION_SET_CUSTOM_ICON:
      setCustomArtDialog(params[DIR], False, strtobool(params[IS_CUSTOM]))
    elif action == ACTION_SET_CUSTOM_BACKGROUND:
      setCustomArtDialog(params[DIR], True, strtobool(params[IS_CUSTOM]))
    elif action == ACTION_UNSET_CUSTOM_ICON:
      unsetCustomArtDialog(params[DIR], False)
    elif action == ACTION_UNSET_CUSTOM_BACKGROUND:
      unsetCustomArtDialog(params[DIR], True)
    elif action == ACTION_REMOVE_FROM_CUSTOMS:
      removeFromCustoms(params[DIR])
    elif action == ACTION_SHOW_DIR:
      createEntries(params[DIR], strtobool(params[IS_CUSTOM]))
    elif action == ACTION_ADD_CUSTOM_FOLDER:
      addCustomFolder(params[DIR])
    elif action == ACTION_MOVE_TO_FOLDER:
      moveItemToFolder(params[DIR])
      
  else:
    createEntries()
    
    xbmc.log('finished')

