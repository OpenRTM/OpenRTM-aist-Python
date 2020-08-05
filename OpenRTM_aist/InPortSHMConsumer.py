#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  InPortSHMConsumer.py
# @brief InPortSHMConsumer class
# @date  $Date: 2016-01-12 $
# @author Nobuhiko Miyamoto
#


import OpenRTM_aist
import OpenRTM__POA

import threading

##
# @if jp
#
# @class InPortSHMConsumer
#
# @brief InPortSHMConsumer クラス
#
# 通信手段に 共有メモリ を利用した入力ポートコンシューマの実装クラス。
#
#
# @else
# @class InPortCorbaCdrConsumer
#
# @brief InPortCorbaCdrConsumer class
#
#
#
# @endif
#


class InPortSHMConsumer(OpenRTM_aist.InPortCorbaCdrConsumer):
    """
    """

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
    # Constructor
    #
    # @param self
    #
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.InPortCorbaCdrConsumer.__init__(self)
        OpenRTM_aist.CorbaConsumer.__init__(
            self, OpenRTM__POA.PortSharedMemory)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("InPortSHMConsumer")
        self._properties = None

        self._shm_address = str(OpenRTM_aist.uuid1())

        self._shmem = OpenRTM_aist.SharedMemory()

        self._mutex = threading.RLock()

        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    # @param CorbaConsumer
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    # @param CorbaConsumer
    #
    # @endif
    #
    def __del__(self, CorbaConsumer=OpenRTM_aist.CorbaConsumer):
        self._rtcout.RTC_PARANOID("~InPortSHMConsumer()")
        CorbaConsumer.__del__(self)
        self._shmem.close_memory(True)

        oid = OpenRTM_aist.Manager.instance().getPOA().servant_to_id(self._shmem)
        OpenRTM_aist.Manager.instance().getPOA().deactivate_object(oid)
        self._endian = True

        return

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    # プロバイダでコネクタプロファイルに共有メモリの空間名を保存するため、init関数で共有メモリの初期化を行う
    #
    # @param self
    # @param prop コネクタプロパティ
    #
    # @else
    # @brief Initializing configuration
    #
    #
    # @endif
    #
    # virtual void init(coil::Properties& prop);
    def init(self, prop):

        self._rtcout.RTC_TRACE("init()")
        self._properties = prop

        ds = prop.getProperty("shem_default_size")
        self._memory_size = self._shmem.string_to_MemorySize(ds)

        if prop.hasKey("serializer"):
            endian = prop.getProperty("serializer.cdr.endian")
            if not endian:
                self._rtcout.RTC_ERROR("init(): endian is not set.")
                endian = "little"

            endian = OpenRTM_aist.split(endian, ",")
            endian = OpenRTM_aist.normalize(endian[0])
            if endian == "little":
                self._endian = True
            elif endian == "big":
                self._endian = False
        else:
            self._endian = True

        return

    def setObject(self, obj):
        if OpenRTM_aist.CorbaConsumer.setObject(self, obj):
            portshmem = self._ptr()
            if portshmem:
                self._shmem.setInterface(portshmem)

                return True
        return False

    ##
    # @if jp
    # @brief 接続先へのデータ送信
    #
    # 接続先のポートへデータを送信する
    #
    # データのサイズは共有メモリも先頭8byteから取得する
    # データは共有メモリに書き込む
    #
    # @param self
    # @param data 送信するデータ
    # @return リターンコード
    #
    # @else
    # @brief Send data to the destination port
    #
    # @param self
    # @param data
    # @return
    #
    # @endif
    #
    # virtual ReturnCode put(const cdrMemoryStream& data);

    def put(self, data):
        self._rtcout.RTC_PARANOID("put()")

        try:
            portshmem = self._ptr()
            if portshmem:

                guard = OpenRTM_aist.ScopedLock(self._mutex)

                self._shmem.setEndian(self._endian)
                self._shmem.create_memory(self._memory_size, self._shm_address)
                self._shmem.write(data)

                ret = portshmem.put()
                del guard
                return self.convertReturnCode(ret)
            return self.CONNECTION_LOST
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST


def InPortSHMConsumerInit():
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("shared_memory",
                       OpenRTM_aist.InPortSHMConsumer)
