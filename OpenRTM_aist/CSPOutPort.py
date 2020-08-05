#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPOutPort.py
# @brief CSPOutPort template class
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
# @class EventInPort
#
# @brief EventInPort テンプレートクラス
#
#
# @since 2.0.0
#
# @else
#
# @class EventInPort
#
# @brief EventInPort template class
#
#
# @since 2.0.0
#
# @endif
#
class CSPOutPort(OpenRTM_aist.OutPortBase):
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
    #
    # @endif
    #
    def __init__(self, name, value, manager=None):
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
        super(CSPOutPort, self).__del__()

    ##
    # @if jp
    #
    # @brief ポート名称を取得する。
    #
    # ポート名称を取得する。
    #
    # @param self
    # @return ポート名称
    #
    # @else
    #
    # @brief Get port name
    #
    # Get port name.
    #
    # @param self
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
    # @param self
    # @param prop 設定情報
    # channel_timeout：データ書き込み、読み込み時のタイムアウト
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param prop
    #
    # @endif
    #
    def init(self, prop):
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
            self._buffdata, self._ctrl, self._channeltimeout)

    ##
    # @if jp
    #
    # @brief CSPManagerの設定
    #
    # @param self
    # @param manager CSPManager
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param manager
    #
    # @endif
    #
    def setManager(self, manager):
        self._readable_listener.setManager(manager)
        self._manager = manager
        if manager:
            self._manager.addOutPort(self)

    ##
    # @if jp
    #
    # @brief CSPManagerの設定解除
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
    def releaseManager(self):
        self._readable_listener.releaseManager()
        self._manager = None

    ##
    # @if jp
    #
    # @brief コネクタ接続関数
    # OutPortBaseの接続処理のほかに、コネクタに読み込み確認時、読み込み時のコールバック関数を設定する
    #
    # @param self
    # @param connector_profile コネクタプロファイル
    # @return ret, prof
    # ret：リターンコード
    # prof：コネクタプロファイル
    #
    # @return ポート名称
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param connector_profile
    # @return ret, prof
    #
    # @endif
    #
    def notify_connect(self, connector_profile):
        ret, prof = super(CSPOutPort, self).notify_connect(connector_profile)
        guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            con.setIsReadableListener(self._readable_listener)
            con.setReadListener(self._read_listener)
        return (ret, prof)

    ##
    # @if jp
    #
    # @brief データが書き込み可能かを確認
    #
    # @param self
    # @return ret, con
    # ret：True(書き込み可能)、False(書き込み不可)
    # con：書き込み可能なコネクタ。書き込み不可の場合はNone
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
    def dataWritable(self):
        guard = OpenRTM_aist.ScopedLock(self._connector_mutex)
        for con in self._connectors:
            if con.isWritable(False):
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
    # @param self
    # @return ret, con
    # ret：True(書き込み可能)、False(書き込み不可)
    # con：書き込み可能なコネクタ。書き込み不可の場合はNone
    #
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return ret, con
    #
    # @endif
    #
    def dataWritableRetry(self):
        cons = self._ctrl._connectors[:]
        for con in cons:
            if con.isWritable(True):
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
    # @param self
    # @return True：書き込み可能、False：書き込み不可
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

    def select(self):
        self._rtcout.RTC_TRACE("select()")
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if self._ctrl._waiting:
            return True
        if self._ctrl._reading:
            self._ctrl._cond.wait(self._channeltimeout)

        if not self._syncmode:
            del guard
            guard = None

        ret, self._writableConnector = self.dataWritable()
        return ret

    ##
    # @if jp
    #
    # @brief 再検索リストのコネクタからデータ書き込み可能なコネクタを選択し、
    # self._writableConnectorに格納する
    #
    #
    # @param self
    # @return True：書き込み可能、False：書き込み不可
    #
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
    def reselect(self):
        self._rtcout.RTC_TRACE("reselect()")
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        if self._ctrl._waiting:
            return True
        if self._ctrl._reading:
            self._ctrl._cond.wait(self._channeltimeout)

        if not self._syncmode:
            del guard

        ret, self._writableConnector = self.dataWritableRetry()
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
    # @param self
    # @param mode True：ロックモード、False：非ロックモード
    #
    #
    # @else
    #
    # @brief
    #
    # @param self
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
    # @param self
    # @return True：ロックモード、False：非ロックモード
    #
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
    def getSyncMode(self):
        return self._syncmode

    ##
    # @if jp
    #
    # @brief self._writableConnectorに格納したコネクタにデータを書き込む
    # このため、事前にselect関数を実行する必要がある
    #
    # @param self
    # @param value データ
    #
    # @else
    #
    # @brief
    #
    # @param self
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
        if self._ctrl._waiting:
            ret, cdr_data = self._connectors[0].serializeData(value)
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
                self.setData(cdr_data)
                self._ctrl._waiting = False
                self._ctrl._cond.notify()
                return True

        if self._writableConnector:
            del guard_con
            self._writableConnector.write(value)

    ##
    # @if jp
    #
    # @brief 待機状態時に移行した場合にデータを一時的に変数に格納する
    #
    # @param self
    # @param data データ
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param data
    #
    # @endif
    #
    def setData(self, data):
        self._buffdata[0] = data

    ##
    # @if jp
    #
    # @brief データを書き込む
    # 書き込み可能なコネクタが存在する場合は、データを書き込んで処理を終了する
    # 書き込み可能なコネクタが存在しない場合は、InPort側からデータを読み込むまで待機する
    #
    # @param self
    # @param value データ
    # @return True：正常完了、False：エラー
    # データのマーシャリング、書き込みのタイムアウトでエラーが発生する
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param value
    # @return
    #
    # @endif
    #
    def write(self, value=None):
        guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)

        self._ctrl._connectors = []
        self._ctrl._searched_connectors = []

        if not self._syncmode:
            del guard
            guard = None

        if not value:
            value = self._value
        if self._OnWrite:
            self._OnWrite(value)

        if not self._connectors:
            return False

        if self._OnWriteConvert:
            value = self._OnWriteConvert(value)

        if not self._ctrl._waiting:
            ret, con = self.dataWritable()
            if ret:
                retcon = con.write(value)
                if retcon == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return True
                else:
                    self._rtcout.RTC_ERROR("write error %d", (retcon))
                    return False

        if not self._syncmode:
            guard_con = OpenRTM_aist.ScopedLock(self._ctrl._cond)

            ret, con = self.dataWritableRetry()
            if ret:
                retcon = con.write(value)
                if retcon == OpenRTM_aist.DataPortStatus.PORT_OK:
                    return True
                else:
                    self._rtcout.RTC_ERROR("write error %d", (retcon))
                    return False

        ret, cdr_data = self._connectors[0].serializeData(value)
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            self.setData(cdr_data)
            if self._ctrl._waiting:
                self._ctrl._waiting = False
                self._ctrl._cond.notify()
                return True
            self._ctrl._readable = True
            self._ctrl._cond.wait(self._channeltimeout)

            if self._ctrl._readable:
                self._rtcout.RTC_ERROR("write timeout")
                self._ctrl._readable = False
                return False
            return True
        else:
            self._rtcout.RTC_ERROR("serialize error")
            return False

    def setOnWrite(self, on_write):
        self._OnWrite = on_write

    def setOnWriteConvert(self, on_wconvert):
        self._OnWriteConvert = on_wconvert

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
    # @brief
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
        # @param self
        # @param control WorkerThreadCtrlオブジェクト
        # @param timeout 読み込み待機のタイムアウト時間
        # @param manager CSPチャネル管理マネージャ
        # managerを指定した場合は、managerが待機中の場合にロック解除の通知を行う
        #
        #
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param control
        # @param timeout
        # @param manager
        #
        # @endif
        #
        def __init__(self, data, control, timeout, port, manager=None):
            self._ctrl = control
            self._data = data
            self._channeltimeout = timeout
            self._port = port
            self._manager = manager
            self._mutex = threading.RLock()
        ##
        # @if jp
        #
        # @brief 読み込み確認時のコールバック関数
        # 他のコネクタがデータ読み込み中の場合は完了まで待機する
        # データ書き込みで待機しているの場合は読み込み状態に移行する
        # このため、読み込み可能な場合は必ずデータを読み込み必要がある
        #
        #
        # @param self
        # @param con OutPortConnector
        # @param retry True：再検索、False：通常の読み込み確認
        # @return True：読み込み可能、False：読み込み不可
        #
        #
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param con
        # @param retry
        # @return
        #
        # @endif
        #

        def __call__(self, con, retry=False):
            guard_manager = OpenRTM_aist.Guard.ScopedLock(self._mutex)

            if retry:
                if con not in self._ctrl._searched_connectors:
                    return False

            if self._manager:
                if self._manager.notify(outport=self._port):
                    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
                    self._ctrl._reading = True
                    return True
            del guard_manager
            guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if self._ctrl._reading:
                self._ctrl._cond.wait(self._channeltimeout)
            if not self._ctrl._readable:
                self._ctrl._reading = False
                self._ctrl._connectors.append(con)
                return False
            else:
                self._ctrl._reading = True
                return True

        ##
        # @if jp
        #
        # @brief CSPManagerの設定
        #
        # @param self
        # @param manager CSPManager
        #
        #
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param manager
        #
        # @endif
        #
        def setManager(self, manager):
            guard_manager = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = manager

        ##
        # @if jp
        #
        # @brief CSPManagerの解除
        #
        # @param self
        #
        #
        #
        # @else
        #
        # @brief
        #
        # @param self
        #
        # @endif
        #
        def releaseManager(self):
            guard_manager = OpenRTM_aist.Guard.ScopedLock(self._mutex)
            self._manager = None

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
    # @brief
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
        # @param self
        # @param data データを格納する変数
        # @param control WorkerThreadCtrlオブジェクト
        #
        #
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param data
        # @param control
        #
        # @endif
        #
        def __init__(self, data, control, timeout):
            self._ctrl = control
            self._data = data
            self._channeltimeout = timeout
        ##
        # @if jp
        #
        # @brief 読み込み時のコールバック関数
        # データを変数から取り出し、読み込み状態を解除する
        #
        #
        # @param self
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
        # @brief
        #
        # @param self
        # @return
        #
        # @endif
        #

        def __call__(self):
            guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
            if self._data[0] is None:
                self._ctrl._waiting = True
                self._ctrl._cond.wait(self._channeltimeout)

            self._ctrl._reading = False
            data = self._data[0]
            self._data[0] = None
            self._ctrl._readable = False
            self._ctrl._cond.notify()
            if data is None:
                return OpenRTM_aist.BufferStatus.BUFFER_ERROR, data
            else:
                return OpenRTM_aist.BufferStatus.BUFFER_OK, data

    class WorkerThreadCtrl:
        def __init__(self):
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._reading = False
            self._readable = False
            self._waiting = False
            self._connectors = []
            self._searched_connectors = []
