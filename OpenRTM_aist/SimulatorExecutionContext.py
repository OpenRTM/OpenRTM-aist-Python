#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file SimulatorExecutionContext.py
# @brief SimulatorExecutionContext class
# @date $Date: 2017/06/12$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import threading
import time

import OpenRTM_aist
import OpenRTM__POA
import RTC


class SimulatorExecutionContext(OpenRTM_aist.OpenHRPExecutionContext):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    #
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.OpenHRPExecutionContext.__init__(self)
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    # @endif
    #
    def __del__(self):
        return

    ##
    # @if jp
    # @brief 対象のRTCをアクティブ化する
    # 内部でinvokeWorkerPreDo関数を呼ぶため、即座に
    # 状態を遷移させることができる。
    # 現在tick実行中の場合は実行終了まで待つ
    #
    # @param self
    # @param comp アクティブ化対象RTコンポーネント
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    # @brief Activate an RT-component
    #
    #
    # @param self
    # @param comp The target RT-Component for activation
    # @return The return code of ReturnCode_t type
    #
    # @endif
    #

    def activate_component(self, comp):
        guard = OpenRTM_aist.ScopedLock(self._tickmutex)
        rtobj = self._worker.findComponent(comp)
        if not rtobj:
            return RTC.BAD_PARAMETER
        if not rtobj.isCurrentState(RTC.INACTIVE_STATE):
            return RTC.PRECONDITION_NOT_MET

        self._syncActivation = False
        OpenRTM_aist.ExecutionContextBase.activateComponent(self, comp)

        self.invokeWorkerPreDo()

        if rtobj.isCurrentState(RTC.ACTIVE_STATE):
            return RTC.RTC_OK

        return RTC.RTC_ERROR

    ##
    # @if jp
    # @brief 対象のRTCを非アクティブ化する
    # 内部でinvokeWorkerPreDo関数を呼ぶため、即座に
    # 状態を遷移させることができる。
    # 現在tick実行中の場合は実行終了まで待つ
    #
    # @param self
    # @param comp 非アクティブ化対象RTコンポーネント
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    # @brief Deactivate an RT-component
    #
    #
    # @param self
    # @param comp The target RT-Component for deactivation
    # @return The return code of ReturnCode_t type
    #
    # @endif
    #

    def deactivate_component(self, comp):
        guard = OpenRTM_aist.ScopedLock(self._tickmutex)
        rtobj = self._worker.findComponent(comp)
        if not rtobj:
            return RTC.BAD_PARAMETER
        if not rtobj.isCurrentState(RTC.ACTIVE_STATE):
            return RTC.PRECONDITION_NOT_MET

        self._syncDeactivation = False
        OpenRTM_aist.ExecutionContextBase.deactivateComponent(self, comp)

        self.invokeWorkerPreDo()
        self.invokeWorkerDo()
        self.invokeWorkerPostDo()

        if rtobj.isCurrentState(RTC.INACTIVE_STATE):
            return RTC.RTC_OK

        return RTC.RTC_ERROR

    ##
    # @if jp
    # @brief 対象のRTCをリセット化する
    # 内部でinvokeWorkerPreDo関数を呼ぶため、即座に
    # 状態を遷移させることができる。
    # 現在tick実行中の場合は実行終了まで待つ
    #
    # @param self
    # @param comp リセット対象RTコンポーネント
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    # @brief Reset an RT-component
    #
    #
    # @param self
    # @param comp The target RT-Component for reset
    # @return The return code of ReturnCode_t type
    #
    # @endif
    #
    def reset_component(self, comp):
        guard = OpenRTM_aist.ScopedLock(self._tickmutex)
        rtobj = self._worker.findComponent(comp)
        if not rtobj:
            return RTC.BAD_PARAMETER
        if not rtobj.isCurrentState(RTC.ERROR_STATE):
            return RTC.PRECONDITION_NOT_MET

        self._syncReset = False
        OpenRTM_aist.ExecutionContextBase.resetComponent(self, comp)

        self.invokeWorkerPreDo()
        self.invokeWorkerDo()
        self.invokeWorkerPostDo()

        if rtobj.isCurrentState(RTC.INACTIVE_STATE):
            return RTC.RTC_OK

        return RTC.RTC_ERROR


##
# @if jp
# @brief ECFactoryへの登録のための初期化関数
# @else
# @brief Initialization function to register to ECFactory
# @endif
#
def SimulatorExecutionContextInit(manager):
    OpenRTM_aist.ExecutionContextFactory.instance().addFactory("SimulatorExecutionContext",
                                                               OpenRTM_aist.SimulatorExecutionContext)
    return
