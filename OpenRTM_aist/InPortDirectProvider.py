#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
#  @file InPortDirectProvider.py
#  @brief InPortDirectProvider class
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
# 




import OpenRTM_aist


##
# @if jp
# @class InPortDirectProvider
# @brief InPortDirectProvider ���饹
#
# �ǡ���������쥯�Ȥ˽񤭹���push���̿���¸�����InPort�ץ�Х������饹
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
class InPortDirectProvider(OpenRTM_aist.InPortProvider):
    
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
  # @param self
  #
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.InPortProvider.__init__(self)

    # PortProfile setting
    self.setInterfaceType("direct")
    
    
    
    self._buffer = None

    self._profile = None
    self._listeners = None
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
  
  ## void init(coil::Properties& prop);
  def init(self, prop):
    pass

  ## void setBuffer(BufferBase<cdrMemoryStream>* buffer);
  def setBuffer(self, buffer):
    self._buffer = buffer
    return

  # void setListener(ConnectorInfo& info,
  #                  ConnectorListeners* listeners);
  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return

  
  ## void onBufferWrite(const cdrMemoryStream& data)
  def onBufferWrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE].notify(self._profile, data)
    return


  ## inline void onBufferFull(const cdrMemoryStream& data)
  def onBufferFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL].notify(self._profile, data)
    return


  ## inline void onBufferWriteTimeout(const cdrMemoryStream& data)
  def onBufferWriteTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT].notify(self._profile, data)
    return

  ## inline void onBufferWriteOverwrite(const cdrMemoryStream& data)
  def onBufferWriteOverwrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE].notify(self._profile, data)
    return


  ## inline void onReceived(const cdrMemoryStream& data)
  def onReceived(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED].notify(self._profile, data)
    return


  ## inline void onReceiverFull(const cdrMemoryStream& data)
  def onReceiverFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL].notify(self._profile, data)
    return


  ## inline void onReceiverTimeout(const cdrMemoryStream& data)
  def onReceiverTimeout(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT].notify(self._profile, data)
    return


  ## inline void onReceiverError(const cdrMemoryStream& data)
  def onReceiverError(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR].notify(self._profile, data)
    return
  




def InPortDirectProviderInit():
  factory = OpenRTM_aist.InPortProviderFactory.instance()
  factory.addFactory("direct",
                     OpenRTM_aist.InPortDirectProvider,
                     OpenRTM_aist.Delete)
