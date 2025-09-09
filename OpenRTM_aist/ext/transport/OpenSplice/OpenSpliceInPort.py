#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OpenSpliceInPort.py
# @brief OpenSplice OutPort class
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
from OpenSpliceTopicManager import OpenSpliceTopicManager
import OpenSpliceMessageInfo
import RTC
import dds
import threading


##
# @if jp
# @class OpenSpliceInPort
# @brief OpenSplice Subscriberに対応するクラス
# InPortProviderオブジェクトとして使用する
#
# @else
# @class OpenSpliceInPort
# @brief
#
#
# @endif
class OpenSpliceInPort(OpenRTM_aist.InPortProvider):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # ポートプロパティに以下の項目を設定する。
    #  - インターフェースタイプ : opensplice
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
        self.setInterfaceType("opensplice")

        self._profile = None
        self._listeners = None

        self._dataType = RTC.TimedLong._NP_RepositoryId
        self._topic = "chatter"
        self._reader = None

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
        if self._reader:
            self._reader.close()
            self._rtcout.RTC_VERBOSE("remove reader")

    ##
    # @if jp
    # @brief 初期化
    #
    # @param self
    # @param prop 接続設定
    # marshaling_type シリアライザの種類 デフォルト：opensplice
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

        self._topicmgr = OpenSpliceTopicManager.instance()

        self._dataType = prop.getProperty("dataport.data_type", self._dataType)

        self._topic = prop.getProperty("opensplice.topic", "chatter")

        topic = self._topicmgr.createTopic(self._dataType, self._topic, prop)

        self._rtcout.RTC_VERBOSE("data type: %s", self._dataType)
        self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)

        self._reader = self._topicmgr.createReader(
            topic, SubListener(self), prop.getNode("opensplice"))

        if self._reader is None:
            raise MemoryError("Reader creation failed")

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
            self._rtcout.RTC_PARANOID("OpenSpliceInPort.put()")
            if not self._connector:
                self.onReceiverError(data)
                return

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

##
# @if jp
# @class SubListener
# @brief OpenSplice Subscriberのデータ受信時のリスナ
#
#
# @else
# @class SubListener
# @brief
#
#
# @endif


class SubListener(dds.Listener):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # @param self
    # @param sub OpenSpliceInPort
    #
    # @else
    # @brief Constructor
    #
    # @param self
    # @param sub
    #
    # @endif
    #
    def __init__(self, subscriber):
        dds.Listener.__init__(self)
        self._sub = subscriber

    ##
    # @if jp
    # @brief 受信処理
    #
    # @param self
    # @param entity
    #
    # @else
    # @brief
    #
    # @param self
    # @param entity
    #
    # @endif
    #
    def on_data_available(self, entity):
        l = entity.read(10)
        for (sd, _) in l:
            self._sub.put(sd)


