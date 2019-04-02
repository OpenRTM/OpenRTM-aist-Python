#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file ROS2Transport.py
# @brief ROS2 Transport class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist
import ROS2InPort
import ROS2OutPort
import ROS2Serializer



##
# @if jp
# @brief モジュール登録関数
#
#
# @else
# @brief 
#
#
# @endif
#
def ROS2TransportInit(mgr):
  ROS2InPort.ROS2InPortInit()
  ROS2OutPort.ROS2OutPortInit()
  ROS2Serializer.ROS2SerializerInit()

