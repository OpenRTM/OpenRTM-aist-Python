#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPMachine.py
# @if jp
# @brief CSP通信とStaticFSMの実行を連携する。
# @else
# @brief Integrate CSP communication with StaticFSM execution.
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
# @brief Integrate CSP communication with StaticFSM execution.
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
    #
    # @param TOP `TOP`の値。
    # @param comp `comp`の値。
    # @param cspmgr `cspmgr`の値。
    # @else
    #
    # @brief A constructor.
    #
    #
    # @param TOP Value of TOP.
    # @param comp Value of comp.
    # @param cspmgr Value of cspmgr.
    # @endif
    #
    def __init__(self, TOP, comp, cspmgr) -> None:
        OpenRTM_aist.StaticFSM.Machine.__init__(self, TOP, comp)
        self._manager = cspmgr
        #self._ctrl = OpenRTM_aist.CSPManager.CSPThreadCtrl()

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    #
    # @else
    #
    # @brief Destructor
    #
    #
    # @endif
    #
    def __del__(self) -> None:
        pass

    ##
    # @if jp
    # @brief `init other`に対応する処理を行う。
    # @param other `other`の値。
    # @else
    # @brief Perform the init other operation.
    # @param other Value of other.
    # @endif
    def init_other(self, other):
        pass

    ##
    # @if jp
    # @brief `equal`に対応する処理を行う。
    # @param snapshot `snapshot`の値。
    # @else
    # @brief Perform the equal operation.
    # @param snapshot Value of snapshot.
    # @endif
    def equal(self, snapshot):
        pass
    ##
    # @if jp
    #
    # @brief RTC取得
    #
    # @return RTC
    #
    # @else
    #
    # @brief Get the RTC owned by the FSM context.
    #
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
    # @param timeout タイムアウトまでの時間
    # @return イベント実行したポート。イベントを実行できなかった場合はNoneを返す。
    #
    # @else
    #
    # @brief Select communication and perform I/O or execute the FSM event.
    #
    # @param timeout
    # @return
    #
    # @endif
    #
    def run_event(self, timeout: int = 10):
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
