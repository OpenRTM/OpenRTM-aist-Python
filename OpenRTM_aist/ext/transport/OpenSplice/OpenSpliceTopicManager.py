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
        self._qosProfile = None
        self._domainParticipant = None
        self._topic = {}
        self._info = {}

        #mgr = OpenRTM_aist.Manager.instance()
        # mgr.addManagerActionListener(ManagerActionListener(self))
        #self._rtcout = mgr.getLogbuf("OpenSpliceTopicManager")

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

    def start(self, qosxml, qosprofile):
        if qosxml and qosprofile:
            self._qosProfile = dds.QosProvider(qosxml, qosprofile)
            self._domainParticipant = dds.DomainParticipant(
                qos=self._qosProfile.get_participant_qos())
            self._publisher = self._domainParticipant.create_publisher(
                qos=self._qosProfile.get_publisher_qos())
            self._subscriber = self._domainParticipant.create_subscriber(
                qos=self._qosProfile.get_subscriber_qos())
        else:
            self._domainParticipant = dds.DomainParticipant()
            self._publisher = self._domainParticipant.create_publisher()
            self._subscriber = self._domainParticipant.create_subscriber()

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
    def createWriter(self, topic):
        global mutex
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._qosProfile:
            return self._publisher.create_datawriter(
                topic, self._qosProfile.get_writer_qos())
        else:
            writer_qos = dds.Qos([dds.DurabilityQosPolicy(dds.DDSDurabilityKind.TRANSIENT),
                                  dds.DeadlineQosPolicy(dds.DDSDuration(500)),
                                  dds.LatencyBudgetQosPolicy(
                                      dds.DDSDuration(3000)),
                                  dds.LivelinessQosPolicy(
                dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT),
                dds.ReliabilityQosPolicy(
                dds.DDSReliabilityKind.RELIABLE, dds.DDSDuration.infinity()),
                dds.DestinationOrderQosPolicy(
                dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP),
                dds.HistoryQosPolicy(
                                      dds.DDSHistoryKind.KEEP_ALL),
                dds.ResourceLimitsQosPolicy(10, 10, 10),
                dds.TransportPriorityQosPolicy(700),
                dds.LifespanQosPolicy(
                                      dds.DDSDuration(10, 500)),
                dds.OwnershipQosPolicy(
                                      dds.DDSOwnershipKind.EXCLUSIVE),
                dds.OwnershipStrengthQosPolicy(100),
                dds.WriterDataLifecycleQosPolicy(False)
            ])
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
    def createReader(self, topic, listener):
        global mutex
        guard = OpenRTM_aist.ScopedLock(mutex)
        if self._qosProfile:
            return self._subscriber.create_datareader(
                topic, self._qosProfile.get_reader_qos(), listener)
        else:
            reader_qos = dds.Qos([dds.DurabilityQosPolicy(dds.DDSDurabilityKind.TRANSIENT),
                                  dds.DeadlineQosPolicy(dds.DDSDuration(500)),
                                  dds.LatencyBudgetQosPolicy(
                                      dds.DDSDuration(3000)),
                                  dds.LivelinessQosPolicy(
                dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT),
                dds.ReliabilityQosPolicy(
                dds.DDSReliabilityKind.RELIABLE, dds.DDSDuration.infinity()),
                dds.DestinationOrderQosPolicy(
                dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP),
                dds.HistoryQosPolicy(
                                      dds.DDSHistoryKind.KEEP_ALL),
                dds.ResourceLimitsQosPolicy(10, 10, 10),
                dds.OwnershipQosPolicy(
                                      dds.DDSOwnershipKind.EXCLUSIVE),
                dds.TimeBasedFilterQosPolicy(
                                      dds.DDSDuration(2, 500)),
                dds.ReaderDataLifecycleQosPolicy(
                                      dds.DDSDuration(3), dds.DDSDuration(5))
            ])
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
    def createTopic(self, datatype, topicname):
        global mutex
        guard = OpenRTM_aist.ScopedLock(mutex)
        if topicname in self._topic:
            return self._topic[topicname]
        else:
            geninfo = self.genInfo(datatype)
            if geninfo:
                if self._qosProfile:
                    self._topic[topicname] = geninfo.register_topic(
                        self._domainParticipant, topicname, self._qosProfile.get_topic_qos())
                else:
                    topic_qos = dds.Qos([dds.DurabilityQosPolicy(dds.DDSDurabilityKind.TRANSIENT),
                                         dds.DurabilityServiceQosPolicy(dds.DDSDuration(
                                             2, 500), dds.DDSHistoryKind.KEEP_ALL, 2, 100, 100, 100),
                                         dds.DeadlineQosPolicy(
                                             dds.DDSDuration(500)),
                                         dds.LatencyBudgetQosPolicy(
                                             dds.DDSDuration(3000)),
                                         dds.LivelinessQosPolicy(
                        dds.DDSLivelinessKind.MANUAL_BY_PARTICIPANT),
                        dds.ReliabilityQosPolicy(
                        dds.DDSReliabilityKind.RELIABLE, dds.DDSDuration.infinity()),
                        dds.DestinationOrderQosPolicy(
                        dds.DDSDestinationOrderKind.BY_SOURCE_TIMESTAMP),
                        dds.HistoryQosPolicy(
                                             dds.DDSHistoryKind.KEEP_ALL),
                        dds.ResourceLimitsQosPolicy(
                                             10, 10, 10),
                        dds.TransportPriorityQosPolicy(700),
                        dds.LifespanQosPolicy(
                                             dds.DDSDuration(10, 500)),
                        dds.OwnershipQosPolicy(
                                             dds.DDSOwnershipKind.EXCLUSIVE)
                    ])
                    self._topic[topicname] = geninfo.register_topic(
                        self._domainParticipant, topicname, topic_qos)
                return self._topic[topicname]
            return None

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
    def instance(qosxml="", qosprofile=""):
        global manager
        global mutex

        guard = OpenRTM_aist.ScopedLock(mutex)
        if manager is None:
            manager = OpenSpliceTopicManager()
            manager.start(qosxml, qosprofile)
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
