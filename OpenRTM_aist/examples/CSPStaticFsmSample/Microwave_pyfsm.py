#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file Microwave_pyfsm.py
# @if jp
# @brief `Microwave_pyfsm`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of Microwave_pyfsm.
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


import sys

import RTC
import OpenRTM_aist
import OpenRTM_aist.StaticFSM_pyfsm as StaticFSM
import OpenRTM_aist.EventPort_pyfsm as EventPort


import MicrowaveFsm_pyfsm as MicrowaveFsm

microwave_spec = ["implementation_id", "Microwave",
                  "type_name", "Microwave",
                  "description", "Console input component",
                  "version", "1.0",
                  "vendor", "Nobuhiko Miyamoto",
                  "category", "example",
                  "activity_type", "DataFlowComponent",
                  "max_instance", "10",
                  "language", "Python",
                  "lang_type", "script",
                  ""]


##
# @if jp
# @brief CSPイベントで電子レンジFSMを駆動するサンプルRTC。
# @else
# @brief Sample RTC driving a microwave FSM with CSP events.
# @endif
class Microwave(OpenRTM_aist.DataFlowComponentBase):
    ##
    # @if jp
    # @brief インスタンスと内部状態を初期化する。
    # @param manager 関連付けるManager。
    # @else
    # @brief Initialize the instance and its internal state.
    # @param manager Manager to associate with the object.
    # @endif
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

        return

    ##
    # @if jp
    # @brief RTCの終了処理を行う。
    # @else
    # @brief Finalize the RTC resources.
    # @endif
    def onFinalize(self):
        self._fsm.exit()
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief RTCのポート・設定・FSMを初期化する。
    # @else
    # @brief Initialize RTC ports, configuration and FSM state.
    # @endif
    def onInitialize(self):
        self._fsm = StaticFSM.Machine(MicrowaveFsm.TOP, self)
        # self._fsm.init()
        self._eventIn = EventPort.EventInPort("event", self._fsm)

        self.addInPort("event", self._eventIn)
        self._eventIn.bindEvent0("open", MicrowaveFsm.TOP.open)
        self._eventIn.bindEvent0("close", MicrowaveFsm.TOP.close)
        self._eventIn.bindEvent1(
            "minute",
            MicrowaveFsm.TOP.minute,
            RTC.TimedLong(
                RTC.Time(
                    0,
                    0),
                0))
        self._eventIn.bindEvent0("start", MicrowaveFsm.TOP.start)
        self._eventIn.bindEvent0("stop", MicrowaveFsm.TOP.stop)
        self._eventIn.bindEvent0("tick", MicrowaveFsm.TOP.tick)

        return RTC.RTC_OK

    ##
    # @if jp
    # @brief 周期実行に対応する通信・制御処理を行う。
    # @param ec_id 実行コンテキストの識別子。
    # @else
    # @brief Perform communication and control for a periodic execution callback.
    # @param ec_id Execution context identifier.
    # @endif
    def onExecute(self, ec_id):
        self._fsm.run_event()

        return RTC.RTC_OK


##
# @if jp
# @brief `Microwave`のFactoryを登録する。
# @param manager 関連付けるManager。
# @else
# @brief Register the factory for Microwave.
# @param manager Manager to associate with the object.
# @endif
def MicrowaveInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=microwave_spec)
    manager.registerFactory(profile,
                            Microwave,
                            OpenRTM_aist.Delete)


##
# @if jp
# @brief サンプルのFactoryを登録して自RTCを生成する。
# @param manager 関連付けるManager。
# @else
# @brief Register the sample factory and create its RTC.
# @param manager Manager to associate with the object.
# @endif
def MyModuleInit(manager):
    MicrowaveInit(manager)

    # Create a component
    _ = manager.createComponent("Microwave")


##
# @if jp
# @brief Managerを初期化してサンプルの実行ループを開始する。
# @else
# @brief Initialize the manager and start the sample execution loop.
# @endif
def main():
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)

    # Set module initialization proceduer
    # This procedure will be invoked in activateManager() function.
    mgr.setModuleInitProc(MyModuleInit)

    # Activate manager and register to naming service
    mgr.activateManager()

    # run the manager in blocking mode
    # runManager(False) is the default
    mgr.runManager()

    # If you want to run the manager in non-blocking mode, do like this
    # mgr.runManager(True)


if __name__ == "__main__":
    main()
