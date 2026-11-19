#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPOutPort.py
# @if jp
# @brief 型付き出力と送信予約を管理する。
# @else
# @brief Manage typed output and send reservations.
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


from omniORB import CORBA
import OpenRTM_aist
from OpenRTM_aist.CSPArbitration import CSPConnectionInfo
import copy
import CSP
import threading
import time
import typing as _typing


##
# @if jp
#
# @class CSPOutPort
#
# @brief CSPOutPort テンプレートクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPOutPort
#
# @brief CSPOutPort template class
#
#
# @since 2.0.0
#
# @endif
#
class CSPOutPort(CSPConnectionInfo, OpenRTM_aist.OutPortBase):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # コンストラクタ。
    # パラメータとして与えられる T 型の変数にバインドされる。
    #
    # @param name CSPOutPort 名。CSPOutPortBase:name() により参照される。
    # @param value この CSPOutPort にバインドされる T 型の変数
    #
    # @param manager 関連付けるManager。
    # @else
    #
    # @brief A constructor.
    #
    # constructor.
    # This is bound to type-T variable given as a parameter.
    #
    # @param name A name of the CSPOutPort. This name is referred by
    #             CSPOutPortBase::name().
    # @param value type-T variable that is bound to this CSPOutPort.
    #
    # @param manager Manager to associate with the object.
    # @endif
    #
    def __init__(self, name: str, value, manager=None) -> None:
        super(CSPOutPort, self).__init__(name, OpenRTM_aist.toTypename(value))
        self._value = value
        self._ctrl = OpenRTM_aist.CSPOutPort.WorkerThreadCtrl()
        self._name = name
        self._OnWrite = None
        self._OnWriteConvert = None
        self._buffdata = [None]

        self._channeltimeout = 10
        self._writableConnector = None
        self._manager = manager
        if manager:
            manager.addOutPort(self)
        self._syncmode = True

        marshaling_types = OpenRTM_aist.SerializerFactories.instance().getSerializerList(value)
        marshaling_types = OpenRTM_aist.flatten(marshaling_types).lstrip()
        self.addProperty("dataport.marshaling_types", marshaling_types)

        self._option = []

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
        super(CSPOutPort, self).__del__()

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
        super(CSPOutPort, self).init(prop)
        num = 10
        ret, num = OpenRTM_aist.stringTo(
            num, self._properties.getProperty("channel_timeout", "10"))
        if ret:
            self._channeltimeout = num

        self._syncmode = OpenRTM_aist.toBool(
            prop.getProperty("csp.sync_wait"), "YES", "NO", True)

        self._readable_listener = OpenRTM_aist.CSPOutPort.IsReadableListener(
            self._buffdata, self._ctrl, self._channeltimeout, self, self._manager)
        self._read_listener = OpenRTM_aist.CSPOutPort.ReadListener(
            self._buffdata, self._ctrl, self._channeltimeout, self)

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
        self.beginSelection()
        self._readable_listener.setManager(manager)
        self._manager = manager
        if manager:
            self._manager.addOutPort(self)

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
        self._readable_listener.releaseManager()
        self._manager = None

    ##
    # @if jp
    # @brief 新しい選択に必要な予約・走査状態を初期化する。
    # @else
    # @brief Initialize reservation and scan state for a new selection.
    # @endif
    def beginSelection(self) -> None:
        with self._ctrl._cond:
            self._ctrl._selection_closed = False

    ##
    # @if jp
    # @brief 選択終了を通知し、未選択側の状態を解除する。
    # @param selected `selected`の値。
    # @else
    # @brief Mark the end of selection and clear unselected state.
    # @param selected Value of selected.
    # @endif
    def endSelection(self, selected) -> None:
        with self._ctrl._cond:
            self._ctrl._selection_closed = True

    ##
    # @if jp
    # @brief `wait Previous Read`に対応する処理を行う。
    # @else
    # @brief Perform the wait previous read operation.
    # @endif
    def _waitPreviousRead(self) -> bool:
        deadline = time.monotonic() + self._channeltimeout
        while self._ctrl._reserved and not self._ctrl._reading:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            self._ctrl._cond.wait(remaining)
        return True

    ##
    # @if jp
    #
    # @brief コネクタ接続関数
    # OutPortBaseの接続処理のほかに、コネクタに読み込み確認時、読み込み時のコールバック関数を設定する
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
        ret, prof = super(CSPOutPort, self).notify_connect(connector_profile)
        _ = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            from OpenRTM_aist.CSPArbitration import arbiter
            arbiter.connect(con, self)
            con.setIsReadableListener(self._readable_listener)
            con.setReadListener(self._read_listener)
        return (ret, prof)

    ##
    # @if jp
    #
    # @brief データが書き込み可能かを確認
    #
    # @return ret, con
    # ret：True(書き込み可能)、False(書き込み不可)
    # con：書き込み可能なコネクタ。書き込み不可の場合はNone
    #
    # @param option ガード照合に使用するオプション。
    # @else
    #
    # @brief Perform the data writable operation.
    #
    # @return
    #
    # @param option Options used for guard matching.
    # @endif
    #
    def dataWritable(self, option: list = []):
        _ = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            if con.isWritable(False, option):
                self._ctrl._searched_connectors = []
                return True, con
            else:
                self._ctrl._searched_connectors.append(con)

        return False, None

    ##
    # @if jp
    #
    # @brief データの再送信確認を行う
    #
    # @return ret, con
    # ret：True(書き込み可能)、False(書き込み不可)
    # con：書き込み可能なコネクタ。書き込み不可の場合はNone
    #
    #
    # @param option ガード照合に使用するオプション。
    # @else
    #
    # @brief Perform the data writable retry operation.
    #
    # @return ret, con
    #
    # @param option Options used for guard matching.
    # @endif
    #
    def dataWritableRetry(self, option: list = []):
        cons = self._ctrl._connectors[:]
        for con in cons:
            if con.isWritable(True, option):
                self._ctrl._connectors = []
                self._ctrl._searched_connectors = []
                return True, con
        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []
        return False, None

    ##
    # @if jp
    #
    # @brief 書き込み可能なコネクタを選択してself._writableConnectorに格納する
    #
    # @return True：書き込み可能、False：書き込み不可
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

        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if not self._waitPreviousRead():
            return False
        if self._ctrl._reserved and self._ctrl._reading:
            return True

        if not self._syncmode:
            guard.unlock()
        ret, self._writableConnector = self.dataWritable(self._option)
        return ret

    ##
    # @if jp
    #
    # @brief 再検索リストのコネクタからデータ書き込み可能なコネクタを選択し、
    # self._writableConnectorに格納する
    #
    #
    # @return True：書き込み可能、False：書き込み不可
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
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        if not self._waitPreviousRead():
            return False
        if self._ctrl._reserved and self._ctrl._reading:
            return True

        if not self._syncmode:
            guard.unlock()

        ret, self._writableConnector = self.dataWritableRetry(self._option)
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
    # @brief self._writableConnectorに格納したコネクタにデータを書き込む
    # このため、事前にselect関数を実行する必要がある
    #
    # @param value データ
    #
    # @else
    #
    # @brief Send data through the selected output.
    #
    # @param value
    #
    # @endif
    #
    def writeData(self, value=None):
        self._rtcout.RTC_TRACE("writeData()")
        if not value:
            value = self._value
        if self._OnWrite:
            self._OnWrite(value)

        if self._OnWriteConvert:
            value = self._OnWriteConvert(value)

        guard_con = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        if not self._waitPreviousRead():
            return False
        if self._ctrl._reading:
            ret, cdr_data = self._connectors[0].serializeData(value)
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                self.setData(cdr_data)
                self._ctrl._reading = False
                self._ctrl._cond.notifyAll()
                self.clearGuard()
                return True
        if self._writableConnector:
            connector = self._writableConnector
            self._writableConnector = None
            guard_con.unlock()
            ret = connector.write(value)
            self.clearGuard()
            return ret == OpenRTM_aist.DataPortStatus.PORT_OK
        return False

    ##
    # @if jp
    #
    # @brief self._writableConnectorにコネクタを格納する
    #
    # @param con コネクタ
    #
    # @else
    #
    # @brief Set writable connector.
    #
    # @param con
    #
    # @endif
    #
    def setWritableConnector(self, con) -> None:
        self._writableConnector = con

    ##
    # @if jp
    #
    # @brief 待機状態時に移行した場合にデータを一時的に変数に格納する
    #
    # @param data データ
    #
    # @else
    #
    # @brief Set data.
    #
    # @param data
    #
    # @endif
    #
    def setData(self, data) -> None:
        self._buffdata[0] = data

    ##
    # @if jp
    #
    # @brief データを書き込む
    # 書き込み可能なコネクタが存在する場合は、データを書き込んで処理を終了する
    # 書き込み可能なコネクタが存在しない場合は、InPort側からデータを読み込むまで待機する
    #
    # @param value データ
    # @return True：正常完了、False：エラー
    # データのマーシャリング、書き込みのタイムアウトでエラーが発生する
    #
    # @else
    #
    # @brief Send data to one ready connection.
    #
    # @param value
    # @return
    #
    # @endif
    #
    def write(self, value=None):
        if self._writableConnector is not None or self._ctrl._reading:
            return self.writeData(value)
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        if not self._waitPreviousRead():
            return False
        self._ctrl._selection_closed = False

        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if not self._syncmode:
            guard.unlock()

        if not value:
            value = self._value
        if self._OnWrite:
            self._OnWrite(value)

        if not self._connectors:
            return False

        if self._OnWriteConvert:
            value = self._OnWriteConvert(value)

        if not self._ctrl._waiting:
            ret, con = self.dataWritable(self._option)
            if ret:
                retcon = con.write(value)
                if retcon == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return True
                else:
                    self._rtcout.RTC_ERROR("write error %d", (retcon))
                    return False

        if not self._syncmode:
            guard.lock()

            ret, con = self.dataWritableRetry(self._option)
            if ret:
                retcon = con.write(value)
                if retcon == OpenRTM_aist.DataPortStatus.PORT_OK:
                    self.clearGuard()
                    return True
                else:
                    self._rtcout.RTC_ERROR("write error %d", (retcon))
                    return False

        ret, cdr_data = self._connectors[0].serializeData(value)
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            self.setData(cdr_data)
            self._ctrl._reading = False
            if self._ctrl._waiting:
                self._ctrl._waiting = False
                self._ctrl._cond.notifyAll()
                self.clearGuard()
                return True
            self._ctrl._readable = True
            # Publish before the final receiver probe, under the same lock
            # used by IsReadableListener. A pull and a push cannot both win.
            ret, con = self.dataWritable(self._option)
            if ret:
                self._ctrl._readable = False
                self.setData(None)
                retcon = con.write(value)
                self.clearGuard()
                return retcon == OpenRTM_aist.DataPortStatus.PORT_OK
            self._ctrl._cond.notify_all()
            deadline = time.monotonic() + self._channeltimeout
            while self._ctrl._readable:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self._ctrl._cond.wait(remaining)

            if self._ctrl._readable:
                self._rtcout.RTC_ERROR("write timeout")
                self._ctrl._readable = False
                self.setData(None)
                return False
            self.clearGuard()
            return True
        else:
            self._rtcout.RTC_ERROR("serialize error")
            return False

    ##
    # @if jp
    # @brief `On Write`を設定する。
    # @param on_write `on_write`の値。
    # @else
    # @brief Set on write.
    # @param on_write Value of on_write.
    # @endif
    def setOnWrite(self, on_write) -> None:
        self._OnWrite = on_write

    ##
    # @if jp
    # @brief `On Write Convert`を設定する。
    # @param on_wconvert `on_wconvert`の値。
    # @else
    # @brief Set on write convert.
    # @param on_wconvert Value of on_wconvert.
    # @endif
    def setOnWriteConvert(self, on_wconvert) -> None:
        self._OnWriteConvert = on_wconvert

    ##
    # @if jp
    #
    # @brief ガード条件判定用のパラメータを設定する
    #
    # @param option パラメータ
    #
    # @else
    #
    # @brief Set sender options used to match the peer input guard.
    #
    # @param option
    #
    # @endif
    #
    def setGuard(self, option) -> None:
        self._option = option
        self._readable_listener.setGuard(option)

    ##
    # @if jp
    #
    # @brief ガード条件判定用のパラメータを初期化する
    #
    #
    # @else
    #
    # @brief Clear guard.
    #
    #
    # @endif
    #
    def clearGuard(self) -> None:
        self._option = []
        self._readable_listener.clearGuard()

    ##
    # @if jp
    #
    # @class IsReadableListener
    #
    # @brief データ読み込み確認リスナ基底クラス
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class IsReadableListener
    #
    # @brief Encapsulate the state and operations of IsReadableListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #
    class IsReadableListener(OpenRTM_aist.IsReadableListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param control WorkerThreadCtrlオブジェクト
        # @param timeout 読み込み待機のタイムアウト時間
        # @param manager CSPチャネル管理マネージャ
        # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
        #
        #
        #
        # @param data 送受信するデータ。
        # @param port 操作対象のポート。
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param control
        # @param timeout
        # @param manager
        #
        # @param data Data to transmit or receive.
        # @param port Port to operate on.
        # @endif
        #
        def __init__(self, data: list, control, timeout: int, port: 'CSPOutPort', manager=None) -> None:
            self._ctrl = control
            self._data = data
            self._channeltimeout = timeout
            self._port = port
            self._manager = manager
            self._mutex = threading.RLock()
            self._option = []
        ##
        # @if jp
        #
        # @brief 読み込み確認時のコールバック関数
        # 他のコネクタがデータ読み込み中の場合は完了まで待機する
        # データ書き込みで待機しているの場合は読み込み状態に移行する
        # このため、読み込み可能な場合は必ずデータを読み込み必要がある
        #
        #
        # @param con OutPortConnector
        # @param retry True：再検索、False：通常の読み込み確認
        # @return True：読み込み可能、False：読み込み不可
        #
        #
        #
        # @param provider 受信側のInPortCsp参照。
        # @else
        #
        # @brief Perform the call operation.
        #
        # @param con
        # @param retry
        # @return
        #
        # @param provider Reference to the receiver InPortCsp interface.
        # @endif
        #

        def __call__(self, con, retry: bool = False, provider=CSP.InPortCsp._nil) -> '_typing.Optional[bool]':
            with self._mutex:
                if retry and con not in self._ctrl._searched_connectors:
                    return False
                if self._option and not provider.match_condition(self._option):
                    return False
                with self._ctrl._cond:
                    if self._ctrl._reserved or self._ctrl._selection_closed:
                        return False
                    manager = self._manager
                    if manager is not None:
                        self._ctrl._reserved = True
                        self._ctrl._reading = True
                        if manager.notify(outport=self._port, connector_id=getattr(con, 'id', lambda: None)()):
                            return True
                        self._ctrl._reserved = False
                        self._ctrl._reading = False
                    elif self._ctrl._readable:
                        self._ctrl._reserved = True
                        self._ctrl._reading = True
                        return True
                    if con not in self._ctrl._connectors:
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
        # @brief ガード条件判定用のパラメータを設定する
        #
        # @param option パラメータ
        #
        # @else
        #
        # @brief Set sender options used to match the peer input guard.
        #
        # @param option
        #
        # @endif
        #
        def setGuard(self, option) -> None:
            self._option = option

        ##
        # @if jp
        #
        # @brief ガード条件判定用のパラメータを初期化する
        #
        #
        # @else
        #
        # @brief Clear guard.
        #
        #
        # @endif
        #
        def clearGuard(self) -> None:
            self._option = []

    ##
    # @if jp
    #
    # @class ReadListener
    #
    # @brief データ読み込み時のリスナ基底クラス
    #
    #
    # @since 2.0.0
    #
    # @else
    #
    # @class ReadListener
    #
    # @brief Encapsulate the state and operations of ReadListener.
    #
    #
    # @since 2.0.0
    #
    # @endif
    #
    class ReadListener(OpenRTM_aist.ReadListenerBase):
        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        #
        # @param data データを格納する変数
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @param timeout 待機期限。秒単位。
        # @param port 操作対象のポート。
        # @else
        #
        # @brief Initialize the instance and its internal state.
        #
        # @param data
        # @param control
        #
        # @param timeout Wait timeout in seconds.
        # @param port Port to operate on.
        # @endif
        #
        def __init__(self, data: list, control, timeout: int, port=None) -> None:
            self._ctrl = control
            self._data = data
            self._channeltimeout = timeout
            self._port = port
        ##
        # @if jp
        #
        # @brief 読み込み時のコールバック関数
        # データを変数から取り出し、読み込み状態を解除する
        #
        #
        # @return ret, data
        # ret：リターンコード
        # BUFFER_OK：正常完了
        # BUFFER_ERROR：データが格納されていない
        # data：データ
        #
        #
        #
        # @else
        #
        # @brief Perform the call operation.
        #
        # @return
        #
        # @endif
        #

        def __call__(self):
            deadline = time.monotonic() + self._channeltimeout
            with self._ctrl._cond:
                try:
                    while self._data[0] is None:
                        self._ctrl._waiting = True
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            return OpenRTM_aist.BufferStatus.BUFFER_ERROR, None
                        self._ctrl._cond.wait(remaining)
                    data = self._data[0]
                    self._data[0] = None
                    self._ctrl._readable = False
                    return OpenRTM_aist.BufferStatus.BUFFER_OK, data
                finally:
                    self._ctrl._waiting = False
                    self._ctrl._reading = False
                    self._ctrl._readable = False
                    self._ctrl._reserved = False
                    self._ctrl._cond.notify_all()

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
            self._reading = False
            self._readable = False
            self._waiting = False
            self._reserved = False
            self._selection_closed = False
            self._connectors = []
            self._searched_connectors = []
