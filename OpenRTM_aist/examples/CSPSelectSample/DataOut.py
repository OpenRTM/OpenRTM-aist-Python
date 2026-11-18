#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file DataOut.py
# @if jp
# @brief CSP出力ポートからデータを送信するサンプルRTC。
# @else
# @brief Sample RTC sending data through CSP output ports.
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

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist

dataout_spec = ["implementation_id", "DataOut",
                "type_name", "DataOut",
                "description", "Data output component",
                "version", "1.0",
                "vendor", "Nobuhiko Miyamoto",
                "category", "example",
                "activity_type", "DataFlowComponent",
                "max_instance", "10",
                "language", "Python",
                "lang_type", "script",
                ""]


##
# @if jp
# @brief CSP出力ポートからデータを送信するサンプルRTC。
# @else
# @brief Sample RTC sending data through CSP output ports.
# @endif
class DataOut(OpenRTM_aist.DataFlowComponentBase):
    ##
    # @if jp
    # @brief インスタンスと内部状態を初期化する。
    # @param manager 関連付けるManager。
    # @else
    # @brief Initialize the instance and its internal state.
    # @param manager Manager to associate with the object.
    # @endif
    def __init__(self, manager):
        OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
        return

    ##
    # @if jp
    # @brief RTCのポート・設定・FSMを初期化する。
    # @else
    # @brief Initialize RTC ports, configuration and FSM state.
    # @endif
    def onInitialize(self):
        self._data = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._cspmanager = OpenRTM_aist.CSPManager()
        self._outport = OpenRTM_aist.CSPOutPort(
            "out", self._data)
        # Set OutPort buffer
        self.addOutPort("out", self._outport)

        return RTC.RTC_OK

    ##
    # @if jp
    # @brief 周期実行に対応する通信・制御処理を行う。
    # @param ec_id 実行コンテキストの識別子。
    # @else
    # @brief Perform communication and control for a periodic execution callback.
    # @param ec_id Execution context identifier.
    # @endif
    def onExecute(self, ec_id):
        self._data.data = 1
        OpenRTM_aist.setTimestamp(self._data)
        # 今回の候補だけを登録する。 / Register candidates for this operation only.
        try:
            self._outport.setManager(self._cspmanager)
            ret, outport, inport = self._cspmanager.select(100)
            if ret:
                if outport:
                    outport.writeData()

        finally:
            # 選択済み通信の後で解除する。 / Detach after the selected communication.
            self._cspmanager.reset()
        return RTC.RTC_OK


##
# @if jp
# @brief `DataOut`のFactoryを登録する。
# @param manager 関連付けるManager。
# @else
# @brief Register the factory for DataOut.
# @param manager Manager to associate with the object.
# @endif
def DataOutInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=dataout_spec)
    manager.registerFactory(profile,
                            DataOut,
                            OpenRTM_aist.Delete)


##
# @if jp
# @brief サンプルのFactoryを登録して自RTCを生成する。
# @param manager 関連付けるManager。
# @else
# @brief Register the sample factory and create its RTC.
# @param manager Manager to associate with the object.
# @endif
def MyModuleInit(manager):
    DataOutInit(manager)

    # Create a component
    _ = manager.createComponent("DataOut")


##
# @if jp
# @brief Managerを初期化してサンプルの実行ループを開始する。
# @else
# @brief Initialize the manager and start the sample execution loop.
# @endif
def main():
    # Initialize manager
    mgr = OpenRTM_aist.Manager.init(sys.argv)

    # Set module initialization proceduer
    # This procedure will be invoked in activateManager() function.
    mgr.setModuleInitProc(MyModuleInit)

    # Activate manager and register to naming service
    mgr.activateManager()

    # run the manager in blocking mode
    # runManager(False) is the default
    mgr.runManager()

    # If you want to run the manager in non-blocking mode, do like this
    # mgr.runManager(True)


if __name__ == "__main__":
    main()
