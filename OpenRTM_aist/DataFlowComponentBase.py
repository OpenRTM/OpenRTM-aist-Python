#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# \file DataFlowComponentBase.py
# \brief DataFlowParticipant RT-Component base class
# \date $Date: 2007/09/04$
# \author Noriaki Ando <n-ando@aist.go.jp>
#
# Copyright (C) 2006-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import OpenRTM__POA
import RTC


##
# @if jp
# @class DataFlowComponentBase
# @brief DataFlowComponentBase クラス
#
# データフロー型RTComponentの基底クラス。
# 各種データフロー型RTComponentを実装する場合は、本クラスを継承する形で実装
# する。
#
# @since 0.4.0
#
# @else
# @class DataFlowComponentBase
# @brief DataFlowComponentBase class
# @endif
class DataFlowComponentBase(OpenRTM_aist.RTObject_impl,
                            OpenRTM__POA.DataFlowComponent):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param manager マネージャオブジェクト
    #
    # @else
    # @brief Constructor
    # @endif
    def __init__(self, manager=None, orb=None, poa=None):
        OpenRTM_aist.RTObject_impl.__init__(self, manager, orb, poa)
        self._objref = self._this()

    ##
    # @if jp
    # @brief 初期化(サブクラス実装用)
    #
    # データフロー型 RTComponent の初期化を実行する。
    # 実際の初期化処理は、各具象クラス内に記述する。
    #
    # @param self
    #
    # @else
    # @brief Initialization
    # @endif

    def init(self):
        pass

    ##
    # @if jp
    #
    # @brief [DataFlowComponentAction CORBA interface] RTC の定常処理(第一周期)
    #
    # 以下の状態が保持されている場合に、設定された周期で定期的に呼び出される。
    # - RTC は Alive 状態である。
    # - 指定された ExecutionContext が Running 状態である。
    # 本オペレーションは、Two-Pass Execution の第一周期で実行される。
    # このオペレーション呼び出しの結果として onExecute() コールバック関数が呼び
    # 出される。
    #
    # 制約
    # - 指定された ExecutionContext の ExecutionKind は、 PERIODIC でなければな
    #   らない
    #
    # @param self
    # @param ec_id 定常処理対象 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [DataFlowComponentAction CORBA interface] Primary Periodic
    #        Operation of RTC
    #
    # This operation will be invoked periodically at the rate of the given
    # execution context as long as the following conditions hold:
    # - The RTC is Active.
    # - The given execution context is Running
    # This callback occurs during the first execution pass.
    #
    # Constraints
    # - The execution context of the given context shall be PERIODIC.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_execute(self, ec_id):
        self._rtcout.RTC_TRACE("on_execute(%d)", ec_id)
        ret = RTC.RTC_ERROR
        try:
            self.preOnExecute(ec_id)
            if self._readAll:
                self.readAll()

            ret = self.onExecute(ec_id)

            if self._writeAll:
                self.writeAll()

        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            ret = RTC.RTC_ERROR
        self.postOnExecute(ec_id, ret)
        return ret

    ##
    # @if jp
    #
    # @brief [DataFlowComponentAction CORBA interface] RTC の定常処理(第二周期)
    #
    # 以下の状態が保持されている場合に、設定された周期で定期的に呼び出される。
    # - RTC は Alive 状態である。
    # - 指定された ExecutionContext が Running 状態である。
    # 本オペレーションは、Two-Pass Execution の第二周期で実行される。
    # このオペレーション呼び出しの結果として onStateUpdate() コールバック関数が
    # 呼び出される。
    #
    # 制約
    # - 指定された ExecutionContext の ExecutionKind は、 PERIODIC でなければな
    #   らない
    #
    # @param self
    # @param ec_id 定常処理対象 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [DataFlowComponentAction CORBA interface] Secondary Periodic
    #        Operation of RTC
    #
    # This operation will be invoked periodically at the rate of the given
    # execution context as long as the following conditions hold:
    # - The RTC is Active.
    # - The given execution context is Running
    # This callback occurs during the second execution pass.
    #
    # Constraints
    # - The execution context of the given context shall be PERIODIC.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_state_update(self, ec_id):
        self._rtcout.RTC_TRACE("on_state_update(%d)", ec_id)
        ret = RTC.RTC_ERROR
        try:
            self.preOnStateUpdate(ec_id)
            ret = self.onStateUpdate(ec_id)
            self._configsets.update()
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            ret = RTC.RTC_ERROR
        self.postOnStateUpdate(ec_id, ret)
        return ret

    ##
    # @if jp
    #
    # @brief [DataFlowComponentAction CORBA interface] 実行周期変更通知
    #
    # 本オペレーションは、ExecutionContext の実行周期が変更されたことを通知する
    # 際に呼び出される。
    # このオペレーション呼び出しの結果として onRateChanged() コールバック関数が
    # 呼び出される。
    #
    # 制約
    # - 指定された ExecutionContext の ExecutionKind は、 PERIODIC でなければな
    #   らない
    #
    # @param self
    # @param ec_id 定常処理対象 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [DataFlowComponentAction CORBA interface] Notify rate chenged
    #
    # This operation is a notification that the rate of the indicated execution
    # context has changed.
    #
    # Constraints
    # - The execution context of the given context shall be PERIODIC.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_rate_changed(self, ec_id):
        self._rtcout.RTC_TRACE("on_rate_changed(%d)", ec_id)
        ret = RTC.RTC_ERROR
        try:
            self.preOnRateChanged(ec_id)
            ret = self.onRateChanged(ec_id)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            ret = RTC.RTC_ERROR
        self.postOnRateChanged(ec_id, ret)
        return ret
