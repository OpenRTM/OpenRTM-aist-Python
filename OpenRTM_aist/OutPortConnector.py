#!/usr/bin/env python3
# -*- coding: euc-jp -*-


##
#
# @file OutPortConnector.py
# @brief OutPort Connector class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2009
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import OpenRTM_aist
import RTC

##
# @if jp
# @class OutPortConnector
# @brief OutPortConnector 基底クラス
#
# OutPort の Push/Pull 各種 Connector を派生させるための
# 基底クラス。
#
# @since 1.0.0
#
# @else
# @class OutPortConnector
# @brief IｎPortConnector base class
#
# The base class to derive subclasses for OutPort's Push/Pull Connectors
#
# @since 1.0.0
#
# @endif
#
class OutPortConnector(OpenRTM_aist.ConnectorBase):
  """
  """

  ##
  # @if jp
  # @brief コンストラクタ
  # @else
  # @brief Constructor
  # @endif
  #
  # OutPortConnector(ConnectorInfo& info);
  def __init__(self, info):
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OutPortConnector")
    self._profile = info
    self._endian = True
    self._directMode = False
    return

  ##
  # @if jp
  # @brief デストラクタ
  # @else
  # @brief Destructor
  # @endif
  #
  def __del__(self):
    pass


  ##
  # @if jp
  # @brief ConnectorInfo 取得
  #
  # ConnectorInfo を取得する
  #
  # @else
  # @brief Getting ConnectorInfo
  #
  # This operation returns ConnectorInfo
  #
  # @endif
  #
  # const ConnectorInfo& profile();
  def profile(self):
    self._rtcout.RTC_TRACE("profile()")
    return self._profile

  ##
  # @if jp
  # @brief Connector ID 取得
  #
  # Connector ID を取得する
  #
  # @else
  # @brief Getting Connector ID
  #
  # This operation returns Connector ID
  #
  # @endif
  #
  # const char* id();
  def id(self):
    self._rtcout.RTC_TRACE("id() = %s", self.profile().id)
    return self.profile().id


  ##
  # @if jp
  # @brief Connector 名取得
  #
  # Connector 名を取得する
  #
  # @else
  # @brief Getting Connector name
  #
  # This operation returns Connector name
  #
  # @endif
  #
  # const char* name();
  def name(self):
    self._rtcout.RTC_TRACE("name() = %s", self.profile().name)
    return self.profile().name


  # ReturnCode_t setConnectorInfo(ConnectorInfo info);
  def setConnectorInfo(self, info):
    self._profile = info

    if self._profile.properties.hasKey("serializer"):
      endian = self._profile.properties.getProperty("serializer.cdr.endian")
      if not endian:
        self._rtcout.RTC_ERROR("InPortConnector.setConnectorInfo(): endian is not supported.")
        return RTC.RTC_ERROR
        
      endian = OpenRTM_aist.split(endian, ",") # Maybe endian is ["little","big"]
      endian = OpenRTM_aist.normalize(endian) # Maybe self._endian is "little" or "big"

      if endian == "little":
        self._endian = True
      elif endian == "big":
        self._endian = False
      else:
        return RTC.RTC_ERROR
            
    else:
      self._endian = True # little endian

    return RTC.RTC_OK

  ##
  # @if jp
  # @brief ダイレクト接続モードに設定
  #
  #
  # @else
  # @brief 
  #
  # This 
  #
  # @endif
  #
  # const char* name();
  def setDirectMode(self):
    self._directMode = True

  ##
  # @if jp
  # @brief ダイレクト接続モードかの判定
  #
  # @return True：ダイレクト接続モード,false：それ以外
  #
  # @else
  # @brief 
  #
  # @return
  #
  # @endif
  #
  # const char* name();
  def directMode(self):
    return self._directMode
