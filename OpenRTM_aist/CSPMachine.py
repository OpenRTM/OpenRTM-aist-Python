#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file StaticFSM.py
# @brief Static FSM framework based on Macho
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import OpenRTM_aist.Macho
import OpenRTM_aist.StaticFSM
import RTC


##
# @if jp
#
# @class CSPMachine
#
# @brief 有限状態機械、CSPOutPort、CSPInPortを管理するクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPMachine
#
# @brief
#
#
# @since 2.0.0
#
# @endif
#
class CSPMachine(OpenRTM_aist.StaticFSM.Machine):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    #
    # @endif
    #
    def __init__(self, TOP, comp, cspmgr):
        OpenRTM_aist.StaticFSM.Machine.__init__(self, TOP, comp)
        self._manager = cspmgr
        #self._ctrl = OpenRTM_aist.CSPManager.CSPThreadCtrl()

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief Destructor
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass

    def init_other(self, other):
        pass

    def equal(self, snapshot):
        pass
    ##
    # @if jp
    #
    # @brief RTC取得
    #
    # @param self
    # @return RTC
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    #

    def getComp(self):
        return self._rtComponent

    ##
    # @if jp
    #
    # @brief FSMのイベントを実行する
    # 受信済みのイベント、送信可能なInPortを選択してイベントを実行する
    # OutPortを登録している場合はデータを送信する。
    # イベント実行可能なポートがない場合はタイムアウトまで待機する
    # この時、送信するデータは事前に設定しておく必要がある
    #
    # @param self
    # @param timeout タイムアウトまでの時間
    # @return イベント実行したポート。イベントを実行できなかった場合はNoneを返す。
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param timeout
    # @return
    #
    # @endif
    #
    def run_event(self, timeout=10):
        ret, outport, inport = self._manager.select(timeout)
        if ret:
            if inport:
                event = inport.readData()
                event()
                return inport
            elif outport:
                outport.write()
                return outport
        return None
