#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPInPort.py
# @if jp
# @brief 型付き入力と受信予約を管理する。
# @else
# @brief Manage typed input and receive reservations.
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

# Copyright (C) 2019
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
from OpenRTM_aist.CSPArbitration import CSPConnectionInfo
import copy
import threading


##
# @if jp
#
# @class CSPInPort
#
# @brief CSPInPort テンプレートクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPInPort
#
# @brief CSPInPort template class
#
#
# @since 2.0.0
#
# @endif
#
class CSPInPort(CSPConnectionInfo, OpenRTM_aist.InPortBase):
    SUCCESSFUL_GET_DATA = 0
    FAILED_DESERIALIZE = 1
    FAILED_TIMEOUT = 2
    FAILED_EMPTY = 3
    FAILED_GET_DATA = 4

    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # コンストラクタ。
    # パラメータとして与えられる T 型の変数にバインドされる。
    #
    # @param name EventInPort 名。EventInPortBase:name() により参照される。
    # @param value この EventInPort にバインドされる T 型の変数
    #
    # @param manager 関連付けるManager。
    # @else
    #
    # @brief A constructor.
    #
    # constructor.
    # This is bound to type-T variable given as a parameter.
    #
    # @param name A name of the EventInPort. This name is referred by
    #             EventInPortBase::name().
    # @param value type-T variable that is bound to this EventInPort.
    #                (The default value:64)
    #
    # @param manager Manager to associate with the object.
    # @endif
    #
    def __init__(self, name: str, value, manager=None) -> None:
        super(CSPInPort, self).__init__(name, "any")
        self._ctrl = OpenRTM_aist.CSPInPort.WorkerThreadCtrl()
        self._name = name
        self._value = value

        self._OnRead = None
        self._OnReadConvert = None

        self._channeltimeout = 10
        self._bufferzeromode = False
        self._manager = manager
        if manager:
            manager.addInPort(self)
        self._writingConnector = None
        self._syncmode = False

        marshaling_types = OpenRTM_aist.SerializerFactories.instance().getSerializerList(value)
        marshaling_types = OpenRTM_aist.flatten(marshaling_types).lstrip()
        self.addProperty("dataport.marshaling_types", marshaling_types)

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

    def __del__(self) -> None:
        super(CSPInPort, self).__del__()

    ##
    # @if jp
    #
    # @brief ポート名称を取得する。
    #
    # ポート名称を取得する。
    #
    # @return ポート名称
    #
    # @else
    #
    # @brief Get port name
    #
    # Get port name.
    #
    # @return The port name
    #
    # @endif
    #
    def name(self):
        return self._name

    ##
    # @if jp
    #
    # @brief 初期化関数
    #
    # @param prop 設定情報
    # channel_timeout：データ書き込み、読み込み時のタイムアウト
    # buffer.lengthが0の場合は非リングバッファモードに設定
    # データ読み込み待機状態に移行していないとデータを書き込むことができない
    # buffer.lengthが1以上の場合はリングバッファモードに設定
    # バッファに空きがある場合はデータの書き込みができる
    #
    # @else
    #
    # @brief Perform the init operation.
    #
    # @param prop
    #
    # @endif
    #
    def init(self, prop: 'OpenRTM_aist.Properties') -> None:
        super(CSPInPort, self).init(prop)

        channeltimeout = 10
        ret, channeltimeout = OpenRTM_aist.stringTo(
            channeltimeout, self._properties.getProperty("channel_timeout", "10"))
        if ret:
            self._channeltimeout = channeltimeout

        buff_prop = prop.getNode("buffer")
        length = 8
        ret, length = OpenRTM_aist.stringTo(
            length, buff_prop.getProperty("length", "8"))

        if length == 0:
            buff_prop.setProperty("length", "1")
            self._bufferzeromode = True

        self._thebuffer.init(buff_prop)

        self._syncmode = OpenRTM_aist.toBool(
            prop.getProperty("csp.sync_wait"), "YES", "NO", False)

        if not self._bufferzeromode:
            self._writable_listener = OpenRTM_aist.CSPInPort.IsWritableListener(
                self._thebuffer, self._ctrl, self._channeltimeout, self, self._manager)
            self._write_listener = OpenRTM_aist.CSPInPort.WriteListener(
                self._thebuffer, self._ctrl)
        else:
            self._writable_listener = OpenRTM_aist.CSPInPort.IsWritableZeroModeListener(
                self._thebuffer, self._ctrl, self._channeltimeout, self, self._manager)
            self._write_listener = OpenRTM_aist.CSPInPort.WriteZeroModeListener(
                self._thebuffer, self._ctrl)

    ##
    # @if jp
    #
    # @brief CSPManagerの設定
    #
    # @param manager CSPManager
    #
    # @else
    #
    # @brief Associate the port with a selection manager.
    #
    # @param manager
    #
    # @endif
    #
    def setManager(self, manager) -> None:
        self._writable_listener.setManager(manager)
        self._manager = manager
        if manager:
            self._manager.addInPort(self)

    ##
    # @if jp
    #
    # @brief CSPManagerの設定解除
    #
    #
    # @else
    #
    # @brief Remove the association between the port and its selection manager.
    #
    #
    # @endif
    #
    def releaseManager(self) -> None:
        self._writable_listener.releaseManager()
        self._manager = None

    ##
    # @if jp
    #
    # @brief 書き込み処理を開始したコネクタを登録
    #
    # @param con InPortConnector
    #
    #
    # @else
    #
    # @brief Set writing connector.
    #
    # @param con
    #
    # @endif
    #
    def setWritingConnector(self, con) -> None:
        self._writingConnector = con

    ##
    # @if jp
    #
    # @brief 接続先のOutPortに入力可能であることを通知
    # バッファがフルになる、もしくは待機中のOutPortがなくなるまで、接続先のコネクタのデータを読み込む
    # バッファからデータを読み込んだ場合は、この関数を呼び出す必要がある
    #
    #
    #
    # @else
    #
    # @brief Notify the manager of a request and determine selection admission.
    #
    #
    # @endif
    #
    def notify(self) -> None:
        for con in self._connectors:
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if not self._syncmode:
                if self._ctrl._writing:
                    self._ctrl._cond.wait(self._channeltimeout)
            else:
                if self._ctrl._writing:
                    self._ctrl._cond.wait(self._channeltimeout)
                guard_ctrl.unlock()
            if not self._thebuffer.full():
                if con.isReadable(False):
                    ret, cdr = con.readBuff()
                    if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                        self._thebuffer.write(cdr)
                    else:
                        self._rtcout.RTC_ERROR(
                            "notify read error:%s", (OpenRTM_aist.DataPortStatus.toString(ret)))

    ##
    # @if jp
    #
    # @brief コネクタ接続関数
    # InPortBaseの接続処理のほかに、コネクタに書き込み確認時、書き込み時のコールバック関数を設定する
    #
    # @param connector_profile コネクタプロファイル
    # @return ret, prof
    # ret：リターンコード
    # prof：コネクタプロファイル
    #
    # @return ポート名称
    #
    # @else
    #
    # @brief Process a connection notification and finalize connector information.
    #
    # @param connector_profile
    # @return ret, prof
    #
    # @endif
    #

    def notify_connect(self, connector_profile):
        ret, prof = super(CSPInPort, self).notify_connect(connector_profile)
        _ = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            con.setIsWritableListener(self._writable_listener)
            con.setWriteListener(self._write_listener)
        return (ret, prof)

    ##
    # @if jp
    #
    # @brief リングバッファ使用モード時に指定コネクタの読み込み確認、データの読み込みを行う
    #
    # @param con コネクタ
    # @param retry True：再検索、False：通常の書き込み確認
    # @return ret, data
    # ret：SUCCESSFUL_GET_DATA：データ取得成功、FAILED_DESERIALIZE：復号失敗、FAILED_TIMEOUT：タイムアウトにより失敗、FAILED_EMPTY：空のデータを取得、FAILED_GET_DATA：データの読み込み可能なコネクタが存在しない
    # prof：読み込んだデータ
    #
    # @return ポート名称
    #
    # @else
    #
    # @brief Get data buffer mode.
    #
    # @param con
    # @param retry
    # @return ret, data
    #
    # @endif
    #
    def getDataBufferMode(self, con, retry: bool):
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
        if not self._syncmode:
            guard_ctrl.lock()
        if not self._thebuffer.empty():
            _, value = self._thebuffer.read()
            guard_ctrl.unlock()
            self.notify()
            ret, data = con.deserializeData(value)
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                return CSPInPort.SUCCESSFUL_GET_DATA, data
            else:
                self._rtcout.RTC_ERROR("deserialize error")
        elif self._ctrl._writing:
            self._ctrl._cond.wait(self._channeltimeout)
            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()
                guard_ctrl.unlock()
                self.notify()
                ret, data = con.deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return CSPInPort.SUCCESSFUL_GET_DATA, data
                else:
                    self._rtcout.RTC_ERROR("deserialize error")
                    return CSPInPort.FAILED_DESERIALIZE, None
            else:
                self._rtcout.RTC_ERROR("read timeout")
                return CSPInPort.FAILED_TIMEOUT, None
        else:
            guard_ctrl.unlock()
            readable = con.isReadable(retry)
            if readable:
                ret, value = con.read()
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return CSPInPort.SUCCESSFUL_GET_DATA, value
                else:
                    self._rtcout.RTC_ERROR("empty read error:%s",
                                           (OpenRTM_aist.DataPortStatus.toString(ret)))
                    return CSPInPort.FAILED_EMPTY, None
        return CSPInPort.FAILED_GET_DATA, None

    ##
    # @if jp
    #
    # @brief リングバッファ使用モード時にデータの受信を行う
    #
    # @return ret, data
    # ret：True：読み込み成功、False：バッファがemptyでかつ読み込み可能なコネクタが存在しない
    # data：データ
    #
    #
    # @else
    #
    # @brief Perform the data pull buffer mode operation.
    #
    # @return ret, data
    #
    # @endif
    #
    def dataPullBufferMode(self):
        guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return False, None

        if self._thebuffer.empty():
            for con in self._connectors:
                ret, value = self.getDataBufferMode(con, False)
                if ret == CSPInPort.SUCCESSFUL_GET_DATA:
                    self._ctrl._connectors = []
                    self._ctrl._searched_connectors = []
                    return True, value
                elif ret != CSPInPort.FAILED_GET_DATA:
                    return False, value
                else:
                    self._ctrl._searched_connectors.append(con)

        else:
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
            if not self._syncmode:
                guard_ctrl.lock()

            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()
                guard_ctrl.unlock()
                self.notify()
                ret, data = self._connectors[0].deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return True, data
                else:
                    self._rtcout.RTC_ERROR("deserialize error")
                    return False, None
            else:
                self._rtcout.RTC_ERROR("value read error")
                guard_ctrl.unlock()
                self.notify()
                return False, None
        return False, None

    ##
    # @if jp
    #
    # @brief リングバッファ使用モード時にデータの再受信を行う
    # データの送受信時は片方がコネクタ選択時にスレッドをロックするロックモード、
    # もう片方がスレッドをロックしない非ロックモードに設定する必要がある。
    # 非ロックモードの場合はデータ選択時にis_writable、is_readable関数が呼ばれた場合、
    # 再検索するコネクタのリストに追加して後で再検索する。
    #
    # @return ret, data
    # ret：True：読み込み成功、False：バッファがemptyでかつ読み込み可能なコネクタが存在しない
    # data：データ
    #
    #
    # @else
    #
    # @brief Perform the data pull buffer mode retry operation.
    #
    # @return ret, data
    #
    # @endif
    #
    def dataPullBufferModeRetry(self):
        if self._thebuffer.empty():
            cons = self._ctrl._connectors[:]
            for con in cons:
                ret, value = self.getDataBufferMode(con, True)
                if ret == CSPInPort.SUCCESSFUL_GET_DATA:
                    self._ctrl._connectors = []
                    self._ctrl._searched_connectors = []
                    return True, value
                elif ret != CSPInPort.FAILED_GET_DATA:
                    return False, value
            self._ctrl._connectors = []
            self._ctrl._searched_connectors = []

        else:
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
            if not self._syncmode:
                guard_ctrl.lock()

            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()
                guard_ctrl.unlock()
                self.notify()
                ret, data = self._connectors[0].deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return True, data
                else:
                    self._rtcout.RTC_ERROR("deserialize error")
                    return False, None
            else:
                self._rtcout.RTC_ERROR("value read error")
                guard_ctrl.unlock()
                self.notify()
                return False, None
        return False, None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時に指定コネクタの読み込み確認、データの読み込みを行う
    #
    # @param con コネクタ
    # @param retry True：再検索、False：通常の書き込み確認
    # @return ret, data
    # ret：SUCCESSFUL_GET_DATA：データ取得成功、FAILED_DESERIALIZE：復号失敗、FAILED_GET_DATA：データの読み込み可能なコネクタが存在しない
    # prof：読み込んだデータ
    #
    #
    # @else
    #
    # @brief Get data zero mode.
    #
    # @param con
    # @param retry
    # @return ret, data
    #
    # @endif
    #
    def getDataZeroMode(self, con, retry: bool):
        if con.isReadable(retry):
            #import time
            # time.sleep(1)
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
            if not self._syncmode:
                guard_ctrl.lock()
            ret, value = con.read()
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                return CSPInPort.SUCCESSFUL_GET_DATA, value
            else:
                self._rtcout.RTC_ERROR(
                    "read error:%s", (OpenRTM_aist.DataPortStatus.toString(ret)))
                return CSPInPort.FAILED_DESERIALIZE, None
        return CSPInPort.FAILED_GET_DATA, None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時にデータの受信を行う
    #
    # @return ret, data
    # ret：True：読み込み成功、False：読み込み可能なコネクタが存在しない
    # data：データ
    #
    #
    # @else
    #
    # @brief Perform the data pull zero mode operation.
    #
    # @return ret, data
    #
    # @endif
    #
    def dataPullZeroMode(self):
        _ = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            ret, value = self.getDataZeroMode(con, False)
            if ret == CSPInPort.SUCCESSFUL_GET_DATA:
                self._ctrl._connectors = []
                self._ctrl._searched_connectors = []
                return True, value
            elif ret == CSPInPort.FAILED_GET_DATA:
                self._ctrl._searched_connectors.append(con)

            else:
                return False, value

        return False, None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時にデータの再受信確認を行う
    #
    # @return ret, data
    # ret：True：読み込み成功、False：バッファがemptyでかつ読み込み可能なコネクタが存在しない
    # data：データ
    #
    #
    # @else
    #
    # @brief Perform the data pull zero mode retry operation.
    #
    # @return ret, data
    #
    # @endif
    #
    def dataPullZeroModeRetry(self):
        cons = self._ctrl._connectors[:]
        self._rtcout.RTC_TRACE("reselect %d connectors", (len(cons)))
        for con in cons:
            ret, value = self.getDataZeroMode(con, True)
            if ret == CSPInPort.SUCCESSFUL_GET_DATA:
                self._ctrl._connectors = []
                self._ctrl._searched_connectors = []
                return True, value
            elif ret != CSPInPort.FAILED_GET_DATA:
                self._ctrl._connectors = []
                self._ctrl._searched_connectors = []
                return False, value
        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []
        return False, None

    ##
    # @if jp
    #
    # @brief データ読み込み可能なコネクタを選択し、
    # self._valueに読み込んだデータを格納する
    #
    #
    # @return True：読み込み成功、False：読み込み不可
    #
    #
    # @else
    #
    # @brief Select one ready registered port.
    #
    # @return
    #
    # @endif
    #

    def select(self):
        self._rtcout.RTC_TRACE("select()")
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if not self._syncmode:
            guard_ctrl.unlock()

        if not self._bufferzeromode:
            ret, value = self.dataPullBufferMode()
        else:
            ret, value = self.dataPullZeroMode()

        guard_ctrl.lock()
        if ret:
            self._value = value
        return ret

    ##
    # @if jp
    #
    # @brief 再検索リストのコネクタからデータ読み込み可能なコネクタを選択し、
    # self._valueに読み込んだデータを格納する
    #
    #
    # @return True：読み込み成功、False：読み込み不可
    #
    #
    # @else
    #
    # @brief Rescan retained communication candidates.
    #
    # @return
    #
    # @endif
    #
    def reselect(self):
        self._rtcout.RTC_TRACE("reselect()")
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
        if self._syncmode:
            guard.lock()

        if not self._bufferzeromode:
            ret, value = self.dataPullBufferModeRetry()
        else:
            ret, value = self.dataPullZeroModeRetry()
        if not self._syncmode:
            guard.lock()
        if ret:
            self._value = value
        return ret

    ##
    # @if jp
    #
    # @brief ロックモード、非ロックモードの設定
    # データの送受信時は片方がコネクタ選択時にスレッドをロックするロックモード、
    # もう片方がスレッドをロックしない非ロックモードに設定する必要がある。
    # 非ロックモードの場合はデータ選択時にis_writable、is_readable関数が呼ばれた場合、
    # 再検索するコネクタのリストに追加して後で再検索する。
    #
    #
    # @param mode True：ロックモード、False：非ロックモード
    #
    #
    # @else
    #
    # @brief Set sync mode.
    #
    # @param mode
    #
    # @endif
    #
    def setSyncMode(self, mode: bool) -> None:
        self._syncmode = mode

    ##
    # @if jp
    #
    # @brief ロックモード、非ロックモードの取得
    #
    #
    # @return True：ロックモード、False：非ロックモード
    #
    #
    # @else
    #
    # @brief Get sync mode.
    #
    # @return
    #
    # @endif
    #
    def getSyncMode(self):
        return self._syncmode

    ##
    # @if jp
    #
    # @brief select関数で格納したデータの取得
    #
    #
    # @return データ
    #
    #
    # @else
    #
    # @brief Get the data or event of the selected input.
    #
    # @return
    #
    # @endif
    #

    def readData(self):
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        self._rtcout.RTC_TRACE("readData()")
        if self._OnRead is not None:
            self._OnRead()
            self._rtcout.RTC_TRACE("OnRead called")

        if self._ctrl._writing:
            self._ctrl._cond.wait(self._channeltimeout)

        if self._writingConnector:
            self._writingConnector = None
            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()
                ret, data = self._connectors[0].deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return data

        return self._value

    ##
    # @if jp
    #
    # @brief データを読み込み可能なコネクタを選択しデータを取得する
    # 読み込み可能なコネクタが存在しない場合は待機する
    #
    #
    # @return データ(タイムアウトした場合はNone)
    #
    #
    # @else
    #
    # @brief Receive data from a connection.
    #
    # @return
    #
    # @endif
    #
    def read(self):
        self._rtcout.RTC_TRACE("DataType read()")
        if self._OnRead is not None:
            self._OnRead()
            self._rtcout.RTC_TRACE("OnRead called")

        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return None

        if not self._bufferzeromode:
            return self.readBufferMode()
        else:
            return self.readZeroMode()

    ##
    # @if jp
    #
    # @brief リングバッファ使用モード時のデータ読み込み処理
    # 読み込み可能なコネクタが存在しない場合は待機する
    #
    #
    # @return データ(タイムアウトした場合はNone)
    #
    #
    # @else
    #
    # @brief Perform the read buffer mode operation.
    #
    # @return
    #
    # @endif
    #

    def readBufferMode(self):
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []
        if not self._syncmode:
            guard.unlock()

        ret, data = self.dataPullBufferMode()
        if ret:
            return data
        else:
            guard.lock()
            if not self._syncmode:
                ret, data = self.dataPullBufferModeRetry()
                if ret:
                    return data
            if self._ctrl._writing or self._thebuffer.empty():
                self._ctrl._cond.wait(self._channeltimeout)
            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()

                ret, data = self._connectors[0].deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return data
                else:
                    self._rtcout.RTC_ERROR("deserialize error")
                    return None
            else:
                self._rtcout.RTC_ERROR("read timeout")
                return None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時のデータ読み込み処理
    # 読み込み可能なコネクタが存在しない場合は待機する
    #
    #
    # @return データ(タイムアウトした場合はNone)
    #
    #
    # @else
    #
    # @brief Perform the read zero mode operation.
    #
    # @return
    #
    # @endif
    #
    def readZeroMode(self):
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []
        if not self._syncmode:
            guard.unlock()

        ret, data = self.dataPullZeroMode()
        if ret:
            return data
        else:
            guard.lock()
            if not self._syncmode:
                ret, data = self.dataPullZeroModeRetry()
                if ret:
                    return data
            self._ctrl._waiting = True
            self._ctrl._cond.wait(self._channeltimeout)
            self._ctrl._waiting = False
            if not self._thebuffer.empty():
                _, value = self._thebuffer.read()
                ret, data = self._connectors[0].deserializeData(value)
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return data
                else:
                    self._rtcout.RTC_ERROR("deserialize error")
                    return None
            else:
                self._rtcout.RTC_ERROR("read timeout")
                return None

    ##
    # @if jp
    # @brief `On Read`を設定する。
    # @param on_read `on_read`の値。
    # @else
    # @brief Set on read.
    # @param on_read Value of on_read.
    # @endif
    def setOnRead(self, on_read) -> None:
        self._OnRead = on_read

    ##
    # @if jp
    # @brief `On Read Convert`を設定する。
    # @param on_rconvert `on_rconvert`の値。
    # @else
    # @brief Set on read convert.
    # @param on_rconvert Value of on_rconvert.
    # @endif
    def setOnReadConvert(self, on_rconvert) -> None:
        self._OnReadConvert = on_rconvert

    ##
    # @if jp
    #
    # @class IsWritableListener
    #
    # @brief データ書き込み確認リスナ基底クラス(リングバッファ使用モード)
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class IsWritableListener
    #
    # @brief Encapsulate the state and operations of IsWritableListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #

    class IsWritableListener(OpenRTM_aist.IsWritableListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param buff リングバッファ
        # @param control WorkerThreadCtrlオブジェクト
        # @param timeout 書き込み待機のタイムアウト時間
        # @param manager CSPチャネル管理マネージャ
        # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
        #
        #
        #
        # @param port 操作対象のポート。
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param buff
        # @param control
        # @param timeout
        # @param manager
        #
        # @param port Port to operate on.
        # @endif
        #
        def __init__(self, buff, control, timeout: int, port: 'CSPInPort', manager=None) -> None:
            self._ctrl = control
            self._buffer = buff
            self._channeltimeout = timeout
            self._manager = manager
            self._port = port
            self._mutex = threading.RLock()
        ##
        # @if jp
        #
        # @brief 書き込み確認時のコールバック関数
        # 他のコネクタがデータ書き込み中の場合は完了まで待機する
        # バッファがフルではない場合は書き込み状態に移行する
        # このため、書き込み可能な場合は必ずデータを書き込む必要がある
        #
        #
        # @param con InPortConnector
        # @param retry True：再検索、False：通常の書き込み確認
        # @return True：書き込み可能、False：書き込み不可
        #
        #
        #
        # @param option ガード照合に使用するオプション。
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param con
        # @param retry
        # @return
        #
        # @param option Options used for guard matching.
        # @endif
        #

        def __call__(self, con, retry: bool = False, option=None) -> bool:
            guard_manager = OpenRTM_aist.Guard.ScopedLock(self._mutex)

            if retry:
                if con not in self._ctrl._searched_connectors:
                    return False

            if self._manager:
                if self._manager.notify(inport=self._port, connector_id=getattr(con, 'id', lambda: None)()):
                    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
                    self._ctrl._writing = True
                    self._port.setWritingConnector(con)
                    return True
            guard_manager.unlock()
            guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if self._ctrl._writing:
                self._ctrl._cond.wait(self._channeltimeout)
            if not self._buffer.full():
                self._ctrl._writing = True
                return True
            else:
                self._ctrl._writing = False
                self._ctrl._connectors.append(con)
                return False

        ##
        # @if jp
        #
        # @brief CSPManagerの設定
        #
        # @param manager CSPManager
        #
        #
        #
        # @else
        #
        # @brief Associate the port with a selection manager.
        #
        # @param manager
        #
        # @endif
        #
        def setManager(self, manager) -> None:
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = manager

        ##
        # @if jp
        #
        # @brief CSPManagerの解除
        #
        #
        #
        #
        # @else
        #
        # @brief Remove the association between the port and its selection manager.
        #
        #
        # @endif
        #
        def releaseManager(self) -> None:
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = None

    ##
    # @if jp
    #
    # @class WriteListener
    #
    # @brief データ書き込み時のリスナ基底クラス(リングバッファ使用モード)
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class WriteListener
    #
    # @brief Encapsulate the state and operations of WriteListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #
    class WriteListener(OpenRTM_aist.WriteListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param buff リングバッファ
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param buff
        # @param control
        #
        # @endif
        #
        def __init__(self, buff, control) -> None:
            self._ctrl = control
            self._buffer = buff
        ##
        # @if jp
        #
        # @brief 書き込み時のコールバック関数
        # データをバッファに追加し、書き込み状態を解除する
        #
        #
        # @param data データ
        # @return リターンコード
        # BUFFER_OK：正常完了
        #
        #
        #
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param data
        # @return
        #
        # @endif
        #

        def __call__(self, data: bytes):
            _ = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            self._buffer.write(data)
            self._ctrl._writing = False
            self._ctrl._cond.notifyAll()
            return OpenRTM_aist.BufferStatus.BUFFER_OK

    ##
    # @if jp
    #
    # @class IsWritableZeroModeListener
    #
    # @brief データ書き込み確認リスナ基底クラス(非リングバッファ使用モード)
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class IsWritableZeroModeListener
    #
    # @brief Encapsulate the state and operations of IsWritableZeroModeListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #
    class IsWritableZeroModeListener(OpenRTM_aist.IsWritableListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param buff リングバッファ
        # @param control WorkerThreadCtrlオブジェクト
        # @param timeout 書き込み待機のタイムアウト時間
        # @param manager CSPチャネル管理マネージャ
        # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
        #
        #
        #
        # @param port 操作対象のポート。
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param buff
        # @param control
        # @param timeout
        # @param manager
        #
        # @param port Port to operate on.
        # @endif
        #
        def __init__(self, buff, control, timeout: int, port: 'CSPInPort', manager=None) -> None:
            self._ctrl = control
            self._buffer = buff
            self._channeltimeout = timeout
            self._port = port
            self._manager = manager
            self._mutex = threading.RLock()
        ##
        # @if jp
        #
        # @brief 書き込み確認時のコールバック関数
        # 他のコネクタがデータ書き込み中の場合は完了まで待機する
        # バッファがフルではない場合は書き込み状態に移行する
        # このため、書き込み可能な場合は必ずデータを書き込む必要がある
        #
        #
        # @param con InPortConnector
        # @param retry True：再検索、False：通常の書き込み確認
        # @return True：書き込み可能、False：書き込み不可
        #
        #
        #
        # @param option ガード照合に使用するオプション。
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param con
        # @param retry
        # @return
        #
        # @param option Options used for guard matching.
        # @endif
        #

        def __call__(self, con, retry: bool = False, option=None) -> bool:
            guard_manager = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            if retry:
                if con not in self._ctrl._searched_connectors:
                    return False
            if self._manager:
                if self._manager.notify(inport=self._port, connector_id=getattr(con, 'id', lambda: None)()):
                    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
                    self._ctrl._writing = True
                    self._port.setWritingConnector(con)
                    return True
            guard_manager.unlock()
            guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if self._ctrl._waiting and self._ctrl._writing:
                self._ctrl._cond.wait(self._channeltimeout)
            if self._ctrl._waiting:
                self._ctrl._writing = True
                return True
            else:
                self._ctrl._writing = False
                self._ctrl._connectors.append(con)
                return False

        ##
        # @if jp
        #
        # @brief CSPManagerの設定
        #
        # @param manager CSPManager
        #
        #
        #
        # @else
        #
        # @brief Associate the port with a selection manager.
        #
        # @param manager
        #
        # @endif
        #
        def setManager(self, manager) -> None:
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = manager

        ##
        # @if jp
        #
        # @brief CSPManagerの解除
        #
        #
        #
        #
        # @else
        #
        # @brief Remove the association between the port and its selection manager.
        #
        #
        # @endif
        #
        def releaseManager(self) -> None:
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = None

    ##
    # @if jp
    #
    # @class WriteZeroModeListener
    #
    # @brief データ書き込み時のリスナ基底クラス(非リングバッファ使用モード)
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class WriteZeroModeListener
    #
    # @brief Encapsulate the state and operations of WriteZeroModeListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #
    class WriteZeroModeListener(OpenRTM_aist.WriteListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param buff リングバッファ
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param buff
        # @param control
        #
        # @endif
        #
        def __init__(self, buff, control) -> None:
            self._ctrl = control
            self._buffer = buff
        ##
        # @if jp
        #
        # @brief 書き込み時のコールバック関数
        # 書き込み状態を解除しバッファにデータを追加する。
        #
        #
        # @param data データ
        # @return リターンコード
        # BUFFER_OK：正常完了
        #
        #
        #
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param data
        # @return
        #
        # @endif
        #

        def __call__(self, data):
            _ = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            self._ctrl._writing = False
            self._buffer.write(data)
            self._ctrl._cond.notifyAll()
            return OpenRTM_aist.BufferStatus.BUFFER_OK

    ##
    # @if jp
    # @brief `WorkerThreadCtrl`の状態と操作をまとめる。
    # @else
    # @brief Encapsulate the state and operations of WorkerThreadCtrl.
    # @endif
    class WorkerThreadCtrl:
        ##
        # @if jp
        # @brief インスタンスと内部状態を初期化する。
        # @else
        # @brief Initialize the instance and its internal state.
        # @endif
        def __init__(self) -> None:
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._writing = False
            self._waiting = False
            self._connectors = []
            self._searched_connectors = []
