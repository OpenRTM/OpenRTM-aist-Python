#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  InPortDSProvider.py
# @brief InPortDSProvider class
# @date  $Date: 2017-06-09 07:49:59 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
import RTC__POA
import RTC

##
# @if jp
# @class InPortDSProvider
# @brief InPortDSProvider クラス
#
# 通信手段に CORBA を利用した入力ポートプロバイダーの実装クラス。
#
# @param DataType 当該プロバイダに割り当てたバッファが保持するデータ型
#
# @since 1.2.0
#
# @else
# @class InPortDSProvider
# @brief InPortDSProvider class
#
# This is an implementation class of the input port Provider
# that uses CORBA for means of communication.
#
# @param DataType Data type held by the buffer that attached
#                 to this provider.
#
# @since 1.2.0
#
# @endif
#


class InPortDSProvider(OpenRTM_aist.InPortProvider,
                       RTC__POA.DataPushService):

    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # ポートプロパティに以下の項目を設定する。
    #  - インターフェースタイプ : CORBA_Any
    #  - データフロータイプ : Push, Pull
    #  - サブスクリプションタイプ : Any
    #
    # @param buffer 当該プロバイダに割り当てるバッファオブジェクト
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    # Set the following items to port properties
    #  - Interface type : CORBA_Any
    #  - Data flow type : Push, Pull
    #  - Subscription type : Any
    #
    # @param buffer Buffer object that is attached to this provider
    #
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.InPortProvider.__init__(self)

        # PortProfile setting
        self.setInterfaceType("data_service")

        # ConnectorProfile setting
        self._objref = self._this()

        self._buffer = None

        self._profile = None
        self._listeners = None

        # set InPort's reference
        orb = OpenRTM_aist.Manager.instance().getORB()

        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.data_service.inport_ior",
                                                          orb.object_to_string(self._objref)))
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.data_service.inport_ref",
                                                          self._objref))

        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @endif
    #
    def __del__(self):
        return

    ##
    # @if jp
    # @brief 終了処理
    #
    # @else
    # @brief
    #
    #
    #
    # @endif
    #
    def exit(self):
        oid = OpenRTM_aist.Manager.instance().getPOA().servant_to_id(self)
        OpenRTM_aist.Manager.instance().getPOA().deactivate_object(oid)

    # virtual void init(coil::Properties& prop);
    def init(self, prop):
        pass

    # virtual void setBuffer(BufferBase<cdrMemoryStream>* buffer);
    def setBuffer(self, buffer):
        self._buffer = buffer
        return

    # void setListener(ConnectorInfo& info,
    #                  ConnectorListeners* listeners);
    def setListener(self, info, listeners):
        self._profile = info
        self._listeners = listeners
        return

    def put(self, data):
        self._rtcout.RTC_PARANOID("InPortDSProvider.put()")
        return RTC.UNKNOWN_ERROR
    ##
    # @if jp
    # @brief [CORBA interface] バッファにデータを書き込む
    #
    # 設定されたバッファにデータを書き込む。
    #
    # @param data 書込対象データ
    #
    # @else
    # @brief [CORBA interface] Write data into the buffer
    #
    # Write data into the specified buffer.
    #
    # @param data The target data for writing
    #
    # @endif
    #
    # virtual ::OpenRTM::PortStatus push(const ::RTC::CdrData& data)
    #  throw (CORBA::SystemException);

    def push(self, data):
        try:
            self._rtcout.RTC_PARANOID("InPortDSProvider.push()")

            if not self._connector:
                self.onReceiverError(data)
                return RTC.PORT_ERROR

            self._rtcout.RTC_PARANOID("received data size: %d", len(data))

            data = self.onReceived(data)

            ret = self._connector.write(data)

            return self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
            return RTC.UNKNOWN_ERROR

    def convertReturn(self, status, data):
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
    # @brief Connector data listener functions
    #
    # inline void onBufferWrite(const cdrMemoryStream& data)

    def onBufferWrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
        return data

    # inline void onBufferFull(const cdrMemoryStream& data)

    def onBufferFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL, self._profile, data)
        return data

    # inline void onBufferWriteTimeout(const cdrMemoryStream& data)

    def onBufferWriteTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT, self._profile, data)
        return data

    # inline void onBufferWriteOverwrite(const cdrMemoryStream& data)
    def onBufferWriteOverwrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
        return data

    # inline void onReceived(const cdrMemoryStream& data)

    def onReceived(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
        return data

    # inline void onReceiverFull(const cdrMemoryStream& data)

    def onReceiverFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
        return data

    # inline void onReceiverTimeout(const cdrMemoryStream& data)

    def onReceiverTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT, self._profile, data)
        return data

    # inline void onReceiverError(const cdrMemoryStream& data)

    def onReceiverError(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR, self._profile, data)
        return data


def InPortDSProviderInit():
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory("data_service",
                       OpenRTM_aist.InPortDSProvider)
