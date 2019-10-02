#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file Inputbutton.py
# @brief example StaticFSM
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist
import OpenRTM_aist.StringUtil

inputbutton_spec = ["implementation_id", "Inputbutton",
                    "type_name", "Inputbutton",
                    "description", "InputButton component for Microwave example",
                    "version", "1.0",
                    "vendor", "Nobuhiko Miyamoto",
                    "category", "example",
                    "activity_type", "DataFlowComponent",
                    "max_instance", "10",
                    "language", "Python",
                    "lang_type", "script",
                    ""]


class Inputbutton(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        return

    def onInitialize(self):
        self._open = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._close = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._minute = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._start = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._stop = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._tick = RTC.TimedLong(RTC.Time(0, 0), 0)

        self._openOut = OpenRTM_aist.OutPort("open", self._open)
        self._closeOut = OpenRTM_aist.OutPort("close", self._close)
        self._minuteOut = OpenRTM_aist.OutPort("minute", self._minute)
        self._startOut = OpenRTM_aist.OutPort("start", self._start)
        self._stopOut = OpenRTM_aist.OutPort("stop", self._stop)
        self._tickOut = OpenRTM_aist.OutPort("tick", self._tick)
        # Set OutPort buffer
        self.addOutPort("open", self._openOut)
        self.addOutPort("close", self._closeOut)
        self.addOutPort("minute", self._minuteOut)
        self.addOutPort("start", self._startOut)
        self.addOutPort("stop", self._stopOut)
        self.addOutPort("tick", self._tickOut)

        return RTC.RTC_OK

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
        cmds = sys.stdin.readline()
        cmds = cmds.split(" ")
        cmds[0] = OpenRTM_aist.StringUtil.eraseBlank(cmds[0])
        cmds[0] = cmds[0].replace("\n", "")
        cmds[0] = cmds[0].replace("\r", "")
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
            min = 0
            ret, min = OpenRTM_aist.StringUtil.stringTo(min, cmds[1])
            if len(cmds) < 2 or not ret:
                print("minute command needs an integer arg.")
                return RTC.RTC_OK

            self._minute.data = min
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


def InputbuttonInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=inputbutton_spec)
    manager.registerFactory(profile,
                            Inputbutton,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    InputbuttonInit(manager)

    # Create a component
    comp = manager.createComponent("Inputbutton")


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
