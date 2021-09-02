#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROSTopicManager.py
# @brief ROS Topic Manager class
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
import threading
import rosgraph.xmlrpc
from rosgraph.network import read_ros_handshake_header
import time
import socket
import select
import sys
import os

try:
    from cStringIO import StringIO
except ImportError:
    from io import BytesIO


manager = None
mutex = threading.RLock()

##
# @if jp
# @class ROSTopicManager
# @brief ROSトピックを管理するクラス
#
#
# @else
# @class ROSTopicManager
# @brief
#
#
# @endif


class ROSTopicManager(rosgraph.xmlrpc.XmlRpcHandler):
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
        super(ROSTopicManager, self).__init__()
        self._node = None
        self._server_sock = None
        self._publishers = []
        self._subscribers = []
        self._pub_mutex = threading.RLock()
        self._sub_mutex = threading.RLock()
        self._addr = ""
        self._port = 0
        self._shutdownflag = False
        self._thread = None
        self._tcp_pub_connecters = []
        self._tcp_sub_connecters = []
        self._publink_mutex = threading.RLock()
        self._sublink_mutex = threading.RLock()
        self._subnum = 0
        self._pubnum = 0

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
    # @brief トピックマネージャ開始
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
    def start(self):
        self._node = rosgraph.xmlrpc.XmlRpcNode(self._port, self)
        self._node.start()
        self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_sock.bind(
            (rosgraph.network.get_bind_address(), self._port))
        (self._addr, self._port) = self._server_sock.getsockname()[0:2]
        self._server_sock.listen(5)
        self._thread = threading.Thread(target=self.run, args=())
        self._thread.daemon = True
        self._thread.start()

    ##
    # @if jp
    # @brief ROSOutPort登録
    #
    # @param self
    # @param publisher 登録対象のROSOutPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param publisher
    #
    # @endif
    def addPublisher(self, publisher):
        guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
        if self._publishers.count(publisher) == 0:
            self._publishers.append(publisher)

    ##
    # @if jp
    # @brief ROSInPort登録
    #
    # @param self
    # @param subscriber 登録対象のROSInPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param subscriber
    #
    # @endif
    def addSubscriber(self, subscriber):
        guard_sub = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
        if self._subscribers.count(subscriber) == 0:
            self._subscribers.append(subscriber)

    ##
    # @if jp
    # @brief ROSOutPort削除
    #
    # @param self
    # @param publisher 削除対象のROSOutPort
    # @return True：削除成功、False：削除対象が存在しない
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param publisher
    # @return
    #
    # @endif

    def removePublisher(self, publisher):
        try:
            guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
            self._publishers.remove(publisher)
            return True
        except ValueError:
            return False

    ##
    # @if jp
    # @brief ROSInPort削除
    #
    # @param self
    # @param subscriber 削除対象のROSInPort
    # @return True：削除成功、False：削除対象が存在しない
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param subscriber
    # @return
    #
    # @endif
    def removeSubscriber(self, subscriber):
        try:
            guard_sub = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
            self._subscribers.remove(subscriber)
            return True
        except ValueError:
            return False

    ##
    # @if jp
    # @brief ROSOutPortが登録済みかの確認
    #
    # @param self
    # @param publisher ROSOutPort
    # @return True：登録済み、False：未登録
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param publisher
    # @return
    #
    # @endif
    def existPublisher(self, publisher):
        guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
        if self._publishers.count(publisher) > 0:
            return True
        else:
            return False

    ##
    # @if jp
    # @brief ROSInPortが登録済みかの確認
    #
    # @param self
    # @param subscriber ROSInPort
    # @return True：登録済み、False：未登録
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param subscriber
    # @return
    #
    # @endif
    def existSubscriber(self, subscriber):
        guard_sub = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
        if self._subscribers.count(subscriber) > 0:
            return True
        else:
            return False

    ##
    # @if jp
    # @brief publisherUpdateコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param publishers publisher一覧
    # @return ret, msg, value
    # ret：リターンコード(1：問題なし)
    # msg：メッセージ
    # value：値
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @param topic
    # @param publishers
    # @return
    #
    # @endif
    def publisherUpdate(self, caller_id, topic, publishers):
        new_con = []
        old_con = []
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        for con in self._tcp_pub_connecters:
            if con.getCallerID() == caller_id and con.getTopic() == topic:
                old_con.append(con)
        del guard_pl

        for uri in publishers:
            already_connected = False
            guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
            for con in self._tcp_pub_connecters:
                if con.getCallerID() == caller_id and con.getTopic() == topic and con.getURI() == uri:
                    already_connected = True
            del guard_pl

            if not already_connected:
                guard_sub = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
                for sub in self._subscribers:
                    sub.connect(caller_id, topic, [uri])
                del guard_sub
            pub = PublisherLink(caller_id=caller_id,
                                topic=topic, xmlrpc_uri=uri)
            new_con.append(pub)

        for old_ in old_con:
            if old_ not in new_con:
                old_.exit()
                guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
                self._tcp_pub_connecters.remove(old_)
                del guard_pl

        return 1, "", 0

    ##
    # @if jp
    # @brief getPidコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return ret, msg, value
    # ret：リターンコード(1：問題なし)
    # msg：メッセージ
    # value：値
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return
    #
    # @endif

    def getPid(self, caller_id):
        return 1, "", os.getpid()

    ##
    # @if jp
    # @brief TCPソケット受信時の処理関数
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
    def run(self):
        while not self._shutdownflag:
            try:
                (client_sock, _) = self._server_sock.accept()
                self.addSubscriberLink(client_sock)

                if sys.version_info[0] == 3:
                    header = read_ros_handshake_header(
                        client_sock, BytesIO(), 65536)
                else:
                    header = read_ros_handshake_header(
                        client_sock, StringIO(), 65536)

                fileno = client_sock.fileno()
                poller = None
                if hasattr(select, 'poll'):
                    ready = False
                    poller = select.poll()
                    poller.register(fileno, select.POLLOUT)
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
                            print("ValueError")
                            return
                client_sock.setblocking(1)

                guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
                for publisher in self._publishers:
                    publisher.connect(client_sock, header)
                del guard_pub

                if poller:
                    poller.unregister(fileno)

            except rosgraph.network.ROSHandshakeException:
                print("read ROS handshake exception")
            except BaseException:
                print(OpenRTM_aist.Logger.print_exception())

    ##
    # @if jp
    # @brief ソケット、スレッド終了処理
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
        self._shutdownflag = True
        try:
            self._server_sock.shutdown(socket.SHUT_WR)
        except BaseException:
            pass
        self._server_sock.close()
        self._thread.join()
        self._node.shutdown(True)

    ##
    # @if jp
    # @brief requestTopicコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param protocols プロトコル一覧
    # @return ret, msg, value
    # ret：リターンコード(1：問題なし、-1：トピックに対応したPublisherが存在しない、0：それ以外のエラー)
    # msg：メッセージ
    # value：プロトコル、アドレス、ポート番号
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @param topic
    # @param protocols
    # @return
    #
    # @endif

    def requestTopic(self, caller_id, topic, protocols):
        if not self.hasPublisher(topic):
            return -1, "Not a publisher of [%s]" % topic, []
        for protocol in protocols:
            protocol_id = protocol[0]
            if protocol_id == "TCPROS":
                addr = rosgraph.network.get_host_name()
                port = self._port
                return 1, "ready on %s:%s" % (addr, port), [
                    "TCPROS", addr, port]
        return 0, "no supported protocol implementations", []

    ##
    # @if jp
    # @brief getSubscriptionsコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return ret, msg, subs
    # ret：リターンコード(1)
    # msg：メッセージ
    # subs：Subscriber一覧
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return ret, msg, subs
    #
    # @endif
    def getSubscriptions(self, caller_id):
        subs = []
        guard_sub = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
        for subscriber in self._subscribers:
            sub = [subscriber.getTopic(), subscriber.datatype()]
            subs.append(sub)

        return 1, "subscriptions", subs

    ##
    # @if jp
    # @brief getPublicationsコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return ret, msg, pubs
    # ret：リターンコード(1)
    # msg：メッセージ
    # pubs：Publisher一覧
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return ret, msg, pubs
    #
    # @endif
    def getPublications(self, caller_id):
        pubs = []
        guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
        for publisher in self._publishers:
            pub = [publisher.getTopic(), publisher.datatype()]
            pubs.append(pub)

        return 1, "publications", pubs

    ##
    # @if jp
    # @brief getBusStatsコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return
    #
    # @endif
    def getBusStats(self, caller_id):
        pubStats = []
        guard_p = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
        for pub in self._publishers:
            pubStats.append(pub.getStats())
        del guard_p
        subStats = []
        guard_s = OpenRTM_aist.Guard.ScopedLock(self._sub_mutex)
        for sub in self._subscribers:
            subStats.append(sub.getStats())
        del guard_s
        srvStats = []
        stats = [pubStats, subStats, srvStats]
        return 1, "", stats

    ##
    # @if jp
    # @brief getBusInfoコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return ret, msg, info
    # ret：リターンコード(1)
    # msg：メッセージ
    # pubs：コネクタの情報一覧
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return ret, msg, info
    #
    # @endif
    def getBusInfo(self, caller_id):
        info = []
        guard_sl = OpenRTM_aist.Guard.ScopedLock(self._sublink_mutex)
        for con in self._tcp_sub_connecters:
            info.append(con.getInfo())
        del guard_sl

        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        for con in self._tcp_pub_connecters:
            info.append(con.getInfo())
        del guard_pl

        return 1, "bus info", info

    ##
    # @if jp
    # @brief getMasterUriコールバック関数
    #
    # @param self
    # @param caller_id 呼び出しID
    # @return
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @return
    #
    # @endif
    # def getMasterUri(self, caller_id):
    #  return 0, "master URI not set", ""

    ##
    # @if jp
    # @brief 指定トピック名のPublisherが登録されているかを確認
    #
    # @param self
    # @param topic トピック名
    # @return True：存在する、False：存在しない
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
    def hasPublisher(self, topic):
        guard_pub = OpenRTM_aist.Guard.ScopedLock(self._pub_mutex)
        for publisher in self._publishers:
            if publisher.getTopic() == topic:
                return True
        return False

    ##
    # @if jp
    # @brief TCPソケットのURIを取得
    #
    # @param self
    # @return URI
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getURI(self):
        for i in range(0, 10):
            if self._node.uri:
                return self._node.uri
            time.sleep(1)
        return None

    ##
    # @if jp
    # @brief PublisherLinkの一覧を取得
    #
    # @param self
    # @return PublisherLinkの一覧
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getPublisherLinkList(self):
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        return self._tcp_pub_connecters

    ##
    # @if jp
    # @brief SubscriberLinkの一覧を取得
    #
    # @param self
    # @return SubscriberLinkの一覧
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getSubscriberLinkList(self):
        guard_sl = OpenRTM_aist.Guard.ScopedLock(self._sublink_mutex)
        return self._tcp_sub_connecters

    ##
    # @if jp
    # @brief 指定のソケットオブジェクト、呼び出しID、トピック名、URI、
    # 受信処理用関数オブジェクト、受信処理用スレッドオブジェクトからSubscriberLinkオブジェクトを追加する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param xmlrpc_uri 接続先のURI
    # @param listener 受信処理用関数オブジェクト
    # @param task 受信処理用スレッドオブジェクト
    # @return True：追加成功
    #
    # @else
    #
    # @brief
    #
    #
    # @param self
    # @param connection
    # @param caller_id
    # @param topic
    # @param xmlrpc_uri
    # @param listener
    # @param task
    # @return
    #
    # @endif
    def addPublisherLink(self, connection, caller_id, topic, xmlrpc_uri, listener, task):
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        self._tcp_pub_connecters.append(PublisherLink(
            connection, self._pubnum, caller_id, topic, xmlrpc_uri, listener, task))
        self._pubnum += 1
        return True

    ##
    # @if jp
    # @brief 指定のソケットオブジェクトからPublisherLinkオブジェクトを削除する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @return True：削除成功
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connection
    # @return
    #
    # @endif
    def removePublisherLink(self, connection):
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        for con in self._tcp_pub_connecters[:]:
            if con.getConnection() == connection:
                con.exit()
                self._tcp_pub_connecters.remove(con)
                return True
        return False

    ##
    # @if jp
    # @brief 指定の呼び出しID、トピック名、URIのPublisherLinkが存在するかを確認
    #
    # @param self
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param xmlrpc_uri 接続先のURI
    # @return True：存在する
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param caller_id
    # @param topic
    # @param xmlrpc_uri
    # @return
    #
    # @endif
    def existPublisherLink(self, caller_id, topic, xmlrpc_uri):
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        for con in self._tcp_pub_connecters:
            if con.getCallerID() == caller_id and con.getTopic() == topic and con.getURI() == xmlrpc_uri:
                return True
        return False

    ##
    # @if jp
    # @brief 指定のソケットオブジェクトからSubscriberLinkオブジェクトを追加する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @return True：追加成功
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connection
    # @return
    #
    # @endif
    def addSubscriberLink(self, connection):
        guard_sl = OpenRTM_aist.Guard.ScopedLock(self._sublink_mutex)
        self._tcp_sub_connecters.append(
            SubscriberLink(connection, self._subnum))
        self._subnum += 1
        return True

    ##
    # @if jp
    # @brief 指定のソケットオブジェクトからSubscriberLinkオブジェクトを削除する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @return True：削除成功
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connection
    # @return
    #
    # @endif
    def removeSubscriberLink(self, connection):
        guard_sl = OpenRTM_aist.Guard.ScopedLock(self._sublink_mutex)
        for con in self._tcp_sub_connecters[:]:
            if con.getConnection() == connection:
                con.exit()
                self._tcp_sub_connecters.remove(con)
                return True
        return False

    ##
    # @if jp
    # @brief 指定のソケットオブジェクトからPublisherLinkオブジェクトを取得する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @return PublisherLinkオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connection
    # @return
    #
    # @endif
    def getPublisherLink(self, connection):
        guard_pl = OpenRTM_aist.Guard.ScopedLock(self._publink_mutex)
        for con in self._tcp_pub_connecters:
            if con.getConnection() == connection:
                return con
        return None

    ##
    # @if jp
    # @brief 指定のソケットオブジェクトからSubscriberLinkオブジェクトを取得する
    #
    # @param self
    # @param connection ソケットオブジェクト
    # @return SubscriberLinkオブジェクト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connection
    # @return
    #
    # @endif
    def getSubscriberLink(self, connection):
        guard_sl = OpenRTM_aist.Guard.ScopedLock(self._sublink_mutex)
        for con in self._tcp_sub_connecters:
            if con.getConnection() == connection:
                return con
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
    # @return インスタンス
    #
    # @endif
    def instance():
        global manager
        global mutex

        guard = OpenRTM_aist.Guard.ScopedLock(mutex)
        if manager is None:
            manager = ROSTopicManager()
            manager.start()

        return manager

    instance = staticmethod(instance)

    ##
    # @if jp
    # @brief ROSTopicManagerを初期化している場合に終了処理を呼び出す
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

        guard = OpenRTM_aist.Guard.ScopedLock(mutex)
        if manager is not None:
            manager.shutdown()

        manager = None

    shutdown_global = staticmethod(shutdown_global)


