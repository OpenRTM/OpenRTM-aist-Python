#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file DataIn.py
# @if jp
# @brief 選択した入力ポートからデータを読み出すサンプルRTC。
# @else
# @brief Sample RTC receiving data from the selected input port.
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

import sys
import time

import RTC
import OpenRTM_aist

datain_spec = ["implementation_id", "DataIn",
               "type_name", "DataIn",
               "description", "Console output component",
               "version", "1.0",
               "vendor", "Shinji Kurihara",
               "category", "example",
               "activity_type", "DataFlowComponent",
               "max_instance", "10",
               "language", "Python",
               "lang_type", "script",
               ""]


##
# @if jp
# @brief 選択した入力ポートからデータを読み出すサンプルRTC。
# @else
# @brief Sample RTC receiving data from the selected input port.
# @endif
class DataIn(OpenRTM_aist.DataFlowComponentBase):
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
        self._inport = OpenRTM_aist.CSPInPort(
            "in", self._data)
        # Set InPort buffer
        self.addInPort("in", self._inport)

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
        # 今回の候補だけを登録する。 / Register candidates for this operation only.
        try:
            self._inport.setManager(self._cspmanager)
            ret, outport, inport = self._cspmanager.select(100)
            if ret:
                if inport:
                    print("aaaaaa")
                    inport.readData()
                    #self._rtcout.RTC_ERROR("dataread: %s", (str(inport.readData())))
        finally:
            # 選択済み通信の後で解除する。 / Detach after the selected communication.
            self._cspmanager.reset()
        return RTC.RTC_OK


##
# @if jp
# @brief `DataIn`のFactoryを登録する。
# @param manager 関連付けるManager。
# @else
# @brief Register the factory for DataIn.
# @param manager Manager to associate with the object.
# @endif
def DataInInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=datain_spec)
    manager.registerFactory(profile,
                            DataIn,
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
    DataInInit(manager)

    # Create a component
    _ = manager.createComponent("DataIn")


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
