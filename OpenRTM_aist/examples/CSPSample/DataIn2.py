#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-


from __future__ import print_function
import sys
import time

import RTC
import OpenRTM_aist

datain2_spec = ["implementation_id", "DataIn2",
                   "type_name",         "DataIn2",
                   "description",       "Console output component",
                   "version",           "1.0",
                   "vendor",            "Shinji Kurihara",
                   "category",          "example",
                   "activity_type",     "DataFlowComponent",
                   "max_instance",      "10",
                   "language",          "Python",
                   "lang_type",         "script",
                   ""]


class DataIn2(OpenRTM_aist.DataFlowComponentBase):
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    return

  def onInitialize(self):
    self._data = RTC.TimedLong(RTC.Time(0,0),0)
    self._inport = OpenRTM_aist.CSPInPort("in", self._data)
    # Set InPort buffer
    self.addInPort("in", self._inport)


    return RTC.RTC_OK

  def onExecute(self, ec_id):
    data = self._inport.read()
    self._rtcout.RTC_ERROR("dataread: %s", str(data))

    return RTC.RTC_OK


def DataIn2Init(manager):
  profile = OpenRTM_aist.Properties(defaults_str=datain2_spec)
  manager.registerFactory(profile,
                          DataIn2,
                          OpenRTM_aist.Delete)

def MyModuleInit(manager):
  DataIn2Init(manager)

  # Create a component
  comp = manager.createComponent("DataIn2")


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
