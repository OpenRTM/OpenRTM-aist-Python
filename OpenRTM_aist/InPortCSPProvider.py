#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file InPortCSPProvider.py
# @if jp
# @brief `InPortCSPProvider`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of InPortCSPProvider.
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
from contextlib import nullcontext


##
# @if jp
# @class InPortCSPProvider
# @brief InPortCSPProvider クラス
#
# CSPモデルのチャネルを模擬した入力ポートプロバイダーの実装クラス。
#
#
# @else
# @class InPortCSPProvider
# @brief InPortCSPProvider class
#
#
#
# @endif
#
class InPortCSPProvider(OpenRTM_aist.InPortProvider, CSP__POA.InPortCsp):

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
        OpenRTM_aist.InPortProvider.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("CSPOutPort")

        # PortProfile setting
        self.setInterfaceType("csp_channel")
        self._objref = self._this()

        self._buffer = None

        self._profile = None
        self._listeners = None

        orb = OpenRTM_aist.Manager.instance().getORB()
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.csp_channel.inport_ior",
                                                          orb.object_to_string(self._objref)))
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.csp_channel.inport_ref",
                                                          self._objref))

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
    # @brief バッファにデータを書き込む
    #
    # データのサイズは共有メモリも先頭8byteから取得する
    # 共有メモリからデータを取り出しバッファに書き込む
    #
    # @param data 書込対象データ
    #
    # @else
    # @brief Deliver CDR data to the receiver.
    #
    #
    #
    # @param data
    #
    # @endif
    #
    # ::OpenRTM::PortStatus put()
    #  throw (CORBA::SystemException);

    def put(self, data: bytes):

        try:
            self._rtcout.RTC_PARANOID("InPortCSPProvider.put()")

            if not self._connector:
                self.onReceiverError(data)
                return RTC.PORT_ERROR

            self._rtcout.RTC_PARANOID("received data size: %d", len(data))

            admission = getattr(self._connector, "_csp_write_admission", None)
            with admission() if admission is not None else nullcontext(True) as allowed:
                if not allowed:
                    return RTC.PORT_ERROR
                data = self.onReceived(data)
                ret = self._connector.write(data)
                return self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
            return RTC.UNKNOWN_ERROR

    ##
    # @if jp
    # @brief データ書き込み可能かを確認
    #
    # @param retry True：再検索、False：通常の書き込み確認
    # @return True：書き込み可能、False：書き込み不可
    #
    #
    # @param option ガード照合に使用するオプション。
    # @else
    # @brief Return receive-side admission as a Readiness value.
    #
    # @param retry
    # @return
    #
    # @param option Options used for guard matching.
    # @endif
    #

    def is_writable(self, retry: bool, option: list):
        self._rtcout.RTC_PARANOID("is_writable()")
        if self._connector:
            state_query = getattr(self._connector, "_isWritableState", None)
            if state_query is not None:
                return state_query(retry, option)
            return CSP.READY if self._connector.isWritable(retry, option) else CSP.NOT_READY
        self._rtcout.RTC_ERROR("self._connector is None")
        return CSP.NOT_READY

    ##
    # @if jp
    # @brief ガード条件を満たすかを確認
    #
    # @param option パラメータ
    # @return True：条件一致、False：条件不一致
    #
    #
    # @else
    # @brief Match the sender options against the receiver guard.
    #
    # @param option
    # @return
    #
    # @endif
    #

    def match_condition(self, option):
        self._rtcout.RTC_PARANOID("match_condition()")
        if self._connector:
            return self._connector.matchCondition(option)
        self._rtcout.RTC_ERROR("self._connector is None")
        return False

    ##
    # @if jp
    # @brief `on Buffer Write`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Write notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferWrite(self, data: bytes):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
        return data

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

    ##
    # @if jp
    # @brief `on Buffer Write Timeout`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Write Timeout notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferWriteTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Buffer Write Overwrite`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Buffer Write Overwrite notification.
    # @param data Data to transmit or receive.
    # @endif
    def onBufferWriteOverwrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Received`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Received notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceived(self, data: bytes):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Receiver Full`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Receiver Full notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceiverFull(self, data) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
        return

    ##
    # @if jp
    # @brief `on Receiver Timeout`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Receiver Timeout notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceiverTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT, self._profile, data)
        return data

    ##
    # @if jp
    # @brief `on Receiver Error`の通知を処理する。
    # @param data 送受信するデータ。
    # @else
    # @brief Handle the on Receiver Error notification.
    # @param data Data to transmit or receive.
    # @endif
    def onReceiverError(self, data: bytes):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR, self._profile, data)
        return data

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
    def convertReturn(self, status: int, data: bytes):
        if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
            self.onBufferWrite(data)
            return RTC.PORT_OK

        elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
            self.onReceiverError(data)
            return RTC.PORT_ERROR

        elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
            data = self.onBufferFull(data)
            self.onReceiverFull(data)
            return RTC.BUFFER_FULL

        elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
            return RTC.BUFFER_EMPTY

        elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
            self.onReceiverError(data)
            return RTC.PORT_ERROR

        elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
            data = self.onBufferWriteTimeout(data)
            self.onReceiverTimeout(data)
            return RTC.BUFFER_TIMEOUT

        else:
            self.onReceiverError(data)
            return RTC.UNKNOWN_ERROR


##
# @if jp
# @brief `InPortCSPProvider`のFactoryを登録する。
# @else
# @brief Register the factory for InPortCSPProvider.
# @endif
def InPortCSPProviderInit() -> None:
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.InPortCSPProvider)
