#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file StaticFSM_pyfsm.py
# @brief Static FSM framework based on pyfsm
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import pyfsm
import RTC


def fsm_topstate(TOP):
    ret = pyfsm.topstate(TOP)

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


def fsm_substate(superstate):
    def _fsm_substate(cls):
        ret = pyfsm.substate(superstate)(cls)

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


def FSM_TOPSTATE(TOP):
    return fsm_topstate(TOP)


def FSM_SUBSTATE(SUPERSTATE):
    return fsm_substate(SUPERSTATE)


class Machine(pyfsm.Machine):
    def __init__(self, TOP, comp):
        self._rtComponent = comp
        super(Machine, self).__init__(TOP)
        self._buffer = OpenRTM_aist.CdrBufferFactory.instance().createObject("ring_buffer")

    def __del__(self):
        pass

    def getBuffer(self):
        return self._buffer

    def init_other(self, other):
        pass

    def equal(self, snapshot):
        pass

    def getComp(self):
        return self._rtComponent

    def run_event(self):
        while self._buffer.readable() > 0:
            _, event = self._buffer.get()
            event()
            self._buffer.advanceRptr()


class Link(pyfsm.StateDef):
    def __init__(self):
        super(Link, self).__init__()
        self._rtComponent = None

    def __del__(self):
        pass

    def setrtc(self):
        if self._rtComponent:
            return
        machine = self._myStateInstance.machine()
        if machine:
            self._rtComponent = machine.getComp()

    def call_entry(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            self.onEntry(*argv)
        else:
            self._rtComponent.postOnFsmStateChange(
                self._state_name(), RTC.RTC_OK)
            self._rtComponent.preOnFsmEntry(self._state_name())
            self._rtComponent.postOnFsmEntry(
                self._state_name(), cls.onEntry(self, *argv))

    def call_init(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            self.onInit(*argv)
        else:
            self._rtComponent.preOnFsmInit(self._state_name())
            self._rtComponent.postOnFsmInit(
                self._state_name(), cls.onInit(self, *argv))

    def call_exit(self, cls, *argv):
        self.setrtc()
        if not self._rtComponent:
            self.onExit(*argv)
        else:
            self._rtComponent.preOnFsmExit(self._state_name())
            self._rtComponent.postOnFsmExit(
                self._state_name(), cls.onExit(self, *argv))
            self._rtComponent.preOnFsmStateChange(self._state_name())

    def onEntry(self):
        return RTC.RTC_OK

    def onInit(self):
        return RTC.RTC_OK

    def onExit(self):
        return RTC.RTC_OK


State = pyfsm.State
deephistory = pyfsm.deephistory
Event = pyfsm.Event
