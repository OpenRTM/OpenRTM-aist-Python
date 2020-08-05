#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file Microwave.py
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


import OpenRTM_aist.StaticFSM_pyfsm as StaticFSM


@StaticFSM.FSM_TOPSTATE
class TOP(StaticFSM.Link):
    def onInit(self):
        self.set_state(StaticFSM.State(Operational))
        return RTC.RTC_OK

    def open(self):
        pass

    def close(self):
        pass

    def minute(self, time_):
        pass

    def start(self):
        pass

    def stop(self):
        pass

    def tick(self):
        pass

    class Data:
        def __init__(self):
            self.myCookingTime = 0

        def printTimer(self):
            print(" Timer set to ", self.myCookingTime, " minutes")

        def incrementTimer(self):
            self.myCookingTime += 1

        def decrementTimer(self):
            self.myCookingTime -= 1

        def resetTimer(self):
            self.myCookingTime = 0

        def getRemainingTime(self):
            return self.myCookingTime


@StaticFSM.FSM_SUBSTATE(TOP)
class Disabled(StaticFSM.Link):
    def onEntry(self):
        print("  Microwave opened")
        return RTC.RTC_OK

    def onExit(self):
        print("  Microwave closed")
        return RTC.RTC_OK

    def close(self):
        # self.setStateHistory(OpenRTM_aist.Macho.State(Operational))
        self.set_state(StaticFSM.State(Operational))


@StaticFSM.deephistory
@StaticFSM.FSM_SUBSTATE(TOP)
class Operational(StaticFSM.Link):
    def open(self):
        self.set_state(StaticFSM.State(Disabled))

    def stop(self):
        self.set_state(StaticFSM.State(Idle))

    def onInit(self):
        self.set_state(StaticFSM.State(Idle))
        return RTC.RTC_OK


@StaticFSM.FSM_SUBSTATE(Operational)
class Idle(StaticFSM.Link):
    def minute(self, time_):
        self.set_state(StaticFSM.State(Programmed))
        self.dispatch(StaticFSM.Event(TOP.minute, time_))

    def onEntry(self):
        self.data(TOP).resetTimer()
        print("  Microwave ready")
        return RTC.RTC_OK


@StaticFSM.FSM_SUBSTATE(Operational)
class Programmed(StaticFSM.Link):
    def minute(self, time_):
        for t in range(time_.data):
            self.data(TOP).incrementTimer()
        self.data(TOP).printTimer()

    def start(self):
        self.set_state(StaticFSM.State(Cooking))


@StaticFSM.FSM_SUBSTATE(Programmed)
class Cooking(StaticFSM.Link):
    def tick(self):
        print("  Clock tick")
        tb = self.data(TOP)
        tb.decrementTimer()
        if tb.getRemainingTime() == 0:
            print("  Finished")
            self.set_state(StaticFSM.State(Idle))
        else:
            tb.printTimer()

    def onEntry(self):
        print("  Heating on")
        return RTC.RTC_OK

    def onExit(self):
        print("  Heating off")
        return RTC.RTC_OK
