#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-


from __future__ import print_function
import sys
import time

import RTC
import OpenRTM_aist

datainout_spec = ["implementation_id", "DataInOut",
                   "type_name",         "DataInOut",
                   "description",       "Console output component",
                   "version",           "1.0",
                   "vendor",            "Shinji Kurihara",
                   "category",          "example",
                   "activity_type",     "DataFlowComponent",
                   "max_instance",      "10",
                   "language",          "Python",
                   "lang_type",         "script",
                   ""]


class DataInOut(OpenRTM_aist.DataFlowComponentBase):
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    return

  def onInitialize(self):
    self._indata1 = RTC.TimedLong(RTC.Time(0,0),0)
    self._indata2 = RTC.TimedLong(RTC.Time(0,0),0)
    self._indata3 = RTC.TimedLong(RTC.Time(0,0),0)
    self._outdata1 = RTC.TimedLong(RTC.Time(0,0),0)
    self._outdata2 = RTC.TimedLong(RTC.Time(0,0),0)
    self._outdata3 = RTC.TimedLong(RTC.Time(0,0),0)
    self._cspmanager = OpenRTM_aist.CSPManager()
    self._inport1 = OpenRTM_aist.CSPInPort("in1", self._indata1, self._cspmanager)
    self._inport2 = OpenRTM_aist.CSPInPort("in2", self._indata2, self._cspmanager)
    self._inport3 = OpenRTM_aist.CSPInPort("in3", self._indata3, self._cspmanager)
    self._outport1 = OpenRTM_aist.CSPOutPort("out1", self._outdata1, self._cspmanager)
    self._outport2 = OpenRTM_aist.CSPOutPort("out2", self._outdata2, self._cspmanager)
    self._outport3 = OpenRTM_aist.CSPOutPort("out3", self._outdata3, self._cspmanager)
    # Set InPort buffer
    self.addInPort("in1", self._inport1)
    self.addInPort("in2", self._inport2)
    self.addInPort("in3", self._inport3)
    self.addOutPort("out1", self._outport1)
    self.addOutPort("out2", self._outport2)
    self.addOutPort("out3", self._outport3)


    return RTC.RTC_OK

  def onExecute(self, ec_id):
    self._outdata1.data = 1
    self._outdata2.data = 1
    self._outdata3.data = 1
    ret, outport, inport = self._cspmanager.select(100)
    if ret:
      if inport:
        inport.readData()
        self._rtcout.RTC_ERROR("dataread: %s", (inport.name()))
        #self._rtcout.RTC_ERROR("dataread: %s %s", (inport.name(), str(inport.readData())))
      elif outport:
        self._rtcout.RTC_ERROR("datawrite: %s", outport.name())
        outport.writeData()


    return RTC.RTC_OK


def DataInOutInit(manager):
  profile = OpenRTM_aist.Properties(defaults_str=datainout_spec)
  manager.registerFactory(profile,
                          DataInOut,
                          OpenRTM_aist.Delete)

def MyModuleInit(manager):
  DataInOutInit(manager)

  # Create a component
  comp = manager.createComponent("DataInOut")


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
