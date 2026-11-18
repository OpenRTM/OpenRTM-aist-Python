#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OutPortCSPProvider.py
# @if jp
# @brief `OutPortCSPProvider`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of OutPortCSPProvider.
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
import CSP__POA


##
# @if jp
# @class OutPortCSPProvider
# @brief OutPortCSPProvider クラス
#
# CSPモデルのチャネルを模擬した出力ポートプロバイダーの実装クラス。
#
#
# @else
# @class InPortCorbaCdrProvider
# @brief InPortCorbaCdrProvider class
#
#
#
# @endif
#
class OutPortCSPProvider(OpenRTM_aist.OutPortProvider, CSP__POA.OutPortCsp):

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
        OpenRTM_aist.OutPortProvider.__init__(self)

        # PortProfile setting
        self.setInterfaceType("csp_channel")
        self._objref = self._this()
        self._buffer = None
        orb = OpenRTM_aist.Manager.instance().getORB()
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.csp_channel.outport_ior",
                                                          orb.object_to_string(self._objref)))
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.csp_channel.outport_ref",
                                                          self._objref))
        self._listeners = None
        self._connector = None
        self._profile = None

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
        return

    ##
    # @if jp
    # @brief 終了処理
    #
    # @else
    # @brief Perform the exit operation.
    #
    #
    #
    # @endif
    #
    def exit(self) -> None:
        oid = OpenRTM_aist.Manager.instance().getPOA().servant_to_id(self)
        OpenRTM_aist.Manager.instance().getPOA().deactivate_object(oid)

    # void init(coil::Properties& prop)
    ##
    # @if jp
    # @brief `init`に対応する処理を行う。
    # @param prop 初期化に使用するプロパティ。
    # @else
    # @brief Perform the init operation.
    # @param prop Properties used for initialization.
    # @endif
    def init(self, prop: 'OpenRTM_aist.Properties'):

        pass

    ##
    # @if jp
    # @brief `Buffer`を設定する。
    # @param buffer `buffer`の値。
    # @else
    # @brief Set buffer.
    # @param buffer Value of buffer.
    # @endif
    def setBuffer(self, buffer) -> None:
        self._buffer = buffer
        return

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
        self._profile = info
        self._listeners = listeners
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
    # @brief バッファからデータを取得する
    #
    # @return (リターンコード、取得データ)
    # PORT_OK：正常完了
    # PORT_ERROR：バッファ読み出しエラー、通常は発生しない
    # BUFFER_FULL：バッファがフル、通常は発生しない
    # BUFFER_EMPTY：バッファが空
    # BUFFER_TIMEOUT：読み込みタイムアウト
    # UNKNOWN_ERROR：その他のエラー
    #
    #
    # @else
    # @brief Get data from the buffer
    #
    # @return
    #
    # @endif
    #
    def get(self):
        self._rtcout.RTC_PARANOID("OutPortCSPProvider.get()")

        if not self._connector:
            self.onSenderError()
            return (RTC.UNKNOWN_ERROR, "")

        try:
            ret, cdr = self._connector.read()

            if ret == OpenRTM_aist.BufferStatus.BUFFER_OK:
                if cdr is None:
                    self._rtcout.RTC_ERROR("buffer is empty.")
                    return (RTC.BUFFER_EMPTY, "")

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
            return (RTC.UNKNOWN_ERROR, "")

        return self.convertReturn(ret, cdr)

    ##
    # @if jp
    # @brief データ読み込み可能かを確認
    #
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能、False：読み込み不可
    #
    #
    # @param provider 受信側のInPortCsp参照。
    # @else
    # @brief Return send-side admission as a Readiness value.
    #
    # @param retry
    # @return
    #
    # @param provider Reference to the receiver InPortCsp interface.
    # @endif
    #

    def is_readable(self, retry: bool, provider):
        self._rtcout.RTC_PARANOID("is_readable(%d %s)", (retry, str(provider)))
        if self._connector:
            state_query = getattr(self._connector, "_isReadableState", None)
            if state_query is not None:
                return state_query(retry, provider)
            return CSP.READY if self._connector.isReadable(retry, provider) else CSP.NOT_READY
        self._rtcout.RTC_ERROR("self._connector is None.")
        return CSP.NOT_READY

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
    # @brief `on Send`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Send notification.
    # @param data Data to transmit or receive.
    # @endif
    def onSend(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_SEND, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Buffer Empty`の通知を処理する。
    # @else
    # @brief Handle the on Buffer Empty notification.
    # @endif
    def onBufferEmpty(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY, self._profile)
        return

    ##
    # @if jp
    # @brief `on Buffer Read Timeout`の通知を処理する。
    # @else
    # @brief Handle the on Buffer Read Timeout notification.
    # @endif
    def onBufferReadTimeout(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT, self._profile)
        return

    ##
    # @if jp
    # @brief `on Sender Empty`の通知を処理する。
    # @else
    # @brief Handle the on Sender Empty notification.
    # @endif
    def onSenderEmpty(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)
        return

    ##
    # @if jp
    # @brief `on Sender Timeout`の通知を処理する。
    # @else
    # @brief Handle the on Sender Timeout notification.
    # @endif
    def onSenderTimeout(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT, self._profile)
        return

    ##
    # @if jp
    # @brief `on Sender Error`の通知を処理する。
    # @else
    # @brief Handle the on Sender Error notification.
    # @endif
    def onSenderError(self) -> None:
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR, self._profile)
        return

    ##
    # @if jp
    # @brief `convert Return`に対応する処理を行う。
    # @param status `status`の値。
    # @param data 送受信するデータ。
    # @else
    # @brief Perform the convert return operation.
    # @param status Value of status.
    # @param data Data to transmit or receive.
    # @endif
    def convertReturn(self, status, data):
        if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
            data = self.onBufferRead(data)
            data = self.onSend(data)
            return (RTC.PORT_OK, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
            self.onSenderError()
            return (RTC.PORT_ERROR, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
            # never come here
            return (RTC.BUFFER_FULL, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
            self.onBufferEmpty()
            self.onSenderEmpty()
            return (RTC.BUFFER_EMPTY, data)

        elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
            self.onSenderError()
            return (RTC.PORT_ERROR, data)

        elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
            self.onBufferReadTimeout()
            self.onSenderTimeout()
            return (RTC.BUFFER_TIMEOUT, data)

        else:
            return (RTC.UNKNOWN_ERROR, data)


##
# @if jp
# @brief `OutPortCSPProvider`のFactoryを登録する。
# @else
# @brief Register the factory for OutPortCSPProvider.
# @endif
def OutPortCSPProviderInit() -> None:
    factory = OpenRTM_aist.OutPortProviderFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.OutPortCSPProvider)
