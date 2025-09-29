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
import rclpy.qos
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

    def start(self, prop):

        tmp_args = prop.getProperty("args").split("\"")
        args = []
        for i, tmp_arg in enumerate(tmp_args):
            if i % 2 == 0:
                args.extend(tmp_arg.strip().split(" "))
            else:
                args.append(tmp_arg)

        args.insert(0, "manager")

        rclpy.init(args=args)

        self._node = Node(prop.getProperty("node.name", "openrtm"))

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
    # @brief 初期化
    #
    #
    # @else
    #
    # @brief
    #
    #
    # @endif

    def init(prop):
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is None:
            manager = ROS2TopicManager()
            manager.start(prop)

    init = staticmethod(init)

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

    def instance():
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is None:
            manager = ROS2TopicManager()
            manager.start()

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

        durability_kind = DurabilityPolicy.SYSTEM_DEFAULT
        durability_kind_str = prop.getProperty(
            "durability.kind")
        if durability_kind_str == "VOLATILE_DURABILITY_QOS":
            durability_kind = DurabilityPolicy.VOLATILE
        elif durability_kind_str == "TRANSIENT_LOCAL_DURABILITY_QOS":
            durability_kind = DurabilityPolicy.TRANSIENT_LOCAL
        elif durability_kind_str == "SYSTEM_DEFAULT_QOS":
            durability_kind = DurabilityPolicy.SYSTEM_DEFAULT

        deadline_period = ROS2TopicManager.getDuration(
            prop.getNode("deadline.period"), Duration)

        if deadline_period is None:
            deadline_period = Duration(
                seconds=0, nanoseconds=0)

        liveliness_kind = LivelinessPolicy.SYSTEM_DEFAULT
        liveliness_kind_str = prop.getProperty(
            "liveliness.kind")
        if liveliness_kind_str == "AUTOMATIC_LIVELINESS_QOS":
            liveliness_kind = LivelinessPolicy.AUTOMATIC
        elif liveliness_kind_str == "MANUAL_BY_TOPIC_LIVELINESS_QOS":
            liveliness_kind = LivelinessPolicy.MANUAL_BY_TOPIC
        elif liveliness_kind_str == "SYSTEM_DEFAULT_LIVELINESS_QOS":
            liveliness_kind = LivelinessPolicy.SYSTEM_DEFAULT

        liveliness_lease_duration_time = ROS2TopicManager.getDuration(
            prop.getNode("liveliness.lease_duration"), Duration)

        if liveliness_lease_duration_time is None:
            liveliness_lease_duration_time = Duration(
                seconds=0, nanoseconds=0)

        reliability_kind = ReliabilityPolicy.SYSTEM_DEFAULT
        reliability_kind_str = prop.getProperty(
            "reliability.kind")
        if reliability_kind_str == "BEST_EFFORT_RELIABILITY_QOS":
            reliability_kind = ReliabilityPolicy.BEST_EFFORT
        elif reliability_kind_str == "RELIABLE_RELIABILITY_QOS":
            reliability_kind = ReliabilityPolicy.RELIABLE
        elif reliability_kind_str == "SYSTEM_DEFAULT_RELIABILITY_QOS":
            reliability_kind = ReliabilityPolicy.SYSTEM_DEFAULT

        history_qos_policy_kind = HistoryPolicy.SYSTEM_DEFAULT
        history_qos_policy_kind_str = prop.getProperty(
            "history.kind")
        if history_qos_policy_kind_str == "KEEP_ALL_HISTORY_QOS":
            history_qos_policy_kind = HistoryPolicy.KEEP_ALL
        elif history_qos_policy_kind_str == "KEEP_LAST_HISTORY_QOS":
            history_qos_policy_kind = HistoryPolicy.KEEP_LAST
        elif history_qos_policy_kind_str == "SYSTEM_DEFAULT_HISTORY_QOS":
            history_qos_policy_kind = HistoryPolicy.SYSTEM_DEFAULT

        history_depth = 1
        try:
            history_depth = int(prop.getProperty(
                "history.depth"))
        except ValueError as error:
            pass
            # self._rtcout.RTC_ERROR(error)

        lifespan_duration = ROS2TopicManager.getDuration(
            prop.getNode("lifespan.duration"), Duration)

        if lifespan_duration is None:
            lifespan_duration = Duration(
                seconds=10000, nanoseconds=2147483647)

        avoid_ros_namespace_conventions = OpenRTM_aist.toBool(prop.getProperty(
            "avoid_ros_namespace_conventions"), "YES", "NO", False)

        qos = QoSProfile(history=history_qos_policy_kind, depth=history_depth,
                         reliability=reliability_kind,
                         durability=durability_kind,
                         lifespan=lifespan_duration,
                         deadline=deadline_period,
                         liveliness=liveliness_kind,
                         liveliness_lease_duration=liveliness_lease_duration_time,
                         avoid_ros_namespace_conventions=avoid_ros_namespace_conventions)

        return qos

    get_qosprofile = staticmethod(get_qosprofile)

    ##
    # @if jp
    # @brief プロパティからDDS::Durationを設定して取得する
    #
    # @param self
    # @param prop プロパティ(sec、nanosecの要素に値を格納する)
    # @return DDS::Duration
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param prop
    # @return
    #
    # @endif
    def getDuration(prop, DDSDuration):
        sec_str = prop.getProperty("sec")
        nanosec_str = prop.getProperty("nanosec")
        try:
            sec = int(sec_str)
            nanosec = int(nanosec_str)
            return DDSDuration(seconds=sec, nanoseconds=nanosec)
        except ValueError as error:
            return None
            # self._rtcout.RTC_ERROR(error)
        return None

    getDuration = staticmethod(getDuration)