opensplice_sub_option = [
    "topic.__value__", "chatter",
    "topic.__widget__", "text",
    "topic.__constraint__", "none",
    "reader_qos.durability.kind.__value__", "TRANSIENT_DURABILITY_QOS",
    "reader_qos.durability.kind.__widget__", "radio",
    "reader_qos.durability.kind.__constraint__", "(VOLATILE_DURABILITY_QOS, TRANSIENT_LOCAL_DURABILITY_QOS, TRANSIENT_DURABILITY_QOS, PERSISTENT_DURABILITY_QOS)",
    "reader_qos.deadline.period.sec.__value__", "2147483647",
    "reader_qos.deadline.period.sec.__widget__", "spin",
    "reader_qos.deadline.period.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.deadline.period.nanosec.__value__", "2147483647",
    "reader_qos.deadline.period.nanosec.__widget__", "text",
    "reader_qos.deadline.period.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.latency_budget.duration.sec.__value__", "0",
    "reader_qos.latency_budget.duration.sec.__widget__", "spin",
    "reader_qos.latency_budget.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.latency_budget.duration.nanosec.__value__", "0",
    "reader_qos.latency_budget.duration.nanosec.__widget__", "spin",
    "reader_qos.latency_budget.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.liveliness.kind.__value__", "AUTOMATIC_LIVELINESS_QOS",
    "reader_qos.liveliness.kind.__widget__", "radio",
    "reader_qos.liveliness.kind.__constraint__", "(AUTOMATIC_LIVELINESS_QOS, MANUAL_BY_PARTICIPANT_LIVELINESS_QOS, MANUAL_BY_TOPIC_LIVELINESS_QOS)",
    "reader_qos.liveliness.lease_duration.sec.__value__", "2147483647",
    "reader_qos.liveliness.lease_duration.sec.__widget__", "spin",
    "reader_qos.liveliness.lease_duration.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.liveliness.lease_duration.nanosec.__value__", "2147483647",
    "reader_qos.liveliness.lease_duration.nanosec.__widget__", "spin",
    "reader_qos.liveliness.lease_duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reliability.kind.__value__", "BEST_EFFORT_RELIABILITY_QOS",
    "reader_qos.reliability.kind.__widget__", "radio",
    "reader_qos.reliability.kind.__constraint__", "(BEST_EFFORT_RELIABILITY_QOS, RELIABLE_RELIABILITY_QOS)",
    "reader_qos.reliability.max_blocking_time.sec.__value__", "2147483647",
    "reader_qos.reliability.max_blocking_time.sec.__widget__", "spin",
    "reader_qos.reliability.max_blocking_time.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reliability.max_blocking_time.nanosec.__value__", "2147483647",
    "reader_qos.reliability.max_blocking_time.nanosec.__widget__", "spin",
    "reader_qos.reliability.max_blocking_time.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.destination_order.kind.__value__", "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS",
    "reader_qos.destination_order.kind.__widget__", "radio",
    "reader_qos.destination_order.kind.__constraint__", "(BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS, BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS)",
    "reader_qos.history.kind.__value__", "KEEP_LAST_HISTORY_QOS",
    "reader_qos.history.kind.__widget__", "radio",
    "reader_qos.history.kind.__constraint__", "(KEEP_LAST_HISTORY_QOS, KEEP_ALL_HISTORY_QOS)",
    "reader_qos.history.depth.__value__", "1",
    "reader_qos.history.depth.__widget__", "spin",
    "reader_qos.history.depth.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.resource_limits.max_samples.__value__", "-1",
    "reader_qos.resource_limits.max_samples.__widget__", "spin",
    "reader_qos.resource_limits.max_samples.__constraint__", "-1 <= x <= 2147483647",
    "reader_qos.resource_limits.max_instances.__value__", "-1",
    "reader_qos.resource_limits.max_instances.__widget__", "spin",
    "reader_qos.resource_limits.max_instances.__constraint__", "-1 <= x <= 2147483647",
    "reader_qos.resource_limits.max_samples_per_instance.__value__", "-1",
    "reader_qos.resource_limits.max_samples_per_instance.__widget__", "spin",
    "reader_qos.resource_limits.max_samples_per_instance.__constraint__", "-1 <= x <= 2147483647",
    "reader_qos.ownership.kind.__value__", "SHARED_OWNERSHIP_QOS",
    "reader_qos.ownership.kind.__widget__", "radio",
    "reader_qos.ownership.kind.__constraint__", "(SHARED_OWNERSHIP_QOS, EXCLUSIVE_OWNERSHIP_QOS)",
    "reader_qos.time_based_filter.minimum_separation.sec.__value__", "0",
    "reader_qos.time_based_filter.minimum_separation.sec.__widget__", "spin",
    "reader_qos.time_based_filter.minimum_separation.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.time_based_filter.minimum_separation.nanosec.__value__", "0",
    "reader_qos.time_based_filter.minimum_separation.nanosec.__widget__", "spin",
    "reader_qos.time_based_filter.minimum_separation.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.sec.__value__", "2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.sec.__widget__", "spin",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.nanosec.__value__", "2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.nanosec.__widget__", "spin",
    "reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay.nanosec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.sec.__value__", "2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.sec.__widget__", "spin",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.sec.__constraint__", "0 <= x <= 2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.nanosec.__value__", "2147483647",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.nanosec.__widget__", "spin",
    "reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.durability.kind.__value__", "TRANSIENT_DURABILITY_QOS",
    "topic_qos.durability.kind.__widget__", "radio",
    "topic_qos.durability.kind.__constraint__", "(VOLATILE_DURABILITY_QOS, TRANSIENT_LOCAL_DURABILITY_QOS, TRANSIENT_DURABILITY_QOS, PERSISTENT_DURABILITY_QOS)",
    "topic_qos.deadline.period.sec.__value__", "2147483647",
    "topic_qos.deadline.period.sec.__widget__", "spin",
    "topic_qos.deadline.period.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.deadline.period.nanosec.__value__", "2147483647",
    "topic_qos.deadline.period.nanosec.__widget__", "spin",
    "topic_qos.deadline.period.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.latency_budget.duration.sec.__value__", "0",
    "topic_qos.latency_budget.duration.sec.__widget__", "spin",
    "topic_qos.latency_budget.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.latency_budget.duration.nanosec.__value__", "0",
    "topic_qos.latency_budget.duration.nanosec.__widget__", "spin",
    "topic_qos.latency_budget.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.liveliness.kind.__value__", "AUTOMATIC_LIVELINESS_QOS",
    "topic_qos.liveliness.kind.__widget__", "radio",
    "topic_qos.liveliness.kind.__constraint__", "(AUTOMATIC_LIVELINESS_QOS, MANUAL_BY_PARTICIPANT_LIVELINESS_QOS, MANUAL_BY_TOPIC_LIVELINESS_QOS)",
    "topic_qos.liveliness.lease_duration.sec.__value__", "2147483647",
    "topic_qos.liveliness.lease_duration.sec.__widget__", "spin",
    "topic_qos.liveliness.lease_duration.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.liveliness.lease_duration.nanosec.__value__", "2147483647",
    "topic_qos.liveliness.lease_duration.nanosec.__widget__", "spin",
    "topic_qos.liveliness.lease_duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.reliability.kind.__value__", "RELIABLE_RELIABILITY_QOS",
    "topic_qos.reliability.kind.__widget__", "radio",
    "topic_qos.reliability.kind.__constraint__", "(BEST_EFFORT_RELIABILITY_QOS, RELIABLE_RELIABILITY_QOS)",
    "topic_qos.reliability.max_blocking_time.sec.__value__", "2147483647",
    "topic_qos.reliability.max_blocking_time.sec.__widget__", "spin",
    "topic_qos.reliability.max_blocking_time.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.reliability.max_blocking_time.nanosec.__value__", "2147483647",
    "topic_qos.reliability.max_blocking_time.nanosec.__widget__", "spin",
    "topic_qos.reliability.max_blocking_time.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.destination_order.kind.__value__", "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS",
    "topic_qos.destination_order.kind.__widget__", "radio",
    "topic_qos.destination_order.kind.__constraint__", "(BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS, BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS)",
    "topic_qos.history.kind.__value__", "KEEP_ALL_HISTORY_QOS",
    "topic_qos.history.kind.__widget__", "radio",
    "topic_qos.history.kind.__constraint__", "(KEEP_LAST_HISTORY_QOS, KEEP_ALL_HISTORY_QOS)",
    "topic_qos.history.depth.__value__", "1",
    "topic_qos.history.depth.__widget__", "spin",
    "topic_qos.history.depth.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.resource_limits.max_samples.__value__", "-1",
    "topic_qos.resource_limits.max_samples.__widget__", "spin",
    "topic_qos.resource_limits.max_samples.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.resource_limits.max_instances.__value__", "-1",
    "topic_qos.resource_limits.max_instances.__widget__", "spin",
    "topic_qos.resource_limits.max_instances.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.resource_limits.max_samples_per_instance.__value__", "-1",
    "topic_qos.resource_limits.max_samples_per_instance.__widget__", "spin",
    "topic_qos.resource_limits.max_samples_per_instance.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.transport_priority.value.__value__", "0",
    "topic_qos.transport_priority.value.__widget__", "spin",
    "topic_qos.transport_priority.value.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.lifespan.duration.sec.__value__", "2147483647",
    "topic_qos.lifespan.duration.sec.__widget__", "spin",
    "topic_qos.lifespan.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.lifespan.duration.nanosec.__value__", "2147483647",
    "topic_qos.lifespan.duration.nanosec.__widget__", "spin",
    "topic_qos.lifespan.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.ownership.kind.__value__", "SHARED_OWNERSHIP_QOS",
    "topic_qos.ownership.kind.__widget__", "radio",
    "topic_qos.ownership.kind.__constraint__", "(SHARED_OWNERSHIP_QOS, EXCLUSIVE_OWNERSHIP_QOS)",
    "topic_qos.transport_priority.value.__value__", "0",
    "topic_qos.transport_priority.value.__widget__", "spin",
    "topic_qos.transport_priority.value.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.durability_service.history_depth.__value__", "1",
    "topic_qos.durability_service.history_depth.__widget__", "spin",
    "topic_qos.durability_service.history_depth.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.durability_service.history_kind.__value__", "KEEP_LAST_HISTORY_QOS",
    "topic_qos.durability_service.history_kind.__widget__", "radio",
    "topic_qos.durability_service.history_kind.__constraint__", "(KEEP_LAST_HISTORY_QOS, KEEP_ALL_HISTORY_QOS)",
    "topic_qos.durability_service.max_instances.__value__", "-1",
    "topic_qos.durability_service.max_instances.__widget__", "spin",
    "topic_qos.durability_service.max_instances.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.durability_service.max_samples.__value__", "-1",
    "topic_qos.durability_service.max_samples.__widget__", "spin",
    "topic_qos.durability_service.max_samples.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.durability_service.max_samples_per_instance.__value__", "-1",
    "topic_qos.durability_service.max_samples_per_instance.__widget__", "spin",
    "topic_qos.durability_service.max_samples_per_instance.__constraint__", "-1 <= x <= 2147483647",
    "topic_qos.durability_service.service_cleanup_delay.sec.__value__", "0",
    "topic_qos.durability_service.service_cleanup_delay.sec.__widget__", "spin",
    "topic_qos.durability_service.service_cleanup_delay.sec.__constraint__", "0 <= x <= 2147483647",
    "topic_qos.durability_service.service_cleanup_delay.nanosec.__value__", "0",
    "topic_qos.durability_service.service_cleanup_delay.nanosec.__widget__", "spin",
    "topic_qos.durability_service.service_cleanup_delay.nanosec.__constraint__", "0 <= x <= 2147483647",
    ""
]

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


def OpenSpliceInPortInit():
    prop = OpenRTM_aist.Properties(defaults_str=opensplice_sub_option)
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory("opensplice",
                       OpenSpliceInPort,
                       prop)
