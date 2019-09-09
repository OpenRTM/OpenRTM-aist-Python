#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file CSPManager.py
# @brief CSP Manager class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import copy
import threading


##
# @if jp
#
# @class CSPManager
#
# @brief CSPOutPort、CSPInPortを管理するクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPManager
#
# @brief
#
#
# @since 2.0.0
#
# @endif
#
class CSPManager(object):
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
    def __init__(self):
        self._outports = []
        self._inports = []
        self._ctrl = OpenRTM_aist.CSPManager.CSPThreadCtrl()
        self._writableOutPort = None
        self._readableInPort = None

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # デストラクタ。
    #
    # @else
    #
    # @brief Destructor
    #
    # Destructor
    #
    # @endif
    #

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief CSPポートに設定したCSPManagerとの関連付けを解除
    #
    # @param self
    #
    # @else
    #
    # @brief
    #
    # @param self
    #
    # @endif
    #
    def reset(self):
        for port in self._outports:
            port.releaseManager()
        for port in self._inports:
            port.releaseManager()
        self._outports = []
        self._inports = []

    ##
    # @if jp
    #
    # @brief 書き込み可能なOutPortを選択する
    #
    # @param self
    # @return ret, port
    # ret：True(書き込み可能なOutPortが存在する)、False(存在しない)
    # port：書き込み可能なOutPort。選択できなかった場合はNone
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
    def selectOutPort(self):
        for port in self._outports:
            if port.select():
                return True, port
        return False, None

    ##
    # @if jp
    #
    # @brief 読み込み可能なInPortを選択する
    #
    # @param self
    # @return ret, port
    # ret：True(読み込み可能なInPortが存在する)、False(存在しない)
    # port：読み込み可能なInPort。選択できなかった場合はNone
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
    def selectInPort(self):
        for port in self._inports:
            if port.select():
                return True, port
        return False, None

    ##
    # @if jp
    #
    # @brief 読み込み可能なInPort、もしくは書き込み可能なOutPortを選択する
    # 読み込み可能なInPort、書き込み可能なOutPortが存在しない場合はタイムアウトまで待機する
    # 待機解除後、読み込み可能なInPort、もしくは書き込み可能なOutPortを再度選択する
    #
    # @param self
    # @param timeout 待機のタイムアウト時間
    # @return ret, outport, inport
    # ret：Ture(書き込み、読み込み可能なポートが存在)、False(タイムアウト)
    # outport：OutPortを選択した場合に、書き込み可能なOutPortを格納
    # inport：InPortを選択した場合に、読み込み可能なInortを格納
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
    def select(self, timeout):
        ret, port = self.selectOutPort()
        if ret:
            return ret, port, None
        ret, port = self.selectInPort()
        if ret:
            return ret, None, port

        if timeout >= 0:
            guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            self._ctrl._waiting = True
            self._ctrl._timeout = True
            self._ctrl._cond.wait(timeout)
            self._ctrl._waiting = False
            del guard
            if self._ctrl._timeout:
                return False, None, None
            else:
                if self._writableOutPort or self._readableInPort:
                    inport = self._readableInPort
                    outport = self._writableOutPort
                    self._writableOutPort = None
                    self._readableInPort = None
                    return True, outport, inport
        return False, None, None

    ##
    # @if jp
    #
    # @brief 待機状態解除を通知
    # select関数で待機している場合に、待機を解除する
    #
    # @param self
    # @return True：待機状態を解除、False：待機状態ではない
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

    def notify(self, outport=None, inport=None):
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        if self._ctrl._waiting:
            self._ctrl._timeout = False
            if outport:
                self._writableOutPort = outport
            elif inport:
                self._readableInPort = inport
            self._ctrl._cond.notify()
            return True
        else:
            return False

    ##
    # @if jp
    #
    # @brief InPortを追加
    #
    # @param self
    # @param port InPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param port
    #
    # @endif
    #
    def addInPort(self, port):
        self._inports.append(port)

    ##
    # @if jp
    #
    # @brief OutPortを追加
    #
    # @param self
    # @param port OutPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param port
    #
    # @endif
    #
    def addOutPort(self, port):
        self._outports.append(port)

    ##
    # @if jp
    #
    # @brief InPortを削除
    #
    # @param self
    # @param port InPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param port
    #
    # @endif
    #
    def removeInPort(self, port):
        self._inports.remove(port)

    ##
    # @if jp
    #
    # @brief Outortを削除
    #
    # @param self
    # @param port OutPort
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param port
    #
    # @endif
    #
    def removeOutPort(self, port):
        self._outports.remove(port)

    class CSPThreadCtrl:
        def __init__(self):
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._port = None
            self._waiting = False
            self._timeout = True
