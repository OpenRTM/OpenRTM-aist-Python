#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
#  @file OutPortDirectConsumer.py
#  @brief OutPortDirectConsumer class
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
# 




import OpenRTM_aist


##
# @if jp
#
# @class InPortDirectConsumer
#
# @brief InPortDirectConsumer ���饹
#
# �ǡ���������쥯�Ȥ˽񤭹���pull���̿���¸�����OutPort���󥷥�ޡ����饹
#
# @else
# @class InPortDirectConsumer
#
# @brief InPortDirectConsumer class
#
#
#
# @endif
#
class OutPortDirectConsumer(OpenRTM_aist.OutPortConsumer):
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
    OpenRTM_aist.OutPortConsumer.__init__(self)
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OutPortDirectConsumer")
    self._listeners = None
    self._profile = None
    self._properties = None
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
  def __del__(self, CorbaConsumer=OpenRTM_aist.CorbaConsumer):
    self._rtcout.RTC_PARANOID("~OutPortDirectConsumer()")
    
    pass


  ##
  # @if jp
  # @brief ��������
  #
  # InPortConsumer�γƼ������Ԥ�
  #
  # @self
  # 
  #
  # @else
  # @brief Initializing configuration
  #
  #
  # @endif
  #
  # virtual void init(coil::Properties& prop);
  def init(self, prop):
    self._rtcout.RTC_TRACE("init()")
    self._properties = prop
    return

  ##
  # @if jp
  # @brief 
  #
  # @param self
  # @param data
  # @return 
  #
  # @else
  # @brief 
  #
  # @param self
  # @param data
  # @return 
  #
  # @endif
  #
  # virtual ReturnCode put(const cdrMemoryStream& data);
  def get(self, data):
    self._rtcout.RTC_PARANOID("get()")
    return self.UNKNOWN_ERROR
  

  # virtual void setBuffer(CdrBufferBase* buffer);
  def setBuffer(self, buffer):
    self._rtcout.RTC_TRACE("setBuffer()")
    return
  

  # void OutPortCorbaCdrConsumer::setListener(ConnectorInfo& info,
  #                                           ConnectorListeners* listeners)
  def setListener(self, info, listeners):
    self._rtcout.RTC_TRACE("setListener()")
    self._listeners = listeners
    self._profile = info
    return


  


  ##
  # @if jp
  # @brief InterfaceProfile������������
  #
  #
  # @param self
  # @param properties InterfaceProfile�����������ץ�ѥƥ�
  #
  # @else
  # @brief Publish InterfaceProfile information
  #
  #
  # @param self
  # @param properties Properties to get InterfaceProfile information
  #
  # @endif
  #
  # virtual void publishInterfaceProfile(SDOPackage::NVList& properties);
  def subscribeInterface(self, properties):
    self._rtcout.RTC_TRACE("subscribeInterface()")
    

    return True


  ##
  # @if jp
  # @brief �ǡ����������Τؤ���Ͽ
  #
  # @param self
  # @param properties ��Ͽ����
  #
  # @return ��Ͽ�������(��Ͽ����:true����Ͽ����:false)
  #
  # @else
  # @brief Subscribe to the data sending notification
  #
  # @param self
  # @param properties Information for subscription
  #
  # @return Subscription result (Successful:true, Failed:false)
  #
  # @endif
  #
  # virtual bool subscribeInterface(const SDOPackage::NVList& properties);
  def unsubscribeInterface(self, properties):
    self._rtcout.RTC_TRACE("unsubscribeInterface()")
    return


  

    
  
  # inline void onBufferWrite(const cdrMemoryStream& data)
  def onBufferWrite(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE].notify(self._profile, data)

    return


  # inline void onBufferFull(const cdrMemoryStream& data)
  def onBufferFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL].notify(self._profile, data)

    return


  # inline void onReceived(const cdrMemoryStream& data)
  def onReceived(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED].notify(self._profile, data)

    return


  # inline void onReceiverFull(const cdrMemoryStream& data)
  def onReceiverFull(self, data):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL].notify(self._profile, data)

    return


  ##
  # @brief Connector listener functions
  #
  # inline void onSenderEmpty()
  def onSenderEmpty(self):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY].notify(self._profile)

    return


  # inline void onSenderTimeout()
  def onSenderTimeout(self):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT].notify(self._profile)

    return

      
  # inline void onSenderError()
  def onSenderError(self):
    if self._listeners is not None and self._profile is not None:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR].notify(self._profile)

    return


def OutPortDirectConsumerInit():
  factory = OpenRTM_aist.OutPortConsumerFactory.instance()
  factory.addFactory("direct",
                     OpenRTM_aist.OutPortDirectConsumer,
                     OpenRTM_aist.Delete)
  return