##
# @if jp
# @class PublisherLink
# @brief Publisherとの接続情報を管理するクラス
# InPort側で保持する
#
# @else
# @class PublisherLink
# @brief
#
#
# @endif
class PublisherLink:
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param conn ソケットオブジェクト
    # @param num 接続ID
    # @param caller_id 呼び出しID
    # @param topic トピック名
    # @param xmlrpc_uri 接続先のURI
    # @param listener 受信処理用コールバック関数オブジェクト
    # @param task 受信処理用スレッドオブジェクト
    #
    # @else
    # @brief Constructor
    #
    # @param self
    # @param conn
    # @param num
    # @param caller_id
    # @param topic
    # @param xmlrpc_uri
    # @param listener
    # @param task
    #
    # @endif
    def __init__(self, conn=None, num=0, caller_id="", topic="", xmlrpc_uri="", listener=None, task=None):
        self._conn = conn
        self._num = num
        self._caller_id = caller_id
        self._topic = topic
        self._xmlrpc_uri = xmlrpc_uri
        self._listener = listener
        self._task = task
        self._done = False

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
    # @brief ソケットオブジェクトを取得
    #
    #
    # @param self
    # @return ソケットオブジェクト
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getConnection(self):
        return self._conn

    ##
    # @if jp
    # @brief ソケットオブジェクトを設定
    #
    #
    # @param self
    # @param conn ソケットオブジェクト
    #
    # @else
    #
    # @brief self
    # @param conn
    #
    # @endif
    def setConnection(self, conn):
        self._conn = conn

    ##
    # @if jp
    # @brief 接続IDの取得
    #
    #
    # @param self
    # @return 接続ID
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getNum(self):
        return self._num

    ##
    # @if jp
    # @brief 呼び出しIDの取得
    #
    #
    # @param self
    # @return 呼び出しID
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getCallerID(self):
        return self._caller_id

    ##
    # @if jp
    # @brief トピック名を取得
    #
    #
    # @param self
    # @return トピック名
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getTopic(self):
        return self._topic

    ##
    # @if jp
    # @brief 接続先のURIを取得
    #
    #
    # @param self
    # @return URI
    #
    # @else
    #
    # @brief self
    # @return URI
    #
    # @endif
    def getURI(self):
        return self._xmlrpc_uri

    ##
    # @if jp
    # @brief 終了処理
    # ソケット通信を切断する
    # 受信処理用スレッドを終了する
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif

    def exit(self):
        self._conn.shutdown(socket.SHUT_RDWR)
        self._conn.close()
        self._listener.shutdown()
        self._task.join()
        self._done = True

    ##
    # @if jp
    # @brief コネクタの情報取得(getBusInfo用)
    #
    # @return コネクタの情報
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #
    def getInfo(self):
        ret = [self.getNum(), self.getURI(), "i",
               "TCPROS", self.getTopic(), True, self.getTransportInfo()]
        return ret

    ##
    # @if jp
    # @brief コネクタの情報取得(getBusInfo用)
    #
    # @return コネクタの情報
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #

    def getTransportInfo(self):
        _, localport = self._conn.getsockname()
        clientaddress, clientport = self._conn.getpeername()
        ret = "TCPROS connection on port " + \
            str(localport) + " to [" + clientaddress + ":" + \
            str(clientport) + " on socket " + str(self._conn.fileno()) + "]"
        return ret

    ##
    # @if jp
    # @brief コネクタの統計データ取得(getBusStats用)
    #
    # @return コネクタの統計データ
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #

    def getStats(self):
        stat_bytes = self._listener.getStatBytes()
        stat_num_msg = self._listener.getStatNumMsg()
        ret = [self._num, stat_bytes, stat_num_msg, -1, self._done]
        return ret

    ##
    # @if jp
    # @brief 等価比較演算子
    # 呼び出しID、トピック名、URIが一致した場合にTrueを返す
    #
    # @param self
    # @param other 比較対象
    # @return　True：一致
    #
    # @else
    #
    # @brief self
    # @param other
    # @return
    #
    # @endif

    def __eq__(self, other):
        if self._caller_id == other._caller_id and self._topic == other._topic and self._xmlrpc_uri == other._xmlrpc_uri:
            return True
        else:
            return False

