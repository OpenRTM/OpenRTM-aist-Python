#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file ROS2TopicManager.py
# @brief ROS2 Topic Manager class
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
import ROS2MessageInfo
import rclpy
from rclpy.node import Node
import threading



manager = None
mutex = threading.RLock()

##
# @if jp
# @class ROS2TopicManager
# @brief ROS2トピックを管理するクラス
#
#
# @else
# @class ROS2TopicManager
# @brief 
#
#
# @endif
class ROS2TopicManager(object):
  """
  """

  ##
  # @if jp
  # @brief コンストラクタ
  #
  # コンストラクタ
  #
  # @param self
  #
  # @else
  # @brief Constructor
  #
  # @param self
  #
  # @endif
  def __init__(self):
    self._qosProfile = None
    self._domainParticipant = None
    self._topic = {}
    self._info = {}

    #mgr = OpenRTM_aist.Manager.instance()
    #mgr.addManagerActionListener(ManagerActionListener(self))
    #self._rtcout = mgr.getLogbuf("ROS2TopicManager")


  ##
  # @if jp
  # @brief デストラクタ
  #
  #
  # @param self
  #
  # @else
  #
  # @brief self
  #
  # @endif
  def __del__(self):
    pass


  ##
  # @if jp
  # @brief ROS2初期化
  #
  # @param self
  # @param args rclpy.initの引数
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @param args
  #
  # @endif
  def start(self, args=[]):
    rclpy.init(args=args)
    self._node = Node("openrtm")
    def spin():
        rclpy.spin(self._node)
    threading.Thread(target=spin).start()
    
      

    
  ##
  # @if jp
  # @brief 終了処理
  #
  # @param self
  #
  # @else
  #
  # @brief 
  #
  # @param self
  #
  # @endif
  def shutdown(self):
    if self._node:
      self._node.destroy_node()
      rclpy.shutdown()


  ##
  # @if jp
  # @brief Publisherオブジェクト生成
  #
  # @param self
  # @param msgtype メッセージ型
  # @param topic トピック名
  # @return Publisherオブジェクト
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @param msgtype 
  # @param topic 
  # @return 
  #
  # @endif
  def createPublisher(self, msgtype, topic):
    if self._node:
      return self._node.create_publisher(msgtype, topic)
    return None

  ##
  # @if jp
  # @brief Subscriberオブジェクト生成
  #
  # @param self
  # @param msgtype メッセージ型
  # @param topic トピック名
  # @param listener コールバック関数
  # @return Subscriberオブジェクト
  #
  # @else
  #
  # @brief 
  #
  # @param self
  # @param msgtype 
  # @param topic 
  # @param listener 
  # @return 
  #
  # @endif
  def createSubscriber(self, msgtype, topic, listener):
    if self._node:
      return self._node.create_subscription(msgtype, topic, listener)
    return None


  def deletePublisher(self, sub):
    pass

  def deleteSubscriber(self, sub):
    pass


  ##
  # @if jp
  # @brief インスタンス取得
  #
  # @return インスタンス
  #
  # @else
  #
  # @brief 
  #
  # @return インスタンス
  #
  # @endif
  def instance(args=[]):
    global manager
    global mutex
    
    guard = OpenRTM_aist.ScopedLock(mutex)
    if manager is None:
      manager = ROS2TopicManager()
      manager.start(args)

    return manager
  
  instance = staticmethod(instance)


##
# @if jp
# @class ManagerActionListener
# @brief ROS2TopicManagerに関するマネージャアクションリスナ
#
#
# @else
# @class ManagerActionListener
# @brief 
#
#
# @endif
class ManagerActionListener:
  ##
  # @if jp
  # @brief コンストラクタ
  #
  #
  # @param self
  #
  # @else
  #
  # @brief self
  #
  # @endif
  def __init__(self, topic_manager):
    self._topic_manager = topic_manager

  def preShutdown(self):
    pass
  ##
  # @if jp
  # @brief RTMマネージャ終了後にROS2TopicManagerの終了処理を実行
  #
  #
  # @param self
  #
  # @else
  #
  # @brief self
  #
  # @endif
  def postShutdown(self):
    self._topic_manager.shutdown()

  def preReinit(self):
    pass

  def postReinit(self):
    pass
