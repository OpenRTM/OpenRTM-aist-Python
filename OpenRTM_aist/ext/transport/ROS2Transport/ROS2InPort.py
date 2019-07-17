#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file ROS2InPort.py
# @brief ROS2 OutPort class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist
from ROS2TopicManager import ROS2TopicManager
import ROS2MessageInfo
import RTC
import threading


##
# @if jp
# @class ROS2InPort
# @brief ROS2 Subscriberに対応するクラス
# InPortProviderオブジェクトとして使用する
#
# @else
# @class ROS2InPort
# @brief 
#
#
# @endif
class ROS2InPort(OpenRTM_aist.InPortProvider):
  """
  """

  ##
  # @if jp
  # @brief コンストラクタ
  #
  # コンストラクタ
  # ポートプロパティに以下の項目を設定する。
  #  - インターフェースタイプ : ROS2
  #  - データフロータイプ : Push
  #
  # @param self 
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  # Set the following items to port properties
  #  - Interface type : CORBA_Any
  #  - Data flow type : Push, Pull
  #
  # @param self 
  #
  # @endif
  #
  def __init__(self):
    OpenRTM_aist.InPortProvider.__init__(self)

    # PortProfile setting
    self.setInterfaceType("ros2")


    self._profile = None
    self._listeners = None

    self._topic = "chatter"
    self._messageType = None
    self._subscriber = None

    self._mutex = threading.RLock()




  ##
  # @if jp
  # @brief デストラクタ
  #
  # デストラクタ
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
  # @brief 終了処理
  #
  # @param self 
  #
  # @else
  # @brief 
  #
  # @param self 
  #
  # @endif
  #
  def exit(self):
    self._rtcout.RTC_PARANOID("exit()")
    

  ##
  # @if jp
  # @brief 初期化
  #
  # @param self 
  # @param prop 接続設定
  # marshaling_type シリアライザの種類 デフォルト：ROS2
  # topic トピック名 デフォルト chatter
  #
  # @else
  # @brief 
  #
  # @param self 
  # @param prop
  #
  # @endif
  #
  ## virtual void init(coil::Properties& prop);
  def init(self, prop):
    self._rtcout.RTC_PARANOID("init()")

    if len(prop.propertyNames()) == 0:
      self._rtcout.RTC_DEBUG("Property is empty.")
      return
    
    self._properties = prop

    args = []
    self._topicmgr = ROS2TopicManager.instance(args)

    self._messageType = prop.getProperty("marshaling_type", "ROS2Float32")
    self._topic = prop.getProperty("ros2.topic", "chatter")

    self._rtcout.RTC_VERBOSE("message type: %s", self._messageType)
    self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)

    factory = ROS2MessageInfo.ROS2MessageInfoFactory.instance()
    info = factory.createObject(self._messageType)

    info_type = info.datatype()

    factory.deleteObject(info)


    self._subscriber = self._topicmgr.createSubscriber(info_type, self._topic, self.ros2_callback)



  ## virtual void setBuffer(BufferBase<cdrMemoryStream>* buffer);
  def setBuffer(self, buffer):
    return

  ##
  # @if jp
  # @brief コネクタリスナの設定
  #
  # @param info 接続情報
  # @param listeners リスナ
  #
  # @else
  # @brief 
  #
  # @param info 
  # @param listeners 
  #
  # @endif
  #
  # void setListener(ConnectorInfo& info,
  #                  ConnectorListeners* listeners);
  def setListener(self, info, listeners):
    self._profile = info
    self._listeners = listeners
    return


  ##
  # @if jp
  # @brief Subscriberメッセージ受信時のコールバック関数
  #
  # @param self 
  # @param msg 受信メッセージ
  #
  # @else
  # @brief 
  #
  # @param self 
  # @param msg 
  #
  # @endif
  #
  def ros2_callback(self, msg):
    self.put(msg)


  ##
  # @if jp
  # @brief バッファにデータを書き込む
  #
  # 設定されたバッファにデータを書き込む。
  #
  # @param data 書込対象データ
  #
  # @else
  # @brief Write data into the buffer
  #
  # Write data into the specified buffer.
  #
  # @param data The target data for writing
  #
  # @endif
  #
  def put(self, data):
    guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
    try:
      self._rtcout.RTC_PARANOID("ROS2InPort.put()")
      if not self._connector:
        self.onReceiverError(data)
        return OpenRTM.PORT_ERROR

      self.onReceived(data)

      ret = self._connector.write(data)

      self.convertReturn(ret, data)

    except:
      self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
      



  def convertReturn(self, status, data):
    if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
      self.onBufferWrite(data)
      return
            
    elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
      self.onReceiverError(data)
      return

    elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
      self.onBufferFull(data)
      self.onReceiverFull(data)
      return

    elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
      return

    elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
      self.onReceiverError(data)
      return

    elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
      self.onBufferWriteTimeout(data)
      self.onReceiverTimeout(data)
      return

    else:
      self.onReceiverError(data)
      return
        

  ##
  # @brief Connector data listener functions
  #
  # inline void onBufferWrite(const cdrMemoryStream& data)
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


##
# @if jp
# @brief モジュール登録関数
#
#
# @else
# @brief 
#
#
# @endif
#
def ROS2InPortInit():
  factory = OpenRTM_aist.InPortProviderFactory.instance()
  factory.addFactory("ros2",
                     ROS2InPort,
                     OpenRTM_aist.Delete)
