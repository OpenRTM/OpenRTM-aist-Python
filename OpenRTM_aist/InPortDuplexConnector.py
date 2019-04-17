#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
#
# @file InPortDuplexConnector.py
# @brief Bidirectional type connector class
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



import OpenRTM_aist
import threading


##
# @if jp
# @class InPortPushConnector
# @brief InPortPushConnector クラス
#
#
# @since 2.0.0
#
# @else
# @class InPortPushConnector
# @brief InPortPushConnector class
#
#
# @since 2.0.0
#
# @endif
#
class InPortDuplexConnector(OpenRTM_aist.InPortConnector):
  """
  """

  ##
  # @if jp
  # @brief コンストラクタ
  #
  # @param info ConnectorInfo
  # @param provider InPortProvider
  # @param listeners ConnectorListeners 型のリスナオブジェクトリスト
  # @param buffer CdrBufferBase 型のバッファ
  #
  # @elsek
  # @brief Constructor
  #
  # @param info ConnectorInfo
  # @param provider InPortProvider
  # @param listeners ConnectorListeners type lsitener object list
  # @param buffer CdrBufferBase type buffer
  #
  # @endif
  #
  def __init__(self, info, provider, listeners, buffer = None):
    OpenRTM_aist.InPortConnector.__init__(self, info, buffer)
    self._provider = provider
    self._listeners = listeners

    
    if not self._provider:
      raise

    self._buffer = None
    self._provider.init(info.properties)
    self._provider.setListener(info, self._listeners)
    self.onConnect()

    self._consumer = None
    self._isWritableCallback = None
    self._writeCallback = None

    self._marshaling_type = info.properties.getProperty("marshaling_type", "corba")
    self._marshaling_type = self._marshaling_type.strip()

    self._serializer = OpenRTM_aist.SerializerFactory.instance().createObject(self._marshaling_type)

    return

    
  ##
  # @if jp
  # @brief デストラクタ
  #
  # disconnect() が呼ばれ、consumer, publisher, buffer が解体・削除される。
  #
  # @else
  #
  # @brief Destructor
  #
  # This operation calls disconnect(), which destructs and deletes
  # the consumer, the publisher and the buffer.
  #
  # @endif
  #
  def __del__(self):
    return

  ##
  # @if jp
  # @brief バッファからデータを読み出す。
  # read関数と違い、アンマーシャリングを実行しない
  #
  # @param self
  # @return リターンコード
  #
  # @brief 
  #  
  # @param self
  # @return 
  #
  # @endif
  #
  def readBuff(self):
    self._rtcout.RTC_TRACE("readBuff()")
    data = [None]
    if self._consumer:
      read_ret = self._consumer.get(data)
      return read_ret, data[0]
    self._rtcout.RTC_ERROR("cunsumer is not set")
    return self.PORT_ERROR, None

  ##
  # @if jp
  # @brief データの読み出し
  #
  # バッファからデータを読み出す。正常に読み出せた場合、戻り値は
  # PORT_OK となり、data に読み出されたデータが格納される。それ以外
  # の場合には、エラー値として BUFFER_EMPTY, TIMEOUT,
  # PRECONDITION_NOT_MET, PORT_ERROR が返される。
  #
  # @return PORT_OK              正常終了
  #         BUFFER_EMPTY         バッファは空である
  #         TIMEOUT              タイムアウトした
  #         PRECONDITION_NOT_MET 事前条件を満たさない
  #         PORT_ERROR           その他のエラー
  #
  # @else
  #
  # @brief Reading data
  #
  # This function reads data from the buffer. If data is read
  # properly, this function will return PORT_OK return code. Except
  # normal return, BUFFER_EMPTY, TIMEOUT, PRECONDITION_NOT_MET and
  # PORT_ERROR will be returned as error codes.
  #  
  # @return PORT_OK              Normal return
  #         BUFFER_EMPTY         Buffer empty
  #         TIMEOUT              Timeout
  #         PRECONDITION_NOT_MET Preconditin not met
  #         PORT_ERROR           Other error
  #
  # @endif
  #
  # virtual ReturnCode read(cdrMemoryStream& data);
  def read(self, data):
    self._rtcout.RTC_TRACE("read()")
    if not self._dataType:
      return self.PRECONDITION_NOT_MET
    ret, cdr = self.readBuff()
    if ret != self.PORT_OK:
      return ret
    else:
      ret, _data = self.deserializeData(cdr)
      if ret == self.PORT_OK:
        if type(data) == list:
          data[0] = _data
        self.onBufferRead(cdr)
      return ret


  #
  # @if jp
  # @brief データを書き込める状態かを判定
  # @param self
  # @return True：書き込み可能
  # @else
  # @brief 
  # @param self
  # @return 
  # @return 
  # @endif
  def isReadable(self):
    if self._consumer:
      return self._consumer.isReadable()
    return False
        

  ##
  # @if jp
  # @brief 接続解除
  #
  # consumer, publisher, buffer が解体・削除される。
  #
  # @return PORT_OK
  #
  # @else
  #
  # @brief disconnect
  #
  # This operation destruct and delete the consumer, the publisher
  # and the buffer.
  #
  # @return PORT_OK
  #
  # @endif
  #
  # virtual ReturnCode disconnect();
  def disconnect(self):
    self._rtcout.RTC_TRACE("disconnect()")
    self.onDisconnect()
    # delete consumer
    if self._provider:
      cfactory = OpenRTM_aist.InPortProviderFactory.instance()
      cfactory.deleteObject(self._provider)
      
      self._provider.exit()
      
    self._provider = None


    if self._consumer:
      prop_list = []
      prop = OpenRTM_aist.Properties()
      node = prop.getNode("dataport")
      node.mergeProperties(self._profile.properties)
      OpenRTM_aist.NVUtil.copyFromProperties(prop_list, prop)
      self._consumer.unsubscribeInterface(prop_list)
      OpenRTM_aist.OutPortConsumerFactory.instance().deleteObject(self._consumer)
    self._consumer = None
    
    return self.PORT_OK

  ##
  # @if jp
  # @brief アクティブ化
  #
  # このコネクタをアクティブ化する
  #
  # @else
  #
  # @brief Connector activation
  #
  # This operation activates this connector
  #
  # @endif
  #
  # virtual void activate(){}; // do nothing
  def activate(self): # do nothing
    pass

  ##
  # @if jp
  # @brief 非アクティブ化
  #
  # このコネクタを非アクティブ化する
  #
  # @else
  #
  # @brief Connector deactivation
  #
  # This operation deactivates this connector
  #
  # @endif
  #
  # virtual void deactivate(){}; // do nothing
  def deactivate(self):  # do nothing
    pass


  ##
  # @if jp
  # @brief Bufferの生成
  #
  # 与えられた接続情報に基づきバッファを生成する。
  #
  # @param info 接続情報
  # @return バッファへのポインタ
  #
  # @else
  # @brief create buffer
  #
  # This function creates a buffer based on given information.
  #
  # @param info Connector information
  # @return The poitner to the buffer
  #
  # @endif
  #
  # virtual CdrBufferBase* createBuffer(Profile& profile);
  def createBuffer(self, profile):
    return None


  ##
  # @if jp
  # @brief データの書き出し
  #
  # バッファにデータを書き出す。正常に書き出せた場合、戻り値は
  # BUFFER_OK となる。それ以外の場合には、エラー値として BUFFER_FULL,TIMEOUT
  # PRECONDITION_NOT_MET, BUFFER_ERROR が返される。
  #
  # @return BUFFER_OK              正常終了
  #         BUFFER_FULL         バッファはいっぱいである
  #         TIMEOUT              タイムアウトした
  #         PRECONDITION_NOT_MET 事前条件を満たさない
  #         BUFFER_ERROR           その他のエラー
  #
  # @else
  #
  # @brief Reading data
  #
  # This function write data to the buffer. If data is write
  # properly, this function will return BUFFER_OK return code. Except
  # normal return, BUFFER_FULL, TIMEOUT, PRECONDITION_NOT_MET and
  # BUFFER_ERROR will be returned as error codes.
  #  
  # @return BUFFER_OK            Normal return
  #         BUFFER_FULL          Buffer full
  #         TIMEOUT              Timeout
  #         PRECONDITION_NOT_MET Preconditin not met
  #         BUFFER_ERROR           Other error
  #
  # @endif
  #
  # ReturnCode write(const OpenRTM::CdrData& data);
  def write(self, data):
    if self._writeCallback:
      return self._writeCallback(data)
    return OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET

  #
  # @if jp
  # @brief データを書き込める状態かを判定
  # @param self
  # @return True：書き込み可能
  # @else
  # @brief 
  # @param self
  # @return 
  # @endif
  def isWritable(self):
    if self._isWritableCallback:
      return self._isWritableCallback(self)
    return False

  #
  # @if jp
  # @brief データ書き込み時のリスナ設定
  # @param self
  # @param listener リスナ
  # @else
  # @brief 
  # @param self
  # @param listener
  # @endif
  def setWriteListener(self, listener):
    self._writeCallback = listener

  #
  # @if jp
  # @brief データ書き込み判定時のリスナ設定
  # @param self
  # @param listener リスナ
  # @else
  # @brief 
  # @param self
  # @param listener
  # @endif
  def setIsWritableListener(self, listener):
    self._isWritableCallback = listener
    
  ##
  # @if jp
  # @brief 接続確立時にコールバックを呼ぶ
  # @else
  # @brief Invoke callback when connection is established
  # @endif
  # void onConnect()
  def onConnect(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_CONNECT].notify(self._profile)
    return

  ##
  # @if jp
  # @brief 接続切断時にコールバックを呼ぶ
  # @else
  # @brief Invoke callback when connection is destroied
  # @endif
  # void onDisconnect()
  def onDisconnect(self):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_DISCONNECT].notify(self._profile)
    return

  ##
  # @if jp
  # @brief コンシューマの設定
  # @else
  # @brief set Consumer
  # @endif
  def setConsumer(self, consumer):
    self._consumer = consumer

  def onBufferRead(self, data):
    if self._listeners and self._profile:
      self._listeners.connectorData_[OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ].notify(self._profile, data)
    return
  def onBufferEmpty(self, data):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY].notify(self._profile)
    return
  def onBufferReadTimeout(self, data):
    if self._listeners and self._profile:
      self._listeners.connector_[OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT].notify(self._profile)
    return

  ##
  # @if jp
  # @brief データの復号化
  # @param self
  # @param cdr 復号化前のデータ
  # @return ret, data
  # ret：リターンコード
  # PORT_OK：正常完了
  # PRECONDITION_NOT_MET：サポートされていないエンディアン
  # SERIALIZE_ERROR：復号化処理でエラー
  # PRECONDITION_NOT_MET：その他のエラー
  # data：復号化後のデータ
  # @else
  # @brief 
  # @param self
  # @param cdr 
  # @return 
  # @endif
  def deserializeData(self, cdr):
    self._serializer.isLittleEndian(self._endian)
    ser_ret, data = self._serializer.deserialize(cdr, self._dataType)

    if ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK:
      return self.PORT_OK, data
    elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN:
      self._rtcout.RTC_ERROR("unknown endian from connector")
      return self.UNKNOWN_ERROR, None
    elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR:
      self._rtcout.RTC_ERROR("unknown error")
      return self.UNKNOWN_ERROR, None
    elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOTFOUND:
      self._rtcout.RTC_ERROR("unknown serializer from connector")
      return self.UNKNOWN_ERROR, None
    return self.PRECONDITION_NOT_MET, None


