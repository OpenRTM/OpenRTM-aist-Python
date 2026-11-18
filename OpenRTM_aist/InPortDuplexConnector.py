#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file InPortDuplexConnector.py
# @if jp
# @brief `InPortDuplexConnector`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of InPortDuplexConnector.
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
    def __init__(self, info, provider, listeners, buffer=None):
        OpenRTM_aist.InPortConnector.__init__(self, info, buffer)
        self._provider = provider
        self._listeners = listeners

        if not self._provider:
            raise

        self._info = info
        self._provider.init(info.properties)
        self._provider.setListener(info, self._listeners)
        self.onConnect()

        self._consumer = None
        self._isWritableCallback = None
        self._isMatchConditionCallback = None
        self._writeCallback = None

        self._marshaling_type = info.properties.getProperty(
            "marshaling_type", "cdr")
        self._marshaling_type = self._marshaling_type.strip()

        self._serializer = None

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

    #
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
    ##
    # @if jp
    # @brief 受信バッファからデータを取得する。
    # @else
    # @brief Get data from the receive buffer.
    # @endif
    def readBuff(self):
        self._rtcout.RTC_TRACE("readBuff()")
        if self._consumer:
            read_ret, data = self._consumer.get()
            return read_ret, data
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
    # @param data 送受信するデータ。
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
    # @param data Data to transmit or receive.
    # @endif
    #
    # virtual ReturnCode read(cdrMemoryStream& data);
    def read(self, data=None):
        self._rtcout.RTC_TRACE("read()")
        if not self._dataType:
            self._rtcout.RTC_ERROR("self._dataType is not set.")
            return self.PRECONDITION_NOT_MET, data
        ret, cdr = self.readBuff()
        if ret != self.PORT_OK:
            return ret, data
        else:
            cdr = self.onBufferRead(cdr)
            ret, _data = self.deserializeData(cdr)
            return ret, _data

    #
    # @if jp
    # @brief データが読み込める状態かを判定
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能
    # @else
    # @brief Check whether the sender is ready.
    # @param retry
    # @return
    # @endif

    def isReadable(self, retry=False):
        self._rtcout.RTC_TRACE("isReadable()")
        if self._consumer:
            return self._consumer.isReadable(retry, getattr(self._provider, "_objref", self._provider))
        self._rtcout.RTC_ERROR("self._consumer is None")
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
            _ = OpenRTM_aist.InPortProviderFactory.instance()

            self._provider.exit()

        self._provider = None

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
    #
    # 与えられた接続情報に基づきバッファを生成する。
    #
    # @return バッファへのポインタ
    #
    # @param profile 接続プロファイル。
    # @else
    # @brief create buffer
    #
    # This function creates a buffer based on given information.
    #
    # @return The poitner to the buffer
    #
    # @param profile Connector profile.
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
    # @param data 送受信するデータ。
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
    # @param data Data to transmit or receive.
    # @endif
    #
    # ReturnCode write(const OpenRTM::CdrData& data);

    def write(self, data):
        self._rtcout.RTC_TRACE("write()")
        if self._writeCallback:
            return self._writeCallback(data)
        self._rtcout.RTC_ERROR("self._writeCallback is None")
        return OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET

    #
    # @if jp
    # @brief データを書き込める状態かを判定
    # @param retry True：再検索、False：通常の書き込み確認
    # @return True：書き込み可能
    # @param option ガード照合に使用するオプション。
    # @else
    # @brief Perform the is writable state operation.
    # @param retry
    # @return
    # @param option Options used for guard matching.
    # @endif
    def _isWritableState(self, retry=False, option=None):
        """Return READY only after the existing callback made a reservation.

        If notify ran, use its locked decision even if the manager advances
        before the callback returns. Pre-notify rejection uses a phase snapshot.
        """
        manager = getattr(self._isWritableCallback, '_manager', None)
        capture = getattr(manager, '_captureReadiness', None)
        if capture is not None:
            with capture(getattr(self._isWritableCallback, '_port', None), self.id()) as response:
                if self.isWritable(retry, option):
                    return CSP.READY
                state = response['state']
                if state is not None:
                    return CSP.NOT_READY if state == CSP.READY else state
                # Guards/closed ports can reject before reaching notify. There
                # is no manager decision to retain in that case.
                return manager._readinessState()
        if self.isWritable(retry, option):
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
    # @brief 受信準備が整っているか確認する。
    # @param retry 再試行の問い合わせかどうか。
    # @param option ガード照合に使用するオプション。
    # @else
    # @brief Check whether the receiver is ready.
    # @param retry Whether this query is a retry.
    # @param option Options used for guard matching.
    # @endif
    def isWritable(self, retry=False, option=[]):
        self._rtcout.RTC_TRACE("isWritable(%d %s)", (retry, str(option)))
        if self._isWritableCallback:
            return self._isWritableCallback(self, retry, option)
        self._rtcout.RTC_ERROR("self._isWritableCallback is None")
        return False

    #
    # @if jp
    # @brief ガード条件を満たすかを判定
    # @param option パラメータ
    # @return True：条件一致、False：条件不一致
    # @else
    # @brief Match the sender options against the receiver guard.
    # @param option
    # @return
    # @endif
    def matchCondition(self, option=[]):
        self._rtcout.RTC_TRACE("matchCondition(%s)", (str(option)))
        if self._isMatchConditionCallback:
            return self._isMatchConditionCallback(option)
        self._rtcout.RTC_ERROR("self._isMatchConditionCallback is None")
        return False

    #
    # @if jp
    # @brief データ書き込み時のリスナ設定
    # @param listener リスナ
    # @else
    # @brief Set write listener.
    # @param listener
    # @endif
    def setWriteListener(self, listener):
        self._writeCallback = listener

    #
    # @if jp
    # @brief データ書き込み判定時のリスナ設定
    # @param listener リスナ
    # @else
    # @brief Set is writable listener.
    # @param listener
    # @endif
    def setIsWritableListener(self, listener):
        self._isWritableCallback = listener

    #
    # @if jp
    # @brief ガード条件判定時のリスナ設定
    # @param listener リスナ
    # @else
    # @brief Set match condition listener.
    # @param listener
    # @endif
    def setMatchConditionListener(self, listener):
        self._isMatchConditionCallback = listener

    ##
    # @if jp
    # @brief 接続確立時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is established
    # @endif
    # void onConnect()
    def onConnect(self):
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
    def onDisconnect(self):
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
    def setConsumer(self, consumer):
        self._consumer = consumer
        self._consumer.setListener(self._info, self._listeners)

    ##
    # @if jp
    # @brief `on Buffer Read`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Read notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferRead(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Buffer Empty`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Empty notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferEmpty(self, data):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY, self._profile)
        return

    ##
    # @if jp
    # @brief `on Buffer Read Timeout`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Read Timeout notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferReadTimeout(self, data):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT, self._profile)
        return

    ##
    # @if jp
    # @brief データの復号化
    # @param cdr 復号化前のデータ
    # @return ret, data
    # ret：リターンコード
    # PORT_OK：正常完了
    # PRECONDITION_NOT_MET：サポートされていないエンディアン
    # SERIALIZE_ERROR：復号化処理でエラー
    # PRECONDITION_NOT_MET：その他のエラー
    # data：復号化後のデータ
    # @else
    # @brief Deserialize typed data from a CDR sequence.
    # @param cdr
    # @return
    # @endif
    def deserializeData(self, cdr):
        if self._serializer is None:
            self._rtcout.RTC_ERROR("serializer creation failure.")
            return self.UNKNOWN_ERROR, None

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
        return self.UNKNOWN_ERROR, None

    ##
    # @if jp
    # @brief コンシューマのインターフェースの登録を取り消す
    # @param prop コネクタプロファイルのプロパティ
    # @else
    # @brief Release the peer CORBA interface reference.
    # @param prop
    # @endif
    def unsubscribeInterface(self, prop):
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
    def setDataType(self, data):
        OpenRTM_aist.InPortConnector.setDataType(self, data)
        self._serializer = OpenRTM_aist.SerializerFactories.instance(
        ).createSerializer(self._marshaling_type, data)
