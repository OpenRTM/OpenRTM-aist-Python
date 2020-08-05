#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ExecutionContextWorker.py
# @brief ExecutionContext's state machine worker class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#     Noriaki Ando
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import threading
from omniORB import CORBA

import OpenRTM_aist
import RTC


##
# @if jp
# @class PeriodicExecutionContext
# @brief PeriodicExecutionContext クラス
#
# Periodic Sampled Data Processing(周期実行用)ExecutionContextクラス。
#
# @since 0.4.0
#
# @else
# @class PeriodicExecutionContext
# @brief PeriodicExecutionContext class
#
# Periodic Sampled Data Processing (for the execution cycles)
# ExecutionContext class
#
# @since 0.4.0
#
# @endif
class ExecutionContextWorker:
    """
    """

    ##
    # @if jp
    # @brief デフォルトコンストラクタ
    #
    # デフォルトコンストラクタ
    # プロファイルに以下の項目を設定する。
    #  - kind : PERIODIC
    #  - rate : 0.0
    #
    # @else
    # @brief Default Constructor
    #
    # Default Constructor
    # Set the following items to profile.
    #  - kind : PERIODIC
    #  - rate : 0.0
    #
    # @endif
    def __init__(self):
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("ec_worker")
        self._running = False
        self._rtcout.RTC_TRACE("ExecutionContextWorker.__init__")
        self._ref = None
        self._comps = []
        self._addedComps = []
        self._removedComps = []
        self._mutex = threading.RLock()
        self._addedMutex = threading.RLock()
        self._removedMutex = threading.RLock()
        return

    ##
    # @if jp
    # @brief ExecutionContextWorker終了処理
    #
    #
    #
    # @else
    # @brief
    #
    #
    #
    # @endif

    def exit(self):
        self._rtcout.RTC_TRACE("exit")
        return

    # ============================================================
    # Object reference to EC
    # ============================================================
    # void setECRef(RTC::ExecutionContextService_ptr ref);

    def setECRef(self, ref):
        self._ref = ref
        return

    # RTC::ExecutionContextService_ptr getECRef();

    def getECRef(self):
        return self._ref

    # ============================================================
    # ExecutionContext
    # ============================================================
    ##
    # @if jp
    # @brief ExecutionContext 実行状態確認関数
    #
    # この操作は ExecutionContext が Runnning 状態の場合に true を返す。
    # Executioncontext が Running の間、当該 Executioncontext に参加し
    # ている全てのアクティブRTコンポーネントが、ExecutionContext の実
    # 行種類に応じて実行される。
    #
    # @return 状態確認関数(動作中:true、停止中:false)
    #
    # @else
    #
    # @brief Check for ExecutionContext running state
    #
    # This operation shall return true if the context is in the
    # Running state.  While the context is Running, all Active RTCs
    # participating in the context shall be executed according to the
    # context’s execution kind.
    #
    # @return Check state function (Running:true、Stopping:false)
    #
    # @endif
    # bool isRunning(void);

    def isRunning(self):
        self._rtcout.RTC_TRACE("isRunning()")
        return self._running

    ##
    # @if jp
    # @brief ExecutionContext の実行を開始
    #
    # ExecutionContext の実行状態を Runnning とするためのリクエストを
    # 発行する。ExecutionContext の状態が遷移すると
    # ComponentAction::on_startup が呼び出される。参加しているRTコンポー
    # ネントが、初期化されるまで ExecutionContext を開始することはでき
    # ない。ExecutionContext は複数回開始/停止を繰り返すことができる。
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Start the ExecutionContext
    #
    # Request that the context enter the Running state.  Once the
    # state transition occurs, the ComponentAction::on_startup
    # operation will be invoked.  An execution context may not be
    # started until the RT-Components that participate in it have
    # been initialized.  An execution context may be started and
    # stopped multiple times.
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t start(void);

    def start(self):
        self._rtcout.RTC_TRACE("start()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        if self._running:
            del guard
            self._rtcout.RTC_WARN("ExecutionContext is already running.")
            return RTC.PRECONDITION_NOT_MET

        # invoke ComponentAction::on_startup for each comps.
        for comp in self._comps:
            comp.onStartup()

        self._rtcout.RTC_DEBUG("%d components started.", len(self._comps))
        # change EC thread state
        self._running = True
        del guard
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief ExecutionContext の実行を停止
    #
    # ExecutionContext の状態を Stopped とするためのリクエストを発行す
    # る。遷移が発生した場合は、ComponentAction::on_shutdown が呼び出
    # される。参加しているRTコンポーネントが終了する前に
    # ExecutionContext を停止する必要がある。ExecutionContext は複数回
    # 開始/停止を繰り返すことができる。
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Stop the ExecutionContext
    #
    # Request that the context enter the Stopped state.  Once the
    # transition occurs, the ComponentAction::on_shutdown operation
    # will be invoked.  An execution context must be stopped before
    # the RT components that participate in it are finalized.  An
    # execution context may be started and stopped multiple times.
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t stop(void);

    def stop(self):
        self._rtcout.RTC_TRACE("stop()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        if not self._running:
            del guard
            self._rtcout.RTC_WARN("ExecutionContext is already stopped.")
            return RTC.PRECONDITION_NOT_MET

        # stop thread
        self._running = False

        # invoke on_shutdown for each comps.
        for comp in self._comps:
            comp.onShutdown()

        del guard
        return RTC.RTC_OK
    #
    # @if jp
    # @brief ExecutionContext の周期が変化した
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Changing execution rate of the ExecutionContext
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t rateChanged(void);

    def rateChanged(self):
        self._rtcout.RTC_TRACE("rateChanged()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        ret = RTC.RTC_OK
        for comp in self._comps:
            tmp = comp.onRateChanged()
            if tmp != RTC.RTC_OK:
                ret = tmp
        del guard
        return ret

    ##
    # @if jp
    # @brief RTコンポーネントをアクティブ化する
    #
    # Inactive 状態にあるRTコンポーネントをActive に遷移させ、アクティ
    # ブ化する。この操作が呼ばれた結果、on_activate が呼び出される。指
    # 定したRTコンポーネントが参加者リストに含まれない場合は、
    # BAD_PARAMETER が返される。指定したRTコンポーネントの状態が
    # Inactive 以外の場合は、PRECONDITION_NOT_MET が返される。
    #
    # @param comp アクティブ化対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Activate an RT-component
    #
    # The given participant RTC is Inactive and is therefore not
    # being invoked according to the execution context’s execution
    # kind. This operation shall cause the RTC to transition to the
    # Active state such that it may subsequently be invoked in this
    # execution context.  The callback on_activate shall be called as
    # a result of calling this operation. This operation shall not
    # return until the callback has returned, and shall result in an
    # error if the callback does.
    #
    # @param comp The target RT-Component for activation
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t activateComponent(RTC::LightweightRTObject_ptr comp,
    #                                     RTObjectStateMachine*& rtobj);
    def activateComponent(self, comp):
        self._rtcout.RTC_TRACE("activateComponent()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        obj_ = self.findComponent(comp)
        if not obj_:
            del guard
            self._rtcout.RTC_ERROR("Given RTC is not participant of this EC.")
            return RTC.BAD_PARAMETER, obj_

        self._rtcout.RTC_DEBUG("Component found in the EC.")
        if not obj_.activate():
            del guard
            self._rtcout.RTC_ERROR("State of the RTC is not INACTIVE_STATE.")
            return RTC.PRECONDITION_NOT_MET, obj_

        self._rtcout.RTC_DEBUG(
            "Component is in INACTIVE state. Going to ACTIVE state.")
        del guard
        self._rtcout.RTC_DEBUG("activateComponent() done.")
        return RTC.RTC_OK, obj_

    # RTC::ReturnCode_t waitActivateComplete(RTObjectStateMachine*& rtobj,
    #                                        coil::TimeValue timeout = 1.0,
    #                                        long int cycle = 1000);

    def waitActivateComplete(self, rtobj, timeout=1.0, cycle=1000):
        pass

    ##
    # @if jp
    # @brief RTコンポーネントを非アクティブ化する
    #
    # Inactive 状態にあるRTコンポーネントを非アクティブ化し、Inactive
    # に遷移させる。この操作が呼ばれた結果、on_deactivate が呼び出され
    # る。指定したRTコンポーネントが参加者リストに含まれない場合は、
    # BAD_PARAMETER が返される。指定したRTコンポーネントの状態が
    # Active 以外の場合は、PRECONDITION_NOT_MET が返される。
    #
    # @param comp 非アクティブ化対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Deactivate an RT-component
    #
    # The given RTC is Active in the execution context. Cause it to
    # transition to the Inactive state such that it will not be
    # subsequently invoked from the context unless and until it is
    # activated again.  The callback on_deactivate shall be called as
    # a result of calling this operation. This operation shall not
    # return until the callback has returned, and shall result in an
    # error if the callback does.
    #
    # @param comp The target RT-Component for deactivate
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t deactivateComponent(RTC::LightweightRTObject_ptr comp,
    #                                       RTObjectStateMachine*& rtobj);
    def deactivateComponent(self, comp):
        self._rtcout.RTC_TRACE("deactivateComponent()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)

        rtobj = self.findComponent(comp)
        if not rtobj:
            del guard
            self._rtcout.RTC_ERROR("Given RTC is not participant of this EC.")
            return RTC.BAD_PARAMETER, rtobj

        if not rtobj.deactivate():
            del guard
            self._rtcout.RTC_ERROR("State of the RTC is not ACTIVE_STATE.")
            return RTC.PRECONDITION_NOT_MET, rtobj

        del guard
        return RTC.RTC_OK, rtobj

    # RTC::ReturnCode_t waitDeactivateComplete(RTObjectStateMachine*& rtobj,
    #                                            coil::TimeValue timeout = 1.0,
    #                                            long int cycle = 1000);

    def waitDeactivateComplete(self, rtobj, timeout=1.0, cycle=1000):
        pass

    ##
    # @if jp
    # @brief RTコンポーネントをリセットする
    #
    # Error 状態のRTコンポーネントの復帰を試みる。この操作が呼ばれた結
    # 果、on_reset が呼び出される。指定したRTコンポーネントが参加者リ
    # ストに含まれない場合は、BAD_PARAMETER が返される。指定したRTコン
    # ポーネントの状態が Error 以外の場合は、PRECONDITION_NOT_MET が返
    # される。
    #
    # @param comp リセット対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Reset the RT-component
    #
    # Attempt to recover the RTC when it is in Error.  The
    # ComponentAction::on_reset callback shall be invoked. This
    # operation shall not return until the callback has returned, and
    # shall result in an error if the callback does. If possible, the
    # RTC developer should implement that callback such that the RTC
    # may be returned to a valid state.
    #
    # @param comp The target RT-Component for reset
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t resetComponent(RTC::LightweightRTObject_ptr com,
    #                                  RTObjectStateMachine*& rtobj);

    def resetComponent(self, comp):
        self._rtcout.RTC_TRACE("resetComponent()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)

        rtobj = self.findComponent(comp)
        if not rtobj:
            del guard
            self._rtcout.RTC_ERROR("Given RTC is not participant of this EC.")
            return RTC.BAD_PARAMETER, rtobj

        if not rtobj.reset():
            del guard
            self._rtcout.RTC_ERROR("State of the RTC is not ERROR_STATE.")
            return RTC.PRECONDITION_NOT_MET, rtobj

        del guard
        return RTC.RTC_OK, rtobj

    # RTC::ReturnCode_t waitResetComplete(RTObjectStateMachine*& rtobj,
    #                                     coil::TimeValue timeout = 1.0,
    #                                     long int cycle = 1000);

    def waitResetComplete(self, rtobj, timeout=1.0, cycle=1000):
        pass

    ##
    # @if jp
    # @brief RTコンポーネントの状態を取得する
    #
    # 指定したRTコンポーネントの状態(LifeCycleState)を取得する。指定し
    # たRTコンポーネントが参加者リストに含まれない場合は、
    # UNKNOWN_STATE が返される。
    #
    # @param comp 状態取得対象RTコンポーネント
    #
    # @return 現在の状態(LifeCycleState)
    #
    # @else
    #
    # @brief Get RT-component's state
    #
    # This operation shall report the LifeCycleState of the given
    # participant RTC.  UNKNOWN_STATE will be returned, if the given
    # RT-Component is not inclued in the participant list.
    #
    # @param comp The target RT-Component to get the state
    #
    # @return The current state of the target RT-Component(LifeCycleState)
    #
    # @endif
    # RTC::LifeCycleState getComponentState(RTC::LightweightRTObject_ptr comp);

    def getComponentState(self, comp):
        self._rtcout.RTC_TRACE("getComponentState()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        rtobj_ = self.findComponent(comp)
        if not rtobj_:
            del guard
            self._rtcout.RTC_WARN("Given RTC is not participant of this EC.")
            return RTC.CREATED_STATE

        state_ = rtobj_.getState()
        self._rtcout.RTC_DEBUG(
            "getComponentState() = %s done",
            self.getStateString(state_))
        return state_

    # const char* getStateString(RTC::LifeCycleState state)

    def getStateString(self, state):
        st = ["CREATED_STATE",
              "INACTIVE_STATE",
              "ACTIVE_STATE",
              "ERROR_STATE"]

        def f(
            x): return st[x._v] if x._v >= RTC.CREATED_STATE._v and x._v <= RTC.ERROR_STATE._v else ""
        return f(state)

    ##
    # @if jp
    # @brief RTコンポーネントを追加する
    #
    # 指定したRTコンポーネントを参加者リストに追加する。追加されたRTコ
    # ンポーネントは attach_context が呼ばれ、Inactive 状態に遷移する。
    # 指定されたRTコンポーネントがnullの場合は、BAD_PARAMETER が返され
    # る。指定されたRTコンポーネントが DataFlowComponent 以外の場合は、
    # BAD_PARAMETER が返される。
    #
    # @param comp 追加対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Add an RT-component
    #
    # The operation causes the given RTC to begin participating in
    # the execution context.  The newly added RTC will receive a call
    # to LightweightRTComponent::attach_context and then enter the
    # Inactive state.  BAD_PARAMETER will be invoked, if the given
    # RT-Component is null or if the given RT-Component is other than
    # DataFlowComponent.
    #
    # @param comp The target RT-Component for add
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t addComponent(RTC::LightweightRTObject_ptr comp);
    def addComponent(self, comp):
        self._rtcout.RTC_TRACE("addComponent()")
        if CORBA.is_nil(comp):
            self._rtcout.RTC_ERROR("nil reference is given.")
            return RTC.BAD_PARAMETER

        try:
            guard = OpenRTM_aist.ScopedLock(self._addedMutex)
            ec_ = self.getECRef()
            id_ = comp.attach_context(ec_)
            self._addedComps.append(
                OpenRTM_aist.RTObjectStateMachine(
                    id_, comp))
            del guard
        except BaseException:
            del guard
            self._rtcout.RTC_ERROR("addComponent() failed.")
            return RTC.RTC_ERROR

        self._rtcout.RTC_DEBUG("addComponent() succeeded.")
        if self._running == False:
            self.updateComponentList()
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief コンポーネントをバインドする。
    #
    # コンポーネントをバインドする。
    #
    # @param rtc RTコンポーネント
    # @return ReturnCode_t 型のリターンコード
    # @else
    # @brief Bind the component.
    #
    # Bind the component.
    #
    # @param rtc RT-Component's instances
    # @return The return code of ReturnCode_t type
    # @endif
    # RTC::ReturnCode_t bindComponent(RTC::RTObject_impl* rtc);

    def bindComponent(self, rtc):
        self._rtcout.RTC_TRACE("bindComponent()")
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        if not rtc:
            del guard
            self._rtcout.RTC_ERROR("NULL pointer is given.")
            return RTC.BAD_PARAMETER

        ec_ = self.getECRef()
        id_ = rtc.bindContext(ec_)
        if id_ < 0 or id_ > OpenRTM_aist.ECOTHER_OFFSET:
            # id should be owned context id < ECOTHER_OFFSET
            del guard
            self._rtcout.RTC_ERROR("bindContext returns invalid id: %d", id_)
            return RTC.RTC_ERROR

        self._rtcout.RTC_DEBUG("bindContext returns id = %d", id_)

        # rtc is owner of this EC
        comp_ = rtc.getObjRef()
        #    RTObjectStateMachine o(id, comp);
        self._comps.append(OpenRTM_aist.RTObjectStateMachine(id_, comp_))
        del guard
        self._rtcout.RTC_DEBUG("bindComponent() succeeded.")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief RTコンポーネントを参加者リストから削除する
    #
    # 指定したRTコンポーネントを参加者リストから削除する。削除された
    # RTコンポーネントは detach_context が呼ばれる。指定されたRTコンポー
    # ネントが参加者リストに登録されていない場合は、BAD_PARAMETER が返
    # される。
    #
    # @param comp 削除対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Remove the RT-Component from participant list
    #
    # This operation causes a participant RTC to stop participating in the
    # execution context.
    # The removed RTC will receive a call to
    # LightweightRTComponent::detach_context.
    # BAD_PARAMETER will be returned, if the given RT-Component is not
    # participating in the participant list.
    #
    # @param comp The target RT-Component for delete
    #
    # @return The return code of ReturnCode_t type
    #
    # @endif
    # RTC::ReturnCode_t removeComponent(RTC::LightweightRTObject_ptr comp);

    def removeComponent(self, comp):
        self._rtcout.RTC_TRACE("removeComponent()")
        if CORBA.is_nil(comp):
            self._rtcout.RTC_ERROR("nil reference is given.")
            return RTC.BAD_PARAMETER

        guard = OpenRTM_aist.ScopedLock(self._mutex)
        rtobj_ = self.findComponent(comp)
        del guard

        if not rtobj_:
            self._rtcout.RTC_ERROR("no RTC found in this context.")
            return RTC.BAD_PARAMETER

        guard = OpenRTM_aist.ScopedLock(self._removedMutex)
        self._removedComps.append(rtobj_)
        del guard
        if self._running == False:
            self.updateComponentList()
        return RTC.RTC_OK

    # RTObjectStateMachine* findComponent(RTC::LightweightRTObject_ptr comp);

    def findComponent(self, comp):
        for comp_ in self._comps:
            if comp_.isEquivalent(comp):
                return comp_

        return None

    # bool isAllCurrentState(RTC::LifeCycleState state);

    def isAllCurrentState(self, state):
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        for comp in self._comps:
            if not comp.isCurrentState(state):
                del guard
                return False

        del guard
        return True

    # bool isAllNextState(RTC::LifeCycleState state);

    def isAllNextState(self, state):
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        for comp in self._comps:
            if not comp.isNextState(state):
                del guard
                return False

        del guard
        return True

    # bool isOneOfCurrentState(RTC::LifeCycleState state);

    def isOneOfCurrentState(self, state):
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        for comp in self._comps:
            if comp.isCurrentState(state):
                del guard
                return True

        del guard
        return False

    # bool isOneOfNextState(RTC::LifeCycleState state);

    def isOneOfNextState(self, state):
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        for comp in self._comps:
            if comp.isNextState(state):
                del guard
                return True

        del guard
        return False

    # void invokeWorker();

    def invokeWorker(self):
        self._rtcout.RTC_PARANOID("invokeWorker()")

        for comp in self._comps:
            comp.workerPreDo()

        for comp in self._comps:
            comp.workerDo()

        for comp in self._comps:
            comp.workerPostDo()

        self.updateComponentList()
        return

    # void invokeWorkerPreDo();

    def invokeWorkerPreDo(self):
        self._rtcout.RTC_PARANOID("invokeWorkerPreDo()")
        # m_comps never changes its size here
        for comp in self._comps:
            comp.workerPreDo()
        return

    # void invokeWorkerDo();
    def invokeWorkerDo(self):
        self._rtcout.RTC_PARANOID("invokeWorkerDo()")
        # m_comps never changes its size here
        for comp in self._comps:
            comp.workerDo()
        return

    # void invokeWorkerPostDo();
    def invokeWorkerPostDo(self):
        self._rtcout.RTC_PARANOID("invokeWorkerPostDo()")
        # m_comps never changes its size here
        for comp in self._comps:
            comp.workerPostDo()
        # m_comps might be changed here
        self.updateComponentList()
        return

    # void updateComponentList();
    def updateComponentList(self):
        guard = OpenRTM_aist.ScopedLock(self._mutex)
        # adding component
        guard_added = OpenRTM_aist.ScopedLock(self._addedMutex)
        for comp in self._addedComps:
            self._comps.append(comp)
            self._rtcout.RTC_TRACE("Component added.")

        self._addedComps = []
        del guard_added

        # removing component
        guard_removed = OpenRTM_aist.ScopedLock(self._removedMutex)
        for comp in self._removedComps:
            lwrtobj_ = comp.getRTObject()
            lwrtobj_.detach_context(comp.getExecutionContextHandle())
            idx_ = -1
            try:
                idx_ = self._comps.index(comp)
            except BaseException:
                idx_ = -1

            if idx_ >= 0:
                del self._comps[idx_]
                self._rtcout.RTC_TRACE("Component deleted.")

        self._removedComps = []
        return