##
# @if jp
# @class WriteListenerBase
# @brief WriteListenerBase クラス
#
# 書き込み時リスナのベースクラス
#
# @since 2.0.0
#
# @else
# @class WriteListenerBase
# @brief WriteListenerBase class
#
#
# @since 2.0.0
#
# @endif
#
class WriteListenerBase(object):
  ##
  # @if jp
  # @brief 仮想コールバック関数
  # @param self
  # @param data 書き込むバイト列のデータ
  # @else
  # @brief Destructor
  # @param self
  # @param data 書き込むバイト列のデータ
  # @endif
  def __call__(self, data):
    return OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET

##
# @if jp
# @class IsWritableListenerBase
# @brief IsWritableListenerBase クラス
#
# 書き込み確認時リスナのベースクラス
#
# @since 2.0.0
#
# @else
# @class IsWritableListenerBase
# @brief IsWritableListenerBase class
#
#
# @since 2.0.0
#
# @endif
#
class IsWritableListenerBase(object):
  ##
  # @if jp
  # @brief 仮想コールバック関数
  # @param self
  # @param con InPortConnector
  # @return True：書き込み可、False：書き込み不可
  # @else
  # @brief Destructor
  # @param self
  # @param con
  # @return
  # @endif
  def __call__(self, con):
    return False