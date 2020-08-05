#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  OutPortCSPProvider.py
# @brief OutPortCSPProvider class
# @date  $Date: 2019/03/12 $
# @author Nobuhiko Miyamoto


import OpenRTM_aist
import OpenRTM
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
    def __init__(self):
        OpenRTM_aist.OutPortProvider.__init__(self)

        # PortProfile setting
        self.setInterfaceType("csp_channel")
        self._objref = self._this()
        self._buffer = None
        orb = OpenRTM_aist.Manager.instance().getORB()
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.outport_ior",
                                                          orb.object_to_string(self._objref)))
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.outport_ref",
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

    # void init(coil::Properties& prop)
    def init(self, prop):

        pass

    def setBuffer(self, buffer):
        self._buffer = buffer
        return

    def setListener(self, info, listeners):
        self._profile = info
        self._listeners = listeners
        return

    def setConnector(self, connector):
        self._connector = connector
        return

    ##
    # @if jp
    # @brief バッファからデータを取得する
    #
    # @param self
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
    # @param self
    # @return
    #
    # @endif
    #
    def get(self):
        self._rtcout.RTC_PARANOID("OutPortCSPProvider.get()")

        if not self._connector:
            self.onSenderError()
            return (OpenRTM.UNKNOWN_ERROR, "")

        try:
            ret, cdr = self._connector.read()

            if ret == OpenRTM_aist.BufferStatus.BUFFER_OK:
                if cdr is None:
                    self._rtcout.RTC_ERROR("buffer is empty.")
                    return (OpenRTM.BUFFER_EMPTY, "")

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
            return (OpenRTM.UNKNOWN_ERROR, "")

        return self.convertReturn(ret, cdr)

    ##
    # @if jp
    # @brief データ読み込み可能かを確認
    #
    # @param self
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能、False：読み込み不可
    #
    #
    # @else
    # @brief
    #
    # @param self
    # @param retry
    # @return
    #
    # @endif
    #

    def is_readable(self, retry):
        self._rtcout.RTC_PARANOID("is_readable()")
        if self._connector:
            return self._connector.isReadable(retry)
        return False

    def onBufferRead(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ, self._profile, data)
        return data

    def onSend(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_SEND, self._profile, data)
        return data

    def onBufferEmpty(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY, self._profile)
        return

    def onBufferReadTimeout(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT, self._profile)
        return

    def onSenderEmpty(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)
        return

    def onSenderTimeout(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT, self._profile)
        return

    def onSenderError(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR, self._profile)
        return

    def convertReturn(self, status, data):
        if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
            data = self.onBufferRead(data)
            data = self.onSend(data)
            return (OpenRTM.PORT_OK, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
            self.onSenderError()
            return (OpenRTM.PORT_ERROR, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
            # never come here
            return (OpenRTM.BUFFER_FULL, data)

        elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
            self.onBufferEmpty()
            self.onSenderEmpty()
            return (OpenRTM.BUFFER_EMPTY, data)

        elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
            self.onSenderError()
            return (OpenRTM.PORT_ERROR, data)

        elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
            self.onBufferReadTimeout()
            self.onSenderTimeout()
            return (OpenRTM.BUFFER_TIMEOUT, data)

        else:
            return (OpenRTM.UNKNOWN_ERROR, data)


def OutPortCSPProviderInit():
    factory = OpenRTM_aist.OutPortProviderFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.OutPortCSPProvider)
