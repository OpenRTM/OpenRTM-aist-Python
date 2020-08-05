#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ExecutionContextProfile.py
# @brief ExecutionContextProfile class
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

DEFAULT_PERIOD = 0.000001

##
# @if jp
# @class ExecutionContextProfile
# @brief ExecutionContextProfile クラス
#
# @since 1.2.0
#
# @else
# @class ExecutionContextProfile
# @brief ExecutionContextProfile class
#
# @since 1.2.0
#
# @endif


class ExecutionContextProfile:
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
    # ExecutionContextProfile(RTC::ExecutionKind kind = RTC::PERIODIC);
    def __init__(self, kind=RTC.PERIODIC):
        global DEFAULT_PERIOD
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("periodic_ecprofile")
        self._period = OpenRTM_aist.TimeValue(DEFAULT_PERIOD)
        self._rtcout.RTC_TRACE("ExecutionContextProfile.__init__()")
        self._rtcout.RTC_DEBUG("Actual rate: %d [sec], %d [usec]",
                               (self._period.sec(), self._period.usec()))
        self._profileMutex = threading.RLock()
        self._ref = RTC.ExecutionContext._nil
        self._profile = RTC.ExecutionContextProfile(RTC.PERIODIC,
                                                    (1.0 / self._period.toDouble()),
                                                    RTC.DataFlowComponent._nil, [], [])
        return

    ##
    # @if jp
    # @brief ExecitionContextProfile終了処理
    #
    #
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @endif

    def exit(self):
        self._rtcout.RTC_TRACE("exit")

        # cleanup EC's profile
        self._profile.owner = RTC.DataFlowComponent._nil
        self._profile.participants = []
        self._profile.properties = []
        self._ref = RTC.ExecutionContext._nil
        return

    ##
    # @if jp
    # @brief CORBA オブジェクト参照をセット
    #
    # ExecutioncontextService としての CORBA オブジェ
    # クト参照をセットする。
    #
    # @param ec_ptr CORBA オブジェクト参照
    #
    # @else
    # @brief Set the reference to the CORBA object
    #
    # Set the reference to the CORBA object as
    # ExecutioncontextService of this object.
    #
    # @param ec_ptr The reference to CORBA object
    #
    # @endif
    # void setObjRef(RTC::ExecutionContextService_ptr ec_ptr);

    def setObjRef(self, ec_ptr):
        self._rtcout.RTC_TRACE("setObjRef()")
        assert(not CORBA.is_nil(ec_ptr))
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        self._ref = ec_ptr
        del guard
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
    # RTC::ExecutionContextService_ptr getObjRef(void) const;

    def getObjRef(self):
        self._rtcout.RTC_TRACE("getObjRef()")
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        return self._ref

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
    # RTC::ReturnCode_t setRate(double rate);

    def setRate(self, rate):
        self._rtcout.RTC_TRACE("setRate(%f)", rate)
        if rate <= 0.0:
            return RTC.BAD_PARAMETER

        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        self._profile.rate = rate
        self._period = OpenRTM_aist.TimeValue(1.0 / rate)
        return RTC.RTC_OK

    # RTC::ReturnCode_t setPeriod(double sec, coil::TimeValue tv);

    def setPeriod(self, sec=None, tv=None):
        if sec:
            self._rtcout.RTC_TRACE("setPeriod(%f [sec])", sec)
            if sec <= 0.0:
                return RTC.BAD_PARAMETER

            guard = OpenRTM_aist.ScopedLock(self._profileMutex)
            self._profile.rate = 1.0 / sec
            self._period = OpenRTM_aist.TimeValue(sec)
            del guard
            return RTC.RTC_OK
        elif tv:
            self._rtcout.RTC_TRACE("setPeriod(%f [sec])", tv.toDouble())
            if tv.toDouble() < 0.0:
                return RTC.BAD_PARAMETER

            guard = OpenRTM_aist.ScopedLock(self._profileMutex)
            self._profile.rate = 1.0 / tv.toDouble()
            self._period = tv
            del guard
            return RTC.RTC_OK
        return RTC.BAD_PARAMETER

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
    # double getRate(void) const;

    def getRate(self):
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        return self._profile.rate

    # coil::TimeValue getPeriod(void) const;

    def getPeriod(self):
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        return self._period

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
    # const char* getKindString(RTC::ExecutionKind kind) const;

    def getKindString(self, kind=None):
        kinds_ = ["PERIODIC", "EVENT_DRIVEN", "OTHER"]
        if not kind:
            kind_ = self._profile.kind
        else:
            kind_ = kind

        if kind_._v < RTC.PERIODIC._v or kind_._v > RTC.OTHER._v:
            return ""

        return kinds_[kind_._v]

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
    # RTC::ReturnCode_t setKind(RTC::ExecutionKind kind);

    def setKind(self, kind):
        if kind._v < RTC.PERIODIC._v or kind._v > RTC.OTHER._v:
            self._rtcout.RTC_ERROR("Invalid kind is given. %d", kind._v)
            return RTC.BAD_PARAMETER

        self._rtcout.RTC_TRACE("setKind(%s)", self.getKindString(kind))
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        self._profile.kind = kind
        del guard
        return RTC.RTC_OK

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
    # RTC::ExecutionKind getKind(void) const;

    def getKind(self):
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        self._rtcout.RTC_TRACE(
            "%s = getKind()",
            self.getKindString(
                self._profile.kind))
        return self._profile.kind

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
    # RTC::ReturnCode_t setOwner(RTC::LightweightRTObject_ptr comp);

    def setOwner(self, comp):
        self._rtcout.RTC_TRACE("setOwner()")
        if CORBA.is_nil(comp):
            return RTC.BAD_PARAMETER
        rtobj_ = comp._narrow(RTC.RTObject)
        if CORBA.is_nil(rtobj_):
            self._rtcout.RTC_ERROR("Narrowing failed.")
            return RTC.RTC_ERROR

        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        self._profile.owner = rtobj_
        del guard
        return RTC.RTC_OK

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
    # const RTC::RTObject_ptr getOwner() const;

    def getOwner(self):
        self._rtcout.RTC_TRACE("getOwner()")
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        return self._profile.owner

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
            self._rtcout.RTC_ERROR("A nil reference was given.")
            return RTC.BAD_PARAMETER

        rtobj_ = comp._narrow(RTC.RTObject)
        if CORBA.is_nil(rtobj_):
            self._rtcout.RTC_ERROR("Narrowing was failed.")
            return RTC.RTC_ERROR

        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        OpenRTM_aist.CORBA_SeqUtil.push_back(self._profile.participants,
                                             rtobj_)
        del guard
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
            self._rtcout.RTC_ERROR("A nil reference was given.")
            return RTC.BAD_PARAMETER

        rtobj_ = comp._narrow(RTC.RTObject)
        if CORBA.is_nil(rtobj_):
            self._rtcout.RTC_ERROR("Narrowing was failed.")
            return RTC.RTC_ERROR

        guard = OpenRTM_aist.ScopedLock(self._profileMutex)

        index_ = OpenRTM_aist.CORBA_SeqUtil.find(self._profile.participants,
                                                 self.find_participant(rtobj_))
        if index_ < 0:
            self._rtcout.RTC_ERROR(
                "The given RTObject does not exist in the EC.")
            return RTC.BAD_PARAMETER
        OpenRTM_aist.CORBA_SeqUtil.erase(self._profile.participants, index_)
        return RTC.RTC_OK

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
    # const RTC::RTCList& getComponentList() const;

    def getComponentList(self):
        self._rtcout.RTC_TRACE(
            "getComponentList(%d)", len(
                self._profile.participants))
        return self._profile.participants

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
    # void setProperties(coil::Properties& props);

    def setProperties(self, props):
        self._rtcout.RTC_TRACE("setProperties()")
        self._rtcout.RTC_DEBUG(props)
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        OpenRTM_aist.NVUtil.copyFromProperties(self._profile.properties, props)
        del guard
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
    # const coil::Properties getProperties() const;

    def getProperties(self):
        self._rtcout.RTC_TRACE("getProperties()")
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        props_ = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(props_, self._profile.properties)
        del guard
        self._rtcout.RTC_DEBUG(props_)
        return props_

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
    # RTC::ExecutionContextProfile* getProfile(void);

    def getProfile(self):
        self._rtcout.RTC_TRACE("getProfile()")
        guard = OpenRTM_aist.ScopedLock(self._profileMutex)
        return self._profile

    ##
    # @if jp
    # @brief ExecutionContextProfileをロックする
    #
    # このオブジェクトが管理する RTC::ExecutionContextProfile をロックする。
    # ロックが不要になった際にはunlock()でロックを解除しなければならない。
    #
    # @else
    # @brief Getting a lock of RTC::ExecutionContextProfile
    #
    # This function locks  RTC::ExecutionContextProfile in the object.
    # The lock should be released when the lock is unneccessary.
    #
    # @endif
    # void lock() const;

    def lock(self):
        self._profileMutex.acquire()
        return

    ##
    # @if jp
    # @brief ExecutionContextProfileをアンロックする
    #
    # このオブジェクトが管理する RTC::ExecutionContextProfile をアンロッ
    # クする。
    #
    # @else
    # @brief Release a lock of the RTC::ExecutionContextProfile
    #
    # This function release the lock of RTC::ExecutionContextProfile
    # in the object.
    #
    # @endif
    # void unlock() const;

    def unlock(self):
        self._profileMutex.release()
        return

    class find_participant:
        def __init__(self, comp):
            self._comp = comp
            return

        def __call__(self, comp):
            return self._comp._is_equivalent(comp)
