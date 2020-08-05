#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file PeriodicExecutionContext.py
# @brief PeriodicExecutionContext class
# @date $Date: 2007/08/29$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2006-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import threading
import time


import OpenRTM_aist

import RTC
import RTC__POA

DEFAULT_PERIOD = 0.000001

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
# @endif


class PeriodicExecutionContext(OpenRTM_aist.ExecutionContextBase,
                               RTC__POA.ExecutionContextService,
                               OpenRTM_aist.Task):
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
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("rtobject.periodic_ec")
        self._rtcout.RTC_TRACE("PeriodicExecutionContext.__init__()")
        OpenRTM_aist.ExecutionContextBase.__init__(self, "periodic_ec")
        OpenRTM_aist.Task.__init__(self)

        self._svc = False
        self._nowait = False
        self._svcmutex = threading.RLock()
        self._workerthread = self.WorkerThreadCtrl()

        global DEFAULT_PERIOD
        self.setObjRef(self._this())
        self.setKind(RTC.PERIODIC)
        self.setRate(1.0 / DEFAULT_PERIOD)
        self._rtcout.RTC_DEBUG("Actual rate: %d [sec], %d [usec]",
                               (self._profile.getPeriod().sec(), self._profile.getPeriod().usec()))

        self._cpu = []

        return

    ##
    # @if jp
    # @brief 終了関数
    #
    # @param self　
    # @param Task　
    #
    # @else
    # @brief
    # @param self　
    # @param Task　
    # @endif
    def exit(self, Task=OpenRTM_aist.Task):
        import OpenRTM_aist.Guard
        self._rtcout.RTC_TRACE("PeriodicExecutionContext.__del__()")
        guard = OpenRTM_aist.Guard.ScopedLock(self._svcmutex)
        self._svc = False
        del guard

        guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
        self._workerthread._cond.acquire()
        self._workerthread._running = True
        self._workerthread._cond.notify()
        self._workerthread._cond.release()
        del guard
        self.wait()
        Task.__del__(self)
        OpenRTM_aist.ExecutionContextBase.exit(self)
        return

    ##
    # @if jp
    # @brief 初期化関数
    #
    # @param self　
    # @param props プロパティ
    #
    # @else
    # @brief
    # @param self　
    # @param props
    # @endif

    def init(self, props):
        OpenRTM_aist.ExecutionContextBase.init(self, props)
        self.setCpuAffinity(props)
        self._rtcout.RTC_DEBUG("init() done")

    ##
    # @if jp
    # @brief コンポーネントのアクティビティスレッド関数
    #
    # コンポーネントの内部アクティビティスレッドの実行関数。
    # ACE_Task サービスクラスメソッドのオーバーライド。
    #
    # @else
    #
    # @brief Create internal activity thread
    #
    # Run by a daemon thread to handle deferred processing.
    # ACE_Task class method override.
    #
    # @endif

    def svc(self):
        self._rtcout.RTC_TRACE("svc()")
        count_ = 0

        if self._cpu:
            ret = OpenRTM_aist.setThreadAffinity(self._cpu)
            if ret == False:
                self._rtcout.RTC_ERROR("CPU affinity mask setting failed")
                
        while self.threadRunning():
            OpenRTM_aist.ExecutionContextBase.invokeWorkerPreDo(self)
            # Thread will stopped when all RTCs are INACTIVE.
            # Therefore WorkerPreDo(updating state) have to be invoked
            # before stopping thread.
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            while not self._workerthread._running:
                self._workerthread._cond.wait()
            del guard

            t0_ = OpenRTM_aist.Time()
            OpenRTM_aist.ExecutionContextBase.invokeWorkerDo(self)
            OpenRTM_aist.ExecutionContextBase.invokeWorkerPostDo(self)
            t1_ = OpenRTM_aist.Time()

            period_ = self.getPeriod()
            exectime_ = (t1_ - t0_).getTime()
            sleeptime_ = period_ - exectime_

            if count_ > 1000:
                self._rtcout.RTC_PARANOID("Period:    %f [s]", period_.toDouble())
                self._rtcout.RTC_PARANOID("Execution: %f [s]", exectime_.toDouble())
                self._rtcout.RTC_PARANOID("Sleep:     %f [s]", sleeptime_.toDouble())

            t2_ = OpenRTM_aist.Time()

            if not self._nowait and exectime_.toDouble() >= 0.0 and sleeptime_.toDouble() > 0.0:
                if count_ > 1000:
                    self._rtcout.RTC_PARANOID("sleeping...")
                time.sleep(sleeptime_.toDouble())

            if count_ > 1000:
                t3_ = OpenRTM_aist.Time()
                self._rtcout.RTC_PARANOID("Slept:     %f [s]", (t3_ - t2_).getTime().toDouble())
                count_ = 0
            count_ += 1

        self._rtcout.RTC_DEBUG("Thread terminated.")
        return 0

    ##
    # @if jp
    # @brief ExecutionContext用アクティビティスレッドを生成する
    # @else
    # @brief Generate internal activity thread for ExecutionContext
    # @endif
    #
    # int PeriodicExecutionContext::open(void *args)

    def open(self, *args):
        self._rtcout.RTC_TRACE("open()")
        self.activate()
        return 0

    ##
    # @if jp
    # @brief ExecutionContext 用のスレッド実行関数
    #
    # ExecutionContext 用のスレッド終了時に呼ばれる。
    # コンポーネントオブジェクトの非アクティブ化、マネージャへの通知を行う。
    # これは ACE_Task サービスクラスメソッドのオーバーライド。
    #
    # @param self
    # @param flags 終了処理フラグ
    #
    # @return 終了処理結果
    #
    # @else
    #
    # @brief Close activity thread
    #
    # close() method is called when activity thread svc() is returned.
    # This method deactivate this object and notify it to manager.
    # ACE_Task class method override.
    #
    # @endif

    def close(self, flags):
        self._rtcout.RTC_TRACE("close()")
        return 0

    ##
    # @if jp
    # @brief ExecutionContext 実行状態確認関数
    #
    # この操作は ExecutionContext が Runnning 状態の場合に true を返す。
    # Executioncontext が Running の間、当該 Executioncontext に参加している
    # 全てのアクティブRTコンポーネントが、 ExecutionContext の実行種類に応じて
    # 実行される。
    #
    # @param self
    #
    # @return 状態確認関数(動作中:true、停止中:false)
    #
    # @else
    #
    # @brief Check for ExecutionContext running state
    #
    # This operation shall return true if the context is in the Running state.
    # While the context is Running, all Active RTCs participating
    # in the context shall be executed according to the context’s execution
    # kind.
    #
    # @endif

    def is_running(self):
        self._rtcout.RTC_TRACE("is_running()")
        return OpenRTM_aist.ExecutionContextBase.isRunning(self)

    ##
    # @if jp
    # @brief ExecutionContext の実行を開始
    #
    # ExecutionContext の実行状態を Runnning とするためのリクエストを発行する。
    # ExecutionContext の状態が遷移すると ComponentAction::on_startup が
    # 呼び出される。
    # 参加しているRTコンポーネントが、初期化されるまで ExecutionContext を開始
    # することはできない。
    # ExecutionContext は複数回開始/停止を繰り返すことができる。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Start ExecutionContext
    #
    # Request that the context enter the Running state.
    # Once the state transition occurs, the ComponentAction::on_startup
    # operation will be invoked.
    # An execution context may not be started until the RT components that
    # participate in it have been initialized.
    # An execution context may be started and stopped multiple times.
    #
    # @endif

    def start(self):
        return OpenRTM_aist.ExecutionContextBase.start(self)

    ##
    # @if jp
    # @brief ExecutionContext の実行を停止
    #
    # ExecutionContext の状態を Stopped とするためのリクエストを発行する。
    # 遷移が発生した場合は、 ComponentAction::on_shutdown が呼び出される。
    # 参加しているRTコンポーネントが終了する前に ExecutionContext を停止する
    # 必要がある。
    # ExecutionContext は複数回開始/停止を繰り返すことができる。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Stop ExecutionContext
    #
    # Request that the context enter the Stopped state.
    # Once the transition occurs, the ComponentAction::on_shutdown operation
    # will be invoked.
    # An execution context must be stopped before the RT components that
    # participate in it are finalized.
    # An execution context may be started and stopped multiple times.
    #
    # @endif

    def stop(self):
        return OpenRTM_aist.ExecutionContextBase.stop(self)

    ##
    # @if jp
    # @brief ExecutionContext の実行周期(Hz)を取得する
    #
    # Active 状態にてRTコンポーネントが実行される周期(単位:Hz)を取得する。
    #
    # @param self
    #
    # @return 処理周期(単位:Hz)
    #
    # @else
    #
    # @brief Get ExecutionRate
    #
    # This operation shall return the rate (in hertz) at which its Active
    # participating RTCs are being invoked.
    #
    # @endif

    def get_rate(self):
        return OpenRTM_aist.ExecutionContextBase.getRate(self)

    ##
    # @if jp
    # @brief ExecutionContext の実行周期(Hz)を設定する
    #
    # Active 状態にてRTコンポーネントが実行される周期(単位:Hz)を設定する。
    # 実行周期の変更は、 DataFlowComponentAction の on_rate_changed によって
    # 各RTコンポーネントに伝達される。
    #
    # @param self
    # @param rate 処理周期(単位:Hz)
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Set ExecutionRate
    #
    # This operation shall set the rate (in hertz) at which this context’s
    # Active participating RTCs are being called.
    # If the execution kind of the context is PERIODIC, a rate change shall
    # result in the invocation of on_rate_changed on any RTCs realizing
    # DataFlowComponentAction that are registered with any RTCs participating
    # in the context.
    #
    # @endif

    def set_rate(self, rate):
        return OpenRTM_aist.ExecutionContextBase.setRate(self, rate)

    ##
    # @if jp
    # @brief RTコンポーネントをアクティブ化する
    #
    # Inactive 状態にあるRTコンポーネントをActive に遷移させ、アクティブ化する。
    # この操作が呼ばれた結果、 on_activate が呼び出される。
    # 指定したRTコンポーネントが参加者リストに含まれない場合は、 BAD_PARAMETER
    # が返される。
    # 指定したRTコンポーネントの状態が Inactive 以外の場合は、
    #  PRECONDITION_NOT_MET が返される。
    #
    # @param self
    # @param comp アクティブ化対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Activate a RT-component
    #
    # The given participant RTC is Inactive and is therefore not being invoked
    # according to the execution context’s execution kind. This operation
    # shall cause the RTC to transition to the Active state such that it may
    # subsequently be invoked in this execution context.
    # The callback on_activate shall be called as a result of calling this
    # operation. This operation shall not return until the callback has
    # returned, and shall result in an error if the callback does.
    #
    # @endif

    def activate_component(self, comp):
        return OpenRTM_aist.ExecutionContextBase.activateComponent(self, comp)

    ##
    # @if jp
    # @brief RTコンポーネントを非アクティブ化する
    #
    # Inactive 状態にあるRTコンポーネントを非アクティブ化し、
    # Inactive に遷移させる。
    # この操作が呼ばれた結果、 on_deactivate が呼び出される。
    # 指定したRTコンポーネントが参加者リストに含まれない場合は、 BAD_PARAMETER
    # が返される。
    # 指定したRTコンポーネントの状態が Active 以外の場合は、
    # PRECONDITION_NOT_MET が返される。
    #
    # @param self
    # @param comp 非アクティブ化対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Deactivate a RT-component
    #
    # The given RTC is Active in the execution context. Cause it to transition
    # to the Inactive state such that it will not be subsequently invoked from
    # the context unless and until it is activated again.
    # The callback on_deactivate shall be called as a result of calling this
    # operation. This operation shall not return until the callback has
    # returned, and shall result in an error if the callback does.
    #
    # @endif

    def deactivate_component(self, comp):
        return OpenRTM_aist.ExecutionContextBase.deactivateComponent(
            self, comp)

    ##
    # @if jp
    # @brief RTコンポーネントをリセットする
    #
    # Error 状態のRTコンポーネントの復帰を試みる。
    # この操作が呼ばれた結果、 on_reset が呼び出される。
    # 指定したRTコンポーネントが参加者リストに含まれない場合は、 BAD_PARAMETER
    # が返される。
    # 指定したRTコンポーネントの状態が Error 以外の場合は、 PRECONDITION_NOT_MET
    # が返される。
    #
    # @param self
    # @param comp リセット対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Reset a RT-component
    #
    # Attempt to recover the RTC when it is in Error.
    # The ComponentAction::on_reset callback shall be invoked. This operation
    # shall not return until the callback has returned, and shall result in an
    # error if the callback does. If possible, the RTC developer should
    # implement that callback such that the RTC may be returned to a valid
    # state.
    #
    # @endif

    def reset_component(self, comp):
        return OpenRTM_aist.ExecutionContextBase.resetComponent(self, comp)

    ##
    # @if jp
    # @brief RTコンポーネントの状態を取得する
    #
    # 指定したRTコンポーネントの状態(LifeCycleState)を取得する。
    # 指定したRTコンポーネントが参加者リストに含まれない場合は、 CREATED_STATE
    # が返される。
    #
    # @param self
    # @param comp 状態取得対象RTコンポーネント
    #
    # @return 現在の状態(LifeCycleState)
    #
    # @else
    #
    # @brief Get RT-component's state
    #
    # This operation shall report the LifeCycleState of the given participant
    # RTC.
    #
    # @endif

    def get_component_state(self, comp):
        return OpenRTM_aist.ExecutionContextBase.getComponentState(self, comp)

    ##
    # @if jp
    # @brief ExecutionKind を取得する
    #
    # 本 ExecutionContext の ExecutionKind を取得する
    #
    # @param self
    #
    # @return ExecutionKind
    #
    # @else
    #
    # @brief Get the ExecutionKind
    #
    # This operation shall report the execution kind of the execution context.
    #
    # @endif

    def get_kind(self):
        return OpenRTM_aist.ExecutionContextBase.getKind(self)

    ##
    # @if jp
    # @brief RTコンポーネントを追加する
    #
    # 指定したRTコンポーネントを参加者リストに追加する。
    # 追加されたRTコンポーネントは attach_context が呼ばれ、Inactive 状態に遷移
    # する。
    # 指定されたRTコンポーネントがnullの場合は、BAD_PARAMETER が返される。
    # 指定されたRTコンポーネントが DataFlowComponent 以外の場合は、
    # BAD_PARAMETER が返される。
    #
    # @param self
    # @param comp 追加対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Add a RT-component
    #
    # The operation causes the given RTC to begin participating in the
    # execution context.
    # The newly added RTC will receive a call to
    # LightweightRTComponent::attach_context and then enter the Inactive state.
    #
    # @endif

    def add_component(self, comp):
        return OpenRTM_aist.ExecutionContextBase.addComponent(self, comp)

    ##
    # @if jp
    # @brief RTコンポーネントを参加者リストから削除する
    #
    # 指定したRTコンポーネントを参加者リストから削除する。
    # 削除されたRTコンポーネントは detach_context が呼ばれる。
    # 指定されたRTコンポーネントが参加者リストに登録されていない場合は、
    # BAD_PARAMETER が返される。
    #
    # @param self
    # @param comp 削除対象RTコンポーネント
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Remove the RT-component from participant list
    #
    # This operation causes a participant RTC to stop participating in the
    # execution context.
    # The removed RTC will receive a call to
    # LightweightRTComponent::detach_context.
    #
    # @endif

    def remove_component(self, comp):
        return OpenRTM_aist.ExecutionContextBase.removeComponent(self, comp)

    ##
    # @if jp
    # @brief ExecutionContextProfile を取得する
    #
    # 本 ExecutionContext のプロファイルを取得する。
    #
    # @param self
    #
    # @return ExecutionContextProfile
    #
    # @else
    #
    # @brief Get the ExecutionContextProfile
    #
    # This operation provides a profile “descriptor” for the execution
    # context.
    #
    # @endif

    def get_profile(self):
        return OpenRTM_aist.ExecutionContextBase.getProfile(self)

    # virtual RTC::ReturnCode_t onStarted();

    def onStarted(self):
        # change EC thread state
        guard = OpenRTM_aist.ScopedLock(self._svcmutex)
        if not self._svc:
            self._svc = True
            self.open(0)
        del guard

        if self.isAllNextState(RTC.INACTIVE_STATE):
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            self._workerthread._running = False
            del guard
        else:
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            self._workerthread._running = True
            self._workerthread._cond.acquire()
            self._workerthread._cond.notify()
            self._workerthread._cond.release()
            del guard
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t onStopping();

    def onStopping(self):
        # stop thread
        guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
        self._workerthread._running = False
        return RTC.RTC_OK

    def onAddedComponent(self, rtobj):
        guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
        if self._workerthread._running == False:
            self._worker.updateComponentList()
        return RTC.RTC_OK

    def onRemovedComponent(self, rtobj):
        guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
        if self._workerthread._running == False:
            self._worker.updateComponentList()
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingActivated(RTC_impl::RTObjectStateMachine* comp, long int count);
    def onWaitingActivated(self, comp, count):
        self._rtcout.RTC_TRACE("onWaitingActivated(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        # Now comp's next state must be ACTIVE state
        # If worker thread is stopped, restart worker thread.
        if self.isRunning():
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == False:
                self._workerthread._running = True
                self._workerthread._cond.acquire()
                self._workerthread._cond.notify()
                self._workerthread._cond.release()
            del guard
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onActivated(RTC_impl::RTObjectStateMachine* comp, long int count);

    def onActivated(self, comp, count):
        self._rtcout.RTC_TRACE("onActivated(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        # count = -1; Asynch mode. Since onWaitingActivated is not
        # called, onActivated() have to send restart singnal to worker
        # thread.
        # count > 0: Synch mode.

        # Now comp's next state must be ACTIVE state
        # If worker thread is stopped, restart worker thread.
        if self.isRunning():
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == False:
                self._workerthread._running = True
                self._workerthread._cond.acquire()
                self._workerthread._cond.notify()
                self._workerthread._cond.release()
            del guard
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingDeactivated(RTC_impl::RTObjectStateMachine* comp, long int
    # count);

    def onWaitingDeactivated(self, comp, count):
        self._rtcout.RTC_TRACE("onWaitingDeactivated(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        if self.isAllNextState(RTC.INACTIVE_STATE):
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == True:
                self._workerthread._running = False
                self._rtcout.RTC_TRACE(
                    "All RTCs are INACTIVE. Stopping worker thread.")
            del guard

        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onDeactivated(RTC_impl::RTObjectStateMachine* comp, long int count);

    def onDeactivated(self, comp, count):
        self._rtcout.RTC_TRACE("onDeactivated(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        if self.isAllNextState(RTC.INACTIVE_STATE):
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == True:
                self._workerthread._running = False
                self._rtcout.RTC_TRACE(
                    "All RTCs are INACTIVE. Stopping worker thread.")
            del guard

        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingReset(RTC_impl::RTObjectStateMachine* comp, long int count);

    def onWaitingReset(self, comp, count):
        self._rtcout.RTC_TRACE("onWaitingReset(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        if self.isAllNextState(RTC.INACTIVE_STATE):
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == True:
                self._workerthread._running = False
                self._rtcout.RTC_TRACE(
                    "All RTCs are INACTIVE. Stopping worker thread.")
            del guard

        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onReset(RTC_impl::RTObjectStateMachine* comp, long int count);

    def onReset(self, comp, count):
        self._rtcout.RTC_TRACE("onReset(count = %d)", count)
        self._rtcout.RTC_PARANOID("curr: %s, next: %s",
                                  (self.getStateString(comp.getStates().curr),
                                   self.getStateString(comp.getStates().next)))
        if self.isAllNextState(RTC.INACTIVE_STATE):
            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            if self._workerthread._running == True:
                self._workerthread._running = False
                self._rtcout.RTC_TRACE(
                    "All RTCs are INACTIVE. Stopping worker thread.")
            del guard

        return RTC.RTC_OK

    # bool threadRunning()

    def threadRunning(self):
        guard = OpenRTM_aist.ScopedLock(self._svcmutex)
        return self._svc

    def setCpuAffinity(self, props):
        self._rtcout.RTC_TRACE("setCpuAffinity()")

        affinity_str = props.getProperty("cpu_affinity")
        if affinity_str:
            self._rtcout.RTC_DEBUG("CPU affinity property: %s", affinity_str)

            tmp = affinity_str.split(",")
            self._cpu = []
            for num in tmp:
                try:
                    self._cpu.append(int(num))
                    self._rtcout.RTC_DEBUG(
                        "CPU affinity int value: %d added.", int(num))
                except ValueError:
                    pass

    ##
    # @if jp
    # @class WorkerThreadCtrl
    # @brief worker 用状態変数クラス
    #
    # @else
    # @class WorkerThreadCtrl
    # @brief Condition variable class for worker
    # @endif
    class WorkerThreadCtrl:

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
        # @endif
        def __init__(self):
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._running = False

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


def PeriodicExecutionContextInit(manager):
    OpenRTM_aist.ExecutionContextFactory.instance().addFactory("PeriodicExecutionContext",
                                                               OpenRTM_aist.PeriodicExecutionContext)
    return
