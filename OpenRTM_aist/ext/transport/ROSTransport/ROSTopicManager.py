#!/usr/bin/env python
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
import time
import socket

try:
  from cStringIO import StringIO
except ImportError:
  from io import StringIO



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
    self._addr = ""
    self._port = 0
    self._shutdownflag = False
    self._thread = None
    self._old_uris = []

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
    self._node = rosgraph.xmlrpc.XmlRpcNode(9000, self)
    self._node.start()
    self._server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self._server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self._server_sock.bind((rosgraph.network.get_bind_address(), self._port))
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
    if not self.existPublisher(publisher):
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
    if not self.existSubscriber(subscriber):
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
    lost_uris = []
    for uri in self._old_uris:
      if not (uri in publishers):
        lost_uris.append(uri)
    


    for subscriber in self._subscribers:
      subscriber.connect(caller_id, topic, publishers)
      for lost_uri in lost_uris:
        subscriber.deleteSocket(lost_uri)
    self._old_uris = publishers[:]

    return 1, "", 0

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
        (client_sock, client_addr) = self._server_sock.accept()
        addr = client_addr[0] + ":" + str(client_addr[1])
        for publisher in self._publishers:
          publisher.connect(client_sock, addr)
      except:
        pass
    
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
    #self._server_sock.shutdown(socket.SHUT_RDWR)
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
      return -1, "Not a publisher of [%s]"%topic, []
    for protocol in protocols:
      protocol_id = protocol[0]
      if protocol_id == "TCPROS":
        addr = rosgraph.network.get_host_name()
        port = self._port
        return 1, "ready on %s:%s"%(addr, port), ["TCPROS", addr, port]
    return 0, "no supported protocol implementations", []

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
    for i in range(0,10):
      if self._node.uri:
        return self._node.uri
      time.sleep(1)
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
    
    guard = OpenRTM_aist.ScopedLock(mutex)
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
    
    guard = OpenRTM_aist.ScopedLock(mutex)
    if manager is not None:
      manager.shutdown()

    manager = None
  
  shutdown_global = staticmethod(shutdown_global)