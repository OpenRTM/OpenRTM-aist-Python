#!/usr/bin/env python3
# -*- Python -*-

##
# @file rtcd.py
# @brief RT component server daemon
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2003-2020
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id: $

import sys,os

import OpenRTM_aist

def main():
  manager = OpenRTM_aist.Manager.init(sys.argv)

  manager.activateManager()

  manager.runManager()

  return

if __name__ == "__main__":
  main()
