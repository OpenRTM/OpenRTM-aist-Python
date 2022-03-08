#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    ddstype = "fast-rtps"

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
        self.setInterfaceType(self.ddstype)

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
    # virtual void init(coil::Properties& prop);

    def init(self, prop):
        self._rtcout.RTC_PARANOID("init()")

        if not prop.propertyNames():
            self._rtcout.RTC_DEBUG("Property is empty.")
            return

        self._properties = prop

        self._topicmgr = ROS2TopicManager.instance()

        self._messageType = prop.getProperty(
            "marshaling_type", "ros2:std_msgs/Float32")
        self._topic = prop.getProperty(self.ddstype+".topic", "chatter")

        self._rtcout.RTC_VERBOSE("message type: %s", self._messageType)
        self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)

        factory = ROS2MessageInfo.ROS2MessageInfoList.instance()
        info = factory.getInfo(self._messageType)

        info_type = info.datatype()

        ddsprop = prop.getNode(self.ddstype)

        qos = ROS2TopicManager.get_qosprofile(ddsprop.getNode("reader_qos"))

        self._rtcout.RTC_VERBOSE("history policy: %s", qos.history)
        self._rtcout.RTC_VERBOSE("depth: %d", qos.depth)
        self._rtcout.RTC_VERBOSE("reliability policy: %s", qos.reliability)
        self._rtcout.RTC_VERBOSE("durability policy: %s", qos.durability)
        self._rtcout.RTC_VERBOSE(
            "lifespan: %d [nsec]", qos.lifespan.nanoseconds)
        self._rtcout.RTC_VERBOSE(
            "deadline: %d [nsec]", qos.deadline.nanoseconds)
        self._rtcout.RTC_VERBOSE("liveliness policy: %s", qos.liveliness)
        self._rtcout.RTC_VERBOSE(
            "liveliness lease duration: %d [nsec]", qos.liveliness_lease_duration.nanoseconds)
        self._rtcout.RTC_VERBOSE(
            "avoid ros namespace conventions: %s", qos.avoid_ros_namespace_conventions)

        self._subscriber = self._topicmgr.createSubscriber(
            info_type, self._topic, self.ros2_callback, qos)

    # virtual void setBuffer(BufferBase<cdrMemoryStream>* buffer);

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

            data = self.onReceived(data)

            ret = self._connector.write(data)

            self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())

    def convertReturn(self, status, data):
        if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
            self.onBufferWrite(data)
            return

        elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
            self.onReceiverError(data)
            return

        elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
            data = self.onBufferFull(data)
            self.onReceiverFull(data)
            return

        elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
            return

        elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
            self.onReceiverError(data)
            return

        elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
            data = self.onBufferWriteTimeout(data)
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
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
        return data

    # inline void onBufferFull(const cdrMemoryStream& data)

    def onBufferFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL, self._profile, data)
        return data

    # inline void onBufferWriteTimeout(const cdrMemoryStream& data)

    def onBufferWriteTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT, self._profile, data)
        return data

    # inline void onBufferWriteOverwrite(const cdrMemoryStream& data)
    def onBufferWriteOverwrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
        return data

    # inline void onReceived(const cdrMemoryStream& data)

    def onReceived(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
        return data

    # inline void onReceiverFull(const cdrMemoryStream& data)

    def onReceiverFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
        return data

    # inline void onReceiverTimeout(const cdrMemoryStream& data)

    def onReceiverTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT, self._profile, data)
        return data

    # inline void onReceiverError(const cdrMemoryStream& data)

    def onReceiverError(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR, self._profile, data)
        return data


ros2_sub_option = [
    "topic.__value__", "chatter",
    "topic.__widget__", "text",
    "topic.__constraint__", "none",
    "reader_qos.durability.kind.__value__", "TRANSIENT_DURABILITY_QOS",
    "reader_qos.durability.kind.__widget__", "radio",
    "reader_qos.durability.kind.__constraint__", "(VOLATILE_DURABILITY_QOS, TRANSIENT_LOCAL_DURABILITY_QOS, SYSTEM_DEFAULT_QOS)",
    "reader_qos.deadline.period.sec.__value__", "0",
    "reader_qos.deadline.period.sec.__widget__", "spin",
    "reader_qos.deadline.period.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.deadline.period.nanosec.__value__", "0",
    "reader_qos.deadline.period.nanosec.__widget__", "text",
    "reader_qos.deadline.period.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.liveliness.kind.__value__", "AUTOMATIC_LIVELINESS_QOS",
    "reader_qos.liveliness.kind.__widget__", "radio",
    "reader_qos.liveliness.kind.__constraint__", "(AUTOMATIC_LIVELINESS_QOS, MANUAL_BY_TOPIC_LIVELINESS_QOS, SYSTEM_DEFAULT_LIVELINESS_QOS)",
    "reader_qos.liveliness.lease_duration.sec.__value__", "0",
    "reader_qos.liveliness.lease_duration.sec.__widget__", "spin",
    "reader_qos.liveliness.lease_duration.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.liveliness.lease_duration.nanosec.__value__", "0",
    "reader_qos.liveliness.lease_duration.nanosec.__widget__", "spin",
    "reader_qos.liveliness.lease_duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reliability.kind.__value__", "RELIABLE_RELIABILITY_QOS",
    "reader_qos.reliability.kind.__widget__", "radio",
    "reader_qos.reliability.kind.__constraint__", "(BEST_EFFORT_RELIABILITY_QOS, RELIABLE_RELIABILITY_QOS, SYSTEM_DEFAULT_RELIABILITY_QOS)",
    "reader_qos.history.kind.__value__", "KEEP_LAST_HISTORY_QOS",
    "reader_qos.history.kind.__widget__", "radio",
    "reader_qos.history.kind.__constraint__", "(KEEP_LAST_HISTORY_QOS, KEEP_ALL_HISTORY_QOS, SYSTEM_DEFAULT_HISTORY_QOS)",
    "reader_qos.history.depth.__value__", "1",
    "reader_qos.history.depth.__widget__", "spin",
    "reader_qos.history.depth.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.lifespan.duration.sec.__value__", "0",
    "reader_qos.lifespan.duration.sec.__widget__", "spin",
    "reader_qos.lifespan.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.lifespan.duration.nanosec.__value__", "0",
    "reader_qos.lifespan.duration.nanosec.__widget__", "spin",
    "reader_qos.lifespan.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.avoid_ros_namespace_conventions.__value__", "YES",
    "reader_qos.avoid_ros_namespace_conventions.__widget__", "radio",
    "reader_qos.avoid_ros_namespace_conventions.__constraint__", "(YES, NO)",
    ""]

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


def ROS2InPortInit(ddstype="fast-rtps"):
    prop = OpenRTM_aist.Properties(defaults_str=ros2_sub_option)
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory(ddstype,
                       ROS2InPort,
                       prop)
    ROS2InPort.ddstype = ddstype
