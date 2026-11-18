#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file MicrowaveFsm_pyfsm.py
# @if jp
# @brief `MicrowaveFsm_pyfsm`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of MicrowaveFsm_pyfsm.
# @endif
# @date $Date: 2026-11-13 15:32:20 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2026
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$

# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


from __future__ import print_function


import RTC
import OpenRTM_aist.StaticFSM_pyfsm as StaticFSM


##
# @if jp
# @brief `TOP`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of TOP.
# @endif
@StaticFSM.FSM_TOPSTATE
class TOP(StaticFSM.Link):
    ##
    # @if jp
    # @brief FSM状態の初期遷移を実行する。
    # @else
    # @brief Perform the initial transition of the FSM state.
    # @endif
    def onInit(self):
        self.set_state(StaticFSM.State(Operational))
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief `open`に対応する処理を行う。
    # @else
    # @brief Perform the open operation.
    # @endif
    def open(self):
        pass

    ##
    # @if jp
    # @brief 新規I/Oを停止し、待機解除と処理中操作の終了を行う。
    # @else
    # @brief Stop new I/O, wake waiters and finish in-flight operations.
    # @endif
    def close(self):
        pass

    ##
    # @if jp
    # @brief `minute`に対応する処理を行う。
    # @param time_ `time_`の値。
    # @else
    # @brief Perform the minute operation.
    # @param time_ Value of time_.
    # @endif
    def minute(self, time_):
        pass

    ##
    # @if jp
    # @brief `start`に対応する処理を行う。
    # @else
    # @brief Perform the start operation.
    # @endif
    def start(self):
        pass

    ##
    # @if jp
    # @brief `stop`に対応する処理を行う。
    # @else
    # @brief Perform the stop operation.
    # @endif
    def stop(self):
        pass

    ##
    # @if jp
    # @brief `tick`に対応する処理を行う。
    # @else
    # @brief Perform the tick operation.
    # @endif
    def tick(self):
        pass

    ##
    # @if jp
    # @brief `Data`の状態と操作をまとめる。
    # @else
    # @brief Encapsulate the state and operations of Data.
    # @endif
    class Data:
        ##
        # @if jp
        # @brief インスタンスと内部状態を初期化する。
        # @else
        # @brief Initialize the instance and its internal state.
        # @endif
        def __init__(self):
            self.myCookingTime = 0

        ##
        # @if jp
        # @brief 残りの調理時間を表示する。
        # @else
        # @brief Print the remaining cooking time.
        # @endif
        def printTimer(self):
            print(" Timer set to ", self.myCookingTime, " minutes")

        ##
        # @if jp
        # @brief 調理タイマーを一つ増やす。
        # @else
        # @brief Increment the cooking timer by one.
        # @endif
        def incrementTimer(self):
            self.myCookingTime += 1

        ##
        # @if jp
        # @brief 調理タイマーを一つ減らす。
        # @else
        # @brief Decrement the cooking timer by one.
        # @endif
        def decrementTimer(self):
            self.myCookingTime -= 1

        ##
        # @if jp
        # @brief 調理タイマーをゼロへ戻す。
        # @else
        # @brief Reset the cooking timer to zero.
        # @endif
        def resetTimer(self):
            self.myCookingTime = 0

        ##
        # @if jp
        # @brief 残りの調理時間を取得する。
        # @else
        # @brief Get the remaining cooking time.
        # @endif
        def getRemainingTime(self):
            return self.myCookingTime


##
# @if jp
# @brief `Disabled`に対応するFSM状態を表す。
# @else
# @brief Represent the Disabled FSM state.
# @endif
@StaticFSM.FSM_SUBSTATE(TOP)
class Disabled(StaticFSM.Link):
    ##
    # @if jp
    # @brief FSM状態への入場処理を実行する。
    # @else
    # @brief Perform the FSM state entry action.
    # @endif
    def onEntry(self):
        print("  Microwave opened")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief FSM状態からの退場処理を実行する。
    # @else
    # @brief Perform the FSM state exit action.
    # @endif
    def onExit(self):
        print("  Microwave closed")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief 新規I/Oを停止し、待機解除と処理中操作の終了を行う。
    # @else
    # @brief Stop new I/O, wake waiters and finish in-flight operations.
    # @endif
    def close(self):
        # self.setStateHistory(OpenRTM_aist.Macho.State(Operational))
        self.set_state(StaticFSM.State(Operational))


