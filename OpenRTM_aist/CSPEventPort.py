#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPEventPort.py
# @if jp
# @brief 受信したCSPイベントをFSMへ引き渡す。
# @else
# @brief Deliver received CSP events to the FSM.
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
import OpenRTM_aist.EventPort
import copy
import threading
import time
from contextlib import contextmanager


##
# @if jp
#
# @class CSPEventPort
#
# @brief CSPEventPort テンプレートクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPEventPort
#
# @brief CSPEventPort template class
#
#
# @since 2.0.0
#
# @endif
#
class CSPEventPort(CSPConnectionInfo, OpenRTM_aist.InPortBase):
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
    # @param fsm FSM
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
    # @param fsm
    #
    # @param manager Manager to associate with the object.
    # @endif
    #

    def __init__(self, name, fsm=None, manager=None):
        super(CSPEventPort, self).__init__(name, "any")
        self._ctrl = CSPEventPort.WorkerThreadCtrl()
        self._name = name
        self._value = None
        self._selected_value_ready = False

        self._OnRead = None

        self._singlebuffer = True
        self._eventbuffer = None

        self._channeltimeout = 10
        self._bufferzeromode = False
        self._fsm = fsm

        self._manager = manager
        if self._manager is not None:
            self._manager.addInPort(self)
        self._writingConnector = None
        self._syncmode = False

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # デストラクタ。
    #
    #
    # @else
    #
    # @brief Destructor
    #
    # Destructor
    #
    #
    # @endif
    #

    def __del__(self):
        super(CSPEventPort, self).__del__()

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
    # @brief 引数なしのイベントハンドラを登録する
    #
    # @param name イベント名
    # @param handler イベントハンドラ
    # コネクタ接続時にfsm_event_nameという要素を設定する。
    # fsm_event_nameとイベント名が一致するとイベントが実行される。
    # イベントハンドラにはMacho等で定義したイベントを入力する
    #
    #
    # @else
    # @brief Bind an event to a handler without a payload argument.
    #
    # @param name
    # @param handler
    #
    # @endif
    #

    def bindEvent0(self, name, handler):
        self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                      OpenRTM_aist.EventPort.EventBinder0(self._fsm, name, handler, self._eventbuffer))

    ##
    # @if jp
    #
    # @brief 引数ありのイベントハンドラを登録する
    #
    # @param name イベント名
    # @param handler イベントハンドラ
    # @param data_type 入力データ
    #
    # @else
    #
    # @brief Bind an event to a payload handler.
    #
    # @param name
    # @param handler
    # @param data_type
    #
    # @endif
    #
    def bindEvent1(self, name, handler, data_type):
        self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                      OpenRTM_aist.EventPort.EventBinder1(self._fsm, name, handler, data_type, self._eventbuffer))

    ##
    # @if jp
    #
    # @brief ガード条件を指定する
    #
    # @param cond ガード条件
    #
    # @else
    #
    # @brief Set the input admission predicate evaluated before communication.
    #
    # @param cond Guard Condition
    #
    # @endif
    #
    def setGuard(self, cond):
        self._cond = cond
        self._writable_listener.setGuard(cond)
        self._condition_listener.setGuard(cond)

    ##
    # @if jp
    #
    # @brief ガード条件を初期化する
    #
    #
    #
    #
    #
    # @else
    #
    # @brief Clear guard.
    #
    #
    # @endif
    #
    def clearGuard(self):
        self._cond = None
        self._writable_listener.clearGuard()
        self._condition_listener.clearGuard()
    ##
    # @if jp
    #
    # @brief 初期化関数
    #
    # @param prop コネクタのプロパティ
    # buffer(dataport.buffer)要素でバッファ長さ等を設定
    # channel_timeout(dataport.channel_timeout)要素で、
    # 送信可能なアウトポートが存在しない場合のブロックのタイムアウトを設定
    #
    # @return ポート名称
    #
    # @else
    #
    # @brief Get port name
    #
    # @param prop
    #
    # @endif
    #

    def init(self, prop):
        super(CSPEventPort, self).init(prop)

        num = 10
        ret, num = OpenRTM_aist.stringTo(
            num, self._properties.getProperty(
                "channel_timeout", "10"))
        if ret:
            self._channeltimeout = num

        buff_prop = prop.getNode("buffer")
        length = 8
        _, length = OpenRTM_aist.stringTo(
            length, buff_prop.getProperty("length", "8"))

        if length == 0:
            buff_prop.setProperty("length", "1")
            self._bufferzeromode = True

        self._eventbuffer = OpenRTM_aist.CdrBufferFactory.instance().createObject("ring_buffer")
        if self._eventbuffer is None:
            self._rtcout.RTC_ERROR("default buffer creation failed")
        self._eventbuffer.init(buff_prop)

        self._syncmode = OpenRTM_aist.toBool(
            prop.getProperty("csp.sync_wait"), "YES", "NO", False)

        if not self._bufferzeromode:
            self._writable_listener = CSPEventPort.IsWritableListener(
                self._eventbuffer, self._ctrl, self._channeltimeout, self, self._manager)
            self._write_listener = CSPEventPort.WriteListener(self._ctrl)
        else:
            self._writable_listener = CSPEventPort.IsWritableZeroModeListener(
                self._ctrl, self._channeltimeout, self, self._manager)
            self._write_listener = CSPEventPort.WriteZeroModeListener(
                self._ctrl)
        self._condition_listener = CSPEventPort.MatchConditionListener()

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
    def setManager(self, manager):
        with self._ctrl._cond:
            self._ctrl._selection_closed = False
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
    def releaseManager(self):
        self._writable_listener.releaseManager()
        with self._ctrl._cond:
            keep_guard = self._ctrl._reserved or self._selected_value_ready
        if not keep_guard:
            self.clearGuard()
        self._manager = None

    ##
    # @if jp
    # @brief 新しい選択に必要な予約・走査状態を初期化する。
    # @else
    # @brief Initialize reservation and scan state for a new selection.
    # @endif
    def beginSelection(self):
        with self._ctrl._cond:
            if not self._ctrl._reserved and not self._selected_value_ready:
                self._ctrl._selection_closed = False

    ##
    # @if jp
    # @brief 選択終了を通知し、未選択側の状態を解除する。
    # @param selected `selected`の値。
    # @else
    # @brief Mark the end of selection and clear unselected state.
    # @param selected Value of selected.
    # @endif
    def endSelection(self, selected):
        with self._ctrl._cond:
            self._ctrl._selection_closed = True

    ##
    # @if jp
    # @brief `reserve Write`に対応する処理を行う。
    # @param con `con`の値。
    # @param retry 再試行の問い合わせかどうか。
    # @param option ガード照合に使用するオプション。
    # @param manager 関連付けるManager。
    # @else
    # @brief Perform the reserve write operation.
    # @param con Value of con.
    # @param retry Whether this query is a retry.
    # @param option Options used for guard matching.
    # @param manager Manager to associate with the object.
    # @endif
    def _reserveWrite(self, con, retry, option, manager):
        with self._ctrl._cond:
            if self._ctrl._selection_closed or self._ctrl._reserved or self._selected_value_ready:
                return False
            if retry and con not in self._ctrl._searched_connectors:
                return False
            # Reserve before publishing readiness: the selected component may
            # wake up and call readData() as soon as notify() returns.
            self._ctrl._reserved = True
            self._ctrl._write_admitted = False
            self._ctrl._writing = True
            self._writingConnector = con
            if manager is not None:
                accepted = manager.notify(inport=self, connector_id=getattr(con, 'id', lambda: None)())
            else:
                accepted = self._ctrl._waiting
            if accepted:
                return True
            self._ctrl._reserved = False
            self._ctrl._writing = False
            self._writingConnector = None
            self._ctrl._offer_generation += 1
            if con not in self._ctrl._connectors:
                self._ctrl._connectors.append(con)
            return False

    ##
    # @if jp
    # @brief `admit Write`に対応する処理を行う。
    # @param con `con`の値。
    # @else
    # @brief Perform the admit write operation.
    # @param con Value of con.
    # @endif
    @contextmanager
    def _admitWrite(self, con):
        # Validate before ON_RECEIVED queues the event, and keep the lease
        # locked through enqueue + completion notification.
        with self._ctrl._cond:
            allowed = (self._ctrl._reserved and self._ctrl._writing and self._writingConnector is con and not self._ctrl._write_admitted)
            if allowed:
                self._ctrl._write_admitted = True
            yield allowed

    ##
    # @if jp
    # @brief `complete Read`に対応する処理を行う。
    # @param value 設定または受け渡す値。
    # @else
    # @brief Perform the complete read operation.
    # @param value Value to configure or transfer.
    # @endif
    def _completeRead(self, value):
        with self._ctrl._cond:
            self._ctrl._waiting = False
            self._ctrl._writing = False
            self._ctrl._reserved = False
            self._ctrl._write_admitted = False
            self._ctrl._selection_closed = True
            self._writingConnector = None
            self._value = None
            self._selected_value_ready = False
            self._ctrl._cond.notify_all()
        self.clearGuard()
        return value

    ##
    # @if jp
    # @brief `read Selected`に対応する処理を行う。
    # @param wait_for_offer `wait_for_offer`の値。
    # @param deadline `deadline`の値。
    # @else
    # @brief Perform the read selected operation.
    # @param wait_for_offer Value of wait_for_offer.
    # @param deadline Value of deadline.
    # @endif
    def _readSelected(self, wait_for_offer=False, deadline=None):
        value = None
        if deadline is None:
            deadline = time.monotonic() + self._channeltimeout
        with self._ctrl._cond:
            if self._selected_value_ready:
                value = self._value
                self._value = None
                self._selected_value_ready = False
            else:
                self._ctrl._waiting = True
                try:
                    while self._eventbuffer.empty() and (wait_for_offer or self._ctrl._reserved or self._ctrl._writing):
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            break
                        self._ctrl._cond.wait(remaining)
                    if not self._eventbuffer.empty():
                        _, value = self._eventbuffer.read()
                finally:
                    # Close acceptance before releasing the data-wait flag.
                    self._ctrl._selection_closed = True
                    self._ctrl._waiting = False
            self._ctrl._selection_closed = True
            self._ctrl._reserved = False
            self._ctrl._write_admitted = False
            self._ctrl._writing = False
            self._writingConnector = None
            self._value = None
            self._selected_value_ready = False
            self._ctrl._cond.notify_all()
        self.clearGuard()
        return value

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

    def setWritingConnector(self, con):
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
    def notify(self):
        for con in self._connectors:
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if not self._syncmode:
                if self._ctrl._writing:
                    self._ctrl._waiting = True
                    self._ctrl._cond.wait(self._channeltimeout)
                    self._ctrl._waiting = False
            else:
                if self._ctrl._writing:
                    self._ctrl._waiting = True
                    self._ctrl._cond.wait(self._channeltimeout)
                    self._ctrl._waiting = False
                guard_ctrl.unlock()

            if not self._eventbuffer.full():
                if con.isReadable(False):
                    ret, _ = con.readBuff()
                    if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                        pass
                    else:
                        self._rtcout.RTC_ERROR(
                            "read error:%s", (OpenRTM_aist.DataPortStatus.toString(ret)))

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
    # @brief Get port name
    #
    # @param connector_profile
    # @return ret, prof
    #
    # @endif
    #

    def notify_connect(self, connector_profile):
        ret, prof = super(CSPEventPort, self).notify_connect(connector_profile)
        _ = OpenRTM_aist.ScopedLock(self._connector_mutex)

        for con in self._connectors:
            from OpenRTM_aist.CSPArbitration import arbiter
            arbiter.connect(con, self)
            con._csp_write_admission = lambda con=con: self._admitWrite(con)
            con.setIsWritableListener(self._writable_listener)
            con.setWriteListener(self._write_listener)
            con.setMatchConditionListener(self._condition_listener)
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
    def getDataBufferMode(self, con, retry):
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
        if not self._syncmode:
            guard_ctrl.lock()

        if not self._eventbuffer.empty():
            _, value = self._eventbuffer.read()
            guard_ctrl.unlock()
            self.notify()
            return CSPEventPort.SUCCESSFUL_GET_DATA, value
        elif self._ctrl._writing:
            self._ctrl._waiting = True
            self._ctrl._cond.wait(self._channeltimeout)
            self._ctrl._waiting = False
            if not self._eventbuffer.empty():
                _, value = self._eventbuffer.read()
                guard_ctrl.unlock()
                self.notify()
                return CSPEventPort.SUCCESSFUL_GET_DATA, value
            else:
                self._rtcout.RTC_ERROR("read timeout")
                return CSPEventPort.FAILED_TIMEOUT, None
        else:
            guard_ctrl.unlock()
            readable = con.isReadable(retry)
            if readable:
                ret, _ = con.readBuff()
                _, value = self._eventbuffer.read()
                if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return CSPEventPort.SUCCESSFUL_GET_DATA, value
                else:
                    self._rtcout.RTC_ERROR(
                        "read error:%s", (OpenRTM_aist.DataPortStatus.toString(ret)))
                    return CSPEventPort.FAILED_DESERIALIZE, None
        return CSPEventPort.FAILED_GET_DATA, None
    ##
    # @if jp
    #
    # @brief リングバッファ使用モード時のデータ読み込み処理
    # バッファがemptyではない場合はバッファから読み込む
    # コネクタの中に読み込み可能なものがある場合は、そのコネクタから読み込む
    # ただし、書き込み中の場合は書き込み終了までブロックする
    #
    # @return ret, prof
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
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
        if not self._syncmode:
            guard_ctrl.lock()

        #self._ctrl._connectors = []
        #self._ctrl._searched_connectors = []

        guard_ctrl.unlock()

        guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return False, None

        if self._eventbuffer.empty():
            for con in self._connectors:
                ret, value = self.getDataBufferMode(con, False)
                if ret == CSPEventPort.SUCCESSFUL_GET_DATA:
                    self._ctrl._searched_connectors = []
                    return True, value
                elif ret != CSPEventPort.FAILED_GET_DATA:
                    return False, value
                else:
                    self._ctrl._searched_connectors.append(con)

        else:
            if not self._syncmode:
                guard_ctrl.lock()
            if not self._eventbuffer.empty():
                _, value = self._eventbuffer.read()
                guard_ctrl.unlock()
                self.notify()
                return True, value
            else:
                self._rtcout.RTC_ERROR(
                    "read error:%s",
                    (OpenRTM_aist.BufferStatus.toString(ret)))
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
                if ret == CSPEventPort.SUCCESSFUL_GET_DATA:
                    self._ctrl._connectors = []
                    self._ctrl._searched_connectors = []
                    return True, value
                elif ret != CSPEventPort.FAILED_GET_DATA:
                    return False, value
            #self._ctrl._connectors = []
            #self._ctrl._searched_connectors = []

        else:
            guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
            if not self._syncmode:
                guard_ctrl.lock()
            if not self._eventbuffer.empty():
                _, value = self._eventbuffer.read()
                guard_ctrl.unlock()
                self.notify()
                return True, value
            else:
                self._rtcout.RTC_ERROR(
                    "read error:%s",
                    (OpenRTM_aist.BufferStatus.toString(ret)))
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
    def getDataZeroMode(self, con, retry):
        ret = con.isReadable(retry)

        if ret:
            #guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond, True)
            # if not self._syncmode:
            #    guard_ctrl.lock()
            ret, _ = con.readBuff()
            _, value = self._eventbuffer.read()

            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                return CSPEventPort.SUCCESSFUL_GET_DATA, value
            else:
                self._rtcout.RTC_ERROR(
                    "read error:%s", (OpenRTM_aist.DataPortStatus.toString(ret)))
                return CSPEventPort.FAILED_DESERIALIZE, None
        return CSPEventPort.FAILED_GET_DATA, None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時のデータ読み込み処理
    # データ読み込み可能なコネクタが存在する場合は、そのコネクタからデータを読み込む
    #
    #
    # @return ret, data
    # ret：True：読み込み成功、False：データ読み込み可能なコネクタが存在しない
    # data：データ(読み込み失敗の場合はNone)
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

            if ret == CSPEventPort.SUCCESSFUL_GET_DATA:
                self._ctrl._searched_connectors = []
                return True, value
            elif ret != CSPEventPort.FAILED_GET_DATA:
                return False, value
            else:
                self._ctrl._searched_connectors.append(con)

            #self._ctrl._connectors = []
            #self._ctrl._searched_connectors = []

        return False, None

    ##
    # @if jp
    #
    # @brief 非リングバッファ使用モード時にデータの再受信を行う
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
            if ret == CSPEventPort.SUCCESSFUL_GET_DATA:
                self._ctrl._connectors = []
                self._ctrl._searched_connectors = []
                return True, value
            elif ret != CSPEventPort.FAILED_GET_DATA:
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
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        #self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if not self._syncmode:
            guard.unlock()

        if not self._bufferzeromode:
            ret, value = self.dataPullBufferMode()
        else:
            ret, value = self.dataPullZeroMode()

        guard.lock()

        if ret:
            self._value = value
            self._selected_value_ready = True
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
            self._selected_value_ready = True
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
    def setSyncMode(self, mode):
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
        if self._OnRead is not None:
            self._OnRead()
        return self._readSelected()

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
    # @param pull `pull`の値。
    # @param retry 再試行の問い合わせかどうか。
    # @else
    #
    # @brief Perform the read standalone operation.
    #
    # @return
    #
    # @param pull Value of pull.
    # @param retry Whether this query is a retry.
    # @endif
    #

    def _readStandalone(self, pull, retry):
        self.beginSelection()
        with self._ctrl._cond:
            self._ctrl._connectors = []
            self._ctrl._searched_connectors = []
        deadline = time.monotonic() + self._channeltimeout
        while True:
            with self._ctrl._cond:
                generation = self._ctrl._offer_generation
            ret, value = pull()
            if not ret:
                ret, value = retry()
            if ret:
                return self._completeRead(value)
            with self._ctrl._cond:
                # Do not advertise a push receiver while pulling. Recheck
                # offers made during the probe before atomically waiting.
                if (generation != self._ctrl._offer_generation and time.monotonic() < deadline):
                    continue
                self._ctrl._waiting = True
                self._ctrl._cond.notify_all()
                break
        return self._readSelected(wait_for_offer=True, deadline=deadline)

    ##
    # @if jp
    # @brief `read Buffer Mode`に対応する処理を行う。
    # @else
    # @brief Perform the read buffer mode operation.
    # @endif
    def readBufferMode(self):
        return self._readStandalone(self.dataPullBufferMode, self.dataPullBufferModeRetry)

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
        return self._readStandalone(self.dataPullZeroMode, self.dataPullZeroModeRetry)

    ##
    # @if jp
    # @brief `On Read`を設定する。
    # @param on_read `on_read`の値。
    # @else
    # @brief Set on read.
    # @param on_read Value of on_read.
    # @endif
    def setOnRead(self, on_read):
        self._OnRead = on_read

    ##
    # @if jp
    #
    # @class IsWritableListener
    #
    # @brief データ書き込み時の確認リスナ基底クラス(リングバッファ使用モード)
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
        # @param timeout 書き込み待機のタイムアウト
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
        def __init__(self, buff, control, timeout, port, manager=None):
            self._ctrl = control
            self._buffer = buff
            self._channeltimeout = timeout
            self._manager = manager
            self._port = port
            self._mutex = threading.RLock()
            self._cond = None
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

        def __call__(self, con, retry=False, option=[]):
            with self._mutex:
                if self._cond is not None and not self._cond(option):
                    return False
                return self._port._reserveWrite(con, retry, option, self._manager)

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
        def setManager(self, manager):
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
        def releaseManager(self):
            with self._mutex:
                self._manager = None

        ##
        # @if jp
        #
        # @brief ガード条件を設定する
        #
        #
        # @param cond ガード条件
        #
        #
        #
        # @else
        #
        # @brief Set the input admission predicate evaluated before communication.
        #
        # @param cond
        #
        # @endif
        #
        def setGuard(self, cond):
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._cond = cond

        ##
        # @if jp
        #
        # @brief ガード条件を初期化する
        #
        #
        #
        #
        #
        # @else
        #
        # @brief Clear guard.
        #
        #
        # @endif
        #
        def clearGuard(self):
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._cond = None

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
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param control
        #
        # @endif
        #
        def __init__(self, control):
            self._ctrl = control
        ##
        # @if jp
        #
        # @brief 書き込み時のコールバック関数
        # CSPEventPortではバッファへの書き込みはON_RECEIVEDコールバックで実行するため、
        # 書き込み状態の解除のみを行う。
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
        # @param control WorkerThreadCtrlオブジェクト
        # @param timeout 書き込み待機のタイムアウト
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
        # @param control
        # @param timeout
        # @param manager
        #
        # @param port Port to operate on.
        # @endif
        #
        def __init__(self, control, timeout, port, manager=None):
            self._ctrl = control
            self._channeltimeout = timeout
            self._manager = manager
            self._port = port
            self._mutex = threading.RLock()
            self._cond = None
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

        def __call__(self, con, retry=False, option=[]):
            with self._mutex:
                if self._cond is not None and not self._cond(option):
                    return False
                return self._port._reserveWrite(con, retry, option, self._manager)

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
        def setManager(self, manager):
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
        def releaseManager(self):
            with self._mutex:
                self._manager = None

        ##
        # @if jp
        #
        # @brief ガード条件を設定する
        #
        #
        # @param cond ガード条件
        #
        #
        #
        # @else
        #
        # @brief Set the input admission predicate evaluated before communication.
        #
        # @param cond
        #
        # @endif
        #
        def setGuard(self, cond):
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._cond = cond

        ##
        # @if jp
        #
        # @brief ガード条件を初期化する
        #
        #
        #
        #
        #
        # @else
        #
        # @brief Clear guard.
        #
        #
        # @endif
        #
        def clearGuard(self):
            _ = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._cond = None

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
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param control
        #
        # @endif
        #
        def __init__(self, control):
            self._ctrl = control
        ##
        # @if jp
        #
        # @brief 書き込み時のコールバック関数
        # CSPEventPortではバッファへの書き込みはON_RECEIVEDコールバックで実行するため、
        # 書き込み状態の解除のみを行う。
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
            self._ctrl._cond.notifyAll()
            return OpenRTM_aist.BufferStatus.BUFFER_OK

    ##
    # @if jp
    #
    # @class MatchConditionListener
    #
    # @brief ガード条件判定時のリスナ基底クラス
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class MatchConditionListener
    #
    # @brief Encapsulate the state and operations of MatchConditionListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #

    class MatchConditionListener(OpenRTM_aist.MatchConditionListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        #
        #
        #
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        #
        # @endif
        #
        def __init__(self):
            self._cond = None
        ##
        # @if jp
        #
        # @brief 条件判定痔のコールバック関数
        #
        #
        # @param option パラメータ
        # @return True：条件一致、False：条件不一致
        #
        #
        #
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param option
        # @return
        #
        # @endif
        #

        def __call__(self, option):
            if not self._cond:
                return True
            else:
                return self._cond(option)
        ##
        # @if jp
        #
        # @brief ガード条件を設定する
        #
        #
        # @param cond ガード条件
        #
        #
        #
        # @else
        #
        # @brief Set the input admission predicate evaluated before communication.
        #
        # @param cond
        #
        # @endif
        #

        def setGuard(self, cond):
            self._cond = cond

        ##
        # @if jp
        #
        # @brief ガード条件を初期化する
        #
        #
        #
        #
        #
        # @else
        #
        # @brief Clear guard.
        #
        #
        # @endif
        #
        def clearGuard(self):
            self._cond = None

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
        def __init__(self):
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._writing = False
            self._waiting = False
            self._reserved = False
            self._write_admitted = False
            self._selection_closed = False
            self._offer_generation = 0
            self._connectors = []
            self._searched_connectors = []
