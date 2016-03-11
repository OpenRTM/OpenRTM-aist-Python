#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file  OutPortSHMProvider.py
# @brief OutPortSHMProvider class
# @date  $Date: 2016-01-12 $
# @author Nobuhiko Miyamoto
#
#

import sys
from omniORB import *
from omniORB import any

import OpenRTM_aist
import OpenRTM__POA,OpenRTM


##
# @if jp
# @class OutPortSHMProvider
# @brief OutPortSHMProvider ���饹
#
# OutPortProvider 
#
# �̿����ʤ� ��ͭ���� �����Ѥ������ϥݡ��ȥץ��Х����μ������饹��
#
#
# @else
# @class OutPortSHMProvider
# @brief OutPortSHMProvider class
#
#
#
# @endif
#
class OutPortSHMProvider(OpenRTM_aist.OutPortProvider,OpenRTM_aist.SharedMemory):
  ##
  # @if jp
  # @brief ���󥹥ȥ饯��
  # ��ͭ����ζ���̾��UUID�Ǻ����������ͥ����ץ��ե������dataport.shared_memory.address����¸����
  #
  # ���󥹥ȥ饯��
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  #
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.OutPortProvider.__init__(self)
    OpenRTM_aist.SharedMemory.__init__(self)
    self.setInterfaceType("shared_memory")
    
    self._objref = self._this()
    self._buffer = None
    orb = OpenRTM_aist.Manager.instance().getORB()
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.outport_ior",
                                                      orb.object_to_string(self._objref)))
    self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.outport_ref",
                                                      self._objref))
    self._listeners = None
    self._connector = None
    self._profile   = None
    

    self._shm_address = str(OpenRTM_aist.uuid1())
    
    

    

    
    
    

    return


  ##
  # @if jp
  # @brief �ǥ��ȥ饯��
  #
  # �ǥ��ȥ饯��
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @endif
  #
  def __del__(self):
    oid = self._default_POA().servant_to_id(self)
    self._default_POA().deactivate_object(oid)
    
      
    return


  
  # virtual void init(coil::Properties& prop);
  def init(self, prop):

    ds = prop.getProperty("shem_default_size")
    self._memory_size = self.string_to_MemorySize(ds)

    
  def setBuffer(self, buffer):
    self._buffer = buffer
    return
  
  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return
  
  def setConnector(self, connector):
    self._connector = connector
    return

  
    
  
  ##
  # @if jp
  # @brief �Хåե�����ǡ������������
  #
  # @return (�꥿���󥳡��ɡ������ǡ���)
  #
  # @else
  # @brief Get data from the buffer
  #
  #
  # @return 
  #
  # @endif
  #
  # virtual ::OpenRTM::PortStatus get(::OpenRTM::CdrData_out data);
  def get(self):
    self._rtcout.RTC_PARANOID("OutPortSHMProvider.get()")
    
    if not self._buffer:
      self.onSenderError()
      return OpenRTM.UNKNOWN_ERROR

    try:
      if self._buffer.empty():
        self._rtcout.RTC_ERROR("buffer is empty.")
        return OpenRTM.BUFFER_EMPTY

      cdr = [None]
      ret = self._buffer.read(cdr)
      
      if ret == OpenRTM_aist.BufferStatus.BUFFER_OK:
        if not cdr[0]:
          self._rtcout.RTC_ERROR("buffer is empty.")
          return OpenRTM.BUFFER_EMPTY
      
    except:
      self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
      return OpenRTM.UNKNOWN_ERROR

    self.create_memory(self._memory_size, self._shm_address)
    self.write(cdr[0])
    
    return self.convertReturn(ret, cdr[0])

    
  def onBufferRead(self, data):
    if self._listeners and self._profile:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ].notify(self._profile, data)
    return

  def onSend(self, data):
    if self._listeners and self._profile:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_SEND].notify(self._profile, data)
    return    
    
    

  def onBufferEmpty(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY].notify(self._profile)
    return
  
  def onBufferReadTimeout(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT].notify(self._profile)
    return

  def onSenderEmpty(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY].notify(self._profile)
    return

  def onSenderTimeout(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT].notify(self._profile)
    return

  def onSenderError(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR].notify(self._profile)
    return

  def convertReturn(self, status, data):
    if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
      self.onBufferRead(data)
      self.onSend(data)
      return OpenRTM.PORT_OK
    
    elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
      self.onSenderError()
      return OpenRTM.PORT_ERROR
    
    elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
      # never come here
      return OpenRTM.BUFFER_FULL

    elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
      self.onBufferEmpty()
      self.onSenderEmpty()
      return OpenRTM.BUFFER_EMPTY

    elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
      self.onSenderError()
      return OpenRTM.PORT_ERROR
    
    elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
      self.onBufferReadTimeout()
      self.onSenderTimeout()
      return OpenRTM.BUFFER_TIMEOUT
    
    else:
      return OpenRTM.UNKNOWN_ERROR
    
    self.onSenderError()
    return OpenRTM.UNKNOWN_ERROR




def OutPortSHMProviderInit():
  factory = OpenRTM_aist.OutPortProviderFactory.instance()
  factory.addFactory("shared_memory",
                     OpenRTM_aist.OutPortSHMProvider,
                     OpenRTM_aist.Delete)