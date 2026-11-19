#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OutPortDuplexConnector.py
# @if jp
# @brief `OutPortDuplexConnector`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of OutPortDuplexConnector.
# @endif
# @date $Date: 2026-11-13 15:32:20 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2026
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$

# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#


import OpenRTM_aist
import CSP
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
    def __init__(self, info, provider, listeners, buffer=None) -> None:
        OpenRTM_aist.OutPortConnector.__init__(self, info)
        self._provider = provider
        self._listeners = listeners

        if not self._provider:
            self._rtcout.RTC_ERROR(
                "Exeption: in OutPortPullConnector.__init__().")
            raise

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

    def __del__(self) -> None:
        return

    ##
    # @if jp
    # @brief データの書き込み
    #
    # 設定したConsumerオブジェクトによりInPort側にデータを送信する
    # 戻り値は設定したConsumerオブジェクトに依存する
    #
    # @param data 書き込むデータ
    # @return リターンコード
    #
    # @else
    # @brief Send data to one ready connection.
    #
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
            self._rtcout.RTC_ERROR("self._consumer is None")
            return self.PORT_ERROR

    ##
    # @if jp
    # @brief データ書き込み可能かOutPort側に確認
    #
    # 設定したConsumerオブジェクトによりInPort側にデー化書き込み可能かを確認する
    # 戻り値は設定したConsumerオブジェクトに依存する
    #
    # @param retry True：再検索、False：通常の書き込み確認
    # @return True：書き込み可能、False：書き込み不可
    #
    # @param option ガード照合に使用するオプション。
    # @else
    #
    # @brief Check whether the receiver is ready.
    #
    # @param retry
    # @return
    #
    # @param option Options used for guard matching.
    # @endif
    #
    def isWritable(self, retry: bool = False, option: list = []):
        self._rtcout.RTC_TRACE("isWritable()")
        if self._consumer:
            return self._consumer.isWritable(retry, option)
        self._rtcout.RTC_ERROR("self._consumer is None")
        return False

    ##
    # @if jp
    # @brief データ読み込み
    # InPort側からリモートに呼び出す
    # 内部でデータ読み込み時のリスナが呼び出される
    # 戻り値はリスナに依存する
    #
    # @param data 読み込んだデータを格納する変数
    # @return リターンコード
    # BUFFER_OK：正常完了
    # PRECONDITION_NOT_MET：エラー
    #
    # @else
    #
    # @brief Receive data from a connection.
    #
    # @param data
    # @return
    #
    # @endif
    #
    def read(self, data=None):
        self._rtcout.RTC_TRACE("read()")
        if self._readCallback:
            ret, data = self._readCallback()
            return ret, data
        self._rtcout.RTC_ERROR("self._readCallback is None")
        return OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET, data

    ##
    # @if jp
    # @brief データ読み込み可能かを確認
    # InPort側からリモートに呼び出す
    # 内部でデータ読み込み確認時のリスナが呼び出される
    # 戻り値はリスナに依存する
    #
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能、False：読み込み不可
    #
    # @param option ガード照合に使用するオプション。
    # @else
    #
    # @brief Perform the is readable state operation.
    #
    # @param retry
    # @return
    #
    # @param option Options used for guard matching.
    # @endif
    #
    def _isReadableState(self, retry: bool = False, option=None):
        """Return READY only after the existing callback made a reservation.

        If notify ran, use its locked decision even if the manager advances
        before the callback returns. Pre-notify rejection uses a phase snapshot.
        """
        manager = getattr(self._isReadableCallback, '_manager', None)
        capture = getattr(manager, '_captureReadiness', None)
        if capture is not None:
            with capture(getattr(self._isReadableCallback, '_port', None), self.id()) as response:
                if self.isReadable(retry, option):
                    return CSP.READY
                state = response['state']
                if state is not None:
                    return CSP.NOT_READY if state == CSP.READY else state
                return manager._readinessState()
        if self.isReadable(retry, option):
            return CSP.READY
        return manager._readinessState() if manager is not None else CSP.NOT_READY

    ##
    # @if jp
    # @brief 直前の接続先問い合わせの応答を取得する。
    # @else
    # @brief Get the response from the most recent peer readiness query.
    # @endif
    def getPeerReadinessState(self):
        consumer = self._consumer
        return consumer.getReadinessState() if consumer is not None else CSP.NOT_READY

    ##
    # @if jp
    # @brief 送信準備が整っているか確認する。
    # @param retry 再試行の問い合わせかどうか。
    # @param option ガード照合に使用するオプション。
    # @else
    # @brief Check whether the sender is ready.
    # @param retry Whether this query is a retry.
    # @param option Options used for guard matching.
    # @endif
    def isReadable(self, retry: bool = False, option=[]):
        self._rtcout.RTC_TRACE("isReadable(%d %s)", (retry, str(option)))
        if self._isReadableCallback:
            return self._isReadableCallback(self, retry, option)
        self._rtcout.RTC_ERROR("self._isReadableCallback is None")
        return False

    ##
    # @if jp
    # @brief データ読み込み時のリスナを登録
    #
    # @param listener リスナ
    #
    # @else
    #
    # @brief Set read listener.
    #
    # @return
    #
    # @param listener Value of listener.
    # @endif
    #

    def setReadListener(self, listener) -> None:
        self._rtcout.RTC_TRACE("setReadListener()")
        self._readCallback = listener

    ##
    # @if jp
    # @brief データ読み込み確認時のリスナを登録
    #
    # @param listener リスナ
    #
    # @else
    #
    # @brief Set is readable listener.
    #
    # @return
    #
    # @param listener Value of listener.
    # @endif
    #
    def setIsReadableListener(self, listener) -> None:
        self._rtcout.RTC_TRACE("setIsReadableListener()")
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

    def getBuffer(self) -> None:
        return None

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
    # @brief 接続確立時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is established
    # @endif
    # void onConnect()

    def onConnect(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_CONNECT, self._profile)
        return

    ##
    # @if jp
    # @brief 接続切断時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is destroied
    # @endif
    # void onDisconnect()

    def onDisconnect(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_DISCONNECT, self._profile)
        return

    ##
    # @if jp
    # @brief コンシューマの設定
    # @param consumer `consumer`の値。
    # @else
    # @brief set Consumer
    # @param consumer Value of consumer.
    # @endif
    def setConsumer(self, consumer) -> None:
        self._rtcout.RTC_TRACE("setConsumer()")
        self._consumer = consumer

    ##
    # @if jp
    # @brief データの符号化
    # @return ret, data
    # ret：リターンコード
    # PORT_OK：正常完了
    # PRECONDITION_NOT_MET：サポートされていないエンディアン
    # SERIALIZE_ERROR：符号化処理でエラー
    # PRECONDITION_NOT_MET：その他のエラー
    # data：符号化後のデータ
    # @param data 送受信するデータ。
    # @else
    # @brief Serialize typed data into a CDR sequence.
    # @return
    # @param data Data to transmit or receive.
    # @endif

    def serializeData(self, data):
        if self._serializer is None:
            self._rtcout.RTC_ERROR("serializer creation failure.")
            return self.UNKNOWN_ERROR, ""
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
    # @brief Release the peer CORBA interface reference.
    # @param prop
    # @endif
    def unsubscribeInterface(self, prop: list) -> None:
        if self._consumer:
            self._consumer.unsubscribeInterface(prop)

    ##
    # @if jp
    # @brief `Data Type`を設定する。
    # @param data 送受信するデータ。
    # @else
    # @brief Set data type.
    # @param data Data to transmit or receive.
    # @endif
    def setDataType(self, data) -> None:
        OpenRTM_aist.OutPortConnector.setDataType(self, data)
        self._serializer = OpenRTM_aist.SerializerFactories.instance(
        ).createSerializer(self._marshaling_type, data)
