#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file  OutPortCorbaCdrConsumer.py
# @brief OutPortCorbaCdrConsumer class
# @date  $Date: 2008-01-13 10:28:27 $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2009
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#


import omniORB
from omniORB import any
from omniORB import CORBA
import OpenRTM_aist
import OpenRTM

##
# @if jp
# @class OutPortCorbaCdrConsumer
#
# @brief OutPortCorbaCdrConsumer クラス
#
# 通信手段に CORBA を利用した出力ポートコンシューマの実装クラス。
#
# @param DataType 本ポートにて扱うデータ型
#
# @since 1.0.0
#
# @else
# @class OutPortCorbaCdrConsumer
#
# @brief OutPortCorbaCdrConsumer class
#
# This is an implementation class of the output Consumer
# that uses CORBA for means of communication.
#
# @param DataType Data type for this port
#
# @since 1.0.0
#
# @endif
#


class OutPortCorbaCdrConsumer(OpenRTM_aist.OutPortCorbaConsumerBase):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param buffer 本ポートに割り当てるバッファ
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param buffer Buffer that is attached to this port
    #
    # @endif
    #
    def __init__(self) -> None:
        OpenRTM_aist.OutPortCorbaConsumerBase.__init__(
            self, OpenRTM.OutPortCdr, "corba_cdr")
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OutPortCorbaCdrConsumer")
        self._buffer = None
        self._profile = None
        self._listeners = None
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
    def __del__(self) -> None:
        self._rtcout.RTC_PARANOID("~OutPortCorbaCdrConsumer()")
        OpenRTM_aist.OutPortCorbaConsumerBase.__del__(self)

    ##
    # @if jp
    # @brief バッファをセットする
    #
    # OutPortConsumerがデータを取り出すバッファをセットする。
    # すでにセットされたバッファがある場合、以前のバッファへの
    # ポインタに対して上書きされる。
    # OutPortProviderはバッファの所有権を仮定していないので、
    # バッファの削除はユーザの責任で行わなければならない。
    #
    # @param buffer OutPortProviderがデータを取り出すバッファへのポインタ
    #
    # @else
    # @brief Setting outside buffer's pointer
    #
    # A pointer to a buffer from which OutPortProvider retrieve data.
    # If already buffer is set, previous buffer's pointer will be
    # overwritten by the given pointer to a buffer.  Since
    # OutPortProvider does not assume ownership of the buffer
    # pointer, destructor of the buffer should be done by user.
    #
    # @param buffer A pointer to a data buffer to be used by OutPortProvider
    #
    # @endif
    #
    # virtual void setBuffer(CdrBufferBase* buffer);

    def setBuffer(self, buffer) -> None:
        self._rtcout.RTC_TRACE("setBuffer()")
        self._buffer = buffer
        return

    # void OutPortCorbaCdrConsumer::setListener(ConnectorInfo& info,
    #                                           ConnectorListeners* listeners)

    def setListener(self, info: 'OpenRTM_aist.ConnectorInfo', listeners) -> None:
        self._rtcout.RTC_TRACE("setListener()")
        self._listeners = listeners
        self._profile = info
        return

    ##
    # @if jp
    # @brief データを読み出す
    #
    # 設定されたデータを読み出す。
    #
    # @param data 読み出したデータを受け取るオブジェクト
    #
    # @return データ読み出し処理結果(読み出し成功:true、読み出し失敗:false)
    #
    # @else
    # @brief Read data
    #
    # Read set data
    #
    # @param data Object to receive the read data
    #
    # @return Read result (Successful:true, Failed:false)
    #
    # @endif
    #
    # virtual ReturnCode get(cdrMemoryStream& data);

    def get(self):
        self._rtcout.RTC_PARANOID("get()")

        try:
            data = None
            outportcdr = self._ptr()
            try:
                ret, cdr_data = outportcdr.get()
            except CORBA.COMM_FAILURE as ex:
                if ex.minor == omniORB.COMM_FAILURE_WaitingForReply:
                    self._rtcout.RTC_DEBUG("Retry get message")
                    ret, cdr_data = outportcdr.get()
                else:
                    raise
            except BaseException:
                raise

            if ret == OpenRTM.PORT_OK:
                self._rtcout.RTC_DEBUG("get() successful")
                data = cdr_data
                data = self.onReceived(data)
                data = self.onBufferWrite(data)

                if self._buffer.full():
                    self._rtcout.RTC_INFO("InPort buffer is full.")
                    data = self.onBufferFull(data)
                    data = self.onReceiverFull(data)

                self._buffer.put(data)
                self._buffer.advanceWptr()
                self._buffer.advanceRptr()

                return self.PORT_OK, data
            return self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_WARN("Exception caught from OutPort.get().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST, None

    ##
    # @if jp
    # @brief リターンコード変換 (DataPortStatus -> BufferStatus)
    # @else
    # @brief Return codes conversion
    # @endif
    #
    # ReturnCode convertReturn(::OpenRTM::PortStatus status,
    #                          const cdrMemoryStream& data)

    def convertReturn(self, status, data):
        if status == OpenRTM.PORT_OK:
            # never comes here
            return self.PORT_OK, data

        elif status == OpenRTM.PORT_ERROR:
            self.onSenderError()
            return self.PORT_ERROR, data

        elif status == OpenRTM.BUFFER_FULL:
            # never comes here
            return self.BUFFER_FULL, data

        elif status == OpenRTM.BUFFER_EMPTY:
            self.onSenderEmpty()
            return self.BUFFER_EMPTY, data

        elif status == OpenRTM.BUFFER_TIMEOUT:
            self.onSenderTimeout()
            return self.BUFFER_TIMEOUT, data

        elif status == OpenRTM.UNKNOWN_ERROR:
            self.onSenderError()
            return self.UNKNOWN_ERROR, data

        else:
            self.onSenderError()
            return self.UNKNOWN_ERROR, data

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

    ##
    # @brief Connector listener functions
    #
    # inline void onSenderEmpty()

    def onSenderEmpty(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)

        return

    # inline void onSenderTimeout()

    def onSenderTimeout(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT, self._profile)

        return

    # inline void onSenderError()

    def onSenderError(self) -> None:
        if self._listeners is not None and self._profile is not None:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR, self._profile)

        return


def OutPortCorbaCdrConsumerInit() -> None:
    factory = OpenRTM_aist.OutPortConsumerFactory.instance()
    factory.addFactory("corba_cdr",
                       OpenRTM_aist.OutPortCorbaCdrConsumer)
    return
