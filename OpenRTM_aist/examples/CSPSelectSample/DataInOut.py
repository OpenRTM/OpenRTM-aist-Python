#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file DataInOut.py
# @if jp
# @brief CSP入力と出力を選択して実行するサンプルRTC。
# @else
# @brief Sample RTC selecting between CSP input and output.
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

datainout_spec = ["implementation_id", "DataInOut",
                  "type_name", "DataInOut",
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
# @brief CSP入力と出力を選択して実行するサンプルRTC。
# @else
# @brief Sample RTC selecting between CSP input and output.
# @endif
class DataInOut(OpenRTM_aist.DataFlowComponentBase):
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
        self._indata1 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._indata2 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._indata3 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._outdata1 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._outdata2 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._outdata3 = RTC.TimedLong(RTC.Time(0, 0), 0)
        self._cspmanager = OpenRTM_aist.CSPManager()
        self._inport1 = OpenRTM_aist.CSPInPort(
            "in1", self._indata1)
        self._inport2 = OpenRTM_aist.CSPInPort(
            "in2", self._indata2)
        self._inport3 = OpenRTM_aist.CSPInPort(
            "in3", self._indata3)
        self._outport1 = OpenRTM_aist.CSPOutPort(
            "out1", self._outdata1)
        self._outport2 = OpenRTM_aist.CSPOutPort(
            "out2", self._outdata2)
        self._outport3 = OpenRTM_aist.CSPOutPort(
            "out3", self._outdata3)
        # Set InPort buffer
        self.addInPort("in1", self._inport1)
        self.addInPort("in2", self._inport2)
        self.addInPort("in3", self._inport3)
        self.addOutPort("out1", self._outport1)
        self.addOutPort("out2", self._outport2)
        self.addOutPort("out3", self._outport3)

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
        self._outdata1.data = 1
        self._outdata2.data = 1
        self._outdata3.data = 1
        # 今回の候補だけを登録する。 / Register candidates for this operation only.
        try:
            self._inport1.setManager(self._cspmanager)
            self._inport2.setManager(self._cspmanager)
            self._inport3.setManager(self._cspmanager)
            self._outport1.setManager(self._cspmanager)
            self._outport2.setManager(self._cspmanager)
            self._outport3.setManager(self._cspmanager)
            ret, outport, inport = self._cspmanager.select(100)
            if ret:
                if inport:
                    inport.readData()
                    self._rtcout.RTC_ERROR("dataread: %s", (inport.name()))
                    #self._rtcout.RTC_ERROR("dataread: %s %s", (inport.name(), str(inport.readData())))
                elif outport:
                    self._rtcout.RTC_ERROR("datawrite: %s", outport.name())
                    outport.writeData()

        finally:
            # 選択済み通信の後で解除する。 / Detach after the selected communication.
            self._cspmanager.reset()
        return RTC.RTC_OK


##
# @if jp
# @brief `DataInOut`のFactoryを登録する。
# @param manager 関連付けるManager。
# @else
# @brief Register the factory for DataInOut.
# @param manager Manager to associate with the object.
# @endif
def DataInOutInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=datainout_spec)
    manager.registerFactory(profile,
                            DataInOut,
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
    DataInOutInit(manager)

    # Create a component
    _ = manager.createComponent("DataInOut")


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
