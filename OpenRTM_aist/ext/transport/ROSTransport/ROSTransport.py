#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
from ROSTopicManager import ROSTopicManager


##
# @if jp
# @class ManagerActionListener
# @brief ROSTopicManagerの終了処理を行うマネージャアクションリスナ
#
#
# @else
# @class ManagerActionListener
# @brief
#
#
# @endif
class ManagerActionListener(OpenRTM_aist.ManagerActionListener):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif
    def __init__(self):
        pass

    def preShutdown(self):
        pass
    ##
    # @if jp
    # @brief RTMマネージャ終了後にROSTopicManagerの終了処理を実行
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif

    def postShutdown(self):
        ROSTopicManager.shutdown_global()

    def preReinit(self):
        pass

    def postReinit(self):
        pass


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

    mgr.addManagerActionListener(ManagerActionListener())
