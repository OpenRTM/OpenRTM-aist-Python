#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
# @file NamingServiceNumberingPolicy.py
# @brief Object numbering policy class
# @date $Date: 2016/02/25$
# @author Nobuhiko Miyamoto
#


import OpenRTM_aist







##
# @if jp
#
# @class NamingServiceNumberingPolicy
# @brief ���֥��������������͡��ߥ󥰡��ݥꥷ��(̿̾��§)�����ѥ��饹
#���͡��ߥ󥰥����ӥ�����RTC�򸡺����ƥʥ�Х�󥰤�Ԥ�
#
#
# @else
#
# @endif
class NamingServiceNumberingPolicy(OpenRTM_aist.NumberingPolicy):
  """
  """

  ##
  # @if jp
  #
  # @brief ���󥹥ȥ饯��
  # 
  # ���󥹥ȥ饯��
  # 
  # @param self
  # 
  # @else
  #
  # @brief virtual destractor
  #
  # @endif
  def __init__(self):
    self._num = 0
    self._objects = []
    self._mgr = OpenRTM_aist.Manager.instance()


  ##
  # @if jp
  #
  # @brief ���֥���������������̾�κ���
  #
  # 
  # 
  # @param self
  # @param obj ̾�������оݥ��֥�������
  #
  # @return �����������֥�������̾��
  #
  # @else
  #
  # @endif
  def onCreate(self, obj):
    num = 0
    while True:
      num_str = OpenRTM_aist.otos(num)
      
      name = obj.getTypeName() + num_str
      if not self.find(name):
        return num_str
      else:
        num += 1
    return OpenRTM_aist.otos(num)

  ##
  # @if jp
  #
  # @brief ���֥������Ⱥ������̾�β���
  #
  # 
  # 
  # @param self
  # @param obj ̾�β����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def onDelete(self, obj):
    pass

  
        
    

  ##
  # @if jp
  #
  # @brief ���֥������Ȥθ���
  #
  # ����̾�Υ��󥹥���̾��RTC�򸡺�����
  # ���פ���RTC��¸�ߤ������True���֤�
  # 
  # @param self
  # @param name RTC�Υ��󥹥���̾
  #
  # @return Ƚ��
  #
  # @else
  #
  # @endif
  def find(self, name):
    rtcs = []
    rtc_name = "rtcname://*/*/"
    rtc_name += name
    rtcs = self._mgr.getNaming().string_to_component(rtc_name)
    
    if len(rtcs) > 0:
      return True
    else:
      return False


def NamingServiceNumberingPolicyInit():
  OpenRTM_aist.NumberingPolicyFactory.instance().addFactory("ns_unique",
                                                      OpenRTM_aist.NamingServiceNumberingPolicy,
                                                      OpenRTM_aist.Delete)
