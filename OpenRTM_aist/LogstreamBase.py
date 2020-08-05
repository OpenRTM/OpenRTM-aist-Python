#!/usr/bin/env python3
# -*- coding: euc-jp -*-


##
# @file LogstreamBase.py
# @brief Logger stream buffer base class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
# Copyright (C) 2017
#   Nobuhiko Miyamoto
#   National Institute of
#      Advanced Industrial Science and Technology (AIST), Japan
#   All rights reserved.
# $Id$



import OpenRTM_aist


##
# @if jp
# @class LogstreamBase
#
# @brief LogstreamBase ���饹
#
# 
#
#
# @else
# @class LogstreamBase
#
# @brief LogstreamBase class
#
#
# @endif
#
class LogstreamBase:
  """
  """

  ##
  # @if jp
  # @brief ���󥹥ȥ饯��
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
    pass

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
    pass
    


  ##
  # @if jp
  # @brief ��������
  #
  # Logstream���饹�γƼ������Ԥ����������饹�Ǥϡ�Ϳ����줿
  # Properties����ɬ�פʾ����������ƳƼ������Ԥ���
  #
  # @param self
  # @param prop �������
  # @return
  #
  # @else
  # @brief Initializing configuration
  #
  # This operation would be called to configure in initialization.
  # In the concrete class, configuration should be performed
  # getting appropriate information from the given Properties data.
  #
  # @param self
  # @param prop Configuration information
  # @return
  #
  # @endif
  #
  def init(self, prop):
    return False


  ##
  # @if jp
  # @brief ����ʸ���������Ϥ���
  #
  #
  # @param self
  # @param msg�������Ϥ���ʸ����
  # @param level ����٥�
  # @return
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @param msg
  # @param level
  # @return
  #
  # @endif
  #
  def log(self, msg, level, name):
    return False



  ##
  # @if jp
  # @brief ����٥�����
  #
  #
  # @param self
  # @param level ����٥�
  # @return
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @param level
  # @return
  #
  # @endif
  #
  def setLogLevel(self, level):
    pass


  ##
  # @if jp
  # @brief ��λ����
  #
  #
  # @param self
  # @return
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @return
  #
  # @endif
  #
  def shutdown(self):
    return True




logstreamfactory = None

class LogstreamFactory(OpenRTM_aist.Factory):
  def __init__(self):
    OpenRTM_aist.Factory.__init__(self)
  def instance():
    global logstreamfactory
    if logstreamfactory is None:
      logstreamfactory = LogstreamFactory()
    return logstreamfactory
  instance = staticmethod(instance)
