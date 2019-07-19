#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist

dataout2_spec = ["implementation_id", "DataOut2",
                  "type_name",         "DataOut2",
                  "description",       "Data output component",
                  "version",           "1.0",
                  "vendor",            "Nobuhiko Miyamoto",
                  "category",          "example",
                  "activity_type",     "DataFlowComponent",
                  "max_instance",      "10",
                  "language",          "Python",
                  "lang_type",         "script",
                  ""]



class DataOut2(OpenRTM_aist.DataFlowComponentBase):
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    return

  def onInitialize(self):
    self._data = RTC.TimedLong(RTC.Time(0,0),0)
    self._outport = OpenRTM_aist.CSPOutPort("out", self._data)
    # Set OutPort buffer
    self.addOutPort("out", self._outport)


    return RTC.RTC_OK


  def onExecute(self, ec_id):
    self._data.data = 1
    self._outport.write()
    self._rtcout.RTC_ERROR("writedata")

    return RTC.RTC_OK


def DataOut2Init(manager):
  profile = OpenRTM_aist.Properties(defaults_str=dataout2_spec)
  manager.registerFactory(profile,
                          DataOut2,
                          OpenRTM_aist.Delete)


def MyModuleInit(manager):
  DataOut2Init(manager)

  # Create a component
  comp = manager.createComponent("DataOut2")

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
