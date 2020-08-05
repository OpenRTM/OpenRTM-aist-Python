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
import sys,os,platform
import time
import subprocess

nsport="2809"
sysinfo = platform.uname()
hostname= sysinfo[1]
plat=sys.platform

if plat == "win32":
    #os.system("rd /S /Q SimpleService")
    #os.system("rd /S /Q SimpleService__POA")
    #os.system("omniidl.exe -bpython MyService.idl")
    subprocess.call("start \"\" \"%RTM_ROOT%\\bin\\rtm-naming.bat\"", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    subprocess.call("start python MyServiceConsumer.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.call("start python MyServiceProvider.py", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    subprocess.call("python Connector.py", shell=True)

else:
    #os.system('rm -rf SimpleService*')
    #os.system('omniidl -bpython MyService.idl')
    p=subprocess.Popen("which xterm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    term, stderr = p.communicate()
    status = p.returncode
    term = term.replace("\n","")
    term += " -e"
    if status != 0:
      p=subprocess.Popen("which kterm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      term, stderr = p.communicate()
      status = p.returncode
      term = term.replace("\n","")
      term += " -e"

    if status != 0:
      p=subprocess.Popen("which uxterm", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      term, stderr = p.communicate()
      status = p.returncode
      term = term.replace("\n","")
      term += " -e"
      
    if status != 0:
      p=subprocess.Popen("which gnome-terminal", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      term, stderr = p.communicate()
      status = p.returncode
      term = term.replace("\n","")
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
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd = '%s python MyServiceConsumer.py &'%term
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd = '%s python MyServiceProvider.py &'%term
    subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(3)
    subprocess.call("python Connector.py", shell=True)
