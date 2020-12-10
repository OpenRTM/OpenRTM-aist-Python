#!/usr/bin/env python3
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
from OpenSpliceTopicManager import OpenSpliceTopicManager


##
# @if jp
# @class ManagerActionListener
# @brief OpenSpliceTopicManagerの終了処理を行うマネージャアクションリスナ
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
    # @brief RTMマネージャ終了後にOpenSpliceTopicManagerの終了処理を実行
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
        OpenSpliceTopicManager.shutdown_global()

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
def OpenSpliceTransportInit(mgr):
    OpenSpliceInPort.OpenSpliceInPortInit()
    OpenSpliceOutPort.OpenSpliceOutPortInit()
    OpenSpliceSerializer.OpenSpliceSerializerInit()

    mgr.addManagerActionListener(ManagerActionListener())
