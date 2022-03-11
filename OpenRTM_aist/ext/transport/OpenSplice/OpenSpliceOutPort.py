#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OpenSpliceOutPort.py
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


##
# @if jp
# @class OpenSpliceOutPort
# @brief OpenSplice Publisherに対応するクラス
# InPortConsumerオブジェクトとして使用する
#
# @else
# @class OpenSpliceOutPort
# @brief
#
#
# @endif
class OpenSpliceOutPort(OpenRTM_aist.InPortConsumer):
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
        OpenRTM_aist.InPortConsumer.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OpenSpliceOutPort")
        self._properties = None
        self._dataType = RTC.TimedLong._NP_RepositoryId
        self._topic = "chatter"
        self._writer = None

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
        self._rtcout.RTC_PARANOID("~OpenSpliceOutPort()")

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    #
    # @param self
    # @param prop 接続設定
    # marshaling_type シリアライザの種類 デフォルト：OpenSplice
    # topic トピック名 デフォルト chatter
    #
    # @else
    # @brief Initializing configuration
    #
    # This operation would be called to configure this consumer
    # in initialization.
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

        self._writer = self._topicmgr.createWriter(
            topic, prop.getNode("opensplice"))

        if self._writer is None:
            raise MemoryError("Writer creation failed")

    ##
    # @if jp
    # @brief 接続先へのデータ送信
    #
    # 接続先のポートへデータを送信するための純粋仮想関数。
    #
    # この関数は、以下のリターンコードを返す。
    #
    # - PORT_OK:       正常終了。
    # - PORT_ERROR:    データ送信の過程で何らかのエラーが発生した。
    # - SEND_FULL:     データを送信したが、相手側バッファがフルだった。
    # - SEND_TIMEOUT:  データを送信したが、相手側バッファがタイムアウトした。
    # - UNKNOWN_ERROR: 原因不明のエラー
    #
    # @param data 送信するデータ
    # @return リターンコード
    #
    # @else
    # @brief Send data to the destination port
    #
    # Pure virtual function to send data to the destination port.
    #
    # This function might the following return codes
    #
    # - PORT_OK:       Normal return
    # - PORT_ERROR:    Error occurred in data transfer process
    # - SEND_FULL:     Buffer full although OutPort tried to send data
    # - SEND_TIMEOUT:  Timeout although OutPort tried to send data
    # - UNKNOWN_ERROR: Unknown error
    #
    # @endif
    #
    # virtual ReturnCode put(const cdrMemoryStream& data);
    def put(self, data):
        self._rtcout.RTC_PARANOID("put()")

        if self._writer:
            try:
                self._writer.write(data)
                return self.PORT_OK
            except BaseException:
                self._rtcout.RTC_ERROR("write error")
                return self.CONNECTION_LOST
        else:
            return self.CONNECTION_LOST

    ##
    # @if jp
    # @brief InterfaceProfile情報を公開する
    #
    # InterfaceProfile情報を公開する。
    # 引数で指定するプロパティ情報内の NameValue オブジェクトの
    # dataport.interface_type 値を調べ、当該ポートに設定されている
    # インターフェースタイプと一致する場合のみ情報を取得する。
    #
    # @param properties InterfaceProfile情報を受け取るプロパティ
    #
    # @else
    # @brief Publish InterfaceProfile information
    #
    # Publish interfaceProfile information.
    # Check the dataport.interface_type value of the NameValue object
    # specified by an argument in property information and get information
    # only when the interface type of the specified port is matched.
    #
    # @param properties Properties to get InterfaceProfile information
    #
    # @endif
    #
    # virtual void publishInterfaceProfile(SDOPackage::NVList& properties);

    def publishInterfaceProfile(self, properties):
        pass

    ##
    # @if jp
    # @brief データ送信通知への登録
    #
    # 指定されたプロパティに基づいて、データ送出通知の受け取りに登録する。
    #
    # @param properties 登録情報
    #
    # @return 登録処理結果(登録成功:true、登録失敗:false)
    #
    # @else
    # @brief Subscribe to the data sending notification
    #
    # Subscribe to the data sending notification based on specified
    # property information.
    #
    # @param properties Information for subscription
    #
    # @return Subscription result (Successful:true, Failed:false)
    #
    # @endif
    #
    # virtual bool subscribeInterface(const SDOPackage::NVList& properties);
    def subscribeInterface(self, properties):
        return True

    ##
    # @if jp
    # @brief データ送信通知からの登録解除
    #
    # データ送出通知の受け取りから登録を解除する。
    #
    # @param properties 登録解除情報
    #
    # @else
    # @brief Unsubscribe the data send notification
    #
    # Unsubscribe the data send notification.
    #
    # @param properties Information for unsubscription
    #
    # @endif
    #
    # virtual void unsubscribeInterface(const SDOPackage::NVList& properties);
    def unsubscribeInterface(self, properties):
        if self._writer:
            self._writer.close()
            self._rtcout.RTC_VERBOSE("remove writer")


