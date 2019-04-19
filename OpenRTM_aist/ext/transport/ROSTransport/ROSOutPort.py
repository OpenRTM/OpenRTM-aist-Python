#!/usr/bin/env python
# -*- coding: euc-jp -*-

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
except:
  import xmlrpc.client as xmlrpclib
from rosgraph.network import read_ros_handshake_header, write_ros_handshake_header
import rosgraph.network
try:
  from cStringIO import StringIO
except ImportError:
  from io import StringIO, BytesIO
import socket
import select
import time
import sys



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
    self._callerid = ""
    self._messageType = "ROSFloat32"
    self._topic = "chatter"
    self._roscorehost = "localhost"
    self._roscoreport = "11311"
    self._tcp_connecters = {}


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
    

    if len(prop.propertyNames()) == 0:
      self._rtcout.RTC_DEBUG("Property is empty.")
      return
    
    self._topicmgr = ROSTopicManager.instance()
    if self._topicmgr.existPublisher(self):
      self._rtcout.RTC_VERBOSE("Publisher already exists.")
      return

    

    self._properties = prop

    self._messageType = prop.getProperty("marshaling_type", "ROSFloat32")
    self._topic = prop.getProperty("topic", "chatter")
    self._topic = "/"+self._topic
    self._roscorehost = prop.getProperty("roscore_host", "localhost")
    self._roscoreport = prop.getProperty("roscore_port", "11311")

    
    self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)
    self._rtcout.RTC_VERBOSE("roscore address: %s:%s", (self._roscorehost, self._roscoreport))

    if not self._callerid:
      self._callerid = str(OpenRTM_aist.uuid1())

    self._rtcout.RTC_VERBOSE("caller id: %s", self._callerid)

    self._topicmgr.addPublisher(self)

    self._client = xmlrpclib.ServerProxy('http://'+self._roscorehost+":"+self._roscoreport)
    try:
      self._client.registerPublisher(self._callerid, self._topic, 'std_msgs/Float32', self._topicmgr.getURI())
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
  def connect(self, client_sock, addr):
    self._rtcout.RTC_PARANOID("connect()")
    if addr in self._tcp_connecters:
      self._rtcout.RTC_DEBUG("%s already exist", addr)
      return
    
    try:
      if sys.version_info[0] == 3:
        header = read_ros_handshake_header(client_sock, BytesIO(), 65536)
      else:
        header = read_ros_handshake_header(client_sock, StringIO(), 65536)
    except rosgraph.network.ROSHandshakeException:
      self._rtcout.RTC_DEBUG("read ROS handshake exception")
      return
    except:
      print(traceback.format_exc()) 

    topic_name = header['topic']
    md5sum = header['md5sum']
    type_name = header['type']

    self._rtcout.RTC_VERBOSE("Topic:%s", topic_name)
    self._rtcout.RTC_VERBOSE("MD5sum:%s", md5sum)
    self._rtcout.RTC_VERBOSE("Type:%s", type_name)

    factory = ROSMessageInfo.ROSMessageInfoFactory.instance()
    info = factory.createObject(self._messageType)

    if info:
      info_type = info.datatype()
      info_md5sum = info.md5sum()
      info_message_definition = info.message_definition()
      factory.deleteObject(info)
    else:
      self._rtcout.RTC_ERROR("can not found %s", self._messageType)
      return
    
    if info_type != type_name:
      self._rtcout.RTC_WARN("topic name in not match(%s:%s)",(info_type, type_name))
      return
    if info_md5sum != md5sum:
      self._rtcout.RTC_WARN("MD5sum in not match(%s:%s)",(info_md5sum, md5sum))
      return

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
          self._rtcout.RTC_ERROR("ValueError")
          return
    client_sock.setblocking(1)
    fields = {'topic': topic_name,
              'message_definition': info_message_definition,
              'tcp_nodelay': '0',
              'md5sum': info_md5sum,
              'type': info_type,
              'callerid': header['callerid']}
    try:
      write_ros_handshake_header(client_sock, fields)
    except rosgraph.network.ROSHandshakeException:
      self._rtcout.RTC_DEBUG("write ROS handshake exception")
      return
    if poller:
      poller.unregister(fileno)


    self._tcp_connecters[addr] = client_sock
    
    

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
    for k, connector in self._tcp_connecters.items():
      try:
        connector.sendall(data)
      except:
        self._rtcout.RTC_ERROR("send error")
        #connector.shutdown(socket.SHUT_RDWR)
        connector.close()
        ret = self.CONNECTION_LOST
        del self._tcp_connecters[k]
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
        ret, _, __ = self._client.unregisterPublisher(self._callerid, self._topic, self._topicmgr.getURI())
        if ret != 1:
          self._rtcout.RTC_ERROR("unregister publisher error")
      except xmlrpclib.Fault as err:
        self._rtcout.RTC_ERROR("XML-RPC Error:%s", err.faultString)
    if self._topicmgr is not None:
      self._rtcout.RTC_VERBOSE("remove publisher")
      self._topicmgr.removePublisher(self)

    for k, connector in self._tcp_connecters.items():
      try:
        self._rtcout.RTC_VERBOSE("connection close")
        connector.shutdown(socket.SHUT_RDWR)
        connector.close()
      except:
        self._rtcout.RTC_ERROR("socket shutdown error")




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
                     ROSOutPort,
                     OpenRTM_aist.Delete)

