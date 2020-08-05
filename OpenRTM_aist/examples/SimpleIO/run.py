#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Python -*-

#
# @file run.py
# @brief ExtTrigger example startup script
# @date $Date: 2007/10/26 $
#
# Copyright (c) 2003-2007 Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#          Task-intelligence Research Group,
#          Intelligent System Research Institute,
#          National Institute of Industrial Science (AIST), Japan
#          All rights reserved.
#

from __future__ import print_function
import sys
import os
import platform
import time
import subprocess

nsport = "2809"
sysinfo = platform.uname()
hostname = sysinfo[1]
plat = sys.platform


def main():
    if plat == "win32":
        subprocess.call('cd \"%RTM_ROOT%\\bin\\\" & start \"\" rtm-naming.bat',
                        shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(5)
        subprocess.call("start python ConsoleIn.py".split(
            " "), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call("start python Consoleout.py".split(
            " "), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.call("python Connector.py".split(" "), shell=True)

    else:
        p = subprocess.Popen("which xterm", shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        term, stderr = p.communicate()
        status = p.returncode
        term = term.decode('utf-8')
        term = term.replace("\n", "")
        term += " -e"
        if status != 0:
            p = subprocess.Popen("which kterm", shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            term, stderr = p.communicate()
            status = p.returncode
            term = term.decode('utf-8')
            term = term.replace("\n", "")
            term += " -e"

        if status != 0:
            p = subprocess.Popen("which uxterm", shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            term, stderr = p.communicate()
            status = p.returncode
            term = term.decode('utf-8')
            term = term.replace("\n", "")
            term += " -e"

        if status != 0:
            p = subprocess.Popen("which gnome-terminal", shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            term, stderr = p.communicate()
            status = p.returncode
            term = term.decode('utf-8')
            term = term.replace("\n", "")
            term += " -x"

        if status != 0:
            print("No terminal program (kterm/xterm/gnome-terminal) exists.")
            sys.exit(0)

        """
    path = None
    for p in sys.path:
      if os.path.exists(os.path.join(p,"OpenRTM_aist")):
        path = os.path.join(p,"OpenRTM_aist","utils","rtm-naming")
        break
    if path is None:
      print("rtm-naming directory not exist.")
      sys.exit(0)
    os.system('python %s/rtm-naming.py &'%path)
    """
        cmd = 'rtm-naming&'
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        cmd = '%s python ConsoleIn.py&' % term
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        cmd = '%s python ConsoleOut.py&' % term
        subprocess.call(cmd, shell=True, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
        time.sleep(3)
        subprocess.call("python Connector.py", shell=True)

    return


if __name__ == "__main__":
    main()
