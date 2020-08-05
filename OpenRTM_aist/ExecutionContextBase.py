#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ExecutionContextBase.py
# @brief ExecutionContext base class
# @date $Date: 2007/08/31$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#    Task-intelligence Research Group,
#    Intelligent Systems Research Institute,
#    National Institute of
#       Advanced Industrial Science and Technology (AIST), Japan
#    All rights reserved.

import time
import OpenRTM_aist
import RTC

DEFAULT_EXECUTION_RATE = 1000

##
# @if jp
# @class ExecutionContextBase
# @brief ExecutionContext用基底クラス
#
# ECの実装クラスでは、この基底クラスを継承し、かつECのCORBAオペレー
# ションを実装しなければならない。さらに、実際にロジックを駆動するた
# め、幾つかの約束に則りExecutionContextBaseの関数を呼び出す必要があ
# る。ECのCORBAオペレーションは以下のものがあり、それぞれ
# ExecutionContextBaseのメンバ関数に対応している。
#
# - is_running(): ExecutionContextBase.isRunning()
# - start(): ExecutionContextBase.start()
# - stop(): ExecutionContextBase.stop()
#
# - get_rate(): ExecutionContextBase.gatRate()
# - set_rate(): ExecutioinContextBase.setRate()
#
# - add_component(): ExecutionContextBase.addComponent()
# - remove_component(): ExecutionContextBase.removeComponent()
#
# - activate_component(): ExecutionContextBase.activateComponent()
# - deactivate_component(): ExecutionContextBase.deactivateComponent()
# - reset_component(): ExecutionContextBase.resetComponent()
#
# - get_component_state(): ExecutionContextBase.getComponentState()
# - get_kind(): ExecutionContextBase.getKind()
# - get_profile(): ExecutionContextBase.getProfile()
#
# @par 実行状態に関係する関数と実装方法
# - is_running(): ExecutionContextBase.isRunning()
# - start(): ExecutionContextBase.start()
# - stop(): ExecutionContextBase.stop()
#
# 実行状態に関係する関数は、is_running(), start(), stop() の3つがあ
# る。ExecutionContextBaseでは単純に running/stopped のフラグを持っ
# ており、start/stopでフラグのON/OFF切り替え、is_running()で状態読み
# 出しを行っている。通常、ECの実装クラスでは、protected な仮想メン
# バ関数 onStarting(), onStarted(), onStopping(), onStopped() 関数を
# 実装したうえで、CORBAオペレーションを以下のように実装する必要がある。
#
# is_running() のCORBAオペレーションでは、単純に
# ExecutionContextBase の isRunning() を呼び出すだけである。この関数
# に関連する protected 仮想関数はonIsRunning() が用意されているが、
# 通常特に実装する必要はない。あえて、現在の running/stopped 状態を
# 書き換えたい場合にこの関数を利用することができるが推奨はされない。
#
# <pre>
# public:
#  CORBA::Boolean is_runing()
#  {
#    return ExecutionContextBase::isRunning();
#  }
# protected:
#  CORBA::Boolean onIsRunning(CORBA::Boolean running)
#  {
#    return running;
#  }
# </pre>
#
# start(), stop() CORBAオペレーションでは、通常
# ExecutionContextBase の start(), stop() 関数を呼び出すよう実装する。
# この関数に関連する protected 仮想関数は、start() および stop() に
# ついてそれぞれ2つづつの onStarting(), onStarted(), および
# onStopping(), onStopped() 関数がある。ECの実装クラスにおいては、そ
# れぞれ以下のように実装する。
#
# <pre>
#  RTC::ReturnCode_t start()
#  {
#    return ExecutionContextBase::start();
#  }
#  RTC::ReturnCode_t stop()
#  {
#    return ExecutionContextBase::stop();
#  }
# protected:
#  RTC::ReturnCode_t onStarting()
#  {
#    RTC::ReturnCode_t ret = // スレッドを開始する処理など
#    return ret;
#  }
#  RTC::ReturnCode_t onStarted()
#  {
#    RTC::ReturnCode_t ret = // スレッドを開始する処理など
#    return ret;
#  }
#  RTC::ReturnCode_t onStopping()
#  {
#    // スレッドを停止する処理など
#    return retcode;
#  }
#  RTC::ReturnCode_t onStopped()
#  {
#    // スレッドを停止する処理など
#    return retcode;
#  }
# </pre>
#
# @par 実行周期に関する関数と実装方法
# - get_rate(): ExecutionContextBase.gatRate()
# - set_rate(): ExecutioinContextBase.setRate()
#
# 実行周期に関する関数は set_rate(), get_rate() の2種類がある。実装
# する実行コンテキストがもし set_rate() により指定される周期を利用する
# 場合、テンプレート関数 onSetRate() をオーバーライドし実装する。
# onSetRate() は引数に double 型の周期を取り、この値は正当な値である
# ことが保証されている。onSetRate() がRTC::RTC_OK 以外の値を返した場
# 合、ECのProfileの周期は設定される以前の値を保持することが保証され
# る。
#
# set_rate() 同様 get_rate() 呼び出し時にonGetRate() が呼び出される
# が、これは通常オーバーライドする必要はない。ただし、get_rate() が
# 返す値を変更したい場合、onGetRate() をオーバーライドすることでその
# 値を書き換えることができる。ただし、これは推奨されない。
#
# <pre>
# public:
#  RTC::ReturnCode_t set_rate(double rate)
#  {
#    return setRate(rate);
#  }
#  double get_rate(void) const
#  {
#    return getRate();
#  }
# protected:
#  virtual RTC::ReturnCode_t onSetRate(double rate)
#  {
#    RTC::ReturnCode_t ret = // 周期を設定する何らかの処理
#    if (ret != RTC::RTC_OK)
#      {
#        RTC_ERROR(("Error message"));
#      }
#    return ret;
#  }
#  virtual double onGetRate(rate)
#  {
#    // get_rate() が返す値を加工したい場合
#    // 通常はこの関数を実装する必要はない。
#    return rate;
#  }
# </pre>
#
# @par コンポーネントの追加と削除に関する関数
# - add_component(): ExecutionContextBase.addComponent()
# - remove_component(): ExecutionContextBase.removeComponent()
#
# コンポーネントの追加と削除に関する関数は、add_component(),
# remove_component() の二種類がある。実行コンテキストの実装クラスに
# おいては、ExecutionContextBase のそれぞれ addComponent(),
# removeComponent() を呼び出す形で実装を行う。これらの関数に関連する
# protected 仮想関数は onAddingComponent(), onAddedComponent(),
# onRemovingComponent(), onRemovedComponent() の4種類ある。ただし、
# これらの仮想関数は通常オーバーライドする必要はなく、使用は推奨され
# ない。
#
# <pre>
# public:
#  RTC::ReturnCode_t add_component(RTC::LightweightRTObject_ptr comp)
#  {
#    return ExecutionContextBase::addComponent(comp);
#  }
#  RTC::ReturnCode_t remove_component(RTC::LightweightRTObject_ptr comp)
#  {
#    return ExecutionContextBase::removeComponent(comp);
#  }
# protected:
#  virtual RTC::ReturnCode_t
#  onAddingComponent(RTC::LightweightRTObject rtobj)
#  {
#     // コンポーネント追加時に実行したい処理を記述
#     // RTC::RTC_OK 以外を返した場合、コンポーネントの追加は行われない。
#     return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onAddedComponent(RTC::LightweightRTObject rtobj)
#  {
#     // コンポーネント追加時に実行したい処理を記述
#     // RTC::RTC_OK 以外を返した場合、removeComponent() が呼び出され、
#     // 追加されたコンポーネントが削除される。
#     return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onRemovingComponent(RTC::LightweightRTObject rtobj)
#  {
#     // コンポーネント削除時に実行したい処理を記述
#     // RTC::RTC_OK 以外を返した場合、コンポーネントの削除は行われない。
#     return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onRemovedComponent(RTC::LightweightRTObject rtobj)
#  {
#     // コンポーネント追加時に実行したい処理を記述
#     // RTC::RTC_OK 以外を返した場合、addComponent() が呼び出され、
#     // 削除されたコンポーネントが再び追加される。
#     return RTC::RTC_OK;
#  }
# </pre>
#
# @par コンポーネントのアクティブ化等に関する関数
# - activate_component(): ExecutionContextBase.activateComponent()
# - deactivate_component(): ExecutionContextBase.deactivateComponent()
# - reset_component(): ExecutionContextBase.resetComponent()
#
# コンポーネントのアクティブ化等に関する関数は、
# activate_component(), deactivate_component(), reset_component() の
# 三種類がある。実行コンテキストの実装クラスにおいては、
# ExecutionContextBase のそれぞれ activateComponent(),
# deactivateComponent(), resetComponent() を呼び出す形で実装を行う。
# これらの関数に関連する protected 仮想関数は
# onActivatingComponent(), onAtivatingComponent(),
# onActivatedComponent(), onDeactivatingComponent(),
# onDeactivatedComponent(), onResettingComponent(),
# onResetComponent() の6種類ある。ただし、これらの仮想関数は通常オー
# バーライドする必要はなく、使用は推奨されない。
#
# <pre>
# public:
#  RTC::ReturnCode_t add_component(RTC::LightweightRTObject_ptr comp)
#  {
#    return ExecutionContextBase::addComponent(comp);
#  }
#  RTC::ReturnCode_t remove_component(RTC::LightweightRTObject_ptr comp)
#  {
#    return ExecutionContextBase::removeComponent(comp);
#  }
# protected:
#  virtual RTC::ReturnCode_t
#  onAddingComponent(RTC::LightweightRTObject rtobj)
#  {
#    // コンポーネント追加時に実行したい処理を記述
#    // RTC::RTC_OK 以外を返した場合、コンポーネントの追加は行われない。
#    return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onAddedComponent(RTC::LightweightRTObject rtobj)
#  {
#    // コンポーネント追加時に実行したい処理を記述
#    // RTC::RTC_OK 以外を返した場合、removeComponent() が呼び出され、
#    // 追加されたコンポーネントが削除される。
#    return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onRemovingComponent(RTC::LightweightRTObject rtobj)
#  {
#    // コンポーネント削除時に実行したい処理を記述
#    // RTC::RTC_OK 以外を返した場合、コンポーネントの削除は行われない。
#    return RTC::RTC_OK;
#  }
#  virtual RTC::ReturnCode_t
#  onRemovedComponent(RTC::LightweightRTObject rtobj)
#  {
#    // コンポーネント追加時に実行したい処理を記述
#    // RTC::RTC_OK 以外を返した場合、addComponent() が呼び出され、
#    // 削除されたコンポーネントが再び追加される。
#    return RTC::RTC_OK;
#  }
# </pre>
#
# @par 実行コンテキストの情報取得に関する関数
# - get_component_state(): ExecutionContextBase.getComponentState()
# - get_kind(): ExecutionContextBase.getKind()
# - get_profile(): ExecutionContextBase.getProfile()
#
# 実行コンテキストの情報取得に関する関数は、get_component_state(),
# get_kind(), get_profile() の3種類がある。実行コンテキストの実装ク
# ラスにおいては、ExecutionContextBase のそれぞれ
# getComponentState(), getKind(), getProfile() を呼び出す形で実装を
# 行う。これらの関数に関連する protected 仮想関数は
# onGetComponentState(), onGetKind(), onGetProfile() の3種類ある。こ
# れらの仮想関数は通常オーバーライドする必要はなく、使用は推奨されな
# い。ただし、返す情報を変更したい場合は、これらの関数を適切に実装す
# ることで、呼び出し側に返す値を上書きすることができる。
#
# <pre>
# public:
#  LifeCycleState get_component_state(RTC::LightweightRTObject_ptr comp)
#  {
#    return getComponentState(comp);
#  }
#  ExecutionKind PeriodicExecutionContext::get_kind()
#  {
#    return getKind();
#  }
#  ExecutionContextProfile* get_profile()
#  {
#    return getProfile();
#  }
#
# protected:
#  virtual LifeCycleState onGetComponentState(LifeCycleState state)
#  { // 返すstateを書き換えたい場合はこの関数を実装する
#    return state;
#  }
#  virtual ExecutionKind onGetKind(ExecutionKind kind)
#  { // 返すkindを書き換えたい場合はこの関数を実装する
#    return kind;
#  }
#  virtual ExecutionContextProfile*
#  onGetProfile(ExecutionContextProfile*& profile)
#  { // 返すprofileを書き換えたい場合はこの関数を実装する
#    return profile;
#  }
# </pre>
#
# ExecutionContextの基底クラス。
#
# @since 0.4.0
#
# @else
# @class ExecutionContextBase
# @brief A base class for ExecutionContext
#
# A base class of ExecutionContext.
#
# @since 0.4.0
#
# @endif
#


