#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  InPortCorbaCdrConsumer.py
# @brief InPortCorbaCdrConsumer class
# @date  $Date: 2007-12-31 03:08:03 $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2006
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
#
# @class InPortCorbaCdrConsumer
#
# @brief InPortCorbaCdrConsumer クラス
#
# 通信手段に CORBA を利用した入力ポートコンシューマの実装クラス。
#
# @param DataType 本ポートにて扱うデータ型
#
# @since 1.0
#
# @else
# @class InPortCorbaCdrConsumer
#
# @brief InPortCorbaCdrConsumer class
#
# This is an implementation class of the input port Consumer
# that uses CORBA for means of communication.
#
# @param DataType Data type for this port
#
# @since 0.4.0
#
# @endif
#


class InPortCorbaCdrConsumer(OpenRTM_aist.InPortCorbaConsumerBase):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param buffer 当該コンシューマに割り当てるバッファオブジェクト
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param buffer The buffer object that is attached to this Consumer
    #
    # @endif
    #
    def __init__(self) -> None:
        OpenRTM_aist.InPortCorbaConsumerBase.__init__(
            self, OpenRTM.InPortCdr, "corba_cdr")
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("InPortCorbaCdrConsumer")
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
        self._rtcout.RTC_PARANOID("~InPortCorbaCdrConsumer()")
        OpenRTM_aist.InPortCorbaConsumerBase.__del__(self)
        return

    ##
    # @if jp
    # @brief 接続先へのデータ送信
    #
    # 接続先のポートへデータを送信するための純粋仮想関数。
    #
    # この関数は、以下のリターンコードを返す。
    #
    # - PORT_OK:       正常終了。
    # - PORT_ERROR:    データ送信の過程で何らかのエラーが発生した。
    # - SEND_FULL:     データを送信したが、相手側バッファがフルだった。
    # - SEND_TIMEOUT:  データを送信したが、相手側バッファがタイムアウトした。
    # - UNKNOWN_ERROR: 原因不明のエラー
    #
    # @param data 送信するデータ
    # @return リターンコード
    #
    # @else
    # @brief Send data to the destination port
    #
    # Pure virtual function to send data to the destination port.
    #
    # This function might the following return codes
    #
    # - PORT_OK:       Normal return
    # - PORT_ERROR:    Error occurred in data transfer process
    # - SEND_FULL:     Buffer full although OutPort tried to send data
    # - SEND_TIMEOUT:  Timeout although OutPort tried to send data
    # - UNKNOWN_ERROR: Unknown error
    #
    # @endif
    #
    # virtual ReturnCode put(const cdrMemoryStream& data);
    def put(self, data: bytes):
        self._rtcout.RTC_PARANOID("put()")

        try:
            inportcdr = self._ptr()

            if inportcdr:
                try:
                    return self.convertReturnCode(inportcdr.put(data))
                except CORBA.COMM_FAILURE as ex:
                    if ex.minor == omniORB.COMM_FAILURE_WaitingForReply:
                        self._rtcout.RTC_DEBUG("Retry put message")
                        return self.convertReturnCode(inportcdr.put(data))
                    else:
                        raise
                except BaseException:
                    raise
            return self.CONNECTION_LOST
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST

    ##
    # @if jp
    # @brief リターンコード変換
    # @else
    # @brief Return codes conversion
    # @endif
    #
    # ReturnCode convertReturnCode(OpenRTM::PortStatus ret)

    def convertReturnCode(self, ret):
        if ret == OpenRTM.PORT_OK:
            return self.PORT_OK

        elif ret == OpenRTM.PORT_ERROR:
            return self.PORT_ERROR

        elif ret == OpenRTM.BUFFER_FULL:
            return self.SEND_FULL

        elif ret == OpenRTM.BUFFER_TIMEOUT:
            return self.SEND_TIMEOUT

        elif ret == OpenRTM.UNKNOWN_ERROR:
            return self.UNKNOWN_ERROR

        else:
            return self.UNKNOWN_ERROR


def InPortCorbaCdrConsumerInit() -> None:
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("corba_cdr",
                       OpenRTM_aist.InPortCorbaCdrConsumer)