##
# @if jp
# @class SubscriberLink
# @brief Subscriberとの接続情報を管理するクラス
# OutPort側で保持する
#
# @else
# @class SubscriberLink
# @brief
#
#
# @endif


class SubscriberLink:
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param conn ソケットオブジェクト
    # @param num 接続ID
    # @param topic トピック名
    # @param caller_id 呼び出しID
    #
    # @else
    # @brief Constructor
    #
    # @param self
    # @param conn
    # @param num
    # @param topic
    # @param caller_id
    #
    # @endif
    def __init__(self, conn=None, num=0, topic="", caller_id=""):
        self._conn = conn
        self._num = num
        self._topic = topic
        self._caller_id = caller_id
        self._stat_bytes = 0
        self._stat_num_msg = 0
        self._done = False

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
    # @brief ソケットオブジェクトを取得する
    #
    #
    # @param self
    # @return ソケットオブジェクト
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getConnection(self):
        return self._conn

    ##
    # @if jp
    # @brief ソケットオブジェクトを設定する
    #
    #
    # @param self
    # @param conn ソケットオブジェクト
    #
    # @else
    #
    # @brief self
    # @param conn
    #
    # @endif
    def setConnection(self, conn):
        self._conn = conn

    ##
    # @if jp
    # @brief 接続IDの取得
    #
    #
    # @param self
    # @return 接続ID
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getNum(self):
        return self._num

    ##
    # @if jp
    # @brief 終了処理
    # ソケット通信を切断する。
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif
    def exit(self):
        self._conn.shutdown(socket.SHUT_RDWR)
        self._conn.close()
        self._done = True

    ##
    # @if jp
    # @brief トピック名を設定する
    #
    #
    # @param self
    # @param topic トピック名
    #
    # @else
    #
    # @brief self
    # @param topic
    #
    # @endif
    def setTopic(self, topic):
        self._topic = topic

    ##
    # @if jp
    # @brief トピック名を取得する
    #
    #
    # @param self
    # @return トピック名
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getTopic(self):
        return self._topic

    ##
    # @if jp
    # @brief 呼び出しIDを設定する
    #
    #
    # @param self
    # @param caller_id 呼び出しID
    #
    # @else
    #
    # @brief self
    # @param caller_id
    #
    # @endif
    def setCallerID(self, caller_id):
        self._caller_id = caller_id

    ##
    # @if jp
    # @brief 呼び出しIDを取得する
    #
    #
    # @param self
    # @return 呼び出しID
    #
    # @else
    #
    # @brief self
    # @return
    #
    # @endif
    def getCallerID(self):
        return self._caller_id

    ##
    # @if jp
    # @brief 過去に送信したデータ量(byte)を設定する
    #
    #
    # @param self
    # @param stat_bytes データ量
    #
    # @else
    #
    # @brief self
    # @param stat_bytes
    #
    # @endif
    def setStatBytes(self, stat_bytes):
        self._stat_bytes = stat_bytes
        self._stat_num_msg = 1

    ##
    # @if jp
    # @brief コネクタの情報取得(getBusInfo用)
    #
    # @return コネクタの情報
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #

    def getInfo(self):
        ret = [self.getNum(), self.getCallerID(), "o",
               "TCPROS", self.getTopic(), True, self.getTransportInfo()]
        return ret

    ##
    # @if jp
    # @brief コネクタの情報取得(getBusInfo用)
    #
    # @return コネクタの情報
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #
    def getTransportInfo(self):
        _, localport = self._conn.getsockname()
        clientaddress, clientport = self._conn.getpeername()
        ret = "TCPROS connection on port " + \
            str(localport) + " to [" + clientaddress + ":" + \
            str(clientport) + " on socket " + str(self._conn.fileno()) + "]"
        return ret

    ##
    # @if jp
    # @brief データ送信
    #
    # @param data データ
    #
    # @else
    # @brief
    #
    # @param data
    #
    # @endif
    #

    def sendall(self, data):
        self._conn.sendall(data)
        self._stat_bytes += len(data)
        self._stat_num_msg += 1

    ##
    # @if jp
    # @brief コネクタの統計データ取得(getBusStats用)
    #
    # @return コネクタの統計データ
    #
    # @else
    # @brief
    #
    # @return
    #
    # @endif
    #

    def getStats(self):
        ret = [self._num, self._stat_bytes, self._stat_num_msg, self._done]
        return ret
