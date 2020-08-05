#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file OutPortDuplexConnector.py
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
# @class OutPortPullConnector
# @brief OutPortPullConnector クラス
#
#
# @since 2.0.0
#
# @else
# @class OutPortPullConnector
# @brief OutPortPullConnector class
#
#
# @since 2.0.0
#
# @endif
#
class OutPortDuplexConnector(OpenRTM_aist.OutPortConnector):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # @param info ConnectorInfo
    # @param provider OutPortProvider
    # @param listeners ConnectorListeners 型のリスナオブジェクトリスト
    # @param buffer CdrBufferBase 型のバッファ
    #
    # @else
    # @brief Constructor
    #
    #
    # @param info ConnectorInfo
    # @param provider OutPortProvider
    # @param listeners ConnectorListeners type lsitener object list
    # @param buffer CdrBufferBase type buffer
    #
    # @endif
    #
    # OutPortPullConnector(ConnectorInfo info,
    #                      OutPortProvider* provider,
    #                      ConnectorListeners& listeners,
    #                      CdrBufferBase* buffer = 0);
    def __init__(self, info, provider, listeners, buffer=None):
        OpenRTM_aist.OutPortConnector.__init__(self, info)
        self._provider = provider
        self._listeners = listeners

        if not self._provider:
            self._rtcout.RTC_ERROR(
                "Exeption: in OutPortPullConnector.__init__().")
            raise

        self._buffer = buffer
        self._info = info
        self._provider.init(info.properties)
        self._provider.setConnector(self)
        self._provider.setListener(info, self._listeners)

        self._consumer = None
        self._isReadableCallback = None
        self._readCallback = None

        self._marshaling_type = info.properties.getProperty(
            "marshaling_type", "cdr")
        self._marshaling_type = self._marshaling_type.strip()

        self._serializer = None

        self.onConnect()

        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # disconnect() が呼ばれ、provider, buffer が解体・削除される。
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
    # @brief データの書き込み
    #
    # 設定したConsumerオブジェクトによりInPort側にデータを送信する
    # 戻り値は設定したConsumerオブジェクトに依存する
    #
    # @param self
    # @param data 書き込むデータ
    # @return リターンコード
    #
    # @else
    #
    # @param self
    # @param data
    # @return
    #
    # @endif
    #
    # virtual ReturnCode write(const cdrMemoryStream& data);

    def write(self, data):
        self._rtcout.RTC_TRACE("write()")

        if self._consumer:
            ret, cdr_data = self.serializeData(data)
            if ret == self.PORT_OK:
                return self._consumer.put(cdr_data)
            else:
                return ret
        else:
            return self.PORT_ERROR

    ##
    # @if jp
    # @brief データ書き込み可能かOutPort側に確認
    #
    # 設定したConsumerオブジェクトによりInPort側にデー化書き込み可能かを確認する
    # 戻り値は設定したConsumerオブジェクトに依存する
    #
    # @param self
    # @param retry True：再検索、False：通常の書き込み確認
    # @return True：書き込み可能、False：書き込み不可
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param retry
    # @return
    #
    # @endif
    #
    def isWritable(self, retry=False):
        if self._consumer:
            return self._consumer.isWritable(retry)
        return False

    ##
    # @if jp
    # @brief データ読み込み
    # InPort側からリモートに呼び出す
    # 内部でデータ読み込み時のリスナが呼び出される
    # 戻り値はリスナに依存する
    #
    # @param self
    # @param data 読み込んだデータを格納する変数
    # @return リターンコード
    # BUFFER_OK：正常完了
    # PRECONDITION_NOT_MET：エラー
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param data
    # @return
    #
    # @endif
    #
    def read(self, data=None):
        if self._readCallback:
            ret, data = self._readCallback()
            return ret, data
        return OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET, data

    ##
    # @if jp
    # @brief データ読み込み可能かを確認
    # InPort側からリモートに呼び出す
    # 内部でデータ読み込み確認時のリスナが呼び出される
    # 戻り値はリスナに依存する
    #
    # @param self
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能、False：読み込み不可
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param retry
    # @return
    #
    # @endif
    #
    def isReadable(self, retry=False):
        if self._isReadableCallback:
            return self._isReadableCallback(self, retry)
        return False

    ##
    # @if jp
    # @brief データ読み込み時のリスナを登録
    #
    # @param self
    # @param listener リスナ
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def setReadListener(self, listener):
        self._readCallback = listener

    ##
    # @if jp
    # @brief データ読み込み確認時のリスナを登録
    #
    # @param self
    # @param listener リスナ
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #
    def setIsReadableListener(self, listener):
        self._isReadableCallback = listener

    ##
    # @if jp
    # @brief 接続解除
    #
    # consumer, publisher, buffer が解体・削除される。
    #
    # @else
    #
    # @brief disconnect
    #
    # This operation destruct and delete the consumer, the publisher
    # and the buffer.
    #
    # @endif
    #
    # virtual ReturnCode disconnect();
    def disconnect(self):
        self._rtcout.RTC_TRACE("disconnect()")
        self.onDisconnect()
        # delete provider
        if self._provider:
            self._provider.exit()
        self._provider = None

        if self._serializer:
            self._rtcout.RTC_DEBUG("delete serializer")
        self._serializer = None

        if self._consumer:
            self._rtcout.RTC_DEBUG("delete consumer")
            cfactory = OpenRTM_aist.InPortConsumerFactory.instance()

        self._consumer = None

        return self.PORT_OK

    ##
    # @if jp
    # @brief Buffer を取得する
    #
    # Connector が保持している Buffer を返す
    #
    # @else
    # @brief Getting Buffer
    #
    # This operation returns this connector's buffer
    #
    # @endif
    #
    # virtual CdrBufferBase* getBuffer();

    def getBuffer(self):
        return self._buffer

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

    def activate(self):  # do nothing
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
    # @else
    # @brief create buffer
    # @endif
    #
    # CdrBufferBase* createBuffer(ConnectorInfo& info);

    def createBuffer(self, info):
        buf_type = info.properties.getProperty("buffer_type", "ring_buffer")
        return OpenRTM_aist.CdrBufferFactory.instance().createObject(buf_type)

    ##
    # @if jp
    # @brief 接続確立時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is established
    # @endif
    # void onConnect()

    def onConnect(self):
        if self._listeners and self._profile:
            self._listeners.notify(OpenRTM_aist.ConnectorListenerType.ON_CONNECT, self._profile)
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
            self._listeners.notify(OpenRTM_aist.ConnectorListenerType.ON_DISCONNECT, self._profile)
        return

    ##
    # @if jp
    # @brief コンシューマの設定
    # @else
    # @brief set Consumer
    # @endif
    def setConsumer(self, consumer):
        self._consumer = consumer
        self._consumer.setListener(self._info, self._listeners)

    ##
    # @if jp
    # @brief データの符号化
    # @param self
    # @param cdr 符号化前のデータ
    # @return ret, data
    # ret：リターンコード
    # PORT_OK：正常完了
    # PRECONDITION_NOT_MET：サポートされていないエンディアン
    # SERIALIZE_ERROR：符号化処理でエラー
    # PRECONDITION_NOT_MET：その他のエラー
    # data：符号化後のデータ
    # @else
    # @brief
    # @param self
    # @param cdr
    # @return
    # @endif

    def serializeData(self, data):
        if self._serializer is None:
            self._rtcout.RTC_ERROR("serializer creation failure.")
            return self.UNKNOWN_ERROR, cdr_data
        self._serializer.isLittleEndian(self._endian)
        ser_ret, cdr_data = self._serializer.serialize(data)
        if ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN:
            self._rtcout.RTC_ERROR(
                "write(): endian %s is not support.", self._endian)
            return self.UNKNOWN_ERROR, cdr_data
        elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR:
            self._rtcout.RTC_ERROR("unkown error.")
            return self.UNKNOWN_ERROR, cdr_data
        elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOTFOUND:
            self._rtcout.RTC_ERROR(
                "write(): serializer %s is not support.", self._marshaling_type)
            return self.UNKNOWN_ERROR, cdr_data
        return self.PORT_OK, cdr_data

    ##
    # @if jp
    # @brief コンシューマのインターフェースの登録を取り消す
    # @param prop コネクタプロファイルのプロパティ
    # @else
    # @brief
    # @param prop
    # @endif
    def unsubscribeInterface(self, prop):
        if self._consumer:
            self._consumer.unsubscribeInterface(prop)


    def setDataType(self, data):
        OpenRTM_aist.OutPortConnector.setDataType(self, data)
        self._serializer = OpenRTM_aist.SerializerFactories.instance().createSerializer(self._marshaling_type, data)


##
# @if jp
# @class ReadListenerBase
# @brief ReadListenerBase クラス
#
# 読み込み時リスナのベースクラス
#
# @since 2.0.0
#
# @else
# @class ReadListenerBase
# @brief ReadListenerBase class
#
#
# @since 2.0.0
#
# @endif
#
class ReadListenerBase(object):
    ##
    # @if jp
    # @brief 仮想コールバック関数
    # @param self
    # @return 読み込んだデータ
    # @else
    # @brief
    # @param self
    # @return 読み込んだデータ
    # @endif
    def __call__(self):
        return (OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET, None)

##
# @if jp
# @class IsReadableListenerBase
# @brief IsReadableListenerBase クラス
#
# 読み込み確認時リスナのベースクラス
#
# @since 2.0.0
#
# @else
# @class IsReadableListenerBase
# @brief IsReadableListenerBase class
#
#
# @since 2.0.0
#
# @endif
#


class IsReadableListenerBase(object):
    ##
    # @if jp
    # @brief 仮想コールバック関数
    # @param self
    # @param con OutPortConnector
    # @return True：読み込み可、False：読み込み不可
    # @else
    # @brief
    # @param self
    # @param con
    # @return
    # @endif
    def __call__(self, con):
        return False
