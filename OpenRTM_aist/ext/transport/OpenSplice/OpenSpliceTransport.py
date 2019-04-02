#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file OpenSpliceTransport.py
# @brief OpenSplice Transport class
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
import OpenSpliceInPort
import OpenSpliceOutPort
import OpenSpliceSerializer



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
def OpenSpliceTransportInit(mgr):
  OpenSpliceInPort.OpenSpliceInPortInit()
  OpenSpliceOutPort.OpenSpliceOutPortInit()
  OpenSpliceSerializer.OpenSpliceSerializerInit()

