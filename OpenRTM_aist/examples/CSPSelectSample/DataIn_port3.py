#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-


from __future__ import print_function
import sys
import time

import RTC
import OpenRTM_aist

datain_port3_spec = ["implementation_id", "DataIn_port3",
                   "type_name",         "DataIn_port3",
                   "description",       "Console output component",
                   "version",           "1.0",
                   "vendor",            "Shinji Kurihara",
                   "category",          "example",
                   "activity_type",     "DataFlowComponent",
                   "max_instance",      "10",
                   "language",          "Python",
                   "lang_type",         "script",
                   ""]


class DataIn_port3(OpenRTM_aist.DataFlowComponentBase):
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    return

  def onInitialize(self):
    self._data1 = RTC.TimedLong(RTC.Time(0,0),0)
    self._data2 = RTC.TimedLong(RTC.Time(0,0),0)
    self._data3 = RTC.TimedLong(RTC.Time(0,0),0)
    self._cspmanager = OpenRTM_aist.CSPManager()
    self._inport1 = OpenRTM_aist.CSPInPort("in1", self._data1, self._cspmanager)
    self._inport2 = OpenRTM_aist.CSPInPort("in2", self._data2, self._cspmanager)
    self._inport3 = OpenRTM_aist.CSPInPort("in3", self._data3, self._cspmanager)
    # Set InPort buffer
    self.addInPort("in1", self._inport1)
    self.addInPort("in2", self._inport2)
    self.addInPort("in3", self._inport3)


    return RTC.RTC_OK

  def onExecute(self, ec_id):
    ret, outport, inport = self._cspmanager.select(100)
    if ret:
      if inport:
        inport.readData()
        self._rtcout.RTC_ERROR("dataread: %s", (inport.name()))
        #self._rtcout.RTC_ERROR("dataread: %s %s", (inport.name(), str(inport.readData())))

    return RTC.RTC_OK


def DataIn_port3Init(manager):
  profile = OpenRTM_aist.Properties(defaults_str=datain_port3_spec)
  manager.registerFactory(profile,
                          DataIn_port3,
                          OpenRTM_aist.Delete)

def MyModuleInit(manager):
  DataIn_port3Init(manager)

  # Create a component
  comp = manager.createComponent("DataIn_port3")


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
