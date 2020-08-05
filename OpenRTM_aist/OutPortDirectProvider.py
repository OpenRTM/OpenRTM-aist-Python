#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
#  @file OutPortDirectProvider.py
#  @brief OutPortDirectProvider class
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
# 




import OpenRTM_aist


##
# @if jp
# @class OutPortDirectProvider
# @brief OutPortDirectProvider ���饹
#
# �ǡ���������쥯�Ȥ˽񤭹���pull���̿���¸�����OutPort�ץ�Х������饹
#
# @param self
#
# @else
# @class InPortDirectProvider
# @brief InPortDirectProvider class
#
#
# @param self
#
# @endif
#
class OutPortDirectProvider(OpenRTM_aist.OutPortProvider):
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
  # @param self
  #
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.OutPortProvider.__init__(self)
    self.setInterfaceType("direct")



    self._listeners = None
    self._buffer = None
    self._profile   = None
    #self._connector = None
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

    return

  ##
  # @if jp
  # @brief ��λ����
  #
  # @else
  # @brief 
  #
  # 
  #
  # @endif
  #
  def exit(self):
    pass
  
  # void init(coil::Properties& prop);
  def init(self, prop):
    pass


  
  # virtual void setBuffer(BufferBase<cdrMemoryStream>* buffer);
  def setBuffer(self, buffer):
    self._buffer = buffer
    return


  
  # virtual void setListener(ConnectorInfo& info,
  #                          ConnectorListeners* listeners);
  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return


  
  # virtual void setConnector(OutPortConnector* connector);
  def setConnector(self, connector):
    self._connector = connector
    return



    
  
  # inline void onBufferRead(const cdrMemoryStream& data)
  def onBufferRead(self, data):
    if self._listeners and self._profile:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ].notify(self._profile, data)
    return

  
  # inline void onSend(const cdrMemoryStream& data)
  def onSend(self, data):
    if self._listeners and self._profile:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_SEND].notify(self._profile, data)
    return

  
  # inline void onBufferEmpty()
  def onBufferEmpty(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY].notify(self._profile)
    return

  
  # inline void onBufferReadTimeout()
  def onBufferReadTimeout(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT].notify(self._profile)
    return

  
  # inline void onSenderEmpty()
  def onSenderEmpty(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY].notify(self._profile)
    return

  
  # inline void onSenderTimeout()
  def onSenderTimeout(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT].notify(self._profile)
    return

  
  # inline void onSenderError()
  def onSenderError(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR].notify(self._profile)
    return


  


def OutPortDirectProviderInit():
  factory = OpenRTM_aist.OutPortProviderFactory.instance()
  factory.addFactory("direct",
                     OpenRTM_aist.OutPortDirectProvider,
                     OpenRTM_aist.Delete)
