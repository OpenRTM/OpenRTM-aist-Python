#!/usr/bin/env python
# -*- coding: euc-jp -*-

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

import sys

import RTC
import OpenRTM_aist


import MicrowaveFsm

microwave_spec = ["implementation_id", "Microwave",
                  "type_name",         "Microwave",
                  "description",       "Console input component",
                  "version",           "1.0",
                  "vendor",            "Nobuhiko Miyamoto",
                  "category",          "example",
                  "activity_type",     "DataFlowComponent",
                  "max_instance",      "10",
                  "language",          "Python",
                  "lang_type",         "script",
                  ""]





class Microwave(OpenRTM_aist.DataFlowComponentBase):
  def __init__(self, manager):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
    
    return

  def onFinalize(self):
    self._fsm.exit()
    return RTC.RTC_OK

  def onInitialize(self):
    self._fsm = OpenRTM_aist.Machine(MicrowaveFsm.TOP, self)
    #self._fsm.init()
    self._eventIn = OpenRTM_aist.EventInPort("event", self._fsm)
    
    self.addInPort("event", self._eventIn)
    self._eventIn.bindEvent0("open", "open")
    self._eventIn.bindEvent0("close", "close")
    self._eventIn.bindEvent1("minute", "minute", RTC.TimedLong(RTC.Time(0,0),0))
    self._eventIn.bindEvent0("start", "start")
    self._eventIn.bindEvent0("stop", "stop")
    self._eventIn.bindEvent0("tick", "tick")
    


    return RTC.RTC_OK

        
  def onExecute(self, ec_id):
    
    
    return RTC.RTC_OK


def MicrowaveInit(manager):
  profile = OpenRTM_aist.Properties(defaults_str=microwave_spec)
  manager.registerFactory(profile,
                          Microwave,
                          OpenRTM_aist.Delete)


def MyModuleInit(manager):
  MicrowaveInit(manager)

  # Create a component
  comp = manager.createComponent("Microwave")

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
