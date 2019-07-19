#!/usr/bin/env python
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

import sys

import RTC
import OpenRTM_aist
import OpenRTM_aist.StaticFSM as StaticFSM
import OpenRTM_aist.EventPort as EventPort


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



  def onInitialize(self):
    self._fsm = StaticFSM.Machine(MicrowaveFsm.TOP, self)
    #self._fsm.init()
    self._eventIn = EventPort.EventInPort("event", self._fsm)
    
    self.addInPort("event", self._eventIn)
    self._eventIn.bindEvent0("open", MicrowaveFsm.TOP.open)
    self._eventIn.bindEvent0("close", MicrowaveFsm.TOP.close)
    self._eventIn.bindEvent1("minute", MicrowaveFsm.TOP.minute, RTC.TimedLong(RTC.Time(0,0),0))
    self._eventIn.bindEvent0("start", MicrowaveFsm.TOP.start)
    self._eventIn.bindEvent0("stop", MicrowaveFsm.TOP.stop)
    self._eventIn.bindEvent0("tick", MicrowaveFsm.TOP.tick)
    


    return RTC.RTC_OK


  def onFinalize(self):
    self._fsm.shutdown()
    return RTC.RTC_OK

        
  def onExecute(self, ec_id):
    self._fsm.run_event()
    
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
