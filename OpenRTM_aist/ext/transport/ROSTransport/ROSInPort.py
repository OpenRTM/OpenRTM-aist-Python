#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROSInPort.py
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
import rosgraph.xmlrpc
import socket
import threading
import select
try:
    import xmlrpclib
except BaseException:
    import xmlrpc.client as xmlrpclib

from rosgraph.network import read_ros_handshake_header, write_ros_handshake_header
from ROSTopicManager import ROSTopicManager
from ROSTopicManager import PublisherLink
import ROSMessageInfo
import struct
import sys
import os
import time

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO, BytesIO


##
# @if jp
# @class ROSInPort
# @brief ROS Subscriberに対応するクラス
# InPortProviderオブジェクトとして使用する
#
# @else
# @class ROSInPort
# @brief
#
#
# @endif
class ROSInPort(OpenRTM_aist.InPortProvider):
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
    # ポートプロパティに以下の項目を設定する。
    #  - インターフェースタイプ : ros
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
        self.setInterfaceType("ros")

        self._profile = None
        self._listeners = None

        self._client = None

        self._topic = "chatter"
        self._callerid = "/rtcomp"
        self._messageType = "ros:std_msgs/Float32"
        self._roscorehost = ""
        self._roscoreport = ""

        self._tcp_connecters = []
        self._con_mutex = threading.RLock()

        self._mutex = threading.RLock()
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("ROSInPort")

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
        if self._client is not None:
            self._rtcout.RTC_PARANOID("unregister Subscriber()")
            try:
                ret, _, __ = self._client.unregisterSubscriber(
                    self._callerid, self._topic, self._topicmgr.getURI())
                if ret != 1:
                    self._rtcout.RTC_ERROR("unregister subscriber error")
            except xmlrpclib.Fault as err:
                self._rtcout.RTC_ERROR("XML-RPC Error:%s", err.faultString)

        if self._topicmgr is not None:
            self._rtcout.RTC_VERBOSE("remove subscriber")
            self._topicmgr.removeSubscriber(self)

        guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
        for connector in self._tcp_connecters:
            try:
                self._rtcout.RTC_VERBOSE("connection close")
                self._topicmgr.removePublisherLink(connector)
            except BaseException:
                self._rtcout.RTC_ERROR("socket shutdown error")

    ##
    # @if jp
    # @brief 接続済みのソケットを終了させる
    #
    # @param self
    # @param uri ソケットの接続先のURI
    #
    # @else
    # @brief
    #
    # @param self
    # @param uri
    #
    # @endif
    #
    def deleteSocket(self, sock):
        guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
        for con in self._tcp_connecters[:]:
            try:
                if con.getConnection() == sock:
                    self._rtcout.RTC_VERBOSE("close socket")
                self._tcp_connecters.remove(con)
            except BaseException:
                self._rtcout.RTC_ERROR("close socket error")

    ##
    # @if jp
    # @brief 初期化
    #
    # @param self
    # @param prop 接続設定
    # marshaling_type シリアライザの種類 デフォルト：ROSFloat32
    # topic トピック名 デフォルト chatter
    # roscore_host roscoreのホスト名 デフォルト：localhost
    # roscore_port roscoreのポート番号 デフォルト：11311
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

        self._topicmgr = ROSTopicManager.instance()
        if self._topicmgr.existSubscriber(self):
            self._rtcout.RTC_VERBOSE("Subscriber already exists.")
            return

        self._messageType = prop.getProperty(
            "marshaling_type", "ros:std_msgs/Float32")
        self._topic = prop.getProperty("ros.topic", "chatter")
        self._topic = "/" + self._topic
        self._roscorehost = prop.getProperty("ros.roscore.host")
        self._roscoreport = prop.getProperty("ros.roscore.port")

        if not self._roscorehost and not self._roscoreport:
            self._rtcout.RTC_VERBOSE(
                "Get the IP address and port number of ros master from environment variable %s.",
                ROSInPort.ROS_MASTER_URI)
            env = os.getenv(ROSInPort.ROS_MASTER_URI)
            if env:
                self._rtcout.RTC_VERBOSE("$%s: %s", (ROSInPort.ROS_MASTER_URI, env))
                env = env.replace("http://","")
                env = env.replace("https://","")
                envsplit = env.split(":")
                self._roscorehost = envsplit[0]
                if len(envsplit) >= 2:
                    self._roscoreport = envsplit[1]

        if not self._roscorehost:
            self._roscorehost = ROSInPort.ROS_DEFAULT_MASTER_ADDRESS

        if not self._roscoreport:
            self._roscoreport = ROSInPort.ROS_DEFAULT_MASTER_PORT


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

        factory = ROSMessageInfo.ROSMessageInfoList.instance()
        info = factory.getInfo(self._messageType)
        if info:
            info_type = info.datatype()
        else:
            self._rtcout.RTC_ERROR("can not found %s", self._messageType)
            return

        self._rtcout.RTC_VERBOSE("caller id: %s", self._callerid)

        self._topicmgr.addSubscriber(self)

        self._client = xmlrpclib.ServerProxy(
            'http://' + self._roscorehost + ":" + self._roscoreport)

        try:
            _, __, val = self._client.registerSubscriber(
                self._callerid, self._topic, info_type, self._topicmgr.getURI())
        except xmlrpclib.Fault as err:
            self._rtcout.RTC_ERROR("XML-RPC ERROR: %s", err.faultString)
            return
        self.connect(self._callerid, self._topic, val)

    ##
    # @if jp
    # @brief publisherと接続
    #
    # @param self
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param publishers publisherのURIのリスト
    #
    # @else
    # @brief
    #
    # @param self
    # @param caller_id
    # @param topic
    # @param publishers
    #
    # @endif
    #
    def connect(self, caller_id, topic, publishers):
        self._rtcout.RTC_VERBOSE("connect()")

        if topic != self._topic:
            self._rtcout.RTC_INFO(
                "Topic name is not match(%s:%s)", (topic, self._topic))
            return

        for uri in publishers:
            pub = PublisherLink(caller_id=caller_id,
                                topic=topic, xmlrpc_uri=uri)

            guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
            if pub in self._tcp_connecters:
                continue
            del guard_con

            self._rtcout.RTC_PARANOID(
                "connectTCP(%s, %s, %s)", (caller_id, topic, uri))
            try:
                pub = xmlrpclib.ServerProxy(uri)
                ret, message, result = pub.requestTopic(
                    self._callerid, topic, [['TCPROS']])
            except BaseException:
                self._rtcout.RTC_ERROR("Failed connect %s", uri)
                continue

            if ret == -1:
                self._rtcout.RTC_WARN("requestTopic error: %s", message)
                continue
            elif ret == 0:
                self._rtcout.RTC_WARN("requestTopic error: %s", message)
                continue
            else:
                _, dest_addr, dest_port = result
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPCNT, 9)
                sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPIDLE, 60)
                sock.setsockopt(socket.SOL_TCP, socket.TCP_KEEPINTVL, 10)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                sock.settimeout(60.0)
                sock.connect((dest_addr, dest_port))

                fileno = sock.fileno()
                if hasattr(select, 'poll'):
                    poller = select.poll()
                    poller.register(fileno, select.POLLOUT)
                    ready = False

                    while not ready:
                        events = poller.poll()
                        for _, flag in events:
                            if flag & select.POLLOUT:
                                ready = True
                else:
                    ready = None
                    while not ready:
                        try:
                            _, ready, _ = select.select([], [fileno], [])
                        except ValueError:
                            self._rtcout.RTC_ERROR("ValueError")
                            return

                self._topicmgr = ROSTopicManager.instance()
                listener = SubListener(self, sock)
                task = threading.Thread(target=listener.recieve, args=())
                self._topicmgr.addPublisherLink(
                    sock, caller_id, topic, uri, listener, task)
                pub = self._topicmgr.getPublisherLink(sock)
                if pub is not None:
                    guard_con = OpenRTM_aist.Guard.ScopedLock(self._con_mutex)
                    self._tcp_connecters.append(pub)
                    del guard_con

                factory = ROSMessageInfo.ROSMessageInfoList.instance()
                info = factory.getInfo(self._messageType)
                if(info):
                    info_type = info.datatype()
                    info_md5sum = info.md5sum()
                    info_message_definition = info.message_definition()
                else:
                    self._rtcout.RTC_ERROR(
                        "Can not found %s", self._messageType)

                sock.setblocking(1)
                fields = {'topic': topic,
                          'message_definition': info_message_definition,
                          'tcp_nodelay': '0',
                          'md5sum': info_md5sum,
                          'type': info_type,
                          'callerid': self._callerid}

                try:
                    write_ros_handshake_header(sock, fields)
                except rosgraph.network.ROSHandshakeException:
                    self._rtcout.RTC_ERROR("write ROS handshake header")
                    continue
                if sys.version_info[0] == 3:
                    read_buff = BytesIO()
                else:
                    read_buff = StringIO()
                sock.setblocking(1)

                try:
                    read_ros_handshake_header(sock, read_buff, 65536)
                except rosgraph.network.ROSHandshakeException:
                    self._rtcout.RTC_ERROR("read ROS handshake header")
                    continue

                self._rtcout.RTC_VERBOSE("Subscriber Listener thread start")

                task.start()

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
            self._rtcout.RTC_PARANOID("ROSInPort.put()")
            if not self._connector:
                self.onReceiverError(data)
                return

            self._rtcout.RTC_PARANOID("received data size: %d", len(data))

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
    # @brief ノード名の取得
    #
    # @return ノード名
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #
    def getTopic(self):
        self._rtcout.RTC_VERBOSE("getTopic")
        return self._topic

    ##
    # @if jp
    # @brief 受信データの統計情報の取得
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
        return [self._topic, stats]

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
# @class SubListener
# @brief ROS Subscriberのデータ受信時のリスナ
#
#
# @else
# @class SubListener
# @brief
#
#
# @endif


