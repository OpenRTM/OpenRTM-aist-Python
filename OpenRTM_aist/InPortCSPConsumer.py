#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file InPortCSPConsumer.py
# @if jp
# @brief `InPortCSPConsumer`の状態と操作をまとめる。
# @else
# @brief Encapsulate the state and operations of InPortCSPConsumer.
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
# @class InPortCSPConsumer
# @brief InPortCSPConsumer クラス
#
# CSPモデルのチャネルを模擬した入力ポートプロバイダーの実装クラス。
#
#
# @else
# @class InPortCSPConsumer
# @brief InPortCSPConsumer class
#
#
#
# @endif
#
class InPortCSPConsumer(OpenRTM_aist.InPortCorbaConsumerBase):

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
        OpenRTM_aist.InPortCorbaConsumerBase.__init__(
            self, CSP.InPortCsp, "csp_channel")
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("InPortCSPConsumer")
        self._query_state = threading.local()
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    #
    # @param CorbaConsumer `CorbaConsumer`の値。
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    #
    # @param CorbaConsumer Value of CorbaConsumer.
    # @endif
    #
    def __del__(self, CorbaConsumer=OpenRTM_aist.CorbaConsumer):
        self._rtcout.RTC_PARANOID("~InPortCSPConsumer()")
        OpenRTM_aist.InPortCorbaConsumerBase.__del__(self)

    ##
    # @if jp
    # @brief バッファにデータを書き込む
    #
    #
    # @param data 書込対象データ
    # @return リターンコード
    # PORT_OK：正常完了
    # PORT_ERROR：バッファ書き込みエラー、通常は発生しない
    # SEND_FULL：バッファがフル
    # SEND_TIMEOUT：書き込みタイムアウト
    # UNKNOWN_ERROR：その他のエラー
    # CONNECTION_LOST：通信エラー
    #
    # @else
    # @brief Deliver CDR data to the receiver.
    #
    #
    # @param data
    # @return
    #
    # @endif
    #

    def put(self, data):
        self._rtcout.RTC_PARANOID("put()")

        try:
            outportcsp = self._ptr()
            if outportcsp:
                ret = outportcsp.put(data)
                return self.convertReturnCode(ret)
            return self.CONNECTION_LOST
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST

    ##
    # @if jp
    # @brief 書き込み可能かを接続先のProviderに確認
    #
    #
    # @return True：書き込み可能、False：書き込み不可
    #
    # @else
    # @brief Get the local admission state.
    #
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
    # @brief 受信準備が整っているか確認する。
    # @param retry 再試行の問い合わせかどうか。
    # @param option ガード照合に使用するオプション。
    # @else
    # @brief Check whether the receiver is ready.
    # @param retry Whether this query is a retry.
    # @param option Options used for guard matching.
    # @endif
    def isWritable(self, retry=False, option=[]):
        self._rtcout.RTC_PARANOID("isWritable()")
        self._query_state.value = CSP.NOT_READY
        try:
            inportcsp = self._ptr()
            if inportcsp:
                self._query_state.value = inportcsp.is_writable(retry, option)
                return self._query_state.value == CSP.READY
            return False
        except BaseException:
            self._rtcout.RTC_WARN("Exception caught from InPort.isWritable().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return False

    ##
    # @if jp
    # @brief ガード条件を満たすかをProviderに確認
    #
    #
    # @param option パラメータ
    # @return True：条件一致、False：条件不一致
    #
    # @else
    # @brief Match the sender options against the receiver guard.
    #
    #
    # @param option
    # @return
    #
    # @endif
    #
    def matchCondition(self, option=[]):
        self._rtcout.RTC_PARANOID("matchCondition()")
        try:
            inportcsp = self._ptr()
            if inportcsp:
                return inportcsp.match_condition(option)
            return False
        except BaseException:
            self._rtcout.RTC_WARN("Exception caught from InPort.matchCondition().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return False

    ##
    # @if jp
    # @brief リターンコード変換
    # @param ret `ret`の値。
    # @else
    # @brief Return codes conversion
    # @param ret Value of ret.
    # @endif
    #
    # ReturnCode convertReturnCode(OpenRTM::PortStatus ret)

    def convertReturnCode(self, ret):
        if ret == RTC.PORT_OK:
            return self.PORT_OK

        elif ret == RTC.PORT_ERROR:
            return self.PORT_ERROR

        elif ret == RTC.BUFFER_FULL:
            return self.SEND_FULL

        elif ret == RTC.BUFFER_TIMEOUT:
            return self.SEND_TIMEOUT

        elif ret == RTC.UNKNOWN_ERROR:
            return self.UNKNOWN_ERROR

        else:
            return self.UNKNOWN_ERROR


##
# @if jp
# @brief `InPortCSPConsumer`のFactoryを登録する。
# @else
# @brief Register the factory for InPortCSPConsumer.
# @endif
def InPortCSPConsumerInit():
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.InPortCSPConsumer)
