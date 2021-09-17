#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ComponentObserverConsumer.py
# @brief Component observer SDO service consumer implementation
# @date $Date$
# @author Nobuhiko Miyamoto<n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import OpenRTM_aist
import OpenRTM
import RTC
import sys
sys.path.insert(1, ".")


##
# @if jp
# @else
# @endif
#

class ComponentObserverConsumer(OpenRTM_aist.SdoServiceConsumerBase):
    """
    """

    ##
    # @if jp
    # @class ComponentObserverConsumer クラス
    # @brief ComponentObserver モジュール
    #
    # コンポーネントの各種状態をComponentObserverサービスに対してコール
    # バックするためのクラス。ツール等、コンポーネントの状態変化を知りた
    # いエンティティがサービスプロバイダを当該コンポーネントに対してセッ
    # トすると、対応する本コンシューマがアタッチされ、コンポーネントの状
    # 態変化に応じて、update_status() オペレーションをSTATUS_KIND とヒン
    # トを引数に呼び出す。本機能は、OMG の FSM4RTC仕様
    # (formal/16-04-01) 7.2.4.2 ComponentObserver Interface に記述されて
    # いる。
    #
    # STATUS_KIND には以下の種類がある。
    #
    # - COMPONENT_PROFILE: コンポーネントのプロファイル情報が変化
    # - RTC_STATUS       : コンポーネントの状態 (Init, Alive) が変化
    # - EC_STATUS        : ECの状態 (Inavtive, Active, Error) が変化
    # - PORT_PROFILE     : ポートのプロファイルが変化
    # - CONFIGURATION    : コンフィギュレーションが変化
    # - RTC_HEARTBEAT    : RTCの生存確認のハートビード
    # - EC_HEARTBEAT     : ECの生存確認のハートビート
    # - FSM_PROFILE      : FSMのプロファイルが変化
    # - FSM_STATUS       : FSMの状態が変化
    # - FSM_STRUCTURE    : FSMの構造が変化
    # - USER_DEFINED     : ユーザ定義
    #
    # \subsection COMPONENT_PROFILE COMPONENT_PROFILE
    # コンポーネントのプロファイル情報が変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。(未実装)
    #
    # \subsection RTC_STATUS RTC_STATUS
    #
    # コンポーネントの状態 (Init, Alive) が変化した際にこのタグ名
    # (enum値)を第1引数にして update_status() オペレーションが呼び出され
    # る。厳密にはECの状態であるが、Inavtive, Active, Error, Finalize の
    # 4つの状態に変化したことを検知することができる。以下の状態変化時に、
    # それぞれヒントとして以下の文字列とともにコールバックされる。
    #
    # - onActivated 呼び出し成功時:   ACTIVE: <EC id>
    # - onDeactivated 呼び出し成功時: INACTIVE: <EC id>
    # - onReset 呼び出し成功時:       INACTIVE: <EC id>
    # - onAborting 呼び出し成功時:    ERROR: <EC id>
    # - onFinalize 呼び出し成功時:    FINALIZE: <EC id>
    #
    # \subsection EC_STATUS EC_STATUS
    #
    # ECの状態 (Inavtive, Active, Error) が変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection PORT_PROFILE PORT_PROFILE
    # ポートのプロファイルが変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection CONFIGURATION CONFIGURATION
    # コンフィギュレーションが変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection RTC_HEARTBEAT RTC_HEARTBEAT
    # RTCの生存確認のハートビードした際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection EC_HEARTBEAT EC_HEARTBEAT
    # ECの生存確認のハートビートした際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection FSM_PROFILE FSM_PROFILE
    # FSMのプロファイルが変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection FSM_STATUS FSM_STATUS
    # FSMの状態が変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection FSM_STRUCTURE FSM_STRUCTURE
    # FSMの構造が変化した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    #
    # \subsection USER_DEFINED USER_DEFINED
    # ユーザ定義した際にこのタグ名(enum値)を
    # 第1引数にして update_status() オペレーションが呼び出される。
    # @else
    # @brief ctor of ComponentObserverConsumer
    # @endif
    #
    def __init__(self):
        self._rtobj = None
        self._profile = None
        self._observer = OpenRTM_aist.CorbaConsumer(
            interfaceType=RTC.ComponentObserver)
        self._observed = [False for i in range(RTC.STATUS_KIND_NUM._v)]

        self._compstat = self.CompStatMsg(self)
        self._portaction = self.PortAction(self)
        self._ecaction = self.ECAction(self)
        self._configMsg = self.ConfigAction(self)
        self._fsmaction = self.FSMAction(self)

        self._rtcInterval = OpenRTM_aist.TimeValue(1, 0)
        self._rtcHeartbeat = False
        self._ecInterval = OpenRTM_aist.TimeValue(1, 0)
        self._ecHeartbeat = False
        self._rtcHbTaskId = None
        self._ecHbTaskId = None

        return

    ##
    # @if jp
    # @brief dtor
    # @else
    # @brief dtor
    # @endif
    #

    def __del__(self):
        return

    ##
    # @if jp
    # @brief 初期化
    # @else
    # @brief Initialization
    # @endif
    #
    # virtual bool init(RTObject_impl& rtobj,
    #                   const SDOPackage::ServiceProfile& profile);

    def init(self, rtobj, profile):
        if not self._observer.setObject(profile.service):
            # narrowing failed
            return False

        self._rtobj = rtobj
        self._profile = profile
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, profile.properties)
        self.setRTCHeartbeat(prop)
        self.setECHeartbeat(prop)
        self.setListeners(prop)
        return True

    ##
    # @if jp
    # @brief 再初期化
    # @else
    # @brief Re-initialization
    # @endif
    #
    # virtual bool reinit(const SDOPackage::ServiceProfile& profile);

    def reinit(self, profile):
        if not self._observer._ptr()._is_equivalent(profile.service):
            tmp = OpenRTM_aist.CorbaConsumer(
                interfaceType=RTC.ComponentObserver)
            if not tmp.setObject(profile.service):
                return False
            self._observer.releaseObject()
            self._observer.setObject(profile.service)

        self._profile = profile
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, profile.properties)
        self.setRTCHeartbeat(prop)
        self.setECHeartbeat(prop)
        self.setListeners(prop)
        return True

    ##
    # @if jp
    # @brief ServiceProfile を取得する
    # @else
    # @brief getting ServiceProfile
    # @endif
    #
    # virtual const SDOPackage::ServiceProfile& getProfile() const;

    def getProfile(self):
        return self._profile

    ##
    # @if jp
    # @brief 終了処理
    # @else
    # @brief Finalization
    # @endif
    #
    # virtual void finalize();

    def finalize(self):
        self.unsetComponentProfileListeners()
        self.unsetComponentStatusListeners()
        self.unsetPortProfileListeners()
        self.unsetExecutionContextListeners()
        self.unsetConfigurationListeners()
        self.unsetRTCHeartbeat()
        return

    ##
    # @if jp
    # @brief リモートオブジェクトコール
    # @else
    # @brief Calling remote object
    # @endif
    #
    # inline void updateStatus(OpenRTM::StatusKind statuskind, const char* msg)

    def updateStatus(self, statuskind, msg):
        try:
            self._observer._ptr().update_status(statuskind, msg)
        except BaseException:
            self._rtobj.removeSdoServiceConsumer(self._profile.id)
        return

    ##
    # @if jp
    # @brief Kindを文字列へ変換する
    # @else
    # @brief Converting kind to string
    # @endif
    #
    # inline const char* toString(OpenRTM::StatusKind kind)
    def toString(self, kind):
        kinds = ["COMPONENT_PROFILE",
                 "RTC_STATUS",
                 "EC_STATUS",
                 "PORT_PROFILE",
                 "CONFIGURATION",
                 "RTC_HEARTBEAT",
                 "EC_HEARTBEAT",
                 "FSM_PROFILE",
                 "FSM_STATUS",
                 "FSM_STRUCTURE",
                 "USER_DEFINED"]
        if kind._v < len(kinds):
            return kinds[kind._v]
        return ""

    ##
    # @if jp
    # @brief RTObjectへのリスナ接続処理
    # @else
    # @brief Connectiong listeners to RTObject
    # @endif
    #
    # void setListeners(coil::Properties& prop);

    def setListeners(self, prop):
        if not prop.getProperty("observed_status"):
            prop.setProperty("observed_status", "ALL")

        observed_ = [s.strip()
                     for s in prop.getProperty("observed_status").split(",")]
        flags_ = [False for i in range(RTC.STATUS_KIND_NUM._v)]

        for i in range(len(observed_)):
            observed_[i] = observed_[i].upper()
            if observed_[i] == "COMPONENT_PROFILE":
                flags_[RTC.COMPONENT_PROFILE._v] = True
            elif observed_[i] == "RTC_STATUS":
                flags_[RTC.RTC_STATUS._v] = True
            elif observed_[i] == "EC_STATUS":
                flags_[RTC.EC_STATUS._v] = True
            elif observed_[i] == "PORT_PROFILE":
                flags_[RTC.PORT_PROFILE._v] = True
            elif observed_[i] == "CONFIGURATION":
                flags_[RTC.CONFIGURATION._v] = True
            elif observed_[i] == "FSM_PROFILE":
                flags_[RTC.FSM_PROFILE._v] = True
            elif observed_[i] == "FSM_STATUS":
                flags_[RTC.FSM_STRUCTURE._v] = True
            elif observed_[i] == "FSM_STRUCTURE":
                flags_[RTC.CONFIGURATION._v] = True
            elif observed_[i] == "ALL":
                for j in range(RTC.STATUS_KIND_NUM._v):
                    flags_[j] = True
                break

        self.switchListeners(flags_[RTC.COMPONENT_PROFILE._v],
                             self._observed,
                             RTC.COMPONENT_PROFILE._v,
                             self.setComponentProfileListeners,
                             self.unsetComponentProfileListeners)

        self.switchListeners(flags_[RTC.RTC_STATUS._v],
                             self._observed,
                             RTC.RTC_STATUS._v,
                             self.setComponentStatusListeners,
                             self.unsetComponentStatusListeners)

        self.switchListeners(flags_[RTC.EC_STATUS._v],
                             self._observed,
                             RTC.EC_STATUS._v,
                             self.setExecutionContextListeners,
                             self.unsetExecutionContextListeners)

        self.switchListeners(flags_[RTC.PORT_PROFILE._v],
                             self._observed,
                             RTC.PORT_PROFILE._v,
                             self.setPortProfileListeners,
                             self.unsetPortProfileListeners)

        self.switchListeners(flags_[RTC.CONFIGURATION._v],
                             self._observed,
                             RTC.CONFIGURATION._v,
                             self.setConfigurationListeners,
                             self.unsetConfigurationListeners)

        self.switchListeners(flags_[RTC.FSM_PROFILE._v],
                             self._observed,
                             RTC.FSM_PROFILE._v,
                             self.setFSMProfileListeners,
                             self.unsetFSMProfileListeners)
        self.switchListeners(flags_[RTC.FSM_STATUS._v],
                             self._observed,
                             RTC.FSM_STATUS._v,
                             self.setFSMStatusListeners,
                             self.unsetFSMStatusListeners)
        self.switchListeners(flags_[RTC.FSM_STRUCTURE._v],
                             self._observed,
                             RTC.FSM_STRUCTURE._v,
                             self.setFSMStructureListeners,
                             self.unsetFSMStructureListeners)

        return

    ##
    # @if jp
    # @brief リスナ接続・切断スイッチング処理
    # @else
    # @brief Switching listeners connecting/disconnecting
    # @endif
    #
    # void switchListeners(bool& next, bool& pre,
    #                      void (ComponentObserverConsumer::*setfunc)(),
    #                      void (ComponentObserverConsumer::*unsetfunc)());

    def switchListeners(self, next, pre, pre_idx, setfunc, unsetfunc):
        if (not pre[pre_idx]) and next:
            setfunc()
            pre[pre_idx] = True
        elif pre[pre_idx] and (not next):
            unsetfunc()
            pre[pre_idx] = False

        return

    # ============================================================
    # Heartbeat related functions

    ##
    # @if jp
    # @brief ハートビートをオブザーバに伝える
    # @else
    # @brief Sending a heartbeart signal to observer
    # @endif
    #
    # void rtcHeartbeat();

    def rtcHeartbeat(self):
        if self._rtcHeartbeat:
            self.updateStatus(RTC.RTC_HEARTBEAT, "")
        return

    ##
    # @if jp
    # @brief ハートビートを設定する
    # @else
    # @brief Setting heartbeat
    # @endif
    #
    # void setRTCHeartbeat(coil::Properties& prop);

    def setRTCHeartbeat(self, prop):
        self.unsetRTCHeartbeat()
        if prop.getProperty("rtc_heartbeat.enable"):
            prop.setProperty(
                "heartbeat.enable",
                prop.getProperty("rtc_heartbeat.enable"))
        if prop.getProperty("rtc_heartbeat.interval"):
            prop.setProperty(
                "heartbeat.interval",
                prop.getProperty("rtc_heartbeat.interval"))

        if OpenRTM_aist.toBool(prop.getProperty(
                "heartbeat.enable"), "YES", "NO", False):
            interval_ = prop.getProperty("heartbeat.interval")
            if not interval_:
                self._rtcInterval.set_time(1.0)
            else:
                tmp_ = float(interval_)
                self._rtcInterval.set_time(tmp_)

            tm_ = self._rtcInterval
            self._rtcHeartbeat = True
            self._rtcHbTaskId = OpenRTM_aist.Manager.instance().addTask(self.rtcHeartbeat, tm_)

        return

    ##
    # @if jp
    # @brief ハートビートを解除する
    # @else
    # @brief Unsetting heartbeat
    # @endif
    #
    # void unsetRTCHeartbeat();

    def unsetRTCHeartbeat(self):
        if self._rtcHeartbeat:
            OpenRTM_aist.Manager.instance().removeTask(self._rtcHbTaskId)
            self._rtcHeartbeat = False
        return


    ##
    # @if jp
    # @brief ハートビートをオブザーバに伝える
    # @else
    # @brief Sending a heartbeart signal to observer
    # @endif
    #
    # void ecHeartbeat();

    def ecHeartbeat(self):
        if self._ecHeartbeat:
            ecs = self._rtobj.get_owned_contexts()
            for i in range(len(ecs)):
                self.updateStatus(RTC.EC_HEARTBEAT, "HEARTBEAT:" + str(i))
            ecs = self._rtobj.get_participating_contexts()
            for i in range(len(ecs)):
                self.updateStatus(RTC.EC_HEARTBEAT, "HEARTBEAT:" +
                                  str(i + OpenRTM_aist.ECOTHER_OFFSET))

        return

    ##
    # @if jp
    # @brief ハートビートを設定する
    # @else
    # @brief Setting heartbeat
    # @endif
    #
    # void setECHeartbeat(coil::Properties& prop);
    def setECHeartbeat(self, prop):
        self.unsetECHeartbeat()
        if OpenRTM_aist.toBool(prop.getProperty(
                "ec_heartbeat.enable"), "YES", "NO", False):
            interval_ = prop.getProperty("ec_heartbeat.interval")
            if not interval_:
                self._ecInterval.set_time(1.0)
            else:
                tmp_ = float(interval_)
                self._ecInterval.set_time(tmp_)

            tm_ = self._ecInterval
            self._ecHeartbeat = True
            self._ecHbTaskId = OpenRTM_aist.Manager.instance().addTask(self.ecHeartbeat, tm_)

        return

    ##
    # @if jp
    # @brief ハートビートを解除する
    # @else
    # @brief Unsetting heartbeat
    # @endif
    #
    # void unsetECHeartbeat();

    def unsetECHeartbeat(self):
        if self._ecHeartbeat:
            OpenRTM_aist.Manager.instance().removeTask(self._ecHbTaskId)
            self._ecHeartbeat = False
        return

    # ============================================================
    # Component status related functions

    ##
    # @if jp
    # @brief RTC状態変化リスナの設定処理
    # @else
    # @brief Setting RTC status listeners
    # @endif
    #
    # void setComponentStatusListeners();

    def setComponentStatusListeners(self):
        postclistener_ = OpenRTM_aist.PostComponentActionListenerType
        if not self._compstat.activatedListener:
            self._compstat.activatedListener = \
                self._rtobj.addPostComponentActionListener(postclistener_.POST_ON_ACTIVATED,
                                                           self._compstat.onActivated)
        if not self._compstat.deactivatedListener:
            self._compstat.deactivatedListener = \
                self._rtobj.addPostComponentActionListener(postclistener_.POST_ON_DEACTIVATED,
                                                           self._compstat.onDeactivated)

        if not self._compstat.resetListener:
            self._compstat.resetListener = \
                self._rtobj.addPostComponentActionListener(postclistener_.POST_ON_RESET,
                                                           self._compstat.onReset)

        if not self._compstat.abortingListener:
            self._compstat.abortingListener = \
                self._rtobj.addPostComponentActionListener(postclistener_.POST_ON_ABORTING,
                                                           self._compstat.onAborting)

        if not self._compstat.finalizeListener:
            self._compstat.finalizeListener = \
                self._rtobj.addPostComponentActionListener(postclistener_.POST_ON_FINALIZE,
                                                           self._compstat.onFinalize)

        return

    ##
    # @if jp
    # @brief RTC状態変化リスナの解除処理
    # @else
    # @brief Unsetting RTC status listeners
    # @endif
    #
    # void unsetComponentStatusListeners();

    def unsetComponentStatusListeners(self):
        postclistener_ = OpenRTM_aist.PostComponentActionListenerType
        if self._compstat.activatedListener:
            self._rtobj.removePostComponentActionListener(postclistener_.POST_ON_ACTIVATED,
                                                          self._compstat.activatedListener)
            self._compstat.activatedListener = None

        if self._compstat.deactivatedListener:
            self._rtobj.removePostComponentActionListener(postclistener_.POST_ON_DEACTIVATED,
                                                          self._compstat.deactivatedListener)
            self._compstat.deactivatedListener = None

        if self._compstat.resetListener:
            self._rtobj.removePostComponentActionListener(postclistener_.POST_ON_RESET,
                                                          self._compstat.resetListener)
            self._compstat.resetListener = None

        if self._compstat.abortingListener:
            self._rtobj.removePostComponentActionListener(postclistener_.POST_ON_ABORTING,
                                                          self._compstat.abortingListener)
            self._compstat.abortingListener = None

        if self._compstat.finalizeListener:
            self._rtobj.removePostComponentActionListener(postclistener_.POST_ON_FINALIZE,
                                                          self._compstat.finalizeListener)
            self._compstat.finalizeListener = None

        return

    def setFSMStatusListeners(self):
        pass

    def unsetFSMStatusListeners(self):
        pass

    # ============================================================
    # Port profile related functions

    ##
    # @if jp
    # @brief Portプロファイル変化リスナの設定処理
    # @else
    # @brief Setting port profile listener
    # @endif
    #
    # void setPortProfileListeners();

    def setPortProfileListeners(self):
        plistener_ = OpenRTM_aist.PortActionListenerType
        if not self._portaction.portAddListener:
            self._portaction.portAddListener = \
                self._rtobj.addPortActionListener(plistener_.ADD_PORT,
                                                  self._portaction.onAddPort)

        if not self._portaction.portRemoveListener:
            self._portaction.portRemoveListener = \
                self._rtobj.addPortActionListener(plistener_.REMOVE_PORT,
                                                  self._portaction.onRemovePort)

        pclistener_ = OpenRTM_aist.PortConnectRetListenerType
        if not self._portaction.portConnectListener:
            self._portaction.portConnectListener = \
                self._rtobj.addPortConnectRetListener(pclistener_.ON_CONNECTED,
                                                      self._portaction.onConnect)

        if not self._portaction.portDisconnectListener:
            self._portaction.portDisconnectListener = \
                self._rtobj.addPortConnectRetListener(pclistener_.ON_DISCONNECTED,
                                                      self._portaction.onDisconnect)

        return

    ##
    # @if jp
    # @brief Portプロファイル変化リスナの解除処理
    # @else
    # @brief Unsetting port profile listener
    # @endif
    #
    # void unsetPortProfileListeners();
    def unsetPortProfileListeners(self):
        plistener_ = OpenRTM_aist.PortActionListenerType
        if self._portaction.portAddListener:
            self._rtobj.removePortActionListener(plistener_.ADD_PORT,
                                                 self._portaction.portAddListener)
            self._portaction.portAddListener = None

        if self._portaction.portRemoveListener:
            self._rtobj.removePortActionListener(plistener_.REMOVE_PORT,
                                                 self._portaction.portRemoveListener)
            self._portaction.portRemoveListener = None

        pclistener_ = OpenRTM_aist.PortConnectRetListenerType
        if self._portaction.portConnectListener:
            self._rtobj.removePortConnectRetListener(pclistener_.ON_CONNECTED,
                                                     self._portaction.portConnectListener)
            self._portaction.portConnectListener = None

        if self._portaction.portDisconnectListener:
            self._rtobj.removePortConnectRetListener(pclistener_.ON_DISCONNECTED,
                                                     self._portaction.portDisconnectListener)
            self._portaction.portDisconnectListener = None

        return

    # ============================================================
    # EC profile related functions

    ##
    # @if jp
    # @brief ECの状態変化リスナの設定
    # @else
    # @brief Setting EC status listener
    # @endif
    #
    # void setExecutionContextListeners();

    def setExecutionContextListeners(self):
        ectype_ = OpenRTM_aist.ExecutionContextActionListenerType
        if not self._ecaction.ecAttached:
            self._ecaction.ecAttached = \
                self._rtobj.addExecutionContextActionListener(ectype_.EC_ATTACHED,
                                                              self._ecaction.onAttached)

        if not self._ecaction.ecDetached:
            self._ecaction.ecDetached = \
                self._rtobj.addExecutionContextActionListener(ectype_.EC_DETACHED,
                                                              self._ecaction.onDetached)

        pcaltype_ = OpenRTM_aist.PostComponentActionListenerType
        if not self._ecaction.ecRatechanged:
            self._ecaction.ecRatechanged = \
                self._rtobj.addPostComponentActionListener(pcaltype_.POST_ON_RATE_CHANGED,
                                                           self._ecaction.onRateChanged)

        if not self._ecaction.ecStartup:
            self._ecaction.ecStartup = \
                self._rtobj.addPostComponentActionListener(pcaltype_.POST_ON_STARTUP,
                                                           self._ecaction.onStartup)

        if not self._ecaction.ecShutdown:
            self._ecaction.ecShutdown = \
                self._rtobj.addPostComponentActionListener(pcaltype_.POST_ON_SHUTDOWN,
                                                           self._ecaction.onShutdown)

        return

    ##
    # @if jp
    # @brief ECの状態変化リスナの解除
    # @else
    # @brief Unsetting EC status listener
    # @endif
    #
    # void unsetExecutionContextListeners();

    def unsetExecutionContextListeners(self):
        ectype_ = OpenRTM_aist.ExecutionContextActionListenerType
        if self._ecaction.ecAttached:
            self._rtobj.removeExecutionContextActionListener(ectype_.EC_ATTACHED,
                                                             self._ecaction.ecAttached)

        if self._ecaction.ecDetached:
            self._rtobj.removeExecutionContextActionListener(ectype_.EC_DETACHED,
                                                             self._ecaction.ecDetached)

        pcaltype_ = OpenRTM_aist.PostComponentActionListenerType
        if self._ecaction.ecRatechanged:
            self._rtobj.removePostComponentActionListener(pcaltype_.POST_ON_RATE_CHANGED,
                                                          self._ecaction.ecRatechanged)

        if self._ecaction.ecStartup:
            self._rtobj.removePostComponentActionListener(pcaltype_.POST_ON_STARTUP,
                                                          self._ecaction.ecStartup)

        if self._ecaction.ecShutdown:
            self._rtobj.removePostComponentActionListener(pcaltype_.POST_ON_SHUTDOWN,
                                                          self._ecaction.ecShutdown)

        return

    # ============================================================
    # ComponentProfile related functions

    ##
    # @if jp
    # @brief ComponentProfile状態変化リスナの設定
    # @else
    # @brief Setting ComponentProfile listener
    # @endif
    #
    # void setComponentProfileListeners();

    def setComponentProfileListeners(self):
        pass

    ##
    # @if jp
    # @brief ComponentProfile状態変化リスナの解除
    # @else
    # @brief Unsetting ComponentProfile listener
    # @endif
    #
    # void unsetComponentProfileListeners();

    def unsetComponentProfileListeners(self):
        pass

    # ============================================================
    # FsmStructure related functions

    ##
    # @if jp
    # @brief FsmStructure状態変化リスナの設定
    # @else
    # @brief Setting FsmStructure listener
    # @endif
    #
    # void setConfigurationListeners();

    def setFSMStructureListeners(self):
        fsmactionlistenertype_ = OpenRTM_aist.PreFsmActionListenerType
        self._fsmaction.preOnFsmInitListener = \
            self._rtobj.addPreFsmActionListener(fsmactionlistenertype_.PRE_ON_INIT,
                                                self._fsmaction.preInit)

        self._fsmaction.preOnFsmEntryListener = \
            self._rtobj.addPreFsmActionListener(fsmactionlistenertype_.PRE_ON_ENTRY,
                                                self._fsmaction.preEntry)

        self._fsmaction.preOnFsmDoListener = \
            self._rtobj.addPreFsmActionListener(fsmactionlistenertype_.PRE_ON_DO,
                                                self._fsmaction.preDo)

        self._fsmaction.preOnFsmExitListener = \
            self._rtobj.addPreFsmActionListener(fsmactionlistenertype_.PRE_ON_EXIT,
                                                self._fsmaction.preExit)

        self._fsmaction.preOnFsmStateChangeListener = \
            self._rtobj.addPreFsmActionListener(fsmactionlistenertype_.PRE_ON_STATE_CHANGE,
                                                self._fsmaction.postInit)

        fsmactionlistenertype_ = OpenRTM_aist.PostFsmActionListenerType

        self._fsmaction.postOnFsmInitListener = \
            self._rtobj.addPostFsmActionListener(fsmactionlistenertype_.POST_ON_INIT,
                                                 self._fsmaction.preStateChange)

        self._fsmaction.postOnFsmEntryListener = \
            self._rtobj.addPostFsmActionListener(fsmactionlistenertype_.POST_ON_ENTRY,
                                                 self._fsmaction.postEntry)

        self._fsmaction.postOnFsmDoListener = \
            self._rtobj.addPostFsmActionListener(fsmactionlistenertype_.POST_ON_DO,
                                                 self._fsmaction.postDo)

        self._fsmaction.postOnFsmExitListener = \
            self._rtobj.addPostFsmActionListener(fsmactionlistenertype_.POST_ON_EXIT,
                                                 self._fsmaction.postExit)

        self._fsmaction.postOnFsmStateChangeListener = \
            self._rtobj.addPostFsmActionListener(fsmactionlistenertype_.POST_ON_STATE_CHANGE,
                                                 self._fsmaction.postStateChange)

    def unsetFSMStructureListeners(self):
        fsmactionlistenertype_ = OpenRTM_aist.FSMActionListenerType
        if self._fsmaction.preOnFsmInitListener:
            self._rtobj.removePreFsmActionListener(fsmactionlistenertype_.PRE_ON_INIT,
                                                   self._fsmaction.preOnFsmInitListener)
            self._fsmaction.preOnFsmInitListener = None

        if self._fsmaction.preOnFsmEntryListener:
            self._rtobj.removePreFsmActionListener(fsmactionlistenertype_.PRE_ON_ENTRY,
                                                   self._fsmaction.preOnFsmEntryListener)
            self._fsmaction.preOnFsmEntryListener = None

        if self._fsmaction.preOnFsmDoListener:
            self._rtobj.removePreFsmActionListener(fsmactionlistenertype_.PRE_ON_DO,
                                                   self._fsmaction.preOnFsmDoListener)
            self._fsmaction.preOnFsmDoListener = None

        if self._fsmaction.preOnFsmExitListener:
            self._rtobj.removePreFsmActionListener(fsmactionlistenertype_.PRE_ON_EXIT,
                                                   self._fsmaction.preOnFsmExitListener)
            self._fsmaction.preOnFsmExitListener = None

        if self._fsmaction.preOnFsmStateChangeListener:
            self._rtobj.removePreFsmActionListener(fsmactionlistenertype_.PRE_ON_STATE_CHANGE,
                                                   self._fsmaction.preOnFsmStateChangeListener)
            self._fsmaction.preOnFsmStateChangeListener = None

        if self._fsmaction.postOnFsmInitListener:
            self._rtobj.removePostFsmActionListener(fsmactionlistenertype_.POST_ON_INIT,
                                                    self._fsmaction.postOnFsmInitListener)
            self._fsmaction.postOnFsmInitListener = None

        if self._fsmaction.postOnFsmEntryListener:
            self._rtobj.removePostFsmActionListener(fsmactionlistenertype_.POST_ON_ENTRY,
                                                    self._fsmaction.postOnFsmEntryListener)
            self._fsmaction.postOnFsmEntryListener = None

        if self._fsmaction.postOnFsmDoListener:
            self._rtobj.removePostFsmActionListener(fsmactionlistenertype_.POST_ON_DO,
                                                    self._fsmaction.postOnFsmDoListener)
            self._fsmaction.postOnFsmDoListener = None

        if self._fsmaction.postOnFsmExitListener:
            self._rtobj.removePostFsmActionListener(fsmactionlistenertype_.POST_ON_EXIT,
                                                    self._fsmaction.postOnFsmExitListener)
            self._fsmaction.postOnFsmExitListener = None

        if self._fsmaction.postOnFsmStateChangeListener:
            self._rtobj.removePostFsmActionListener(fsmactionlistenertype_.POST_ON_EXIT,
                                                    self._fsmaction.postOnFsmStateChangeListener)
            self._fsmaction.postOnFsmStateChangeListener = None

    # ============================================================
    # Configuration related functions

    ##
    # @if jp
    # @brief Configuration状態変化リスナの設定
    # @else
    # @brief Setting Configuration listener
    # @endif
    #
    # void setConfigurationListeners();
    def setConfigurationListeners(self):
        confprmlistenertype_ = OpenRTM_aist.ConfigurationParamListenerType
        self._configMsg.updateConfigParamListener = \
            self._rtobj.addConfigurationParamListener(confprmlistenertype_.ON_UPDATE_CONFIG_PARAM,
                                                      self._configMsg.updateConfigParam)

        confsetlistenertype_ = OpenRTM_aist.ConfigurationSetListenerType
        self._configMsg.setConfigSetListener = \
            self._rtobj.addConfigurationSetListener(confsetlistenertype_.ON_SET_CONFIG_SET,
                                                    self._configMsg.setConfigSet)

        self._configMsg.addConfigSetListener = \
            self._rtobj.addConfigurationSetListener(confsetlistenertype_.ON_ADD_CONFIG_SET,
                                                    self._configMsg.addConfigSet)

        confsetnamelistenertype_ = OpenRTM_aist.ConfigurationSetNameListenerType
        self._configMsg.updateConfigSetListener = \
            self._rtobj.addConfigurationSetNameListener(confsetnamelistenertype_.ON_UPDATE_CONFIG_SET,
                                                        self._configMsg.updateConfigSet)

        self._configMsg.removeConfigSetListener = \
            self._rtobj.addConfigurationSetNameListener(confsetnamelistenertype_.ON_REMOVE_CONFIG_SET,
                                                        self._configMsg.removeConfigSet)
        self._configMsg.activateConfigSetListener = \
            self._rtobj.addConfigurationSetNameListener(confsetnamelistenertype_.ON_ACTIVATE_CONFIG_SET,
                                                        self._configMsg.activateConfigSet)
        return

    ##
    # @if jp
    # @brief Configuration状態変化リスナの解除
    # @else
    # @brief Unsetting Configurationlistener
    # @endif
    #
    # void unsetConfigurationListeners();

    def unsetConfigurationListeners(self):
        confprmlistenertype_ = OpenRTM_aist.ConfigurationParamListenerType
        if self._configMsg.updateConfigParamListener:
            self._rtobj.removeConfigurationParamListener(confprmlistenertype_.ON_UPDATE_CONFIG_PARAM,
                                                         self._configMsg.updateConfigParamListener)
            self._configMsg.updateConfigParamListener = None

        confsetlistenertype_ = OpenRTM_aist.ConfigurationSetListenerType
        if self._configMsg.setConfigSetListener:
            self._rtobj.removeConfigurationSetListener(confsetlistenertype_.ON_SET_CONFIG_SET,
                                                       self._configMsg.setConfigSetListener)
            self._configMsg.setConfigSetListener = None

        if self._configMsg.addConfigSetListener:
            self._rtobj.removeConfigurationSetListener(confsetlistenertype_.ON_ADD_CONFIG_SET,
                                                       self._configMsg.addConfigSetListener)
            self._configMsg.addConfigSetListener = None

        confsetnamelistenertype_ = OpenRTM_aist.ConfigurationSetNameListenerType
        if self._configMsg.updateConfigSetListener:
            self._rtobj.removeConfigurationSetNameListener(confsetnamelistenertype_.ON_UPDATE_CONFIG_SET,
                                                           self._configMsg.updateConfigSetListener)
            self._configMsg.updateConfigSetListener = None

        if self._configMsg.removeConfigSetListener:
            self._rtobj.removeConfigurationSetNameListener(confsetnamelistenertype_.ON_REMOVE_CONFIG_SET,
                                                           self._configMsg.removeConfigSetListener)
            self._configMsg.removeConfigSetListener = None

        if self._configMsg.activateConfigSetListener:
            self._rtobj.removeConfigurationSetNameListener(confsetnamelistenertype_.ON_ACTIVATE_CONFIG_SET,
                                                           self._configMsg.activateConfigSetListener)
            self._configMsg.activateConfigSetListener = None

        return

    ##
    # @if jp
    # @brief FsmProfile状態変化リスナの設定
    # @else
    # @brief Setting FsmProfile listener
    # @endif
    #
    def setFSMProfileListeners(self):
        pass

    ##
    # @if jp
    # @brief FsmProfile状態変化リスナの設定
    # @else
    # @brief Setting FsmProfile listener
    # @endif
    #
    def unsetFSMProfileListeners(self):
        pass

    ##
    # @if jp
    # @brief PostComponentActionListener class
    # @else
    # @brief PostComponentActionListener class
    # @endif
    #

    class CompStatMsg:
        """
        """

        #CompStatMsg(ComponentObserverConsumer& coc)
        def __init__(self, coc):
            self.activatedListener = None
            self.deactivatedListener = None
            self.resetListener = None
            self.abortingListener = None
            self.finalizeListener = None
            self._coc = coc
            return

        def __del__(self):
            del self._coc
            return

        # void onGeneric(const char* msgprefix, UniqueId ec_id, ReturnCode_t
        # ret)
        def onGeneric(self, msgprefix, ec_id, ret):
            if ret == RTC.RTC_OK:
                msg_ = msgprefix
                msg_ += str(ec_id)
                self._coc.updateStatus(RTC.RTC_STATUS, msg_)
            return

        # void onActivated(UniqueId ec_id, ReturnCode_t ret)
        def onActivated(self, ec_id, ret):
            self.onGeneric("ACTIVE:", ec_id, ret)
            return

        # void onDeactivated(UniqueId ec_id, ReturnCode_t ret)
        def onDeactivated(self, ec_id, ret):
            self.onGeneric("INACTIVE:", ec_id, ret)
            return

        # void onReset(UniqueId ec_id, ReturnCode_t ret)
        def onReset(self, ec_id, ret):
            self.onGeneric("INACTIVE:", ec_id, ret)
            return

        # void onAborting(UniqueId ec_id, ReturnCode_t ret)
        def onAborting(self, ec_id, ret):
            self.onGeneric("ERROR:", ec_id, ret)
            return

        # void onFinalize(UniqueId ec_id, ReturnCode_t ret)
        def onFinalize(self, ec_id, ret):
            self._coc.unsetRTCHeartbeat()
            self._coc.unsetECHeartbeat()
            self.onGeneric("FINALIZE:", ec_id, ret)
            return

    ##
    # @if jp
    # @brief PortActionListener
    # @else
    # @brief PortActionListener
    # @endif
    #
    class PortAction:
        """
        """

        #PortAction(ComponentObserverConsumer& coc)
        def __init__(self, coc):
            self.portAddListener = None
            self.portRemoveListener = None
            self.portConnectListener = None
            self.portDisconnectListener = None
            self._coc = coc
            return

        def __del__(self):
            del self._coc
            return

        # void onGeneric(const char* _msg, const char* portname)
        def onGeneric(self, _msg, portname):
            msg_ = _msg
            msg_ += portname
            self._coc.updateStatus(RTC.PORT_PROFILE, msg_)
            return

        # void onAddPort(const ::RTC::PortProfile& pprof)
        def onAddPort(self, pprof):
            self.onGeneric("ADD:", str(pprof.name))
            return

        # void onRemovePort(const ::RTC::PortProfile& pprof)
        def onRemovePort(self, pprof):
            self.onGeneric("REMOVE:", str(pprof.name))
            return

        # void onConnect(const char* portname,
        #                 ::RTC::ConnectorProfile& pprof, ReturnCode_t ret)
        def onConnect(self, portname, pprof, ret):
            if ret == RTC.RTC_OK:
                self.onGeneric("CONNECT:", portname)
            return

        # void onDisconnect(const char* portname,
        #                  ::RTC::ConnectorProfile& pprof, ReturnCode_t ret)
        def onDisconnect(self, portname, pprof, ret):
            if ret == RTC.RTC_OK:
                self.onGeneric("DISCONNECT:", portname)
            return

    ##
    # @if jp
    # @brief ExecutionContextActionListener
    # @else
    # @brief ExecutionContextActionListener
    # @endif
    #

    class ECAction:
        """
        """

        #ECAction(ComponentObserverConsumer& coc)
        def __init__(self, coc):
            self.ecAttached = None
            self.ecDetached = None
            self.ecRatechanged = None
            self.ecStartup = None
            self.ecShutdown = None
            self._coc = coc
            return

        def __del__(self):
            del self._coc
            return

        # void onGeneric(const char* _msg, UniqueId ec_id)
        def onGeneric(self, _msg, ec_id):
            msg_ = _msg + str(ec_id)
            self._coc.updateStatus(RTC.EC_STATUS, msg_)
            return

        # void onAttached(UniqueId ec_id)
        def onAttached(self, ec_id):
            self.onGeneric("ATTACHED:", ec_id)
            return

        # void onDetached(UniqueId ec_id)
        def onDetached(self, ec_id):
            self.onGeneric("DETACHED:", ec_id)
            return

        # void onRateChanged(UniqueId ec_id, ReturnCode_t ret)
        def onRateChanged(self, ec_id, ret):
            if ret == RTC.RTC_OK:
                self.onGeneric("RATE_CHANGED:", ec_id)
            return

        # void onStartup(UniqueId ec_id, ReturnCode_t ret)
        def onStartup(self, ec_id, ret):
            if ret == RTC.RTC_OK:
                self.onGeneric("STARTUP:", ec_id)
            return

        # void onShutdown(UniqueId ec_id, ReturnCode_t ret)
        def onShutdown(self, ec_id, ret):
            if ret == RTC.RTC_OK:
                self.onGeneric("SHUTDOWN:", ec_id)
            return

    ##
    # @if jp
    # @brief ConfigActionListener
    # @else
    # @brief ConfigActionListener
    # @endif
    #

    class ConfigAction:
        """
        """

        #ConfigAction(ComponentObserverConsumer& coc)
        def __init__(self, coc):
            self.updateConfigParamListener = None
            self.setConfigSetListener = None
            self.addConfigSetListener = None
            self.updateConfigSetListener = None
            self.removeConfigSetListener = None
            self.activateConfigSetListener = None
            self._coc = coc

        def __del__(self):
            del self._coc
            return

        # void updateConfigParam(const char* configsetname,
        #                       const char* configparamname)
        def updateConfigParam(self, configsetname, configparamname):
            msg_ = "UPDATE_CONFIG_PARAM: "
            msg_ += configsetname
            msg_ += "."
            msg_ += configparamname
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

        # void setConfigSet(const coil::Properties& config_set)
        def setConfigSet(self, config_set):
            msg_ = "SET_CONFIG_SET: "
            msg_ += config_set.getName()
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

        # void addConfigSet(const coil::Properties& config_set)
        def addConfigSet(self, config_set):
            msg_ = "ADD_CONFIG_SET: "
            msg_ += config_set.getName()
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

        # void updateConfigSet(const char* config_set_name)
        def updateConfigSet(self, config_set_name):
            msg_ = "UPDATE_CONFIG_SET: "
            msg_ += config_set_name
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

        # void removeConfigSet(const char* config_set_name)
        def removeConfigSet(self, config_set_name):
            msg_ = "REMOVE_CONFIG_SET: "
            msg_ += config_set_name
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

        # void activateConfigSet(const char* config_set_name)
        def activateConfigSet(self, config_set_name):
            msg_ = "ACTIVATE_CONFIG_SET: "
            msg_ += config_set_name
            self._coc.updateStatus(RTC.CONFIGURATION, msg_)
            return

    ##
    # @if jp
    # @brief FSMActionListener
    # @else
    # @brief FSMActionListener
    # @endif
    #

    class FSMAction:
        """
        """

        #ConfigAction(ComponentObserverConsumer& coc)
        def __init__(self, coc):
            self.updateFsmStatusListener = None
            self.preOnFsmInitListener = None
            self.preOnFsmEntryListener = None
            self.preOnFsmDoListener = None
            self.preOnFsmExitListener = None
            self.preOnFsmStateChangeListener = None
            self.postOnFsmInitListener = None
            self.postOnFsmEntryListener = None
            self.postOnFsmDoListener = None
            self.postOnFsmExitListener = None
            self.postOnFsmStateChangeListener = None
            self._coc = coc

        def __del__(self):
            del self._coc
            return

        def updateFsmStatus(self, state):
            self._coc.updateStatus(RTC.FSM_STATUS, state)
            return

        def preInit(self, state):
            msg_ = state + " PRE_ON_INIT"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def preEntry(self, state):
            msg_ = state + " PRE_ONENTRY"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def preDo(self, state):
            msg_ = state + " PRE_ON_DO"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def preExit(self, state):
            msg_ = state + " PRE_ON_EXIT"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def preStateChange(self, state):
            msg_ = state + " PRE_ON_STATE_CHANGE"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def postInit(self, state):
            msg_ = state + " POST_ON_INIT"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def postEntry(self, state):
            msg_ = state + " POST_ONENTRY"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def postDo(self, state):
            msg_ = state + " POST_ON_DO"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def postExit(self, state):
            msg_ = state + " POST_ON_EXIT"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return

        def postStateChange(self, state):
            msg_ = state + " POST_ON_STATE_CHNAGE"
            self._coc.updateStatus(RTC.FSM_STATUS, msg_)
            return


def ComponentObserverConsumerInit(mgr=None):
    factory = OpenRTM_aist.SdoServiceConsumerFactory.instance()
    factory.addFactory(RTC.ComponentObserver._NP_RepositoryId,
                       ComponentObserverConsumer)
    return
