#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
# @file SimulatorExecutionContext.py
# @brief SimulatorExecutionContext class
# @date $Date: 2017/06/12$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import threading
import time

import OpenRTM_aist
import OpenRTM__POA, RTC


class SimulatorExecutionContext(OpenRTM_aist.OpenHRPExecutionContext):
  """
  """

  ##
  # @if jp
  # @brief ���󥹥ȥ饯��
  #
  # ���󥹥ȥ饯��
  #
  # @param self
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  #
  # @param self
  #
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.OpenHRPExecutionContext.__init__(self)
    return

  ##
  # @if jp
  # @brief �ǥ��ȥ饯��
  #
  # �ǥ��ȥ饯��
  #
  # @param self
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  # @endif
  #
  def __del__(self):
    return


  ##
  # @if jp
  # @brief �оݤ�RTC�򥢥��ƥ��ֲ�����
  # ������invokeWorkerPreDo�ؿ���Ƥ֤��ᡢ¨�¤�
  # ���֤����ܤ����뤳�Ȥ��Ǥ��롣
  # ����tick�¹���ξ��ϼ¹Խ�λ�ޤ��Ԥ�
  #
  # @param self
  # @param comp �����ƥ��ֲ��о�RT����ݡ��ͥ��
  # @return ReturnCode_t ���Υ꥿���󥳡���
  #
  # @else
  # @brief Activate an RT-component
  #
  #
  # @param self
  # @param comp The target RT-Component for activation
  # @return The return code of ReturnCode_t type
  #
  # @endif
  #
  def activate_component(self, comp):
    guard = OpenRTM_aist.ScopedLock(self._tickmutex)
    rtobj = self._worker.findComponent(comp)
    if not rtobj:
      return RTC.BAD_PARAMETER
    if not rtobj.isCurrentState(RTC.INACTIVE_STATE):
      return RTC.PRECONDITION_NOT_MET
      
    self._syncActivation = False
    OpenRTM_aist.ExecutionContextBase.activateComponent(self, comp)
    
    self.invokeWorkerPreDo()

    if rtobj.isCurrentState(RTC.ACTIVE_STATE):
      return RTC.RTC_OK

    return RTC.RTC_ERROR
    

  ##
  # @if jp
  # @brief �оݤ�RTC���󥢥��ƥ��ֲ�����
  # ������invokeWorkerPreDo�ؿ���Ƥ֤��ᡢ¨�¤�
  # ���֤����ܤ����뤳�Ȥ��Ǥ��롣
  # ����tick�¹���ξ��ϼ¹Խ�λ�ޤ��Ԥ�
  #
  # @param self
  # @param comp �󥢥��ƥ��ֲ��о�RT����ݡ��ͥ��
  # @return ReturnCode_t ���Υ꥿���󥳡���
  #
  # @else
  # @brief Deactivate an RT-component
  #
  #
  # @param self
  # @param comp The target RT-Component for deactivation
  # @return The return code of ReturnCode_t type
  #
  # @endif
  #
  def deactivate_component(self, comp):
    guard = OpenRTM_aist.ScopedLock(self._tickmutex)
    rtobj = self._worker.findComponent(comp)
    if not rtobj:
      return RTC.BAD_PARAMETER
    if not rtobj.isCurrentState(RTC.ACTIVE_STATE):
      return RTC.PRECONDITION_NOT_MET
      
    self._syncActivation = False
    OpenRTM_aist.ExecutionContextBase.deactivateComponent(self, comp)
    
    self.invokeWorkerPreDo()
    self.invokeWorkerDo()
    self.invokeWorkerPostDo()

    if rtobj.isCurrentState(RTC.INACTIVE_STATE):
      return RTC.RTC_OK

    return RTC.RTC_ERROR

  ##
  # @if jp
  # @brief �оݤ�RTC��ꥻ�åȲ�����
  # ������invokeWorkerPreDo�ؿ���Ƥ֤��ᡢ¨�¤�
  # ���֤����ܤ����뤳�Ȥ��Ǥ��롣
  # ����tick�¹���ξ��ϼ¹Խ�λ�ޤ��Ԥ�
  #
  # @param self
  # @param comp �ꥻ�å��о�RT����ݡ��ͥ��
  # @return ReturnCode_t ���Υ꥿���󥳡���
  #
  # @else
  # @brief Reset an RT-component
  #
  #
  # @param self
  # @param comp The target RT-Component for reset
  # @return The return code of ReturnCode_t type
  #
  # @endif
  #
  def reset_component(self, comp):
    guard = OpenRTM_aist.ScopedLock(self._tickmutex)
    rtobj = self._worker.findComponent(comp)
    if not rtobj:
      return RTC.BAD_PARAMETER
    if not rtobj.isCurrentState(RTC.ERROR_STATE):
      return RTC.PRECONDITION_NOT_MET
      
    self._syncActivation = False
    OpenRTM_aist.ExecutionContextBase.activateComponent(self, comp)
    
    self.invokeWorkerPreDo()
    self.invokeWorkerDo()
    self.invokeWorkerPostDo()

    if rtobj.isCurrentState(RTC.INACTIVE_STATE):
      return RTC.RTC_OK

    return RTC.RTC_ERROR


##
# @if jp
# @brief ECFactory�ؤ���Ͽ�Τ���ν�����ؿ�
# @else
# @brief Initialization function to register to ECFactory
# @endif
#
def SimulatorExecutionContextInit(manager):
  OpenRTM_aist.ExecutionContextFactory.instance().addFactory("SimulatorExecutionContext",
                                                             OpenRTM_aist.SimulatorExecutionContext,
                                                             OpenRTM_aist.ECDelete)
  return
