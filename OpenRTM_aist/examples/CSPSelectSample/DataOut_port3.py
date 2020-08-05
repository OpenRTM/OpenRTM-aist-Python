#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist

dataout_port3_spec = ["implementation_id", "DataOut_port3",
                      "type_name", "DataOut_port3",
                      "description", "Data output component",
                      "version", "1.0",
                      "vendor", "Nobuhiko Miyamoto",
                      "category", "example",
                      "activity_type", "DataFlowComponent",
                      "max_instance", "10",
                      "language", "Python",
                      "lang_type", "script",
                      ""]


class DataOut_port3(OpenRTM_aist.DataFlowComponentBase):
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        return

    def onInitialize(self):
        self._data1 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._data2 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._data3 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._cspmanager = OpenRTM_aist.CSPManager()
        self._outport1 = OpenRTM_aist.CSPOutPort(
            "out1", self._data1, self._cspmanager)
        self._outport2 = OpenRTM_aist.CSPOutPort(
            "out2", self._data2, self._cspmanager)
        self._outport3 = OpenRTM_aist.CSPOutPort(
            "out3", self._data3, self._cspmanager)
        # Set OutPort buffer
        self.addOutPort("out1", self._outport1)
        self.addOutPort("out2", self._outport2)
        self.addOutPort("out3", self._outport3)

        return RTC.RTC_OK

    def onExecute(self, ec_id):
        self._data1.data = 1
        self._data2.data = 2
        self._data3.data = 3
        OpenRTM_aist.setTimestamp(self._data1)
        OpenRTM_aist.setTimestamp(self._data2)
        OpenRTM_aist.setTimestamp(self._data3)
        ret, outport, inport = self._cspmanager.select(100)
        if ret:
            if outport:
                self._rtcout.RTC_ERROR("datawrite: %s", outport.name())
                outport.writeData()

        return RTC.RTC_OK


def DataOut_port3Init(manager):
    profile = OpenRTM_aist.Properties(defaults_str=dataout_port3_spec)
    manager.registerFactory(profile,
                            DataOut_port3,
                            OpenRTM_aist.Delete)


def MyModuleInit(manager):
    DataOut_port3Init(manager)

    # Create a component
    comp = manager.createComponent("DataOut_port3")


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
