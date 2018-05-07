# -*- coding: utf8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import platform

myOS = platform.system()
print myOS
if myOS == "Linux":
  import AppListerLinux as MyAppLister
elif myOS == "Windows":
  import AppListerWindows as MyAppLister
elif myOS == "Darwin":
  import AppListerOSX as MyAppLister
else:
  import AppListerLinux as MyAppLister

def getAppsWithIcons(additionalDir=""):
  return MyAppLister.getAppsWithIcons()

