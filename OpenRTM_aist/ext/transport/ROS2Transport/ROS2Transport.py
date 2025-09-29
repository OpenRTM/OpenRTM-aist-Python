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

import os
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
    ddstype_env = os.getenv("RMW_IMPLEMENTATION")
    ddstype = "fast-rtps"
    if ddstype_env == "rmw_fastrtps_cpp" or ddstype_env == "rmw_fastrtps_dynamic_cpp":
        ddstype = "fast-rtps"
    elif ddstype_env == "rmw_connext_cpp" or ddstype_env == "rti_connext_cpp" or ddstype_env == "rmw_connextdds":
        ddstype = "rti-connext-dds"
    elif ddstype_env == "rmw_opensplice_cpp":
        ddstype = "opensplice"
    elif ddstype_env == "rmw_iceoryx_cpp":
        ddstype = "iceoryx"
    elif ddstype_env == "rmw_connextddsmicro":
        ddstype = "rti-connext-dds-micro"
    elif ddstype_env == "rmw_cyclonedds_cpp":
        ddstype = "cyclone-dds"

    ROS2OutPort.ROS2OutPortInit(ddstype)
    ROS2InPort.ROS2InPortInit(ddstype)

    ROS2Serializer.ROS2SerializerInit()

    ROS2TopicManager.init(mgr.getConfig().getNode("ros2"))

    mgr.addManagerActionListener(ManagerActionListener())