class SubListener:
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # @param self
    # @param sub ROSInPort
    # @param sock ソケット
    # @param uri 接続先のURI
    #
    # @else
    # @brief Constructor
    #
    # @param self
    # @param sub
    # @param sock
    # @param uri
    #
    # @endif
    #
    def __init__(self, sub, sock):
        self._sub = sub
        self._sock = sock
        self._shutdown = False
        self._stat_bytes = 0
        self._stat_num_msg = 0

    ##
    # @if jp
    # @brief 受信データ量(bytes)を取得する
    #
    # @param self
    # @retuen 受信データ量
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #
    def getStatBytes(self):
        return self._stat_bytes

    ##
    # @if jp
    # @brief 受信回数を取得する
    #
    # @param self
    # @retuen 受信回数
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #
    def getStatNumMsg(self):
        return self._stat_num_msg

    ##
    # @if jp
    # @brief 終了処理開始
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

    def shutdown(self):
        self._shutdown = True

    ##
    # @if jp
    # @brief 受信処理
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
    def recieve(self):
        buff_size = 65536
        start = 0
        size = -1
        if sys.version_info[0] == 3:
            b = BytesIO()
        else:
            b = StringIO()
        self._sock.setblocking(True)
        while not self._shutdown:
            try:
                btell = b.tell()
                pos = start
                left = btell - pos
                if left > 4:
                    b.seek(pos)
                    if size < 0 and btell >= 4:
                        (size,) = struct.unpack('<I', b.read(4))
                        start += 4
                        pos = start
                    if size > 0:
                        if left >= size:
                            start = 0
                            b.seek(start)
                            data = b.read(size+4)
                            self._sub.put(data)
                            b.seek(start)
                            pos += size
                            size = -1
                        if btell == pos:
                            b.seek(start)
                            b.truncate(start)
                        elif pos != start:
                            b.seek(pos)
                            leftovers = b.read(btell-pos)
                            b.truncate(start + len(leftovers))
                            b.seek(start)
                            b.write(leftovers)
                        else:
                            b.seek(btell)
                if b.tell() <= size+4:
                    d = self._sock.recv(buff_size)
                    if d:
                        b.write(d)
                        self._stat_bytes += len(d)
                        self._stat_num_msg += 1
                    else:
                        raise BaseException
            except BaseException:
                self._sub.deleteSocket(self._sock)
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
def ROSInPortInit():
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory("ros",
                       ROSInPort)
