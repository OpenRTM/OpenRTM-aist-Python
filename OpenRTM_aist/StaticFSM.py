#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file StaticFSM.py
# @brief Static FSM framework based on Macho
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import OpenRTM_aist.Macho
import RTC


##
# @if jp
#
# @brief FSMの最上位の状態生成
#
# @param TOP 状態遷移マシンの最上位状態を定義したクラス
# @return 最上位の状態
#
# @else
#
# @brief
#
# @param TOP
#
# @endif
#
def fsm_topstate(TOP):
    ret = OpenRTM_aist.Macho.topstate(TOP)

    class STATE(ret):
        def __init__(self, instance):
            ret.__init__(self, instance)

        def on_entry(self, *argv):
            ret.call_entry(self, ret, *argv)

        def on_exit(self, *argv):
            ret.call_exit(self, ret, *argv)

        def on_init(self, *argv):
            ret.call_init(self, ret, *argv)
    return STATE

##
# @if jp
#
# @brief FSMのサブ状態生成
#
# @param TOP 状態遷移マシンのサブ状態を定義したクラス
# @return サブ状態
#
# @else
#
# @brief
#
# @param TOP
#
# @endif
#


def fsm_substate(superstate):
    def _fsm_substate(cls):
        ret = OpenRTM_aist.Macho.substate(superstate)(cls)

        class STATE(ret):
            def __init__(self, instance):
                ret.__init__(self, instance)

            def on_entry(self, *argv):
                ret.call_entry(self, cls, *argv)

            def on_exit(self, *argv):
                ret.call_exit(self, cls, *argv)

            def on_init(self, *argv):
                ret.call_init(self, cls, *argv)

        return STATE
    return _fsm_substate


##
# @if jp
#
# @brief FSMの最上位状態生成関数
# Machoやpyfsmで定義したクラスにデコレートして使用する
# @StaticFSM.FSM_TOPSTATE
# class TOP(StaticFSM.Link):
#
# @param TOP 最上位状態
# @return 最上位状態
#
# @else
#
# @brief
#
# @param TOP
# @return
#
#
# @endif
#
def FSM_TOPSTATE(TOP):
    return fsm_topstate(TOP)

##
# @if jp
#
# @brief FSMのサブ位状態生成関数
# Machoやpyfsmで定義したクラスにデコレートして使用する
# @StaticFSM.FSM_SUBSTATE(TOP)
# class Disabled(StaticFSM.Link):
#
# @param SUPERSTATE 上位の状態
# @return サブ状態を生成する関数
#
# @else
#
# @brief
#
# @param SUPERSTATE
# @return
#
#
# @endif
#


def FSM_SUBSTATE(SUPERSTATE):
    return fsm_substate(SUPERSTATE)


##
# @if jp
#
# @class CSPMachine
#
# @brief 有限状態マシン
# 初期化時に最上位状態、RTCを指定する
# 最上位状態から開始し、その後イベントによって状態遷移する
# EventPortで受信したイベントは一旦バッファに保存されるため、
# run_event関数を呼び出すことでバッファ内のイベントを実行する必要がある
# バッファは全てのEventPortで共有される
#
# @since 2.0.0
#
# @else
#
# @class CSPMachine
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#
class Machine(OpenRTM_aist.Macho.Machine):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param TOP 最上位状態
    # @param comp RTC
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param TOP
    # @param comp
    #
    # @endif
    #
    def __init__(self, TOP, comp):
        #super(Machine,self).__init__(TOP, OpenRTM_aist.Macho.TopBase(TOP))
        self._rtComponent = comp
        super(Machine, self).__init__(TOP)
        self._buffer = OpenRTM_aist.CdrBufferFactory.instance().createObject("ring_buffer")
    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A destructor.
    #
    # @param self
    #
    # @endif
    #

    def __del__(self):
        pass
    ##
    # @if jp
    #
    # @brief バッファ取得
    #
    # @param self
    # @return バッファ
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def getBuffer(self):
        return self._buffer

    def init_other(self, other):
        pass

    def equal(self, snapshot):
        pass
    ##
    # @if jp
    #
    # @brief RTC取得
    #
    # @param self
    # @return RTC
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def getComp(self):
        return self._rtComponent
    ##
    # @if jp
    #
    # @brief イベント実行
    # バッファが空になるまでイベントを実行する
    #
    # @param self
    #
    # @else
    #
    # @brief
    #
    # @param self
    #
    # @endif
    #

    def run_event(self):
        while self._buffer.readable() > 0:
            _, event = self._buffer.get()
            event()
            self._buffer.advanceRptr()


