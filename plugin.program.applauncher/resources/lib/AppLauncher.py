# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import sys
import subprocess
import platform
if (__name__ == "__main__"):
  #print sys.argv[1:-1]
  subprocess.call(sys.argv[1:-1])
  #print sys.argv[-1:]
  if platform.system() == "Linux":
    subprocess.Popen("kodi")
  else:
    subprocess.Popen(sys.argv[-1:])

