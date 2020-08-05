#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
#  @file OutPortDirectProvider.py
#  @brief OutPortDirectProvider class
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
#


import OpenRTM_aist


##
# @if jp
# @class OutPortDirectProvider
# @brief OutPortDirectProvider クラス
#
# データをダイレクトに書き込むpull型通信を実現するOutPortプロバイダクラス
#
# @param self
#
# @else
# @class InPortDirectProvider
# @brief InPortDirectProvider class
#
#
# @param self
#
# @endif
#
class OutPortDirectProvider(OpenRTM_aist.OutPortProvider):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # @param self
    #
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.OutPortProvider.__init__(self)
        self.setInterfaceType("direct")

        self._listeners = None
        self._buffer = None
        self._profile = None
        #self._connector = None
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
        pass

    # void init(coil::Properties& prop);
    def init(self, prop):
        pass

    # virtual void setBuffer(BufferBase<cdrMemoryStream>* buffer);

    def setBuffer(self, buffer):
        self._buffer = buffer
        return

    # virtual void setListener(ConnectorInfo& info,
    #                          ConnectorListeners* listeners);

    def setListener(self, info, listeners):
        self._profile = info
        self._listeners = listeners
        return

    # virtual void setConnector(OutPortConnector* connector);

    def setConnector(self, connector):
        self._connector = connector
        return

    # inline void onBufferRead(const cdrMemoryStream& data)

    def onBufferRead(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ, self._profile, data)
        return data

    # inline void onSend(const cdrMemoryStream& data)

    def onSend(self, data):
        if self._listeners and self._profile:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_SEND, self._profile, data)
        return data

    # inline void onBufferEmpty()

    def onBufferEmpty(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY, self._profile)
        return

    # inline void onBufferReadTimeout()

    def onBufferReadTimeout(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_BUFFER_READ_TIMEOUT, self._profile)
        return

    # inline void onSenderEmpty()

    def onSenderEmpty(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)
        return

    # inline void onSenderTimeout()

    def onSenderTimeout(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_TIMEOUT, self._profile)
        return

    # inline void onSenderError()

    def onSenderError(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_SENDER_ERROR, self._profile)
        return


def OutPortDirectProviderInit():
    factory = OpenRTM_aist.OutPortProviderFactory.instance()
    factory.addFactory("direct",
                       OpenRTM_aist.OutPortDirectProvider)
