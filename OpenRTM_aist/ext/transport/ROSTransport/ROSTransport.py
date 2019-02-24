#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file ROSTransport.py
# @brief ROS Transport class
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
import ROSInPort
import ROSOutPort
import ROSSerializer



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
def ROSTransportInit(mgr):
  ROSInPort.ROSInPortInit()
  ROSOutPort.ROSOutPortInit()
  ROSSerializer.ROSSerializerInit()

