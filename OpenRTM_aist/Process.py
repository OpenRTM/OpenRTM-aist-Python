#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# \file Process.py
# \brief Process handling functions
# \author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2010
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import os
import sys
import traceback
import subprocess
import shlex

##
# @if jp
# @brief プロセスを起動する
# @else
# @brief Launching a process
# @endif
#
# int launch_shell(std::string command)


def launch_shell(command):
    #args = command.split(" ")
    args = shlex.split(command, " ")

    if os.name == "nt":
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        subproc_args = {'stdin': None,
                        'stdout': None,
                        'stderr': None,
                        'cwd': None,
                        'close_fds': False,
                        'creationflags': CREATE_NEW_PROCESS_GROUP}
    else:
        subproc_args = {'stdin': None,
                        'stdout': None,
                        'stderr': None,
                        'cwd': None,
                        'close_fds': False,
                        'preexec_fn': os.setsid}

    try:
        subprocess.Popen(args, **subproc_args)
    except OSError:
        # fork failed
        if sys.version_info[0:3] >= (2, 4, 0):
            print(traceback.format_exc())
        else:
            _exc_list = traceback.format_exception(*sys.exc_info())
            print("".join(_exc_list))

        return -1
    return 0


##
# @if jp
# @brief プロセスを複製する
# @else
# @brief fork process
# @endif
#
# int fork()
def fork():
    if os.name == "nt":
        return -1
    else:
        pid = os.fork()
        return pid

##
# @if jp
# @brief プロセスを起動し出力を取得する
# @else
# @brief fork process
# @endif
#
# string popen(string command)


def popen(command):
    args = shlex.split(command, " ")
    sp = subprocess.Popen(args, stdout=subprocess.PIPE)
    return sp.communicate()[0].decode("utf-8")
