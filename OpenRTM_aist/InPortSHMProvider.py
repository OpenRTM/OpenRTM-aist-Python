#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file  InPortSHMProvider.py
# @brief InPortSHMProvider class
# @date  $Date: 2016/01/08 $
# @author Nobuhiko Miyamoto


import sys
from omniORB import *
from omniORB import any

import OpenRTM_aist
import OpenRTM__POA,OpenRTM


##
# @if jp
# @class InPortSHMProvider
# @brief InPortSHMProvider ���饹
#
# �̿����ʤ� ��ͭ���� �����Ѥ������ϥݡ��ȥץ��Х������μ������饹��
#
#
# @else
# @class InPortCorbaCdrProvider
# @brief InPortCorbaCdrProvider class
#
#
#
# @endif
#
class InPortSHMProvider(OpenRTM_aist.InPortProvider, OpenRTM_aist.SharedMemory):
    
  """
  """

  ##
  # @if jp
  # @brief ���󥹥ȥ饯��
  #
  # ���󥹥ȥ饯��
  # Interface Type�ˤ�shared_memory����ꤹ��
  # ��ͭ����ζ���̾��UUID�Ǻ����������ͥ����ץ��ե������dataport.shared_memory.address����¸����
  #
  # self
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  #
  # self
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.InPortProvider.__init__(self)
    OpenRTM_aist.SharedMemory.__init__(self)

    # PortProfile setting
    self.setInterfaceType("shared_memory")
    self._objref = self._this()
    
    
    
    self._buffer = None

    self._profile = None
    self._listeners = None

    orb = OpenRTM_aist.Manager.instance().getORB()
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ior",
                                                      orb.object_to_string(self._objref)))
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ref",
                                                      self._objref))
    

    
    
    

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
  #
  # @endif
  #
  def __del__(self):
    oid = OpenRTM_aist.Manager.instance().getPOA().servant_to_id(self)
    OpenRTM_aist.Manager.instance().getPOA().deactivate_object(oid)
    
      
      
    return

  
  # void init(coil::Properties& prop)
  def init(self, prop):
          
    pass

  def setBuffer(self, buffer):
    self._buffer = buffer
    return

  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return


  ##
  # @if jp
  # @brief �Хåե��˥ǡ�����񤭹���
  #
  # �ǡ����Υ������϶�ͭ�������Ƭ8byte�����������
  # ��ͭ���꤫��ǡ�������Ф��Хåե��˽񤭹���
  #
  # @param data ����оݥǡ���
  #
  # @else
  # @brief 
  #
  # 
  #
  # @param data 
  #
  # @endif
  #
  # ::OpenRTM::PortStatus put(const ::OpenRTM::CdrData& data)
  #  throw (CORBA::SystemException);
  def put(self):
    
    try:
      self._rtcout.RTC_PARANOID("InPortCorbaCdrProvider.put()")
            
      
      

      
      shm_data = self.read()

      if not self._buffer:
        self.onReceiverError(shm_data)
        return OpenRTM.PORT_ERROR

      self._rtcout.RTC_PARANOID("received data size: %d", len(shm_data))

      self.onReceived(shm_data)

      if not self._connector:
        return OpenRTM.PORT_ERROR



      ret = self._connector.write(shm_data)
      

      return self.convertReturn(ret, shm_data)

    except:
      self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
      return OpenRTM.UNKNOWN_ERROR
    return OpenRTM.UNKNOWN_ERROR
    
      
      
      
    return self.convertReturn(ret, data)
      
      
  def onBufferWrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE].notify(self._profile, data)
    return

  def onBufferFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL].notify(self._profile, data)
    return

  def onBufferWriteTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT].notify(self._profile, data)
    return

  def onBufferWriteOverwrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE].notify(self._profile, data)
    return

  def onReceived(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED].notify(self._profile, data)
    return

  def onReceiverFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL].notify(self._profile, data)
    return

  def onReceiverTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT].notify(self._profile, data)
    return

  def onReceiverError(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR].notify(self._profile, data)
    return

      

      
      

  

def InPortSHMProviderInit():
  factory = OpenRTM_aist.InPortProviderFactory.instance()
  factory.addFactory("shared_memory",
                     OpenRTM_aist.InPortSHMProvider,
                     OpenRTM_aist.Delete)