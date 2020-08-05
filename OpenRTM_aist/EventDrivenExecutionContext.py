#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file EventDrivenExecutionContext.py
# @brief EventDrivenExecutionContext class
# @date  $Date: 2017-06-09 07:49:59 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
import RTC

##
# @if jp
# @class PeriodicExecutionContext
# @brief PeriodicExecutionContext クラス
#
# Periodic EventDrivenExecutionContextクラス。
#
# @since 2.0.0
#
# @else
# @class EventDrivenExecutionContext
# @brief EventDrivenExecutionContext class
# @endif


class EventDrivenExecutionContext(OpenRTM_aist.PeriodicExecutionContext):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # 設定された値をプロファイルに設定する。
    #
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):
        OpenRTM_aist.PeriodicExecutionContext.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("rtobject.eventdriven_ec")
        self.setKind(RTC.EVENT_DRIVEN)

        return


##
# @if jp
# @brief ExecutionContext を初期化する
#
# ExecutionContext 起動用ファクトリを登録する。
#
# @param manager マネージャオブジェクト
#
# @else
#
# @endif
def EventDrivenExecutionContextInit(manager):
    OpenRTM_aist.ExecutionContextFactory.instance().addFactory("EventDrivenExecutionContext",
                                                               OpenRTM_aist.EventDrivenExecutionContext)
    return
