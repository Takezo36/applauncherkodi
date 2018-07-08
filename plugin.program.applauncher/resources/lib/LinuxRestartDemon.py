# -*- coding: utf-8 -*-

# Copyright (C) 2018 - Benjamin Hebgen
# This program is Free Software see LICENSE file for details

import sys
import subprocess
import platform
if (__name__ == "__main__"):
  #print sys.argv[1:-1]
  subprocess.call(sys.argv[1:])
  subprocess.Popen("kodi")

