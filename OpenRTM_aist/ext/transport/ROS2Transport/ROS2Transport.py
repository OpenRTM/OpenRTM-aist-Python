#!/usr/bin/env python3
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
from ROS2TopicManager import ROS2TopicManager


##
# @if jp
# @class ManagerActionListener
# @brief ROS2TopicManagerの終了処理を行うマネージャアクションリスナ
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
        ROS2TopicManager.shutdown_global()

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
def ROS2TransportInit(mgr):
    ROS2InPort.ROS2InPortInit()
    ROS2OutPort.ROS2OutPortInit()
    ROS2Serializer.ROS2SerializerInit()

    mgr.addManagerActionListener(ManagerActionListener())
