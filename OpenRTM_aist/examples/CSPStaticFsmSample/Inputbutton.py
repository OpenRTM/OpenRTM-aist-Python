#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file Inputbutton.py
# @if jp
# @brief 電子レンジFSMへの入力イベントを送信するサンプルRTC。
# @else
# @brief Sample RTC sending input events to the microwave FSM.
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
import OpenRTM_aist.StringUtil

inputbutton_spec = ["implementation_id", "Inputbutton",
                    "type_name", "Inputbutton",
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
# @brief 電子レンジFSMへの入力イベントを送信するサンプルRTC。
# @else
# @brief Sample RTC sending input events to the microwave FSM.
# @endif
class Inputbutton(OpenRTM_aist.DataFlowComponentBase):
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
    # @brief RTCのポート・設定・FSMを初期化する。
    # @else
    # @brief Initialize RTC ports, configuration and FSM state.
    # @endif
    def onInitialize(self):
        self._open = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._close = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._minute = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._start = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._stop = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._tick = RTC.TimedLong(RTC.Time(0, 0), 0)

        self._openOut = OpenRTM_aist.CSPOutPort("open", self._open)
        self._closeOut = OpenRTM_aist.CSPOutPort("close", self._close)
        self._minuteOut = OpenRTM_aist.CSPOutPort("minute", self._minute)
        self._startOut = OpenRTM_aist.CSPOutPort("start", self._start)
        self._stopOut = OpenRTM_aist.CSPOutPort("stop", self._stop)
        self._tickOut = OpenRTM_aist.CSPOutPort("tick", self._tick)
        # Set OutPort buffer
        self.addOutPort("open", self._openOut)
        self.addOutPort("close", self._closeOut)
        self.addOutPort("minute", self._minuteOut)
        self.addOutPort("start", self._startOut)
        self.addOutPort("stop", self._stopOut)
        self.addOutPort("tick", self._tickOut)

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
        print("")
        print("Please select action!!")
        print("Commands: ")
        print("  open         : Open the microwave's door.")
        print("  close        : Close the microwave's door.")
        print("  minute <int> : Increment timer. ")
        print("  start        : Start the microwave.")
        print("  stop         : Stop the microwave.")
        print("  tick         : Proceed time.")
        print("  -> others are interpreted as tick commnad.")
        print(">> ", end="")
        #print(">> ",end="")
        line = sys.stdin.readline()
        # EOFでは送信しない。 / Do not send an event at EOF.
        if line == "":
            return RTC.RTC_OK
        cmds = line.split() or [""]
        print("[command]: ", cmds[0])
        #print("  [args]: ",end="")
        print("  [args]: ", end="")
        for n in range(len(cmds)):
            if n == 0:
                continue
            # print(cmds[n],end="")
            print(cmds[n], end="")
        print("")
        if cmds[0] == "open":
            self._open.data = 0
            self._openOut.write()
        elif cmds[0] == "close":
            self._close.data = 0
            self._closeOut.write()
        elif cmds[0] == "minute":
            # stringToは成功フラグと値を返す。 / stringTo returns success and value.
            valid, minute_value = OpenRTM_aist.StringUtil.stringTo(
                0, cmds[1] if len(cmds) > 1 else "")
            if not valid:
                print("minute command needs an integer arg.")
                return RTC.RTC_OK

            self._minute.data = minute_value
            self._minuteOut.write()
        elif cmds[0] == "start":
            self._start.data = 0
            self._startOut.write()
        elif cmds[0] == "stop":
            self._stop.data = 0
            self._stopOut.write()
        else:
            print("tick")
            self._tick.data = 0
            self._tickOut.write()

        return RTC.RTC_OK


##
# @if jp
# @brief `Inputbutton`のFactoryを登録する。
# @param manager 関連付けるManager。
# @else
# @brief Register the factory for Inputbutton.
# @param manager Manager to associate with the object.
# @endif
def InputbuttonInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=inputbutton_spec)
    manager.registerFactory(profile,
                            Inputbutton,
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
    InputbuttonInit(manager)

    # Create a component
    _ = manager.createComponent("Inputbutton")


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