##
# @if jp
# @brief `Operational`に対応するFSM状態を表す。
# @else
# @brief Represent the Operational FSM state.
# @endif
@StaticFSM.deephistory
@StaticFSM.FSM_SUBSTATE(TOP)
class Operational(StaticFSM.Link):
    ##
    # @if jp
    # @brief `open`に対応する処理を行う。
    # @else
    # @brief Perform the open operation.
    # @endif
    def open(self):
        self.set_state(StaticFSM.State(Disabled))

    ##
    # @if jp
    # @brief `stop`に対応する処理を行う。
    # @else
    # @brief Perform the stop operation.
    # @endif
    def stop(self):
        self.set_state(StaticFSM.State(Idle))

    ##
    # @if jp
    # @brief FSM状態の初期遷移を実行する。
    # @else
    # @brief Perform the initial transition of the FSM state.
    # @endif
    def onInit(self):
        self.set_state(StaticFSM.State(Idle))
        return RTC.RTC_OK


##
# @if jp
# @brief `Idle`に対応するFSM状態を表す。
# @else
# @brief Represent the Idle FSM state.
# @endif
@StaticFSM.FSM_SUBSTATE(Operational)
class Idle(StaticFSM.Link):
    ##
    # @if jp
    # @brief `minute`に対応する処理を行う。
    # @param time_ `time_`の値。
    # @else
    # @brief Perform the minute operation.
    # @param time_ Value of time_.
    # @endif
    def minute(self, time_):
        self.set_state(StaticFSM.State(Programmed))
        self.dispatch(StaticFSM.Event(TOP.minute, time_))

    ##
    # @if jp
    # @brief FSM状態への入場処理を実行する。
    # @else
    # @brief Perform the FSM state entry action.
    # @endif
    def onEntry(self):
        self.data(TOP).resetTimer()
        print("  Microwave ready")
        return RTC.RTC_OK


##
# @if jp
# @brief `Programmed`に対応するFSM状態を表す。
# @else
# @brief Represent the Programmed FSM state.
# @endif
@StaticFSM.FSM_SUBSTATE(Operational)
class Programmed(StaticFSM.Link):
    ##
    # @if jp
    # @brief `minute`に対応する処理を行う。
    # @param time_ `time_`の値。
    # @else
    # @brief Perform the minute operation.
    # @param time_ Value of time_.
    # @endif
    def minute(self, time_):
        for t in range(time_.data):
            self.data(TOP).incrementTimer()
        self.data(TOP).printTimer()

    ##
    # @if jp
    # @brief `start`に対応する処理を行う。
    # @else
    # @brief Perform the start operation.
    # @endif
    def start(self):
        self.set_state(StaticFSM.State(Cooking))


##
# @if jp
# @brief `Cooking`に対応するFSM状態を表す。
# @else
# @brief Represent the Cooking FSM state.
# @endif
@StaticFSM.FSM_SUBSTATE(Programmed)
class Cooking(StaticFSM.Link):
    ##
    # @if jp
    # @brief `tick`に対応する処理を行う。
    # @else
    # @brief Perform the tick operation.
    # @endif
    def tick(self):
        print("  Clock tick")
        tb = self.data(TOP)
        tb.decrementTimer()
        if tb.getRemainingTime() == 0:
            print("  Finished")
            self.set_state(StaticFSM.State(Idle))
        else:
            tb.printTimer()

    ##
    # @if jp
    # @brief FSM状態への入場処理を実行する。
    # @else
    # @brief Perform the FSM state entry action.
    # @endif
    def onEntry(self):
        print("  Heating on")
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief FSM状態からの退場処理を実行する。
    # @else
    # @brief Perform the FSM state exit action.
    # @endif
    def onExit(self):
        print("  Heating off")
        return RTC.RTC_OK
