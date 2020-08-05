#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  InPortSHMProvider.py
# @brief InPortSHMProvider class
# @date  $Date: 2016/01/08 $
# @author Nobuhiko Miyamoto


import OpenRTM_aist
import OpenRTM


##
# @if jp
# @class InPortSHMProvider
# @brief InPortSHMProvider クラス
#
# 通信手段に 共有メモリ を利用した入力ポートプロバイダーの実装クラス。
#
#
# @else
# @class InPortSHMProvider
# @brief InPortSHMProvider class
#
#
#
# @endif
#
class InPortSHMProvider(OpenRTM_aist.InPortProvider,
                        OpenRTM_aist.SharedMemory):

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
        OpenRTM_aist.InPortProvider.__init__(self)
        OpenRTM_aist.SharedMemory.__init__(self)

        # PortProfile setting
        self.setInterfaceType("shared_memory")
        self._objref = self._this()

        self._buffer = None

        self._profile = None
        self._listeners = None

        orb = OpenRTM_aist.Manager.instance().getORB()
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ior",
                                                          orb.object_to_string(self._objref)))
        self._properties.append(OpenRTM_aist.NVUtil.newNV("dataport.corba_cdr.inport_ref",
                                                          self._objref))

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
    # @brief
    #
    #
    #
    # @param data
    #
    # @endif
    #
    # ::OpenRTM::PortStatus put()
    #  throw (CORBA::SystemException);
    def put(self):

        try:
            self._rtcout.RTC_PARANOID("InPortCorbaCdrProvider.put()")

            shm_data = self.read()

            if not self._connector:
                self.onReceiverError(shm_data)
                return OpenRTM.PORT_ERROR

            self._rtcout.RTC_PARANOID("received data size: %d", len(shm_data))

            shm_data = self.onReceived(shm_data)

            ret = self._connector.write(shm_data)

            return self.convertReturn(ret, shm_data)

        except BaseException:
            self._rtcout.RTC_TRACE(OpenRTM_aist.Logger.print_exception())
            return OpenRTM.UNKNOWN_ERROR

    def onBufferWrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
        return data

    def onBufferFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_FULL, self._profile, data)
        return data

    def onBufferWriteTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE_TIMEOUT, self._profile, data)
        return data

    def onBufferWriteOverwrite(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
        return data

    def onReceived(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
        return data

    def onReceiverFull(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
        return data

    def onReceiverTimeout(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_TIMEOUT, self._profile, data)
        return data

    def onReceiverError(self, data):
        if self._listeners is not None and self._profile is not None:
            _, data = self._listeners.notifyData(
                OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_ERROR, self._profile, data)
        return data

    def convertReturn(self, status, data):
        if status == OpenRTM_aist.BufferStatus.BUFFER_OK:
            self.onBufferWrite(data)
            return OpenRTM.PORT_OK

        elif status == OpenRTM_aist.BufferStatus.BUFFER_ERROR:
            self.onReceiverError(data)
            return OpenRTM.PORT_ERROR

        elif status == OpenRTM_aist.BufferStatus.BUFFER_FULL:
            data = self.onBufferFull(data)
            self.onReceiverFull(data)
            return OpenRTM.BUFFER_FULL

        elif status == OpenRTM_aist.BufferStatus.BUFFER_EMPTY:
            return OpenRTM.BUFFER_EMPTY

        elif status == OpenRTM_aist.BufferStatus.PRECONDITION_NOT_MET:
            self.onReceiverError(data)
            return OpenRTM.PORT_ERROR

        elif status == OpenRTM_aist.BufferStatus.TIMEOUT:
            data = self.onBufferWriteTimeout(data)
            self.onReceiverTimeout(data)
            return OpenRTM.BUFFER_TIMEOUT

        else:
            self.onReceiverError(data)
            return OpenRTM.UNKNOWN_ERROR


def InPortSHMProviderInit():
    factory = OpenRTM_aist.InPortProviderFactory.instance()
    factory.addFactory("shared_memory",
                       OpenRTM_aist.InPortSHMProvider)
