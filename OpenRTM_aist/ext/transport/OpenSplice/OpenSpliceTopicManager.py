#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OpenSpliceTopicManager.py
# @brief OpenSplice Topic Manager class
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
import OpenSpliceMessageInfo
import dds
import ddsutil
import threading


manager = None
mutex = threading.RLock()

##
# @if jp
# @class OpenSpliceTopicManager
# @brief OpenSpliceトピックを管理するクラス
#
#
# @else
# @class OpenSpliceTopicManager
# @brief
#
#
# @endif


class OpenSpliceTopicManager(object):
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
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OpenSpliceTopicManager")
        self._qosProfile = None
        self._domainParticipant = None
        self._topic = {}
        self._info = {}
        self._publisher = None
        self._subscriber = None
        # mgr = OpenRTM_aist.Manager.instance()
        # mgr.addManagerActionListener(ManagerActionListener(self))
        # self._rtcout = mgr.getLogbuf("OpenSpliceTopicManager")

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
    # @brief ドメインパティシパント、パブリッシャー、サブスクライバー初期化
    #
    # @param self
    # @param qosxml QOS設定XMLファイル
    # DDS_DefaultQoS_All.xml、DDS_VolatileQoS_All.xml等の設定ファイルを指定する
    # 指定しない場合は以下のデフォルトのQOSに設定する
    # DurabilityQosPolicy: TRANSIENT
    # DeadlineQosPolicy: 500
    # LatencyBudgetQosPolicy 3000
    # LivelinessQosPolicy: MANUAL_BY_PARTICIPANT
    # ReliabilityQosPolicy: RELIABLE, infinity
    # DestinationOrderQosPolicy: BY_SOURCE_TIMESTAMP
    # HistoryQosPolicy: KEEP_ALL
    # ResourceLimitsQosPolicy: 10,10,10
    # TransportPriorityQosPolicy: 700
    # LifespanQosPolicy:10, 500
    # OwnershipQosPolicy: EXCLUSIVE
    # OwnershipStrengthQosPolicy 100
    # WriterDataLifecycleQosPolicy: False
    # ReaderDataLifecycleQosPolicy: 3,3
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param qosxml
    #
    # @endif

    def start(self, prop):
        self._rtcout.RTC_PARANOID("OpenSpliceManager::start()")
        self._rtcout.RTC_DEBUG("%s", prop)
        uri = prop.getProperty("uri")
        profile = prop.getProperty("profile")
        domainid = -1
        try:
            domainid = int(prop.getProperty("domain.id"))
        except ValueError as error:
            pass
        if uri and profile:
            self._qosProfile = dds.QosProvider(uri, profile)
            # participant_name = prop.getProperty("participant_qos.name")
            if domainid == -1:
                self._domainParticipant = dds.DomainParticipant(
                    qos=self._qosProfile.get_participant_qos())
            else:
                self._domainParticipant = dds.DomainParticipant(
                    did=domainid,
                    qos=self._qosProfile.get_participant_qos())
            self._rtcout.RTC_INFO(
                "DomainParticipantQos initialisation successful")

        else:
            self._rtcout.RTC_INFO(
                "DomainParticipantQos has been set to the default value.")
            if domainid == -1:
                self._domainParticipant = dds.DomainParticipant()
            else:
                self._domainParticipant = dds.DomainParticipant(did=domainid)

        self.createPublisher(prop)
        self.createSubscriber(prop)

    ##
    # @if jp
    # @brief Publisher生成
    #
    # @param self
    # @param prop 設定プロパティ
    # @return True：生成成功、False：エラー
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
    def createPublisher(self, prop):
        self._rtcout.RTC_INFO("OpenSpliceManager::createPublisher()")

        if self._publisher:
            return True

        if self._qosProfile:
            self._rtcout.RTC_INFO("QoSProvider set PublisherQos")
            pub_qos = self._qosProfile.get_publisher_qos()
            self._publisher = self._domainParticipant.create_publisher(
                qos=pub_qos)
        else:
            self._rtcout.RTC_INFO(
                "PublisherQos has been set to the default value.")

            presentation_access_scope = dds.DDSPresentationAccessScopeKind.INSTANCE
            presentation_access_scope_str = prop.getProperty(
                "publisher_qos.presentation.access_scope")
            if presentation_access_scope_str == "INSTANCE_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.INSTANCE
            elif presentation_access_scope_str == "TOPIC_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.TOPIC
            elif presentation_access_scope_str == "GROUP_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.GROUP

            coherent_access = OpenRTM_aist.toBool(prop.getProperty(
                "publisher_qos.presentation.coherent_access"), "YES", "NO", True)
            ordered_access = OpenRTM_aist.toBool(prop.getProperty(
                "publisher_qos.presentation.ordered_access"), "YES", "NO", True)
            presentation_qos_policy = dds.PresentationQosPolicy(
                kind=presentation_access_scope, coherent_access=coherent_access, ordered_access=ordered_access)

            pub_qos = dds.Qos([presentation_qos_policy])

            self._publisher = self._domainParticipant.create_publisher(pub_qos)

            self._rtcout.RTC_DEBUG("PublisherQos setting: publisher_qos.presentation.access_scope: %s",
                                   str(presentation_qos_policy.kind))
            self._rtcout.RTC_DEBUG("PublisherQos setting: publisher_qos.presentation.coherent_access: %s",
                                   str(presentation_qos_policy.coherent_access))
            self._rtcout.RTC_DEBUG("PublisherQos setting: publisher_qos.presentation.ordered_access: %s",
                                   str(presentation_qos_policy.ordered_access))

        return True

    ##
    # @if jp
    # @brief Subscriber生成
    #
    # @param self
    # @param prop 設定プロパティ
    # @return True：生成成功、False：エラー
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

    def createSubscriber(self, prop):
        self._rtcout.RTC_INFO("OpenSpliceManager::createSubscriber()")

        if self._subscriber:
            return True

        if self._qosProfile:
            self._rtcout.RTC_INFO("QoSProvider set SubscriberQos")
            sub_qos = self._qosProfile.get_subscriber_qos()
            self._subscriber = self._domainParticipant.create_subscriber(
                qos=sub_qos)
        else:
            self._rtcout.RTC_INFO(
                "SubscriberQos has been set to the default value.")

            presentation_access_scope = dds.DDSPresentationAccessScopeKind.INSTANCE
            presentation_access_scope_str = prop.getProperty(
                "subscriber_qos.presentation.access_scope")
            if presentation_access_scope_str == "INSTANCE_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.INSTANCE
            elif presentation_access_scope_str == "TOPIC_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.TOPIC
            elif presentation_access_scope_str == "GROUP_PRESENTATION_QOS":
                presentation_access_scope = dds.DDSPresentationAccessScopeKind.GROUP

            coherent_access = OpenRTM_aist.toBool(prop.getProperty(
                "subscriber_qos.presentation.coherent_access"), "YES", "NO", True)
            ordered_access = OpenRTM_aist.toBool(prop.getProperty(
                "subscriber_qos.presentation.ordered_access"), "YES", "NO", True)
            presentation_qos_policy = dds.PresentationQosPolicy(
                kind=presentation_access_scope, coherent_access=coherent_access, ordered_access=ordered_access)

            sub_qos = dds.Qos([presentation_qos_policy])

            self._subscriber = self._domainParticipant.create_subscriber(
                qos=sub_qos)

            self._rtcout.RTC_DEBUG("SubscriberQos setting: subscriber_qos.presentation.access_scope: %s",
                                   str(presentation_qos_policy.kind))
            self._rtcout.RTC_DEBUG("SubscriberQos setting: subscriber_qos.presentation.coherent_access: %s",
                                   str(presentation_qos_policy.coherent_access))
            self._rtcout.RTC_DEBUG("SubscriberQos setting: subscriber_qos.presentation.ordered_access: %s",
                                   str(presentation_qos_policy.ordered_access))

        return True

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
        global manager

        manager = None
        for _, v in self._topic.items():
            v.close()
        if self._publisher:
            self._publisher.close()
        if self._subscriber:
            self._subscriber.close()
        if self._domainParticipant:
            self._domainParticipant.close()

        self._qosProfile = None
        self._domainParticipant = None
        self._topic = {}
        self._info = {}

    ##
    # @if jp
    # @brief 指定データ型のロード、Infoオブジェクト生成
    #
    # @param self
    # @param datatype データ型名
    # @return Infoオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param datatype
    # @return
    #
    # @endif
    def genInfo(self, datatype):
        global mutex
        guard = OpenRTM_aist.ScopedLock(mutex)
        if datatype in self._info:
            return self._info[datatype]
        datainfo = OpenSpliceMessageInfo.OpenSpliceMessageInfoList.instance().getInfo(datatype)
        if datainfo:
            datatype = datainfo.datatype()
            idlfile = datainfo.idlFile()
            self._info[datatype] = ddsutil.get_dds_classes_from_idl(idlfile,
                                                                    datatype)
            return self._info[datatype]
        return None

    ##
    # @if jp
    # @brief Writerオブジェクト生成
    #
    # @param self
    # @param topic トピックオブジェクト
    # @return Writerオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param topic
    # @return
    #
    # @endif
    def createWriter(self, topic, prop):
        global mutex
        self._rtcout.RTC_INFO(
            "OpenSpliceManager::createWriter()")
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._qosProfile:
            self._rtcout.RTC_INFO("QoSProvider set DataWriterQos")
            return self._publisher.create_datawriter(
                topic, self._qosProfile.get_writer_qos())
        else:
            self._rtcout.RTC_INFO(
                "DataWriterQos has been set to the default value.")
            durability_kind = dds.DDSDurabilityKind.VOLATILE
            durability_kind_str = prop.getProperty(
                "writer_qos.durability.kind")
            if durability_kind_str == "VOLATILE_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.VOLATILE
            elif durability_kind_str == "TRANSIENT_LOCAL_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.TRANSIENT_LOCAL
            elif durability_kind_str == "TRANSIENT_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.TRANSIENT
            elif durability_kind_str == "PERSISTENT_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.PERSISTENT

            durability_qos_policy = dds.DurabilityQosPolicy(durability_kind)

            deadline_period = self.getDuration(
                prop.getNode("writer_qos.deadline.period"))

            if deadline_period is None:
                deadline_period = dds.DDSDuration.infinity()

            deadline_qos_policy = dds.DeadlineQosPolicy(deadline_period)

            latency_budget_duration = self.getDuration(
                prop.getNode("writer_qos.latency_budget.duration"))

            if latency_budget_duration is None:
                latency_budget_duration = dds.DDSDuration()

            latency_budget_qos_policy = dds.LatencyBudgetQosPolicy(
                latency_budget_duration)

            liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
            liveliness_kind_str = prop.getProperty(
                "writer_qos.liveliness.kind")
            if liveliness_kind_str == "AUTOMATIC_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
            elif liveliness_kind_str == "MANUAL_BY_PARTICIPANT_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT
            elif liveliness_kind_str == "MANUAL_BY_TOPIC_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_TOPIC

            liveliness_lease_duration_time = self.getDuration(
                prop.getNode("writer_qos.liveliness.lease_duration"))

            if liveliness_lease_duration_time is None:
                liveliness_lease_duration_time = dds.DDSDuration.infinity()

            liveliness_qos_policy = dds.LivelinessQosPolicy(
                liveliness_kind,
                liveliness_lease_duration_time)

            reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
            reliability_kind_str = prop.getProperty(
                "writer_qos.reliability.kind")
            if reliability_kind_str == "BEST_EFFORT_RELIABILITY_QOS":
                reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
            elif reliability_kind_str == "RELIABLE_RELIABILITY_QOS":
                reliability_kind = dds.DDSReliabilityKind.RELIABLE

            reliability_max_blocking_time = self.getDuration(
                prop.getNode("writer_qos.reliability.max_blocking_time"))

            if reliability_max_blocking_time is None:
                reliability_max_blocking_time = dds.DDSDuration(0, 100000000)

            reliability_qos_policy = dds.ReliabilityQosPolicy(
                reliability_kind, reliability_max_blocking_time)

            destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
            destination_order_kind_str = prop.getProperty(
                "writer_qos.destination_order.kind")
            if destination_order_kind_str == "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS":
                destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
            elif destination_order_kind_str == "BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS":
                destination_order_kind = dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP

            destinatio_order_qos_policy = dds.DestinationOrderQosPolicy(
                destination_order_kind)

            history_qos_policy_kind = dds.DDSHistoryKind.KEEP_LAST
            history_qos_policy_kind_str = prop.getProperty(
                "writer_qos.history.kind")
            if history_qos_policy_kind_str == "KEEP_ALL_HISTORY_QOS":
                history_qos_policy_kind = dds.DDSHistoryKind.KEEP_ALL
            elif history_qos_policy_kind_str == "KEEP_LAST_HISTORY_QOS":
                history_qos_policy_kind = dds.DDSHistoryKind.KEEP_LAST

            history_depth = 1
            try:
                history_depth = int(prop.getProperty(
                    "writer_qos.history.depth"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            history_qos_policy = dds.HistoryQosPolicy(
                history_qos_policy_kind, history_depth)

            max_samples = -1
            max_instances = -1
            max_samples_per_instance = -1
            try:
                max_samples = int(prop.getProperty(
                    "writer_qos.resource_limits.max_samples"))
                max_instances = int(prop.getProperty(
                    "writer_qos.resource_limits.max_instances"))
                max_samples_per_instance = int(prop.getProperty(
                    "writer_qos.resource_limits.max_samples_per_instance"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            resource_limits_qos_policy = dds.ResourceLimitsQosPolicy(
                max_samples, max_instances, max_samples_per_instance)

            transport_priority = 0
            try:
                transport_priority = int(prop.getProperty(
                    "writer_qos.transport_priority.value"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            transport_priority_qos_policy = dds.TransportPriorityQosPolicy(
                transport_priority)

            lifespan_duration = self.getDuration(
                prop.getNode("writer_qos.lifespan.duration"))

            if lifespan_duration is None:
                lifespan_duration = dds.DDSDuration.infinity()

            lifespan_qos_policy = dds.LifespanQosPolicy(lifespan_duration)

            ownership_kind = dds.DDSOwnershipKind.SHARED
            ownership_kind_str = prop.getProperty(
                "writer_qos.ownership.kind")
            if ownership_kind_str == "SHARED_OWNERSHIP_QOS":
                ownership_kind = dds.DDSOwnershipKind.SHARED
            elif ownership_kind_str == "EXCLUSIVE_OWNERSHIP_QOS":
                ownership_kind = dds.DDSOwnershipKind.EXCLUSIVE

            ownership_qos_policy = dds.OwnershipQosPolicy(ownership_kind)

            ownership_strength = 0
            try:
                ownership_strength = int(prop.getProperty(
                    "writer_qos.ownership_strength.value"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            ownership_strength_qos_policy = dds.OwnershipStrengthQosPolicy(
                ownership_strength)

            autodispose_unregistered_instances = OpenRTM_aist.toBool(prop.getProperty(
                "writer_qos.writer_data_lifecycle.autodispose_unregistered_instances"), "YES", "NO", True)
            writer_data_lifecycle_qos_policy = dds.WriterDataLifecycleQosPolicy(
                autodispose_unregistered_instances)

            writer_qos = dds.Qos([durability_qos_policy,
                                  deadline_qos_policy,
                                  latency_budget_qos_policy,
                                  liveliness_qos_policy,
                                  reliability_qos_policy,
                                  destinatio_order_qos_policy,
                                  history_qos_policy,
                                  resource_limits_qos_policy,
                                  transport_priority_qos_policy,
                                  lifespan_qos_policy,
                                  ownership_qos_policy,
                                  ownership_strength_qos_policy,
                                  writer_data_lifecycle_qos_policy])

            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.durability.kind: %s", str(durability_qos_policy.kind))
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.deadline.period: %lf",
                                   deadline_qos_policy.deadline)
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.latency_budget.duration: %lf",
                                   latency_budget_qos_policy.duration)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.liveliness.kind: %s", str(liveliness_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.liveliness.lease_duration: %lf", liveliness_qos_policy.lease_duration)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.reliability.kind: %s", str(reliability_qos_policy.kind))
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.reliability.max_blocking_time: %lf",
                                   reliability_qos_policy.max_blocking_time)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.destination_order.kind: %s", str(destinatio_order_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.history.kind: %s", str(history_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.history.depth: %d", history_qos_policy.depth)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.resource_limits.max_samples: %d", resource_limits_qos_policy.max_samples)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.resource_limits.max_instances: %d", resource_limits_qos_policy.max_instances)
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.resource_limits.max_samples_per_instance: %d",
                                   resource_limits_qos_policy.max_samples_per_instance)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.transport_priority.value: %d", transport_priority_qos_policy.value)
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.lifespan.duration: %lf",
                                   lifespan_qos_policy.lifespan)
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.ownership.kind: %s", str(ownership_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataWriterQos setting: writer_qos.ownership_strength.value: %d", ownership_strength_qos_policy.value)
            self._rtcout.RTC_DEBUG("DataWriterQos setting: writer_qos.writer_data_lifecycle.autodispose_unregistered_instances: %s", str(
                writer_data_lifecycle_qos_policy.autodispose_unregistered_instances))

            return self._publisher.create_datawriter(topic, writer_qos)

    ##
    # @if jp
    # @brief Readerオブジェクト生成
    #
    # @param self
    # @param topic トピックオブジェクト
    # @return Readerオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param topic
    # @return
    #
    # @endif
    def createReader(self, topic, listener, prop):
        global mutex
        self._rtcout.RTC_INFO(
            "OpenSpliceManager::createReader(topic)")
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._qosProfile:
            self._rtcout.RTC_INFO("QoSProvider set DataReaderQos")
            return self._subscriber.create_datareader(
                topic, self._qosProfile.get_reader_qos(), listener)
        else:
            self._rtcout.RTC_INFO(
                "DataReaderQos has been set to the default value.")

            durability_kind = dds.DDSDurabilityKind.VOLATILE
            durability_kind_str = prop.getProperty(
                "reader_qos.durability.kind")
            if durability_kind_str == "VOLATILE_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.VOLATILE
            elif durability_kind_str == "TRANSIENT_LOCAL_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.TRANSIENT_LOCAL
            elif durability_kind_str == "TRANSIENT_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.TRANSIENT
            elif durability_kind_str == "PERSISTENT_DURABILITY_QOS":
                durability_kind = dds.DDSDurabilityKind.PERSISTENT

            durability_qos_policy = dds.DurabilityQosPolicy(durability_kind)

            deadline_period = self.getDuration(
                prop.getNode("reader_qos.deadline.period"))

            if deadline_period is None:
                deadline_period = dds.DDSDuration.infinity()

            deadline_qos_policy = dds.DeadlineQosPolicy(deadline_period)

            latency_budget_duration = self.getDuration(
                prop.getNode("reader_qos.latency_budget.duration"))

            if latency_budget_duration is None:
                latency_budget_duration = dds.DDSDuration()

            latency_budget_qos_policy = dds.LatencyBudgetQosPolicy(
                latency_budget_duration)

            liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
            liveliness_kind_str = prop.getProperty(
                "reader_qos.liveliness.kind")
            if liveliness_kind_str == "AUTOMATIC_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
            elif liveliness_kind_str == "MANUAL_BY_PARTICIPANT_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT
            elif liveliness_kind_str == "MANUAL_BY_TOPIC_LIVELINESS_QOS":
                liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_TOPIC

            liveliness_lease_duration_time = self.getDuration(
                prop.getNode("reader_qos.liveliness.lease_duration"))

            if liveliness_lease_duration_time is None:
                liveliness_lease_duration_time = dds.DDSDuration.infinity()

            liveliness_qos_policy = dds.LivelinessQosPolicy(
                liveliness_kind,
                liveliness_lease_duration_time)

            reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
            reliability_kind_str = prop.getProperty(
                "reader_qos.reliability.kind")
            if reliability_kind_str == "BEST_EFFORT_RELIABILITY_QOS":
                reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
            elif reliability_kind_str == "RELIABLE_RELIABILITY_QOS":
                reliability_kind = dds.DDSReliabilityKind.RELIABLE

            reliability_max_blocking_time = self.getDuration(
                prop.getNode("reader_qos.reliability.max_blocking_time"))

            if reliability_max_blocking_time is None:
                reliability_max_blocking_time = dds.DDSDuration(0, 100000000)

            reliability_qos_policy = dds.ReliabilityQosPolicy(
                reliability_kind, reliability_max_blocking_time)

            destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
            destination_order_kind_str = prop.getProperty(
                "reader_qos.destination_order.kind")
            if destination_order_kind_str == "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS":
                destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
            elif destination_order_kind_str == "BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS":
                destination_order_kind = dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP

            destinatio_order_qos_policy = dds.DestinationOrderQosPolicy(
                destination_order_kind)

            history_qos_kind = dds.DDSHistoryKind.KEEP_LAST
            history_qos_kind_str = prop.getProperty(
                "reader_qos.history.kind")
            if history_qos_kind_str == "KEEP_ALL":
                history_qos_kind = dds.DDSHistoryKind.KEEP_ALL
            elif history_qos_kind_str == "KEEP_LAST":
                history_qos_kind = dds.DDSHistoryKind.KEEP_LAST

            history_depth = 1
            try:
                history_depth = int(prop.getProperty(
                    "reader_qos.history.depth"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            history_qos_policy = dds.HistoryQosPolicy(
                history_qos_kind, history_depth)

            max_samples = -1
            max_instances = -1
            max_samples_per_instance = -1
            try:
                max_samples = int(prop.getProperty(
                    "reader_qos.resource_limits.max_samples"))
                max_instances = int(prop.getProperty(
                    "reader_qos.resource_limits.max_instances"))
                max_samples_per_instance = int(prop.getProperty(
                    "reader_qos.resource_limits.max_samples_per_instance"))
            except ValueError as error:
                pass
                # self._rtcout.RTC_ERROR(error)

            resource_limits_qos_policy = dds.ResourceLimitsQosPolicy(
                max_samples, max_instances, max_samples_per_instance)

            ownership_kind = dds.DDSOwnershipKind.SHARED
            ownership_kind_str = prop.getProperty(
                "reader_qos.ownership.kind")
            if ownership_kind_str == "SHARED_OWNERSHIP_QOS":
                ownership_kind = dds.DDSOwnershipKind.SHARED
            elif ownership_kind_str == "EXCLUSIVE_OWNERSHIP_QOS":
                ownership_kind = dds.DDSOwnershipKind.EXCLUSIVE

            ownership_qos_policy = dds.OwnershipQosPolicy(ownership_kind)

            time_based_filter_minimum_separation = self.getDuration(
                prop.getNode("reader_qos.time_based_filter.minimum_separation"))

            if time_based_filter_minimum_separation is None:
                time_based_filter_minimum_separation = dds.DDSDuration(0, 0)

            time_based_filter_qos_policy = dds.TimeBasedFilterQosPolicy(
                time_based_filter_minimum_separation)

            autopurge_disposed_samples_delay = self.getDuration(
                prop.getNode("reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay"))

            if autopurge_disposed_samples_delay is None:
                autopurge_disposed_samples_delay = dds.DDSDuration.infinity()

            autopurge_nowriter_samples_delay = self.getDuration(
                prop.getNode("reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay"))

            if autopurge_nowriter_samples_delay is None:
                autopurge_nowriter_samples_delay = dds.DDSDuration.infinity()

            reader_data_lifecycle_qos_policy = dds.ReaderDataLifecycleQosPolicy(
                autopurge_nowriter_samples_delay, autopurge_disposed_samples_delay)

            reader_qos = dds.Qos([durability_qos_policy,
                                  deadline_qos_policy,
                                  latency_budget_qos_policy,
                                  liveliness_qos_policy,
                                  reliability_qos_policy,
                                  destinatio_order_qos_policy,
                                  history_qos_policy,
                                  resource_limits_qos_policy,
                                  ownership_qos_policy,
                                  time_based_filter_qos_policy,
                                  reader_data_lifecycle_qos_policy])

            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.durability.kind: %s", str(durability_qos_policy.kind))
            self._rtcout.RTC_DEBUG("DataReaderQos setting: reader_qos.deadline.period: %lf",
                                   deadline_qos_policy.deadline)
            self._rtcout.RTC_DEBUG("DataReaderQos setting: reader_qos.latency_budget.duration: %lf",
                                   latency_budget_qos_policy.duration)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.liveliness.kind: %s", str(liveliness_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.liveliness.lease_duration: %lf", liveliness_qos_policy.lease_duration)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.reliability.kind: %s", str(reliability_qos_policy.kind))
            self._rtcout.RTC_DEBUG("DataReaderQos setting: reader_qos.reliability.max_blocking_time: %lf",
                                   reliability_qos_policy.max_blocking_time)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.destination_order.kind: %s", str(destinatio_order_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.history.kind: %s", str(history_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.history.depth: %d", history_qos_policy.depth)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.resource_limits.max_samples: %d", resource_limits_qos_policy.max_samples)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.resource_limits.max_instances: %d", resource_limits_qos_policy.max_instances)
            self._rtcout.RTC_DEBUG("DataReaderQos setting: reader_qos.resource_limits.max_samples_per_instance: %d",
                                   resource_limits_qos_policy.max_samples_per_instance)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.ownership.kind: %s", str(ownership_qos_policy.kind))
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.time_based_filter.minimum_separation: %lf",
                time_based_filter_qos_policy.minimum_separation)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.reader_data_lifecycle.autopurge_disposed_samples_delay: %lf",
                reader_data_lifecycle_qos_policy.autopurge_disposed_samples_delay)
            self._rtcout.RTC_DEBUG(
                "DataReaderQos setting: reader_qos.reader_data_lifecycle.autopurge_nowriter_samples_delay: %lf",
                reader_data_lifecycle_qos_policy.autopurge_nowriter_samples)

            return self._subscriber.create_datareader(
                topic, reader_qos, listener)

    ##
    # @if jp
    # @brief Topicオブジェクト生成
    #
    # @param self
    # @param datatype データ型名
    # @param topicname トピック名
    # @return Topicオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param datatype
    # @param topicname
    # @return
    #
    # @endif

    def createTopic(self, datatype, topicname, prop):
        global mutex
        self._rtcout.RTC_INFO("OpenSpliceManager")
        guard = OpenRTM_aist.ScopedLock(mutex)
        if topicname in self._topic:
            return self._topic[topicname]
        else:
            geninfo = self.genInfo(datatype)
            if geninfo:
                if self._qosProfile:
                    self._rtcout.RTC_INFO("QoSProvider set TopicQos")
                    self._topic[topicname] = geninfo.register_topic(
                        self._domainParticipant, topicname, self._qosProfile.get_topic_qos())
                else:
                    self._rtcout.RTC_INFO(
                        "TopicQos has been set to the default value.")

                    durability_kind = dds.DDSDurabilityKind.VOLATILE
                    durability_kind_str = prop.getProperty(
                        "topic_qos.durability.kind")
                    if durability_kind_str == "VOLATILE_DURABILITY_QOS":
                        durability_kind = dds.DDSDurabilityKind.VOLATILE
                    elif durability_kind_str == "TRANSIENT_LOCAL_DURABILITY_QOS":
                        durability_kind = dds.DDSDurabilityKind.TRANSIENT_LOCAL
                    elif durability_kind_str == "TRANSIENT_DURABILITY_QOS":
                        durability_kind = dds.DDSDurabilityKind.TRANSIENT
                    elif durability_kind_str == "PERSISTENT_DURABILITY_QOS":
                        durability_kind = dds.DDSDurabilityKind.PERSISTENT

                    durability_qos_policy = dds.DurabilityQosPolicy(
                        durability_kind)

                    deadline_period = self.getDuration(
                        prop.getNode("topic_qos.deadline.period"))

                    if deadline_period is None:
                        deadline_period = dds.DDSDuration.infinity()

                    deadline_qos_policy = dds.DeadlineQosPolicy(
                        deadline_period)

                    latency_budget_duration = self.getDuration(
                        prop.getNode("topic_qos.latency_budget.duration"))

                    if latency_budget_duration is None:
                        latency_budget_duration = dds.DDSDuration()

                    latency_budget_qos_policy = dds.LatencyBudgetQosPolicy(
                        latency_budget_duration)

                    liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
                    liveliness_kind_str = prop.getProperty(
                        "topic_qos.liveliness.kind")
                    if liveliness_kind_str == "AUTOMATIC_LIVELINESS_QOS":
                        liveliness_kind = dds.DDSLivelinessKind.AUTOMATIC
                    elif liveliness_kind_str == "MANUAL_BY_PARTICIPANT_LIVELINESS_QOS":
                        liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT
                    elif liveliness_kind_str == "MANUAL_BY_TOPIC_LIVELINESS_QOS":
                        liveliness_kind = dds.DDSLivelinessKind.MANUAL_BY_TOPIC

                    liveliness_lease_duration_time = self.getDuration(
                        prop.getNode("topic_qos.liveliness.lease_duration"))

                    if liveliness_lease_duration_time is None:
                        liveliness_lease_duration_time = dds.DDSDuration.infinity()

                    liveliness_qos_policy = dds.LivelinessQosPolicy(
                        liveliness_kind,
                        liveliness_lease_duration_time)

                    reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
                    reliability_kind_str = prop.getProperty(
                        "topic_qos.reliability.kind")
                    if reliability_kind_str == "BEST_EFFORT_RELIABILITY_QOS":
                        reliability_kind = dds.DDSReliabilityKind.BEST_EFFORT
                    elif reliability_kind_str == "RELIABLE_RELIABILITY_QOS":
                        reliability_kind = dds.DDSReliabilityKind.RELIABLE

                    reliability_max_blocking_time = self.getDuration(
                        prop.getNode("topic_qos.reliability.max_blocking_time"))

                    if reliability_max_blocking_time is None:
                        reliability_max_blocking_time = dds.DDSDuration(
                            0, 100000000)

                    reliability_qos_policy = dds.ReliabilityQosPolicy(
                        reliability_kind, reliability_max_blocking_time)

                    destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
                    destination_order_kind_str = prop.getProperty(
                        "topic_qos.destination_order.kind")
                    if destination_order_kind_str == "BY_RECEPTION_TIMESTAMP_DESTINATIONORDER_QOS":
                        destination_order_kind = dds.DDSDestinationOrderKind.BY_RECEPTION_TIMESTAMP
                    elif destination_order_kind_str == "BY_SOURCE_TIMESTAMP_DESTINATIONORDER_QOS":
                        destination_order_kind = dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP

                    destinatio_order_qos_policy = dds.DestinationOrderQosPolicy(
                        destination_order_kind)

                    history_qos_kind = dds.DDSHistoryKind.KEEP_LAST
                    history_qos_kind_str = prop.getProperty(
                        "topic_qos.history.kind")
                    if history_qos_kind_str == "KEEP_ALL":
                        history_qos_kind = dds.DDSHistoryKind.KEEP_ALL
                    elif history_qos_kind_str == "KEEP_LAST":
                        history_qos_kind = dds.DDSHistoryKind.KEEP_LAST

                    history_depth = 1
                    try:
                        history_depth = int(prop.getProperty(
                            "topic_qos.history.depth"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    history_qos_policy = dds.HistoryQosPolicy(
                        history_qos_kind, history_depth)

                    max_samples = -1
                    max_instances = -1
                    max_samples_per_instance = -1
                    try:
                        max_samples = int(prop.getProperty(
                            "topic_qos.resource_limits.max_samples"))
                        max_instances = int(prop.getProperty(
                            "topic_qos.resource_limits.max_instances"))
                        max_samples_per_instance = int(prop.getProperty(
                            "topic_qos.resource_limits.max_samples_per_instance"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    resource_limits_qos_policy = dds.ResourceLimitsQosPolicy(
                        max_samples, max_instances, max_samples_per_instance)

                    transport_priority = 0
                    try:
                        transport_priority = int(prop.getProperty(
                            "topic_qos.transport_priority.value"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    transport_priority_qos_policy = dds.TransportPriorityQosPolicy(
                        transport_priority)

                    lifespan_duration = self.getDuration(
                        prop.getNode("topic_qos.lifespan.duration"))

                    if lifespan_duration is None:
                        lifespan_duration = dds.DDSDuration.infinity()

                    lifespan_qos_policy = dds.LifespanQosPolicy(
                        lifespan_duration)

                    ownership_kind = dds.DDSOwnershipKind.SHARED
                    ownership_kind_str = prop.getProperty(
                        "topic_qos.ownership.kind")
                    if ownership_kind_str == "SHARED_OWNERSHIP_QOS":
                        ownership_kind = dds.DDSOwnershipKind.SHARED
                    elif ownership_kind_str == "EXCLUSIVE_OWNERSHIP_QOS":
                        ownership_kind = dds.DDSOwnershipKind.EXCLUSIVE

                    ownership_qos_policy = dds.OwnershipQosPolicy(
                        ownership_kind)

                    durability_service_history_depth = 1
                    try:
                        durability_service_history_depth = int(prop.getProperty(
                            "topic_qos.durability_service.history_depth"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    durability_service_history_kind = dds.DDSHistoryKind.KEEP_LAST
                    durability_service_history_kind_str = prop.getProperty(
                        "topic_qos.durability_service.history_kind")
                    if durability_service_history_kind_str == "KEEP_LAST_HISTORY_QOS":
                        durability_service_history_kind = dds.DDSHistoryKind.KEEP_LAST
                    elif durability_service_history_kind_str == "KEEP_ALL_HISTORY_QOS":
                        durability_service_history_kind = dds.DDSHistoryKind.KEEP_ALL

                    durability_service_max_instances = -1
                    try:
                        durability_service_max_instances = int(prop.getProperty(
                            "topic_qos.durability_service.max_instances"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    durability_service_max_samples = -1
                    try:
                        durability_service_max_samples = int(prop.getProperty(
                            "topic_qos.durability_service.max_samples"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    durability_service_max_samples_per_instance = -1
                    try:
                        durability_service_max_samples_per_instance = int(prop.getProperty(
                            "topic_qos.durability_service.max_samples_per_instance"))
                    except ValueError as error:
                        pass
                        # self._rtcout.RTC_ERROR(error)

                    durability_service_service_cleanup_delay = self.getDuration(
                        prop.getNode("topic_qos.durability_service.service_cleanup_delay"))

                    if durability_service_service_cleanup_delay is None:
                        durability_service_service_cleanup_delay = dds.DDSDuration(
                            0, 0)

                    durability_service_qos_policy = dds.DurabilityServiceQosPolicy(durability_service_service_cleanup_delay,
                                                                                   durability_service_history_kind,
                                                                                   durability_service_history_depth,
                                                                                   durability_service_max_samples,
                                                                                   durability_service_max_instances,
                                                                                   durability_service_max_samples_per_instance)
                    topic_qos = dds.Qos([durability_qos_policy,
                                         deadline_qos_policy,
                                         latency_budget_qos_policy,
                                         liveliness_qos_policy,
                                         reliability_qos_policy,
                                         destinatio_order_qos_policy,
                                         history_qos_policy,
                                         resource_limits_qos_policy,
                                         transport_priority_qos_policy,
                                         lifespan_qos_policy,
                                         ownership_qos_policy,
                                         durability_service_qos_policy])

                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.durability.kind: %s", str(durability_qos_policy.kind))
                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.deadline.period: %lf",
                                           deadline_qos_policy.deadline)
                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.latency_budget.duration: %lf",
                                           latency_budget_qos_policy.duration)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.liveliness.kind: %s", str(liveliness_qos_policy.kind))
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.liveliness.lease_duration: %lf", liveliness_qos_policy.lease_duration)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.reliability.kind: %s", str(reliability_qos_policy.kind))
                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.reliability.max_blocking_time: %lf",
                                           reliability_qos_policy.max_blocking_time)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.destination_order.kind: %s", str(destinatio_order_qos_policy.kind))
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.history.kind: %s", str(history_qos_policy.kind))
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.history.depth: %d", history_qos_policy.depth)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.resource_limits.max_samples: %d", resource_limits_qos_policy.max_samples)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.resource_limits.max_instances: %d", resource_limits_qos_policy.max_instances)
                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.resource_limits.max_samples_per_instance: %d",
                                           resource_limits_qos_policy.max_samples_per_instance)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.transport_priority.value: %d", transport_priority_qos_policy.value)
                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.lifespan.duration: %lf",
                                           lifespan_qos_policy.lifespan)
                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.ownership.kind: %s", str(ownership_qos_policy.kind))

                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.durability_service.history_depth: %d",
                                           durability_service_qos_policy.history_depth)

                    self._rtcout.RTC_DEBUG(
                        "TopicQos setting: topic_qos.durability_service.history_kind: %s", str(durability_service_qos_policy.history_kind))

                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.durability_service.max_instances: %d",
                                           durability_service_qos_policy.max_instances)

                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.durability_service.max_samples: %d",
                                           durability_service_qos_policy.max_samples)

                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.durability_service.max_samples_per_instance: %d",
                                           durability_service_qos_policy.max_samples_per_instance)

                    self._rtcout.RTC_DEBUG("TopicQos setting: topic_qos.durability_service.service_cleanup_delay: %lf",
                                           durability_service_qos_policy.service_cleanup_delay)

                    self._topic[topicname] = geninfo.register_topic(
                        self._domainParticipant, topicname, topic_qos)
                return self._topic[topicname]
            return None

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
    def getDuration(self, prop):
        sec_str = prop.getProperty("sec")
        nanosec_str = prop.getProperty("nanosec")
        if sec_str == "2147483647" and nanosec_str == "2147483647":
            return dds.DDSDuration.infinity()
        try:
            sec = int(sec_str)
            nanosec = int(nanosec_str)
            return dds.DDSDuration(sec=sec, nanosec=nanosec)
        except ValueError as error:
            return None
            # self._rtcout.RTC_ERROR(error)

    ##
    # @if jp
    # @brief Topicオブジェクト取得
    #
    # @param self
    # @param topicname トピック名
    # @return Topicオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param topicname
    # @return
    #
    # @endif

    def getTopic(self, topicname):
        if topicname in self._topic:
            return self._topic[topicname]
        return None

    ##
    # @if jp
    # @brief 初期化
    #
    # @param prop 設定プロパティ
    #
    # @return インスタンス
    #
    # @else
    #
    # @brief
    #
    # @param prop
    #
    # @return
    #
    # @endif

    def init(prop=OpenRTM_aist.Properties()):
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is None:
            manager = OpenSpliceTopicManager()
            manager.start(prop)
        return manager

    instance = staticmethod(init)

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
    # @return
    #
    # @endif

    def instance(prop=OpenRTM_aist.Properties()):
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is None:
            manager = OpenSpliceTopicManager()
            manager.start(prop)
        return manager

    instance = staticmethod(instance)

    ##
    # @if jp
    # @brief OpenSpliceTopicManagerを初期化している場合に終了処理を呼び出す
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
