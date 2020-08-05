#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
#  @file InPortDirectConsumer.py
#  @brief InPortDirectConsumer class
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
# �ǡ���������쥯�Ȥ˽񤭹���push���̿���¸�����InPort���󥷥�ޡ����饹
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
class InPortDirectConsumer(OpenRTM_aist.InPortConsumer):
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
    OpenRTM_aist.InPortConsumer.__init__(self)
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("InPortDirectConsumer")
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
  def __del__(self):
    self._rtcout.RTC_PARANOID("~InPortDirectConsumer()")
    
    return

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
  def put(self, data):
    self._rtcout.RTC_PARANOID("put()")

        
    return self.UNKNOWN_ERROR

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
  def publishInterfaceProfile(self, properties):
    return

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
  def subscribeInterface(self, properties):
    self._rtcout.RTC_TRACE("subscribeInterface()")
    
    
    return True
    
  ##
  # @if jp
  # @brief �ǡ����������Τ������Ͽ���
  #
  # @param self
  # @param properties ��Ͽ�������
  #
  # @else
  # @brief Unsubscribe the data send notification
  #
  # 
  # @param self
  # @param properties Information for unsubscription
  #
  # @endif
  #
  # virtual void unsubscribeInterface(const SDOPackage::NVList& properties);
  def unsubscribeInterface(self, properties):
    self._rtcout.RTC_TRACE("unsubscribeInterface()")
    
    return

  


def InPortDirectConsumerInit():
  factory = OpenRTM_aist.InPortConsumerFactory.instance()
  factory.addFactory("direct",
                     OpenRTM_aist.InPortDirectConsumer,
                     OpenRTM_aist.Delete)