opensplice_pub_option = [
    "topic.__value__", "chatter",
    "topic.__widget__", "text",
    "topic.__constraint__", "none",
    "writer_qos.durability.kind.__value__", "TRANSIENT_DURABILITY_QOS",
    "writer_qos.durability.kind.__widget__", "radio",
    "writer_qos.durability.kind.__constraint__", "(VOLATILE_DURABILITY_QOS, TRANSIENT_LOCAL_DURABILITY_QOS, TRANSIENT_DURABILITY_QOS, PERSISTENT_DURABILITY_QOS)",
    "writer_qos.deadline.period.sec.__value__", "2147483647",
    "writer_qos.deadline.period.sec.__widget__", "spin",
    "writer_qos.deadline.period.sec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.deadline.period.nanosec.__value__", "2147483647",
    "writer_qos.deadline.period.nanosec.__widget__", "text",
    "writer_qos.deadline.period.nanosec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.latency_budget.duration.sec.__value__", "0",
    "writer_qos.latency_budget.duration.sec.__widget__", "spin",
    "writer_qos.latency_budget.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.latency_budget.duration.nanosec.__value__", "0",
    "writer_qos.latency_budget.duration.nanosec.__widget__", "spin",
    "writer_qos.latency_budget.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.liveliness.kind.__value__", "AUTOMATIC_LIVELINESS_QOS",
    "writer_qos.liveliness.kind.__widget__", "radio",
    "writer_qos.liveliness.kind.__constraint__", "(AUTOMATIC_LIVELINESS_QOS, MANUAL_BY_PARTICIPANT_LIVELINESS_QOS, MANUAL_BY_TOPIC_LIVELINESS_QOS)",
    "writer_qos.liveliness.lease_duration.sec.__value__", "2147483647",
    "writer_qos.liveliness.lease_duration.sec.__widget__", "spin",
    "writer_qos.liveliness.lease_duration.sec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.liveliness.lease_duration.nanosec.__value__", "2147483647",
    "writer_qos.liveliness.lease_duration.nanosec.__widget__", "spin",
    "writer_qos.liveliness.lease_duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.reliability.kind.__value__", "RELIABLE_RELIABILITY_QOS",
    "writer_qos.reliability.kind.__widget__", "radio",
    "writer_qos.reliability.kind.__constraint__", "(BEST_EFFORT_RELIABILITY_QOS, RELIABLE_RELIABILITY_QOS)",
    "writer_qos.reliability.max_blocking_time.sec.__value__", "2147483647",
    "writer_qos.reliability.max_blocking_time.sec.__widget__", "spin",
    "writer_qos.reliability.max_blocking_time.sec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.reliability.max_blocking_time.nanosec.__value__", "2147483647",
    "writer_qos.reliability.max_blocking_time.nanosec.__widget__", "spin",
    "writer_qos.reliability.max_blocking_time.nanosec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.destination_order.kind.__value__", "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS",
    "writer_qos.destination_order.kind.__widget__", "radio",
    "writer_qos.destination_order.kind.__constraint__", "(BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS, BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS)",
    "writer_qos.history.kind.__value__", "KEEP_LAST_HISTORY_QOS",
    "writer_qos.history.kind.__widget__", "radio",
    "writer_qos.history.kind.__constraint__", "(KEEP_LAST_HISTORY_QOS, KEEP_ALL_HISTORY_QOS)",
    "writer_qos.history.depth.__value__", "1",
    "writer_qos.history.depth.__widget__", "spin",
    "writer_qos.history.depth.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.resource_limits.max_samples.__value__", "-1",
    "writer_qos.resource_limits.max_samples.__widget__", "spin",
    "writer_qos.resource_limits.max_samples.__constraint__", "-1 <= x <= 2147483647",
    "writer_qos.resource_limits.max_instances.__value__", "-1",
    "writer_qos.resource_limits.max_instances.__widget__", "spin",
    "writer_qos.resource_limits.max_instances.__constraint__", "-1 <= x <= 2147483647",
    "writer_qos.resource_limits.max_samples_per_instance.__value__", "-1",
    "writer_qos.resource_limits.max_samples_per_instance.__widget__", "spin",
    "writer_qos.resource_limits.max_samples_per_instance.__constraint__", "-1 <= x <= 2147483647",
    "writer_qos.transport_priority.value.__value__", "0",
    "writer_qos.transport_priority.value.__widget__", "spin",
    "writer_qos.transport_priority.value.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.lifespan.duration.sec.__value__", "2147483647",
    "writer_qos.lifespan.duration.sec.__widget__", "spin",
    "writer_qos.lifespan.duration.sec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.lifespan.duration.nanosec.__value__", "2147483647",
    "writer_qos.lifespan.duration.nanosec.__widget__", "spin",
    "writer_qos.lifespan.duration.nanosec.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.ownership.kind.__value__", "SHARED_OWNERSHIP_QOS",
    "writer_qos.ownership.kind.__widget__", "radio",
    "writer_qos.ownership.kind.__constraint__", "(SHARED_OWNERSHIP_QOS, EXCLUSIVE_OWNERSHIP_QOS)",
    "writer_qos.ownership_strength.value.__value__", "0",
    "writer_qos.ownership_strength.value.__widget__", "spin",
    "writer_qos.ownership_strength.value.__constraint__", "0 <= x <= 2147483647",
    "writer_qos.writer_data_lifecycle.autodispose_unregistered_instances.__value__", "YES",
    "writer_qos.writer_data_lifecycle.autodispose_unregistered_instances.__widget__", "radio",
    "writer_qos.writer_data_lifecycle.autodispose_unregistered_instances.__constraint__", "(YES, NO)",
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


def OpenSpliceOutPortInit():
    prop = OpenRTM_aist.Properties(defaults_str=opensplice_pub_option)
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("opensplice",
                       OpenSpliceOutPort,
                       prop)