class ExecutionContextBase:
    """
    """

    def __init__(self, name):
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("ec_base")
        self._activationTimeout = OpenRTM_aist.TimeValue(0.5)
        self._deactivationTimeout = OpenRTM_aist.TimeValue(0.5)
        self._resetTimeout = OpenRTM_aist.TimeValue(0.5)
        self._syncActivation = True
        self._syncDeactivation = True
        self._syncReset = True
        self._worker = OpenRTM_aist.ExecutionContextWorker()
        self._profile = OpenRTM_aist.ExecutionContextProfile()

    ##
    # @if jp
    # @brief ExecutionContextの初期化処理
    #
    # @else
    # @brief Initialization function of the ExecutionContext
    #
    # @endif
    # virtual void init(coil::Properties& props);

    def init(self, props):
        self._rtcout.RTC_TRACE("init()")
        self._rtcout.RTC_DEBUG(props)

        # setting rate
        self.setExecutionRate(props)

        # getting sync/async mode flag
        transitionMode_ = False
        ret, transitionMode_ = self.setTransitionMode(
            props, "sync_transition", transitionMode_)
        if ret:
            self._syncActivation = transitionMode_
            self._syncDeactivation = transitionMode_
            self._syncReset = transitionMode_

        syncactivation_ = self._syncActivation
        syncdeactivation_ = self._syncDeactivation
        syncreset_ = self._syncReset
        _, syncactivation_ = self.setTransitionMode(
            props, "sync_activation", syncactivation_)
        _, syncdeactivation_ = self.setTransitionMode(
            props, "sync_deactivation", syncdeactivation_)
        _, syncreset_ = self.setTransitionMode(props, "sync_reset", syncreset_)
        self._syncActivation = syncactivation_
        self._syncDeactivation = syncdeactivation_
        self._syncReset = syncreset_

        # getting transition timeout
        timeout_ = 0.0
        ret, timeout_ = self.setTimeout(props, "transition_timeout", timeout_)
        if ret:
            self._activationTimeout = timeout_
            self._deactivationTimeout = timeout_
            self._resetTimeout = timeout_

        activationTO_ = self._activationTimeout
        deactivationTO_ = self._deactivationTimeout
        resetTO_ = self._resetTimeout
        _, activationTO_ = self.setTimeout(
            props, "activation_timeout", activationTO_)
        _, deactivationTO_ = self.setTimeout(
            props, "deactivation_timeout", deactivationTO_)
        _, resetTO_ = self.setTimeout(props, "reset_timeout", resetTO_)
        self._activationTimeout = activationTO_
        self._deactivationTimeout = deactivationTO_
        self._resetTimeout = resetTO_

        self._rtcout.RTC_DEBUG("ExecutionContext's configurations:")
        self._rtcout.RTC_DEBUG("Exec rate   : %f [Hz]", self.getRate())

        def toSTR_(x): return "YES" if x else "NO"

        self._rtcout.RTC_DEBUG("Activation  : Sync = %s, Timeout = %f",
                               (toSTR_(self._syncActivation), float(self._activationTimeout.toDouble())))
        self._rtcout.RTC_DEBUG("Deactivation: Sync = %s, Timeout = %f",
                               (toSTR_(self._syncActivation), float(self._deactivationTimeout.toDouble())))
        self._rtcout.RTC_DEBUG("Reset       : Sync = %s, Timeout = %f",
                               (toSTR_(self._syncReset), float(self._resetTimeout.toDouble())))
        # Setting given Properties to EC's profile::properties
        self.setProperties(props)
        return

    ##
    # @if jp
    # @brief ExecutionContextの終了処理
    #
    # @else
    # @brief
    #
    # @endif
    # virtual void exit();
    def exit(self):
        self._rtcout.RTC_TRACE("exit()")
        ret_ = self._worker.removeComponent(self._profile.getOwner())
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: ECWorker removeComponent() faild.")
        self._profile.exit()
        self._worker.exit()

    ##
    # @if jp
    # @brief ExecutionContextの処理を進める(サブクラス実装用)
    #
    # ExecutionContextの処理を１周期分進める。<BR>
    # ※サブクラスでの実装参照用
    #
    # @param self
    #
    # @else
    # @brief Destructor
    # @endif
    # def tick(self):
    #  pass

    ##
    # @if jp
    # @brief コンポーネントをバインドする。
    #
    # コンポーネントをバインドする。
    #
    # @else
    # @brief Bind the component.
    #
    # Bind the component.
    #
    # @endif

    def bindComponent(self, rtc):
        self.setOwner(rtc.getObjRef())
        return self._worker.bindComponent(rtc)

    # ============================================================
    # Functions to be delegated by EC's CORBA operations

    ##
    # @if jp
    # @brief ExecutionContext 実行状態確認関数
    # @else
    # @brief Check for ExecutionContext running state
    # @endif
    # CORBA::Boolean ExecutionContextBase::isRunning()

    def isRunning(self):
        self._rtcout.RTC_TRACE("isRunning()")
        return self._worker.isRunning()

    ##
    # @if jp
    # @brief ExecutionContext の実行を開始
    # @else
    # @brief Start the ExecutionContext
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::start()

    def start(self):
        self._rtcout.RTC_TRACE("start()")
        ret_ = self.onStarting()  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onStarting() failed. Starting EC aborted.")
            return ret_

        ret_ = self._worker.start()  # Actual start()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR(
                "Invoking on_startup() for each RTC failed.")
            return ret_

        ret_ = self.onStarted()  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onStartted() failed. Started EC aborted..")
            self._worker.stop()
            self._rtcout.RTC_ERROR(
                "on_shutdown() was invoked, because of onStarted")
            return ret_

        return ret_

    ##
    # @if jp
    # @brief ExecutionContext の実行を停止
    # @else
    # @brief Stopping the ExecutionContext
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::stop()

    def stop(self):
        self._rtcout.RTC_TRACE("stop()")
        ret_ = self.onStopping()  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onStopping() failed. Stopping EC aborted.")
            return ret_

        ret_ = self._worker.stop()  # Actual stop()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR(
                "Invoking on_shutdown() for each RTC failed.")
            return ret_

        ret_ = self.onStopped()  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onStopped() failed. Stopped EC aborted.")
            return ret_

        return ret_

    ##
    # @if jp
    # @brief ExecutionContext の実行周期(Hz)を取得する
    #
    # Active 状態にてRTコンポーネントが実行される周期(単位:Hz)を取得す
    # る。
    #
    # @return 処理周期(単位:Hz)
    #
    # @else
    #
    # @brief Get execution rate(Hz) of ExecutionContext
    #
    # This operation shall return the rate (in hertz) at which its
    # Active participating RTCs are being invoked.
    #
    # @return Execution cycle(Unit:Hz)
    #
    # @endif
    # double getRate(void) const

    def getRate(self):
        rate_ = self._profile.getRate()  # Actual getRate()
        return self.onGetRate(rate_)  # Template

    # coil::TimeValue ExecutionContextBase::getPeriod(void) const

    def getPeriod(self):
        return self._profile.getPeriod()

    ##
    # @if jp
    # @brief ExecutionContext の実行周期(Hz)を設定する
    #
    # Active 状態にてRTコンポーネントが実行される周期(単位:Hz)を設定す
    # る。実行周期の変更は、DataFlowComponentAction の
    # on_rate_changed によって各RTコンポーネントに伝達される。
    #
    # @param rate 処理周期(単位:Hz)
    #
    # @return ReturnCode_t 型のリターンコード
    #         RTC_OK: 正常終了
    #         BAD_PARAMETER: 設定値が負の値
    #
    # @else
    #
    # @brief Set execution rate(Hz) of ExecutionContext
    #
    # This operation shall set the rate (in hertz) at which this
    # context’s Active participating RTCs are being called.  If the
    # execution kind of the context is PERIODIC, a rate change shall
    # result in the invocation of on_rate_changed on any RTCs
    # realizing DataFlowComponentAction that are registered with any
    # RTCs participating in the context.
    #
    # @param rate Execution cycle(Unit:Hz)
    #
    # @return The return code of ReturnCode_t type
    #         RTC_OK: Succeed
    #         BAD_PARAMETER: Invalid value. The value might be negative.
    #
    # @endif
    # RTC::ReturnCode_t setRate(double rate)

    def setRate(self, rate):
        self._rtcout.RTC_TRACE("setRate(%f)", rate)
        ret_ = self._profile.setRate(self.onSettingRate(rate))
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Setting execution rate failed. %f", rate)
            return ret_

        ret_ = self._worker.rateChanged()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR(
                "Invoking on_rate_changed() for each RTC failed.")
            return ret_

        ret_ = self.onSetRate(rate)
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onSetRate(%f) failed.", rate)
            return ret_

        self._rtcout.RTC_INFO("setRate(%f) done", rate)
        return ret_

    ##
    # @if jp
    # @brief RTコンポーネントを追加する
    # @else
    # @brief Add an RT-component
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::
    # addComponent(RTC::LightweightRTObject_ptr comp)
    def addComponent(self, comp):

        self._rtcout.RTC_TRACE("addComponent()")
        ret_ = self.onAddingComponent(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR(
                "Error: onAddingComponent(). RTC is not attached.")
            return ret_

        ret_ = self._worker.addComponent(comp)  # Actual addComponent()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: ECWorker addComponent() faild.")
            return ret_

        ret_ = self._profile.addComponent(comp)  # Actual addComponent()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: ECProfile addComponent() faild.")
            return ret_

        ret_ = self.onAddedComponent(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: onAddedComponent() faild.")
            self._rtcout.RTC_INFO("Removing attached RTC.")
            self._worker.removeComponent(comp)
            self._profile.removeComponent(comp)
            return ret_

        self._rtcout.RTC_INFO("Component has been added to this EC.")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief RTコンポーネントを参加者リストから削除する
    # @else
    # @brief Remove the RT-Component from participant list
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::
    # removeComponent(RTC::LightweightRTObject_ptr comp)

    def removeComponent(self, comp):
        self._rtcout.RTC_TRACE("removeComponent()")
        ret_ = self.onRemovingComponent(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: onRemovingComponent(). "
                                   "RTC will not not attached.")
            return ret_

        ret_ = self._worker.removeComponent(comp)  # Actual removeComponent()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: ECWorker removeComponent() faild.")
            return ret_

        ret_ = self._profile.removeComponent(comp)  # Actual removeComponent()
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: ECProfile removeComponent() faild.")
            return ret_

        ret_ = self.onRemovedComponent(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("Error: onRemovedComponent() faild.")
            self._rtcout.RTC_INFO("Removing attached RTC.")
            self._worker.removeComponent(comp)
            self._profile.removeComponent(comp)
            return ret_

        self._rtcout.RTC_INFO("Component has been removeed to this EC.")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief RTコンポーネントをアクティブ化する
    # @else
    # @brief Activate an RT-component
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::
    # activateComponent(RTC::LightweightRTObject_ptr comp)

    def activateComponent(self, comp):
        self._rtcout.RTC_TRACE("activateComponent()")
        ret_ = self.onActivating(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onActivating() failed.")
            return ret_

        ret_, rtobj_ = self._worker.activateComponent(
            comp)  # Actual activateComponent()
        if ret_ != RTC.RTC_OK:
            return ret_

        if not self._syncActivation:  # Asynchronous activation mode
            ret_ = self.onActivated(rtobj_, -1)
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onActivated() failed.")

            return ret_

        # ------------------------------------------------------------
        # Synchronized activation mode
        self._rtcout.RTC_DEBUG("Synchronous activation mode. "
                               "Waiting for the RTC to be ACTIVE state. ")
        return self.waitForActivated(rtobj_)

    # RTC::ReturnCode_t ExecutionContextBase::
    # waitForActivated(RTC_impl::RTObjectStateMachine* rtobj)

    def waitForActivated(self, rtobj):
        count_ = 0
        ret_ = self.onWaitingActivated(rtobj, count_)
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onWaitingActivated failed.")
            return ret_

        cycle_ = int(float(self._activationTimeout.toDouble()) /
                     float(self.getPeriod().toDouble()))
        self._rtcout.RTC_DEBUG("Timeout is %f [s] (%f [s] in %d times)",
                               (float(self._activationTimeout.toDouble()), self.getRate(), cycle_))
        # Wating INACTIVE -> ACTIVE
        starttime_ = OpenRTM_aist.Time().gettimeofday()

        while rtobj.isCurrentState(RTC.INACTIVE_STATE):

            ret_ = self.onWaitingActivated(rtobj, count_)  # Template method
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onWaitingActivated failed.")
                return ret_

            time.sleep(self.getPeriod().toDouble())
            delta_ = OpenRTM_aist.Time().gettimeofday() - starttime_
            self._rtcout.RTC_DEBUG("Waiting to be ACTIVE state. %f [s] slept (%d/%d)",
                                   (float(delta_.toDouble()), count_, cycle_))
            count_ += 1
            if delta_.toDouble() > self._activationTimeout.toDouble() or count_ > cycle_:
                self._rtcout.RTC_WARN("The component is not responding.")
                break

        # Now State must be ACTIVE or ERROR
        if rtobj.isCurrentState(RTC.INACTIVE_STATE):
            self._rtcout.RTC_ERROR("Unknown error: Invalid state transition.")
            return RTC.RTC_ERROR

        if rtobj.isCurrentState(RTC.ERROR_STATE):
            self._rtcout.RTC_ERROR(
                "State of the RTC transitioned to ERROR_STATE.")
            return RTC.PRECONDITION_NOT_MET

        self._rtcout.RTC_DEBUG(
            "Current state is %s",
            self.getStateString(
                rtobj.getState()))
        ret_ = self.onActivated(rtobj, count_)  # Template method
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onActivated() failed.")

        self._rtcout.RTC_DEBUG("onActivated() done.")
        return ret_

    ##
    # @if jp
    # @brief RTコンポーネントを非アクティブ化する
    # @else
    # @brief Deactivate an RT-component
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::
    # deactivateComponent(RTC::LightweightRTObject_ptr comp)

    def deactivateComponent(self, comp):
        self._rtcout.RTC_TRACE("deactivateComponent()")
        ret_ = self.onDeactivating(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onDeactivating() failed.")
            return ret_

        # Deactivate all the RTCs
        ret_, rtobj_ = self._worker.deactivateComponent(comp)
        if ret_ != RTC.RTC_OK:
            return ret_

        if not self._syncDeactivation:
            ret_ = self.onDeactivated(rtobj_, -1)
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onDeactivated() failed.")
            return ret_

        # ------------------------------------------------------------
        # Waiting for synchronized deactivation
        self._rtcout.RTC_DEBUG("Synchronous deactivation mode. "
                               "Waiting for the RTC to be INACTIVE state. ")
        return self.waitForDeactivated(rtobj_)

    # RTC::ReturnCode_t ExecutionContextBase::
    # waitForDeactivated(RTC_impl::RTObjectStateMachine* rtobj)

    def waitForDeactivated(self, rtobj):
        count_ = 0
        ret_ = self.onWaitingDeactivated(rtobj, count_)
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onWaitingDeactivated failed.")
            return ret_

        cycle_ = int(
            float(
                self._deactivationTimeout.toDouble()) /
            float(
                self.getPeriod().toDouble()))
        self._rtcout.RTC_DEBUG("Timeout is %f [s] (%f [s] in %d times)",
                               (float(self._deactivationTimeout.toDouble()), self.getRate(), cycle_))
        # Wating ACTIVE -> INACTIVE
        starttime_ = OpenRTM_aist.Time().gettimeofday()
        while rtobj.isCurrentState(RTC.ACTIVE_STATE):
            ret_ = self.onWaitingDeactivated(rtobj, count_)  # Template method
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onWaitingDeactivated failed.")
                return ret_

            time.sleep(self.getPeriod().toDouble())
            delta_ = OpenRTM_aist.Time().gettimeofday() - starttime_
            self._rtcout.RTC_DEBUG("Waiting to be INACTIVE state. Sleeping %f [s] (%d/%d)",
                                   (float(delta_.toDouble()), count_, cycle_))
            count_ += 1
            if delta_.toDouble() > self._deactivationTimeout.toDouble() or count_ > cycle_:
                self._rtcout.RTC_ERROR("The component is not responding.")
                break

        # Now State must be INACTIVE or ERROR
        if rtobj.isCurrentState(RTC.ACTIVE_STATE):
            self._rtcout.RTC_ERROR("Unknown error: Invalid state transition.")
            return RTC.RTC_ERROR

        if rtobj.isCurrentState(RTC.ERROR_STATE):
            self._rtcout.RTC_ERROR(
                "State of the RTC transitioned to ERROR_STATE.")
            return RTC.PRECONDITION_NOT_MET

        self._rtcout.RTC_DEBUG(
            "Current state is %s",
            self.getStateString(
                rtobj.getState()))
        ret_ = self.onDeactivated(rtobj, count_)
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onDeactivated() failed.")

        self._rtcout.RTC_DEBUG("onDeactivated() done.")
        return ret_

    ##
    # @if jp
    # @brief RTコンポーネントをリセットする
    # @else
    # @brief Reset the RT-component
    # @endif
    # RTC::ReturnCode_t ExecutionContextBase::
    # resetComponent(RTC::LightweightRTObject_ptr comp)

    def resetComponent(self, comp):
        self._rtcout.RTC_TRACE("resetComponent()")
        ret_ = self.onResetting(comp)  # Template
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onResetting() failed.")
            return ret_

        ret_, rtobj_ = self._worker.resetComponent(
            comp)  # Actual resetComponent()
        if ret_ != RTC.RTC_OK:
            return ret_
        if not self._syncReset:
            ret_ = self.onReset(rtobj_, -1)
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onReset() failed.")
            return ret_

        # ------------------------------------------------------------
        # Waiting for synchronized reset
        self._rtcout.RTC_DEBUG("Synchronous reset mode. "
                               "Waiting for the RTC to be INACTIVE state. ")
        return self.waitForReset(rtobj_)

    # RTC::ReturnCode_t ExecutionContextBase::
    # waitForReset(RTC_impl::RTObjectStateMachine* rtobj)

    def waitForReset(self, rtobj):
        count_ = 0
        ret_ = self.onWaitingReset(rtobj, count_)
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onWaitingReset() failed.")
            return ret_

        cycle_ = int(float(self._resetTimeout.toDouble()) /
                     float(self.getPeriod().toDouble()))
        self._rtcout.RTC_DEBUG("Timeout is %f [s] (%f [s] in %d times)",
                               (float(self._resetTimeout.toDouble()), self.getRate(), cycle_))
        # Wating ERROR -> INACTIVE
        starttime_ = OpenRTM_aist.Time().gettimeofday()
        while rtobj.isCurrentState(RTC.ERROR_STATE):
            ret_ = self.onWaitingReset(rtobj, count_)  # Template
            if ret_ != RTC.RTC_OK:
                self._rtcout.RTC_ERROR("onWaitingReset failed.")
                return ret_

            time.sleep(self.getPeriod().toDouble())
            delta_ = OpenRTM_aist.Time().gettimeofday() - starttime_
            self._rtcout.RTC_DEBUG("Waiting to be INACTIVE state. Sleeping %f [s] (%d/%d)",
                                   (float(delta_.toDouble()), count_, cycle_))
            count_ += 1
            if delta_.toDouble() > self._resetTimeout.toDouble() or count_ > cycle_:
                self._rtcout.RTC_ERROR("The component is not responding.")
                break

        # Now State must be INACTIVE
        if not rtobj.isCurrentState(RTC.INACTIVE_STATE):
            self._rtcout.RTC_ERROR("Unknown error: Invalid state transition.")
            return RTC.RTC_ERROR

        self._rtcout.RTC_DEBUG(
            "Current state is %s",
            self.getStateString(
                rtobj.getState()))
        ret_ = self.onReset(rtobj, count_)  # Template method
        if ret_ != RTC.RTC_OK:
            self._rtcout.RTC_ERROR("onResetd() failed.")

        self._rtcout.RTC_DEBUG("onReset() done.")
        return ret_

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
    # RTC::LifeCycleState ExecutionContextBase::
    # getComponentState(RTC::LightweightRTObject_ptr comp)

    def getComponentState(self, comp):
        state_ = self._worker.getComponentState(comp)
        self._rtcout.RTC_TRACE(
            "getComponentState() = %s",
            self.getStateString(state_))
        if state_ == RTC.CREATED_STATE:
            self._rtcout.RTC_ERROR("CREATED state: not initialized "
                                   "RTC or unknwon RTC specified.")

        return self.onGetComponentState(state_)

    # const char* ExecutionContextBase::getStateString(RTC::LifeCycleState
    # state)

    def getStateString(self, state):
        return self._worker.getStateString(state)

    ##
    # @if jp
    # @brief ExecutionKind を取得する
    #
    # 本 ExecutionContext の ExecutionKind を取得する
    #
    # @return ExecutionKind
    #
    # @else
    #
    # @brief Get the ExecutionKind
    #
    # This operation shall report the execution kind of the execution
    # context.
    #
    # @return ExecutionKind
    #
    # @endif
    # RTC::ExecutionKind ExecutionContextBase::getKind(void) const

    def getKind(self):
        kind_ = self._profile.getKind()
        self._rtcout.RTC_TRACE("getKind() = %s", self.getKindString(kind_))
        kind_ = self.onGetKind(kind_)
        self._rtcout.RTC_DEBUG(
            "onGetKind() returns %s",
            self.getKindString(kind_))
        return kind_

    ##
    # @if jp
    # @brief Profileを取得する
    #
    # RTC::ExecutionContextProfile を取得する。取得した
    # ExecutionContextProfile の所有権は呼び出し側にある。取得されたオ
    # ブジェクトが不要になった場合、呼び出し側が開放する責任を負う。
    #
    # @return RTC::ExecutionContextProfile
    #
    # @else
    # @brief Getting Profile
    #
    # This function gets RTC::ExecutionContextProfile.  The ownership
    # of the obtained ExecutionContextProfile is given to caller. The
    # caller should release obtained object when it is unneccessary
    # anymore.
    #
    # @return RTC::ExecutionContextProfile
    #
    # @endif
    # RTC::ExecutionContextProfile* ExecutionContextBase::getProfile(void)

    def getProfile(self):
        self._rtcout.RTC_TRACE("getProfile()")
        prof_ = self._profile.getProfile()
        self._rtcout.RTC_DEBUG("kind: %s", self.getKindString(prof_.kind))
        self._rtcout.RTC_DEBUG("rate: %f", prof_.rate)
        self._rtcout.RTC_DEBUG("properties:")
        props_ = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(props_, prof_.properties)
        self._rtcout.RTC_DEBUG(props_)
        return self.onGetProfile(prof_)

    # ============================================================
    # Delegated functions to ExecutionContextProfile
    # ============================================================
    ##
    # @if jp
    # @brief CORBA オブジェクト参照の取得
    #
    # 本オブジェクトの ExecutioncontextService としての CORBA オブジェ
    # クト参照を取得する。
    #
    # @return CORBA オブジェクト参照
    #
    # @else
    # @brief Get the reference to the CORBA object
    #
    # Get the reference to the CORBA object as
    # ExecutioncontextService of this object.
    #
    # @return The reference to CORBA object
    #
    # @endif
    # void setObjRef(RTC::ExecutionContextService_ptr ec_ptr)

    def setObjRef(self, ec_ptr):
        self._worker.setECRef(ec_ptr)
        self._profile.setObjRef(ec_ptr)
        return

    ##
    # @if jp
    # @brief CORBA オブジェクト参照の取得
    #
    # 本オブジェクトの ExecutioncontextService としての CORBA オブジェ
    # クト参照を取得する。
    #
    # @return CORBA オブジェクト参照
    #
    # @else
    # @brief Get the reference to the CORBA object
    #
    # Get the reference to the CORBA object as
    # ExecutioncontextService of this object.
    #
    # @return The reference to CORBA object
    #
    # @endif

    def getObjRef(self):
        return self._profile.getObjRef()

    ##
    # @if jp
    # @brief ExecutionKind を文字列化する
    #
    # RTC::ExecutionKind で定義されている PERIODIC, EVENT_DRIVEN,
    # OTHER を文字列化する。
    #
    # @param kind ExecutionKind
    # @return 文字列化されたExecutionKind
    #
    # @else
    #
    # @brief Converting ExecutionKind enum to string
    #
    # This function converts enumeration (PERIODIC, EVENT_DRIVEN,
    # OTHER) defined in RTC::ExecutionKind to string.
    #
    # @param kind ExecutionKind
    # @return String of ExecutionKind
    #
    # @endif
    # const char* getKindString(RTC::ExecutionKind kind) const

    def getKindString(self, kind):
        return self._profile.getKindString(kind)

    ##
    # @if jp
    # @brief ExecutionKind を設定する
    #
    # この ExecutionContext の ExecutionKind を設定する
    #
    # @param kind ExecutionKind
    #
    # @else
    #
    # @brief Set the ExecutionKind
    #
    # This operation sets the kind of the execution context.
    #
    # @param kind ExecutionKind
    #
    # @endif
    # RTC::ReturnCode_t setKind(RTC::ExecutionKind kind)

    def setKind(self, kind):
        return self._profile.setKind(kind)

    ##
    # @if jp
    # @brief Ownerコンポーネントをセットする。
    #
    # このECのOwnerとなるRTCをセットする。
    #
    # @param comp OwnerとなるRTコンポーネント
    # @return ReturnCode_t 型のリターンコード
    # @else
    # @brief Setting owner component of the execution context
    #
    # This function sets an RT-Component to be owner of the execution context.
    #
    # @param comp an owner RT-Component of this execution context
    # @return The return code of ReturnCode_t type
    # @endif
    # RTC::ReturnCode_t setOwner(RTC::LightweightRTObject_ptr comp)

    def setOwner(self, comp):
        return self._profile.setOwner(comp)

    ##
    # @if jp
    # @brief Ownerコンポーネントの参照を取得する
    #
    # このECのOwnerであるRTCの参照を取得する。
    #
    # @return OwnerRTコンポーネントの参照
    # @else
    # @brief Getting a reference of the owner component
    #
    # This function returns a reference of the owner RT-Component of
    # this execution context
    #
    # @return a reference of the owner RT-Component
    # @endif
    # const RTC::RTObject_ptr getOwner() const

    def getOwner(self):
        return self._profile.getOwner()

    ##
    # @if jp
    # @brief RTコンポーネントの参加者リストを取得する
    #
    # 現在登録されている参加者RTCのリストを取得する。
    #
    # @return 参加者RTCのリスト
    #
    # @else
    #
    # @brief Getting participant RTC list
    #
    # This function returns a list of participant RTC of the execution context.
    #
    # @return Participants RTC list
    #
    # @endif
    # const RTC::RTCList& getComponentList() const

    def getComponentList(self):
        return self._profile.getComponentList()

    ##
    # @if jp
    # @brief Propertiesをセットする
    #
    # ExecutionContextProfile::properties をセットする。
    #
    # @param props ExecutionContextProfile::properties にセットするプ
    #              ロパティー
    #
    # @else
    # @brief Setting Properties
    #
    # This function sets ExecutionContextProfile::properties by
    # coil::Properties.
    #
    # @param props Properties to be set to
    #              ExecutionContextProfile::properties.
    #
    # @endif
    # void setProperties(coil::Properties& props)

    def setProperties(self, props):
        self._profile.setProperties(props)
        return

    ##
    # @if jp
    # @brief Propertiesを取得する
    #
    # ExecutionContextProfile::properties を取得する。
    #
    # @return coil::Propertiesに変換された
    #              ExecutionContextProfile::properties
    #
    # @else
    # @brief Setting Properties
    #
    # This function sets ExecutionContextProfile::properties by
    # coil::Properties.
    #
    # @param props Properties to be set to ExecutionContextProfile::properties.
    #
    # @endif
    # const coil::Properties getProperties() const

    def getProperties(self):
        return self._profile.getProperties()

    ##
    # @if jp
    # @brief Profileを取得する
    #
    # RTC::ExecutionContextProfile を取得する。取得した
    # ExecutionContextProfile の所有権は呼び出し側にある。取得されたオ
    # ブジェクトが不要になった場合、呼び出し側が開放する責任を負う。
    #
    # @return RTC::ExecutionContextProfile
    #
    # @else
    # @brief Getting Profile
    #
    # This function gets RTC::ExecutionContextProfile.  The ownership
    # of the obtained ExecutionContextProfile is given to caller. The
    # caller should release obtained object when it is unneccessary
    # anymore.
    #
    # @return RTC::ExecutionContextProfile
    #
    # @endif
    # RTC::ExecutionContextProfile* getProfile(void)
    # def getProfile(self):
    #  return self._profile.getProfile()

    # end of delegated functions to ExecutionContextProfile
    # ============================================================

    # ============================================================
    # Delegated functions to ExecutionContextWorker
    # ============================================================
    # bool isAllCurrentState(RTC::LifeCycleState state)

    def isAllCurrentState(self, state):
        return self._worker.isAllCurrentState(state)

    # bool isAllNextState(RTC::LifeCycleState state)
    def isAllNextState(self, state):
        return self._worker.isAllNextState(state)

    # bool isOneOfCurrentState(RTC::LifeCycleState state)
    def isOneOfCurrentState(self, state):
        return self._worker.isOneOfCurrentState(state)

    # bool isOneOfNextState(RTC::LifeCycleState state)
    def isOneOfNextState(self, state):
        return self._worker.isOneOfNextState(state)

    # void invokeWorker()       { m_worker.invokeWorker(); }
    def invokeWorker(self):
        self._worker.invokeWorker()
        return

    # void invokeWorkerPreDo()  { m_worker.invokeWorkerPreDo(); }
    def invokeWorkerPreDo(self):
        self._worker.invokeWorkerPreDo()
        return

    # void invokeWorkerDo()     { m_worker.invokeWorkerDo(); }
    def invokeWorkerDo(self):
        self._worker.invokeWorkerDo()
        return

    # void invokeWorkerPostDo() { m_worker.invokeWorkerPostDo(); }
    def invokeWorkerPostDo(self):
        self._worker.invokeWorkerPostDo()
        return

    # template virtual functions related to start/stop
    # virtual bool onIsRunning(bool running) { return running; }
    def onIsRunning(self, running):
        return running

    # virtual RTC::ReturnCode_t onStarting() { return RTC::RTC_OK; }
    def onStarting(self):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t onStarted() { return RTC::RTC_OK; }
    def onStarted(self):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t onStopping() { return RTC::RTC_OK; }
    def onStopping(self):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t onStopped() { return RTC::RTC_OK; }
    def onStopped(self):
        return RTC.RTC_OK

    # template virtual functions getting/setting execution rate
    # virtual double onGetRate(double rate) const { return rate; }
    def onGetRate(self, rate):
        return rate

    # virtual double onSettingRate(double rate) { return rate; }
    def onSettingRate(self, rate):
        return rate

    # virtual RTC::ReturnCode_t onSetRate(double rate) { return RTC::RTC_OK; }
    def onSetRate(self, rate):
        return RTC.RTC_OK

    # template virtual functions adding/removing component
    # virtual RTC::ReturnCode_t
    # onAddingComponent(RTC::LightweightRTObject_ptr rtobj)
    def onAddingComponent(self, rtobj):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onAddedComponent(RTC::LightweightRTObject_ptr rtobj)
    def onAddedComponent(self, rtobj):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onRemovingComponent(RTC::LightweightRTObject_ptr rtobj)
    def onRemovingComponent(self, rtobj):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onRemovedComponent(RTC::LightweightRTObject_ptr rtobj)
    def onRemovedComponent(self, rtobj):
        return RTC.RTC_OK

    # template virtual functions related to activation/deactivation/reset
    # virtual RTC::ReturnCode_t
    # onActivating(RTC::LightweightRTObject_ptr comp)
    def onActivating(self, comp):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingActivated(RTC_impl::RTObjectStateMachine* comp, long int count)
    def onWaitingActivated(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onActivated(RTC_impl::RTObjectStateMachine* comp,
    #             long int count)
    def onActivated(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onDeactivating(RTC::LightweightRTObject_ptr comp)
    def onDeactivating(self, comp):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingDeactivated(RTC_impl::RTObjectStateMachine* comp, long int
    # count)
    def onWaitingDeactivated(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onDeactivated(RTC_impl::RTObjectStateMachine* comp, long int count)
    def onDeactivated(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t onResetting(RTC::LightweightRTObject_ptr comp)
    def onResetting(self, comp):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onWaitingReset(RTC_impl::RTObjectStateMachine* comp, long int count)
    def onWaitingReset(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::ReturnCode_t
    # onReset(RTC_impl::RTObjectStateMachine* comp, long int count)
    def onReset(self, comp, count):
        return RTC.RTC_OK

    # virtual RTC::LifeCycleState
    # onGetComponentState(RTC::LifeCycleState state)
    def onGetComponentState(self, state):
        return state

    # virtual RTC::ExecutionKind
    # onGetKind(RTC::ExecutionKind kind) const
    def onGetKind(self, kind):
        return kind

    # virtual RTC::ExecutionContextProfile*
    # onGetProfile(RTC::ExecutionContextProfile*& profile)
    def onGetProfile(self, profile):
        return profile

    # ============================================================
    # private functions

    ##
    # @if jp
    # @brief Propertiesから実行コンテキストをセットする
    # @else
    # @brief Setting execution rate from given properties.
    # @endif
    # bool ExecutionContextBase::setExecutionRate(coil::Properties& props)

    def setExecutionRate(self, props):
        if props.findNode("rate"):
            rate_ = 0.0
            ret, rate_ = OpenRTM_aist.stringTo(
                rate_, props.getProperty("rate"))
            if ret:
                self.setRate(rate_)
                return True
        return False

    ##
    # @if jp
    # @brief Propertiesから状態遷移モードをセットする
    # @else
    # @brief Setting state transition mode from given properties.
    # @endif
    # bool ExecutionContextBase::
    # setTransitionMode(coil::Properties& props, const char* key, bool& flag)

    def setTransitionMode(self, props, key, flag=False):
        self._rtcout.RTC_TRACE("setTransitionMode(%s)", key)
        def toSTR_(x): return "YES" if x else "NO"
        if props.findNode(key):
            flag = OpenRTM_aist.toBool(
                props.getProperty(key), "YES", "NO", "YES")
            self._rtcout.RTC_DEBUG("Transition Mode: %s = %s",
                                   (key, toSTR_(flag)))
            return True, flag

        self._rtcout.RTC_DEBUG("Configuration %s not found.", key)
        return False, flag

    ##
    # @if jp
    # @brief Propertiesから状態遷移Timeoutをセットする
    # @else
    # @brief Setting state transition timeout from given properties.
    # @endif
    # bool ExecutionContextBase::
    # setTimeout(coil::Properties& props, const char* key,
    #            coil::TimeValue& timevalue)

    def setTimeout(self, props, key, timevalue=0.0):
        self._rtcout.RTC_TRACE("setTimeout(%s)", key)
        if props.findNode(key):
            timeout_ = 0.0
            ret, timeout_ = OpenRTM_aist.stringTo(
                timeout_, props.getProperty(key))
            if ret:
                timevalue = OpenRTM_aist.TimeValue(timeout_)
                self._rtcout.RTC_DEBUG("Timeout (%s): %f [s]", (key, timeout_))
                return True, timevalue
        self._rtcout.RTC_DEBUG("Configuration %s not found.", key)
        return False, timevalue

    def is_running(self):
        self._rtcout.RTC_TRACE("is_running()")
        return self.isRunning()

    def get_rate(self):
        return self.getRate()

    def set_rate(self, rate):
        return self.setRate(rate)

    def activate_component(self, comp):
        return self.activateComponent(comp)

    def deactivate_component(self, comp):
        return self.deactivateComponent(comp)

    def reset_component(self, comp):
        return self.resetComponent(comp)

    def get_component_state(self, comp):
        return self.getComponentState(comp)

    def get_kind(self):
        return self.getKind()

    def add_component(self, comp):
        return self.addComponent(comp)

    def remove_component(self, comp):
        return self.removeComponent(comp)

    def get_profile(self):
        return self.getProfile()


executioncontextfactory = None


class ExecutionContextFactory(OpenRTM_aist.Factory, ExecutionContextBase):
    def __init__(self):
        OpenRTM_aist.Factory.__init__(self)
        return

    def __del__(self):
        pass

    def instance():
        global executioncontextfactory

        if executioncontextfactory is None:
            executioncontextfactory = ExecutionContextFactory()

        return executioncontextfactory

    instance = staticmethod(instance)
