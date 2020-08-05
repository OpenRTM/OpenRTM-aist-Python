#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file RTObjectStateMachine.py
# @brief ExecutionContext's state machine worker class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#     Noriaki Ando
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

from omniORB import CORBA

import OpenRTM_aist
import RTC

NUM_OF_LIFECYCLESTATE = 4


class RTObjectStateMachine:
    """
    """

    # RTObjectStateMachine(RTC::ExecutionContextHandle_t id,
    #                      RTC::LightweightRTObject_ptr comp);
    def __init__(self, id, comp):
        global NUM_OF_LIFECYCLESTATE
        self._id = id
        self._rtobj = comp
        self._sm = OpenRTM_aist.StateMachine(NUM_OF_LIFECYCLESTATE)
        self._ca = False
        self._dfc = False
        self._fsm = False
        self._mode = False
        self._caVar = None
        self._dfcVar = None
        self._fsmVar = None
        self._modeVar = None
        self._rtObjPtr = None
        self._activation = False
        self._deactivation = False
        self._reset = False

        # Setting Action callback objects
        self.setComponentAction(comp)
        self.setDataFlowComponentAction(comp)
        self.setFsmParticipantAction(comp)
        self.setMultiModeComponentAction(comp)
        # Setting callback functions to StateMachine
        self._sm.setListener(self)
        self._sm.setEntryAction(RTC.ACTIVE_STATE,
                                self.onActivated)
        self._sm.setDoAction(RTC.ACTIVE_STATE,
                             self.onExecute)
        self._sm.setPostDoAction(RTC.ACTIVE_STATE,
                                 self.onStateUpdate)
        self._sm.setExitAction(RTC.ACTIVE_STATE,
                               self.onDeactivated)
        # self._sm.setDoAction  (RTC.ACTIVE_STATE,
        #                        self.onAction)
        self._sm.setEntryAction(RTC.ERROR_STATE,
                                self.onAborting)
        self._sm.setDoAction(RTC.ERROR_STATE,
                             self.onError)
        self._sm.setExitAction(RTC.ERROR_STATE,
                               self.onReset)
        # Setting inital state
        st = OpenRTM_aist.StateHolder()
        st.prev = RTC.INACTIVE_STATE
        st.curr = RTC.INACTIVE_STATE
        st.next = RTC.INACTIVE_STATE
        self._sm.setStartState(st)
        self._sm.goTo(RTC.INACTIVE_STATE)
        return

    def __del__(self):
        if self._ca:
            self._ca = False
            self._caVar = None

        if self._dfc:
            self._dfc = False
            self._dfcVar = None

        if self._fsm:
            self._fsm = False
            self._fsmVar = None

        if self._mode:
            self._mode = False
            self._modeVar = None

        return

    # functions for stored RTObject reference
    # RTC::LightweightRTObject_ptr getRTObject();

    def getRTObject(self):
        return self._rtobj

    # bool isEquivalent(RTC::LightweightRTObject_ptr comp);
    def isEquivalent(self, comp):
        return self._rtobj._is_equivalent(comp)

    # RTC::ExecutionContextHandle_t getExecutionContextHandle();
    def getExecutionContextHandle(self):
        return self._id

    # RTC::ComponentAction operations
    # void onStartup(void);
    def onStartup(self):
        if self._rtObjPtr:
            self._rtObjPtr.on_startup(self._id)
            return
        if not self._ca:
            return
        self._caVar.on_startup(self._id)
        return

    # void onShutdown(void);
    def onShutdown(self):
        if self._rtObjPtr:
            self._rtObjPtr.on_shutdown(self._id)
            return

        if not self._ca:
            return
        self._caVar.on_shutdown(self._id)
        return

    # void onActivated(const ExecContextStates& st);
    def onActivated(self, st):
        if self._rtObjPtr:
            if self._rtObjPtr.on_activated(self._id) != RTC.RTC_OK:
                self._sm.goTo(RTC.ERROR_STATE)
            return

        if not self._ca:
            return
        if self._caVar.on_activated(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # void onDeactivated(const ExecContextStates& st);
    def onDeactivated(self, st):
        if self._rtObjPtr:
            self._rtObjPtr.on_deactivated(self._id)
            return

        if not self._ca:
            return
        self._caVar.on_deactivated(self._id)
        return

    # void onAborting(const ExecContextStates& st);
    def onAborting(self, st):
        if self._rtObjPtr:
            self._rtObjPtr.on_aborting(self._id)
            return

        if not self._ca:
            return
        self._caVar.on_aborting(self._id)
        return

    # void onError(const ExecContextStates& st);
    def onError(self, st):
        if self._rtObjPtr:
            self._rtObjPtr.on_error(self._id)
            return

        if not self._ca:
            return
        self._caVar.on_error(self._id)
        return

    # void onReset(const ExecContextStates& st);
    def onReset(self, st):
        if self._rtObjPtr:
            if self._rtObjPtr.on_reset(self._id) != RTC.RTC_OK:
                self._sm.goTo(RTC.ERROR_STATE)
            return

        if not self._ca:
            return
        if self._caVar.on_reset(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # RTC::DataflowComponentAction
    # void onExecute(const ExecContextStates& st);
    def onExecute(self, st):
        if self.isNextState(RTC.ERROR_STATE):
            return
        if self._rtObjPtr:
            if self._rtObjPtr.on_execute(self._id) != RTC.RTC_OK:
                self._sm.goTo(RTC.ERROR_STATE)
            return

        if not self._dfc:
            return

        if self._dfcVar.on_execute(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # void onStateUpdate(const ExecContextStates& st);
    def onStateUpdate(self, st):
        if self.isNextState(RTC.ERROR_STATE):
            return
        if self._rtObjPtr:
            if self._rtObjPtr.on_state_update(self._id) != RTC.RTC_OK:
                self._sm.goTo(RTC.ERROR_STATE)
            return

        if not self._dfc:
            return

        if self._dfcVar.on_state_update(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # RTC::ReturnCode_t onRateChanged(void);
    def onRateChanged(self):
        if self._rtObjPtr:
            ret = self._rtObjPtr.on_rate_changed(self._id)
            if ret != RTC.RTC_OK:
                self._sm.goTo(RTC.ERROR_STATE)
            return ret

        if not self._dfc:
            return RTC.RTC_ERROR

        ret = self._dfcVar.on_rate_changed(self._id)
        if ret != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return ret

    # FsmParticipantAction
    # void onAction(const ExecContextStates& st);
    def onAction(self, st):
        if not self._fsm:
            return

        if self._fsmVar.on_action(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # MultiModeComponentAction
    # void onModeChanged(const ExecContextStates& st);
    def onModeChanged(self, st):
        if not self._mode:
            return

        if self._modeVar.on_mode_changed(self._id) != RTC.RTC_OK:
            self._sm.goTo(RTC.ERROR_STATE)
        return

    # Getting state of the context
    # ExecContextState getState(void);
    def getState(self):
        return self._sm.getState()

    # ExecContextStates getStates(void);
    def getStates(self):
        return self._sm.getStates()

    # bool isCurrentState(ExecContextState state);
    def isCurrentState(self, state):
        return self.getState() == state

    # bool isNextState(ExecContextState state);
    def isNextState(self, state):
        return self._sm.getStates().next == state

    # void goTo(ExecContextState state);
    def goTo(self, state):
        self._sm.goTo(state)
        return

    # Workers
    # void workerPreDo(void);
    def workerPreDo(self):
        self.updateState()
        return self._sm.worker_pre()

    # void workerDo(void);
    def workerDo(self):
        return self._sm.worker_do()

    # void workerPostDo(void);
    def workerPostDo(self):
        return self._sm.worker_post()

    def activate(self):
        if self.isCurrentState(RTC.INACTIVE_STATE):
            self._activation = True
            return True
        return False

    def deactivate(self):
        if self.isCurrentState(RTC.ACTIVE_STATE):
            self._deactivation = True
            return True
        return False

    def reset(self):
        if self.isCurrentState(RTC.ERROR_STATE):
            self._reset = True
            return True
        return False

    def updateState(self):
        if self._activation:
            if self.isCurrentState(RTC.INACTIVE_STATE) and not self.isNextState(RTC.ERROR_STATE):
                self._sm.goTo(RTC.ACTIVE_STATE)
            self._activation = False

        if self._deactivation:
            if self.isCurrentState(RTC.ACTIVE_STATE) and not self.isNextState(RTC.ERROR_STATE):
                self._sm.goTo(RTC.INACTIVE_STATE)
            self._deactivation = False

        if self._reset:
            if self.isCurrentState(RTC.ERROR_STATE):
                self._sm.goTo(RTC.INACTIVE_STATE)
            self._reset = False

    # void setComponentAction(const RTC::LightweightRTObject_ptr comp);

    def setComponentAction(self, comp):
        self._caVar = comp._narrow(RTC.ComponentAction)
        if CORBA.is_nil(self._caVar):
            return
        self._ca = True

        poa = OpenRTM_aist.Manager.instance().getPOA()
        try:
            self._rtObjPtr = poa.reference_to_servant(comp)
        except CORBA.SystemException:
            self._rtObjPtr = None
        except BaseException:
            self._rtObjPtr = None

        return

    # void setDataFlowComponentAction(const RTC::LightweightRTObject_ptr comp);
    def setDataFlowComponentAction(self, comp):
        self._dfcVar = comp._narrow(RTC.DataFlowComponentAction)
        if not CORBA.is_nil(self._dfcVar):
            self._dfc = True
        return

    # void setFsmParticipantAction(const RTC::LightweightRTObject_ptr comp);
    def setFsmParticipantAction(self, comp):
        self._fsmVar = comp._narrow(RTC.FsmParticipantAction)
        if not CORBA.is_nil(self._fsmVar):
            self._fsm = True
        return

    # void setMultiModeComponentAction(const RTC::LightweightRTObject_ptr
    # comp);
    def setMultiModeComponentAction(self, comp):
        self._modeVar = comp._narrow(RTC.MultiModeComponentAction)
        if not CORBA.is_nil(self._modeVar):
            self._mode = True
        return
