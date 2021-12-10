#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROSOutPort.py
# @brief ROS OutPort class
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
from ROSTopicManager import ROSTopicManager
import ROSMessageInfo
try:
    import xmlrpclib
except BaseException:
    import xmlrpc.client as xmlrpclib
from rosgraph.network import write_ros_handshake_header
import rosgraph.network
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO
import socket
import select
import time
import sys
import threading
import os
import time


##
# @if jp
# @class ROSOutPort
# @brief ROS Publisherに対応するクラス
# InPortConsumerオブジェクトとして使用する
#
# @else
# @class ROSOutPort
# @brief
#
#
# @endif
class ROSOutPort(OpenRTM_aist.InPortConsumer):
    """
    """
    ROS_MASTER_URI = "ROS_MASTER_URI"
    ROS_DEFAULT_MASTER_ADDRESS = "localhost"
    ROS_DEFAULT_MASTER_PORT = "11311"
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
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("ROSOutPort")
        self._properties = None
        self._callerid = "/rtcomp"
        self._messageType = "ros:std_msgs/Float32"
        self._topic = "chatter"
        self._roscorehost = ""
        self._roscoreport = ""
        self._tcp_connecters = []
        self._con_mutex = threading.RLock()
        self._message_data_sent = 0

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
        self._rtcout.RTC_PARANOID("~ROSOutPort()")

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    #
    # @param self
    # @param prop 接続設定
    # marshaling_type シリアライザの種類 デフォルト：ROSFloat32
    # topic トピック名 デフォルト chatter
    # roscore_host roscoreのホスト名 デフォルト：localhost
    # roscore_port roscoreのポート番号 デフォルト：11311
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

        self._topicmgr = ROSTopicManager.instance()
        if self._topicmgr.existPublisher(self):
            self._rtcout.RTC_VERBOSE("Publisher already exists.")
            return

        self._properties = prop

        self._messageType = prop.getProperty(
            "marshaling_type", "ros:std_msgs/Float32")
        self._topic = prop.getProperty("ros.topic", "chatter")
        self._topic = "/" + self._topic
        self._roscorehost = prop.getProperty("ros.roscore.host")
        self._roscoreport = prop.getProperty("ros.roscore.port")

        if not self._roscorehost and not self._roscoreport:
            self._rtcout.RTC_VERBOSE(
                "Get the IP address and port number of ros master from environment variable %s.",
                ROSOutPort.ROS_MASTER_URI)
            env = os.getenv(ROSOutPort.ROS_MASTER_URI)
            if env:
                self._rtcout.RTC_VERBOSE(
                    "$%s: %s", (ROSOutPort.ROS_MASTER_URI, env))
                env = env.replace("http://", "")
                env = env.replace("https://", "")
                envsplit = env.split(":")
                self._roscorehost = envsplit[0]
                if len(envsplit) >= 2:
                    self._roscoreport = envsplit[1]

        if not self._roscorehost:
            self._roscorehost = ROSOutPort.ROS_DEFAULT_MASTER_ADDRESS

        if not self._roscoreport:
            self._roscoreport = ROSOutPort.ROS_DEFAULT_MASTER_PORT

        self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)
        self._rtcout.RTC_VERBOSE(
            "roscore address: %s:%s",
            (self._roscorehost,
             self._roscoreport))

        self._callerid = "/" + prop.getProperty("ros.node.name", "rtcomp")
        if OpenRTM_aist.toBool(prop.getProperty(
                "ros.node.anonymous"), "YES", "NO", False):
            self._callerid = self._callerid + "_" + \
                str(os.getpid()) + "_" + str(int(time.time()*1000))

        self._rtcout.RTC_VERBOSE("caller id: %s", self._callerid)

        self._topicmgr.addPublisher(self)

        self._client = xmlrpclib.ServerProxy(
            'http://' + self._roscorehost + ":" + self._roscoreport)
        messageType = "std_msgs/Float32"
        messageTypeList = self._messageType.split(":")
        if len(messageType) >= 2:
            messageType = messageTypeList[1]

        try:
            self._client.registerPublisher(
                self._callerid,
                self._topic,
                messageType,
                self._topicmgr.getURI())
        except xmlrpclib.Fault as err:
            self._rtcout.RTC_ERROR("XML-RPC ERROR: %s", err.faultString)

    ##
    # @if jp
    # @brief トピック名取得
    #
    #
    # @return トピック名
    #
    # @else
    # @brief get topic name
    #
    # @return topic name
    #
    # @endif
    #
    def getTopic(self):
        self._rtcout.RTC_PARANOID("getTopic()")
        return self._topic

    ##
    # @if jp
    # @brief Subscriberとの接続
    #
    #
    # @param self
    # @param client_sock ソケット
    # @param addr 接続先のURI
    #
    # @else
    # @brief
    #
    # @param self
    # @param client_sock
    # @param addr
    #
    # @endif
    #
    def connect(self, client_sock, header):
        self._rtcout.RTC_PARANOID("connect()")

        topic_name = header['topic']
        md5sum = header['md5sum']
        type_name = header['type']
        caller_id = header['callerid']

        if self._topic != topic_name:
            self._rtcout.RTC_INFO(
                "Topic name is not match(%s:%s)", (topic_name, self._topic))
            return

        self._rtcout.RTC_VERBOSE("Topic:%s", topic_name)
        self._rtcout.RTC_VERBOSE("MD5sum:%s", md5sum)
        self._rtcout.RTC_VERBOSE("Type:%s", type_name)

        factory = ROSMessageInfo.ROSMessageInfoList.instance()
        info = factory.getInfo(self._messageType)

        if info:
            info_type = info.datatype()
            info_md5sum = info.md5sum()
            info_message_definition = info.message_definition()
        else:
            self._rtcout.RTC_ERROR("can not found %s", self._messageType)
            return

        if info_type != type_name:
            self._rtcout.RTC_WARN(
                "type name in not match(%s:%s)", (info_type, type_name))
            return
        if info_md5sum != md5sum:
            self._rtcout.RTC_WARN(
                "MD5sum in not match(%s:%s)", (info_md5sum, md5sum))
            return

        fields = {'topic': topic_name,
                  'message_definition': info_message_definition,
                  'tcp_nodelay': '0',
                  'md5sum': info_md5sum,
                  'type': info_type,
                  'callerid': self._callerid}

        try:
            stat_bytes = write_ros_handshake_header(client_sock, fields)
        except rosgraph.network.ROSHandshakeException:
            self._rtcout.RTC_ERROR("write ROS handshake exception")
            return

        self._topicmgr = ROSTopicManager.instance()
        sub = self._topicmgr.getSubscriberLink(client_sock)
        if sub is not None:
            guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
            sub.setTopic(topic_name)
            sub.setCallerID(caller_id)
            sub.setStatBytes(stat_bytes)
            self._tcp_connecters.append(sub)

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

        ret = self.PORT_OK
        self._message_data_sent += len(data)
        guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
        for connector in self._tcp_connecters[:]:
            try:
                connector.sendall(data)
            except BaseException:
                self._rtcout.RTC_ERROR("send error")
                self._topicmgr.removeSubscriberLink(connector.getConnection())
                # connector.shutdown(socket.SHUT_RDWR)

                ret = self.CONNECTION_LOST
                self._tcp_connecters.remove(connector)
        return ret

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
        if self._client is not None:
            try:
                ret, _, __ = self._client.unregisterPublisher(
                    self._callerid, self._topic, self._topicmgr.getURI())
                if ret != 1:
                    self._rtcout.RTC_ERROR("unregister publisher error")
            except xmlrpclib.Fault as err:
                self._rtcout.RTC_ERROR("XML-RPC Error:%s", err.faultString)
        if self._topicmgr is not None:
            self._rtcout.RTC_VERBOSE("remove publisher")
            self._topicmgr.removePublisher(self)

        guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
        for connector in self._tcp_connecters:
            try:
                self._rtcout.RTC_VERBOSE("connection close")
                self._topicmgr.removeSubscriberLink(connector.getConnection())
            except BaseException:
                self._rtcout.RTC_ERROR("socket shutdown error")

    ##
    # @if jp
    # @brief 送信データの統計情報の取得
    #
    # @return データ
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #

    def getStats(self):
        self._rtcout.RTC_VERBOSE("getStats")
        stats = []
        for connector in self._tcp_connecters:
            stats.append(connector.getStats())
        return [self._topic, self._message_data_sent, stats]

    ##
    # @if jp
    # @brief メッセージ型の取得
    #
    # @return メッセージ型
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #
    def datatype(self):
        self._rtcout.RTC_VERBOSE("datatype")
        return self._messageType


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


def ROSOutPortInit():
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("ros",
                       ROSOutPort)
