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

import os
import shutil
import subprocess
import sys
import time


def main():
    components = ('SliderComp.py', 'TkMotorComp.py')
    if sys.platform == "win32":
        subprocess.Popen(
            [os.environ.get("COMSPEC", "cmd.exe"), "/c", "rtm-naming.bat"],
            cwd=os.path.join(os.environ["RTM_ROOT"], "bin"),
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        time.sleep(5)
        for component in components:
            subprocess.Popen([sys.executable, component], creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        terminal = None
        for name, option in (("xterm", "-e"), ("kterm", "-e"), ("uxterm", "-e"), ("gnome-terminal", "--")):
            executable = shutil.which(name)
            if executable:
                terminal = [executable, option]
                break
        if terminal is None:
            print("No terminal program (xterm/kterm/uxterm/gnome-terminal) exists.")
            return
        subprocess.Popen(["rtm-naming"])
        for component in components:
            subprocess.Popen([*terminal, sys.executable, component])
    subprocess.call([sys.executable, "Connector.py"])


if __name__ == "__main__":
    main()
