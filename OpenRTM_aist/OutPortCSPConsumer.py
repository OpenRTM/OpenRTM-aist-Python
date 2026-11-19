#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OutPortCSPConsumer.py
# @if jp
# @brief `OutPortCSPConsumer`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of OutPortCSPConsumer.
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

import OpenRTM_aist
import RTC
import CSP
import threading


##
# @if jp
# @class OutPortCSPConsumer
# @brief OutPortCSPConsumer クラス
#
# CSPモデルのチャネルを模擬した出力ポートプロバイダーの実装クラス。
#
#
# @else
# @class OutPortCSPConsumer
# @brief OutPortCSPConsumer class
#
#
#
# @endif
#
class OutPortCSPConsumer(OpenRTM_aist.OutPortCorbaConsumerBase):

    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # Interface Typeにはshared_memoryを指定する
    # 共有メモリの空間名はUUIDで作成し、コネクタプロファイルのdataport.shared_memory.addressに保存する
    #
    # self
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # self
    # @endif
    #
    def __init__(self) -> None:
        OpenRTM_aist.OutPortCorbaConsumerBase.__init__(
            self, CSP.OutPortCsp, "csp_channel")
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OutPortCSPConsumer")
        self._properties = None
        self._query_state = threading.local()
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    #
    # @endif
    #
    def __del__(self) -> None:
        self._rtcout.RTC_PARANOID("~OutPortCSPConsumer()")
        OpenRTM_aist.CorbaConsumer.__del__(self)

    # void init(coil::Properties& prop)

    ##
    # @if jp
    # @brief `init`に対応する処理を行う。
    # @param prop 初期化に使用するプロパティ。
    # @else
    # @brief Perform the init operation.
    # @param prop Properties used for initialization.
    # @endif
    def init(self, prop: 'OpenRTM_aist.Properties') -> None:
        self._rtcout.RTC_TRACE("init()")
        self._properties = prop

    ##
    # @if jp
    # @brief バッファをセットする
    #
    #
    # @param buffer OutPortProviderがデータを取り出すバッファへのポインタ
    #
    # @else
    # @brief Setting outside buffer's pointer
    #
    # @param buffer A pointer to a data buffer to be used by OutPortProvider
    #
    # @endif
    #
    # virtual void setBuffer(CdrBufferBase* buffer);

    def setBuffer(self, buffer):
        pass

    # void OutPortCorbaCdrConsumer::setListener(ConnectorInfo& info,
    #                                           ConnectorListeners* listeners)

    ##
    # @if jp
    # @brief `Listener`を設定する。
    # @param info `info`の値。
    # @param listeners `listeners`の値。
    # @else
    # @brief Set listener.
    # @param info Value of info.
    # @param listeners Value of listeners.
    # @endif
    def setListener(self, info, listeners) -> None:
        self._rtcout.RTC_TRACE("setListener()")
        self._listeners = listeners
        self._profile = info
        return

    ##
    # @if jp
    # @brief `Connector`を設定する。
    # @param connector `connector`の値。
    # @else
    # @brief Set connector.
    # @param connector Value of connector.
    # @endif
    def setConnector(self, connector) -> None:
        self._connector = connector
        return

    ##
    # @if jp
    # @brief 接続先のProviderからデータを取得する
    #
    # @return リターンコード
    # PORT_OK：正常終了
    # PORT_ERROR：バッファの読み込みエラー、通常は発生しない
    # BUFFER_FULL：バッファフル、通常は発生しない
    # BUFFER_EMPTY：バッファが空
    # BUFFER_TIMEOUT：一定時間以内にバッファにデータが追加されなかった
    # CONNECTION_LOST：通信エラー
    # UNKNOWN_ERROR：その他のエラー
    #
    # @else
    # @brief Retrieve CDR data from the sender.
    #
    #
    # @return
    #
    # @endif
    #
    # ::OpenRTM::PortStatus put()
    #  throw (CORBA::SystemException);
    def get(self):
        self._rtcout.RTC_PARANOID("get()")

        try:
            data = None
            outportcsp = self._ptr()
            ret, cdr_data = outportcsp.get()

            if ret == RTC.PORT_OK:
                self._rtcout.RTC_DEBUG("get() successful")
                data = cdr_data
                self.onReceived(data)
                self.onBufferWrite(data)

                return self.PORT_OK, data
            return self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_WARN("Exception caught from OutPort.get().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST, None

    ##
    # @if jp
    # @brief データ読み込み可能かを接続先のproviderに確認
    #
    #
    # @return True：読み込み可能、False：読み込み不可
    # 通信エラーが発生した場合はFalseを返す
    #
    # @else
    # @brief Get the local admission state.
    #
    # @return
    #
    # @endif
    #
    def getReadinessState(self):
        """Read the result of this thread's last readiness RPC without an RPC."""
        return getattr(self._query_state, 'value', CSP.NOT_READY)

    ##
    # @if jp
    # @brief 送信準備が整っているか確認する。
    # @param retry 再試行の問い合わせかどうか。
    # @param provider 受信側のInPortCsp参照。
    # @else
    # @brief Check whether the sender is ready.
    # @param retry Whether this query is a retry.
    # @param provider Reference to the receiver InPortCsp interface.
    # @endif
    def isReadable(self, retry: bool = False, provider=CSP.InPortCsp._nil):
        self._rtcout.RTC_PARANOID("isReadable()")
        self._query_state.value = CSP.NOT_READY
        try:
            outportcsp = self._ptr()
            self._query_state.value = outportcsp.is_readable(retry, provider)
            return self._query_state.value == CSP.READY
        except BaseException:
            self._rtcout.RTC_WARN(
                "Exception caught from OutPort.isReadable().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return False

    ##
    # @if jp
    # @brief リターンコード変換 (DataPortStatus -> BufferStatus)
    # @param status `status`の値。
    # @param data 送受信するデータ。
    # @else
    # @brief Return codes conversion
    # @param status Value of status.
    # @param data Data to transmit or receive.
    # @endif
    #
    # ReturnCode convertReturn(::OpenRTM::PortStatus status,
    #                          const cdrMemoryStream& data)
    def convertReturn(self, status, data):
        if status == RTC.PORT_OK:
            # never comes here
            return self.PORT_OK, data

        elif status == RTC.PORT_ERROR:
            self.onSenderError()
            return self.PORT_ERROR, data

        elif status == RTC.BUFFER_FULL:
            # never comes here
            return self.BUFFER_FULL, data

        elif status == RTC.BUFFER_EMPTY:
            self.onSenderEmpty()
            return self.BUFFER_EMPTY, data

        elif status == RTC.BUFFER_TIMEOUT:
            self.onSenderTimeout()
            return self.BUFFER_TIMEOUT, data

        elif status == RTC.UNKNOWN_ERROR:
            self.onSenderError()
            return self.UNKNOWN_ERROR, data

        else:
            self.onSenderError()
            return self.UNKNOWN_ERROR, data

    #
    # @brief Connector data listener functions
    #
    # inline void onBufferWrite(const cdrMemoryStream& data)

    ##
    # @if jp
    # @brief `on Buffer Write`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Write notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferWrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)

        return data

    # inline void onBufferFull(const cdrMemoryStream& data)

    ##
    # @if jp
    # @brief `on Buffer Full`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Full notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL, self._profile, data)

        return data

    # inline void onReceived(const cdrMemoryStream& data)

    ##
    # @if jp
    # @brief `on Received`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Received notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceived(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)

        return data

    # inline void onReceiverFull(const cdrMemoryStream& data)

    ##
    # @if jp
    # @brief `on Receiver Full`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Receiver Full notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceiverFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)

        return data

    #
    # @brief Connector listener functions
    #
    # inline void onSenderEmpty()

    ##
    # @if jp
    # @brief `on Sender Empty`の通知を処理する。
    # @else
    # @brief Handle the on Sender Empty notification.
    # @endif
    def onSenderEmpty(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)

        return

    # inline void onSenderTimeout()

    ##
    # @if jp
    # @brief `on Sender Timeout`の通知を処理する。
    # @else
    # @brief Handle the on Sender Timeout notification.
    # @endif
    def onSenderTimeout(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT, self._profile)

        return

    # inline void onSenderError()

    ##
    # @if jp
    # @brief `on Sender Error`の通知を処理する。
    # @else
    # @brief Handle the on Sender Error notification.
    # @endif
    def onSenderError(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR, self._profile)

        return

##
# @if jp
# @brief モジュール登録関数
#
#
# @else
# @brief Register the factory for OutPortCSPConsumer.
#
#
# @endif
#


def OutPortCSPConsumerInit() -> None:
    factory = OpenRTM_aist.OutPortConsumerFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.OutPortCSPConsumer)
