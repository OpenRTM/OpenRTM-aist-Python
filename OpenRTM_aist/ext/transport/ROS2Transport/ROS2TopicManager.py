#!/usr/bin/env python3
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
from rclpy.qos import QoSProfile

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
        self._thread = None
        self._loop = True

        #mgr = OpenRTM_aist.Manager.instance()
        # mgr.addManagerActionListener(ManagerActionListener(self))
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
            while self._loop:
                rclpy.spin_once(self._node, timeout_sec=0.01)
        self._thread = threading.Thread(target=spin)
        self._thread.daemon = True
        self._thread.start()

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
            self._loop = False
            self._node.destroy_node()
            # rclpy.try_shutdown()
            # if self._thread:
            #  self._thread.join()

    ##
    # @if jp
    # @brief Publisherオブジェクト生成
    #
    # @param self
    # @param msgtype メッセージ型
    # @param topic トピック名
    # @param qos QoSProfile
    # @return Publisherオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param msgtype
    # @param topic
    # @param qos 
    # @return
    #
    # @endif

    def createPublisher(self, msgtype, topic, qos=None):
        global mutex
        if qos is None:
            qos = QoSProfile(depth=10)
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._node:
            return self._node.create_publisher(msgtype, topic, qos)
        return None

    ##
    # @if jp
    # @brief Subscriberオブジェクト生成
    #
    # @param self
    # @param msgtype メッセージ型
    # @param topic トピック名
    # @param listener コールバック関数
    # @param qos QoSProfile
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
    # @param qos 
    # @return
    #
    # @endif
    def createSubscriber(self, msgtype, topic, listener, qos=None):
        global mutex
        if qos is None:
            qos = QoSProfile(depth=10)
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._node:
            return self._node.create_subscription(msgtype, topic, listener, qos)
        return None

    def deletePublisher(self, pub):
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
    # @brief ROS2TopicManagerを初期化している場合に終了処理を呼び出す
    #
    #
    # @else
    #
    # @brief
    #
    #
    # @endif

    def shutdown_global():
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is not None:
            manager.shutdown()

        manager = None

    shutdown_global = staticmethod(shutdown_global)


    ##
    # @if jp
    # @brief プロパティからQoSProfileを設定する
    # @param prop プロパティ
    # @return QoSProfile
    #
    # @else
    #
    # @brief
    # @param prop
    # @return QoSProfile
    #
    # @endif
    def get_qosprofile(prop):

        if hasattr(rclpy.qos, "HistoryPolicy"):
            HistoryPolicy = rclpy.qos.HistoryPolicy
        else:
            HistoryPolicy = rclpy.qos.QoSHistoryPolicy

        if hasattr(rclpy.qos, "Duration"):
            Duration = rclpy.qos.Duration
        else:
            Duration = rclpy.qos.QoSDuration

        if hasattr(rclpy.qos, "ReliabilityPolicy"):
            ReliabilityPolicy = rclpy.qos.ReliabilityPolicy
        else:
            ReliabilityPolicy = rclpy.qos.QoSReliabilityPolicy

        if hasattr(rclpy.qos, "DurabilityPolicy"):
            DurabilityPolicy = rclpy.qos.DurabilityPolicy
        else:
            DurabilityPolicy = rclpy.qos.QoSDurabilityPolicy

        if hasattr(rclpy.qos, "LivelinessPolicy"):
            LivelinessPolicy = rclpy.qos.LivelinessPolicy
        else:
            LivelinessPolicy = rclpy.qos.QoSLivelinessPolicy

        history = HistoryPolicy.KEEP_LAST
        history_type = prop.getProperty("history", "KEEP_LAST")
        
        if history_type == "SYSTEM_DEFAULT":
            history = HistoryPolicy.SYSTEM_DEFAULT
        elif history_type == "KEEP_ALL":
            history = HistoryPolicy.KEEP_ALL
        else:
            history = HistoryPolicy.KEEP_LAST

        
        depth = 10
        depth_value_str = prop.getProperty("depth", "10")
        try:
            depth = int(depth_value_str)
        except ValueError:
            pass

        reliability = ReliabilityPolicy.RELIABLE
        reliability_type = prop.getProperty("reliability", "RELIABLE")
        if reliability_type == "SYSTEM_DEFAULT":
            reliability = ReliabilityPolicy.SYSTEM_DEFAULT
        elif reliability_type == "BEST_EFFORT":
            reliability = ReliabilityPolicy.BEST_EFFORT
        else:
            reliability = ReliabilityPolicy.RELIABLE

        durability = DurabilityPolicy.VOLATILE
        durability_type = prop.getProperty("durability", "VOLATILE")
        if durability_type == "SYSTEM_DEFAULT":
            durability = DurabilityPolicy.SYSTEM_DEFAULT
        elif durability_type == "TRANSIENT_LOCAL":
            durability = DurabilityPolicy.TRANSIENT_LOCAL
        else:
            durability = DurabilityPolicy.VOLATILE
        
        lifespan = Duration(seconds=0, nanoseconds=0)
        lifespan_value_str = prop.getProperty("lifespan", "0")
        try:
            lifespan_value = int(lifespan_value_str)
            lifespan = Duration(nanoseconds=lifespan_value)
        except ValueError:
            pass

        deadline = Duration(seconds=0, nanoseconds=0)
        deadline_value_str = prop.getProperty("deadline", "0")
        try:
            deadline_value = int(deadline_value_str)
            deadline = Duration(nanoseconds=deadline_value)
        except ValueError:
            pass

        liveliness = LivelinessPolicy.SYSTEM_DEFAULT
        liveliness_type = prop.getProperty("liveliness", "SYSTEM_DEFAULT")
        if liveliness_type == "AUTOMATIC":
            liveliness = LivelinessPolicy.AUTOMATIC
        elif liveliness_type == "MANUAL_BY_NODE":
            liveliness = LivelinessPolicy.MANUAL_BY_NODE
        elif liveliness_type == "MANUAL_BY_TOPIC":
            liveliness = LivelinessPolicy.MANUAL_BY_TOPIC
        else:
            liveliness = LivelinessPolicy.SYSTEM_DEFAULT

        liveliness_lease_duration = Duration(seconds=0, nanoseconds=0)
        liveliness_lease_duration_value_str = prop.getProperty("liveliness_lease_duration", "0")
        try:
            liveliness_lease_duration_value = int(liveliness_lease_duration_value_str)
            liveliness_lease_duration = Duration(nanoseconds=liveliness_lease_duration_value)
        except ValueError:
            pass

        avoid_ros_namespace_conventions = False
        if OpenRTM_aist.toBool(prop.getProperty(
            "avoid_ros_namespace_conventions"), "YES", "NO", False):
            avoid_ros_namespace_conventions = True
        else:
            avoid_ros_namespace_conventions = False
            

        qos = QoSProfile(history=history, depth=depth, reliability=reliability, durability=durability, 
                        lifespan=lifespan, deadline=deadline, liveliness=liveliness,
                        liveliness_lease_duration=liveliness_lease_duration, 
                        avoid_ros_namespace_conventions=avoid_ros_namespace_conventions)

        return qos

    get_qosprofile = staticmethod(get_qosprofile)