##
# @if jp
#
# @class Link
#
# @brief 状態定義の基底クラス
# 最上位状態、サブ状態を定義する場合はこのクラスを継承する必要がある
#
# @since 2.0.0
#
# @else
#
# @class Link
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#
class Link(OpenRTM_aist.Macho.StateDef):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param instance
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param instance
    #
    # @endif
    #
    def __init__(self, instance):
        super(Link, self).__init__(instance)
        self._rtComponent = None
    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A destructor.
    #
    # @param self
    #
    # @endif
    #

    def __del__(self):
        pass
    ##
    # @if jp
    #
    # @brief 内部の変数に状態遷移マシンが保持するRTCの参照を格納する
    #
    # @param self
    #
    # @else
    #
    # @brief
    #
    # @param self
    #
    # @endif
    #

    def setrtc(self):
        if self._rtComponent:
            return
        machine = self._myStateInstance.machine()
        if machine:
            self._rtComponent = machine.getComp()

    ##
    # @if jp
    #
    # @brief 現在の状態のonEntry関数を呼び出す
    # RTCを設定している場合はpostOnFsmStateChange、preOnFsmEntry、postOnFsmEntryコールバックを呼び出す
    #
    # @param self
    # @param cls 現在の状態
    # @param argv
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param cls
    # @param argv
    #
    # @endif
    #
    def call_entry(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            cls.onEntry(self, *argv)
        else:
            self._rtComponent.postOnFsmStateChange(
                self._state_name(), RTC.RTC_OK)
            self._rtComponent.preOnFsmEntry(self._state_name())
            self._rtComponent.postOnFsmEntry(
                self._state_name(), cls.onEntry(self, *argv))

    ##
    # @if jp
    #
    # @brief 現在の状態のonInit関数を呼び出す
    # RTCを設定している場合はpostOnFsmStateChange、preOnFsmEntry、postOnFsmEntryコールバックを呼び出す
    #
    # @param self
    # @param cls 現在の状態
    # @param argv
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param cls
    # @param argv
    #
    # @endif
    #
    def call_init(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            cls.onInit(self, *argv)
        else:
            self._rtComponent.preOnFsmInit(self._state_name())
            self._rtComponent.postOnFsmInit(
                self._state_name(), cls.onInit(self, *argv))

    ##
    # @if jp
    #
    # @brief 現在の状態のonExit関数を呼び出す
    # RTCを設定している場合はpostOnFsmStateChange、preOnFsmEntry、postOnFsmEntryコールバックを呼び出す
    #
    # @param self
    # @param cls 現在の状態
    # @param argv
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param cls
    # @param argv
    #
    # @endif
    #
    def call_exit(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            cls.onExit(self, *argv)
        else:
            self._rtComponent.preOnFsmExit(self._state_name())
            self._rtComponent.postOnFsmExit(
                self._state_name(), cls.onExit(self, *argv))
            self._rtComponent.preOnFsmStateChange(self._state_name())

    ##
    # @if jp
    #
    # @brief 入場動作を定義した関数
    # Linkを継承したクラスでonEntry関数を定義し処理を実装する
    #
    # @param self
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #
    def onEntry(self):
        return RTC.RTC_OK
    ##
    # @if jp
    #
    # @brief 開始動作を定義した関数
    # Linkを継承したクラスでonInit関数を定義し処理を実装する
    #
    # @param self
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def onInit(self):
        return RTC.RTC_OK
    ##
    # @if jp
    #
    # @brief 退場動作を定義した関数
    # Linkを継承したクラスでonExit関数を定義し処理を実装する
    #
    # @param self
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def onExit(self):
        return RTC.RTC_OK


State = OpenRTM_aist.Macho.State
deephistory = OpenRTM_aist.Macho.deephistory
Event = OpenRTM_aist.Macho.Event
