#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file InPort.py
# @brief InPort template class
# @date $Date: 2007/09/20 $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2003-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import copy


import OpenRTM_aist
import threading

##
# @if jp
#
# @class InPort
#
# @brief InPort クラス
#
# InPort の実装クラス。
# InPort は内部にリングバッファを持ち、外部から送信されたデータを順次
# このリングバッファに格納する。リングバッファのサイズはデフォルトで64と
# なっているが、コンストラクタ引数によりサイズを指定することができる。
# データはフラグによって未読、既読状態が管理され、isNew(), getNewDataLen()
# getNewList(), getNewListReverse() 等のメソッドによりハンドリングすることが
# できる。
#
# @since 0.2.0
#
# @else
#
# @class InPort
#
# @brief InPort template class
#
# This class template provides interfaces to input port.
# Component developer can define input value, which act as input
# port from other components, using this template.
# This is class template. This class have to be incarnated class as port
# value types. This value types are previously define RtComponent IDL.
# ex. type T: TimedFload, TimedLong etc...
#
# @since 0.2.0
#
# @endif


class InPort(OpenRTM_aist.InPortBase):
    """
    """

    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # コンストラクタ。
    #
    # @param self
    # @param name InPort 名。InPortBase:name() により参照される。
    # @param value この InPort にバインドされる変数
    #
    # @else
    #
    # @brief A constructor.
    #
    # Setting channel name and registering channel value.
    #
    # @param self
    # @param name A name of the InPort. This name is referred by
    #             InPortBase::name().
    # @param value A channel value related with the channel.
    #
    # @endif
    def __init__(self, name, value):
        OpenRTM_aist.InPortBase.__init__(
            self, name, OpenRTM_aist.toTypename(value))
        self._name = name
        self._value = value
        self._OnRead = None
        self._OnReadConvert = None

        self._directNewData = False
        self._valueMutex = threading.RLock()

        marshaling_types = OpenRTM_aist.SerializerFactories.instance().getSerializerList(value)
        marshaling_types = OpenRTM_aist.flatten(marshaling_types).lstrip()
        self.addProperty("dataport.marshaling_types", marshaling_types)

        self._listeners.setDataType(copy.deepcopy(value))
        self._listeners.setPortType(OpenRTM_aist.PortType.InPortType)

        self.addConnectorDataListener(
            OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
            OpenRTM_aist.Timestamp("on_received"))
        self.addConnectorDataListener(
            OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ,
            OpenRTM_aist.Timestamp("on_read"))

    def __del__(self, InPortBase=OpenRTM_aist.InPortBase):
        InPortBase.__del__(self)
        return

    ##
    # @if jp
    # @brief ポート名称を取得する。
    #
    # ポート名称を取得する。
    #
    # @param self
    #
    # @return ポート名称
    #
    # @else
    #
    # @endif
    #
    # const char* name()
    def name(self):
        return self._name

    ##
    # @if jp
    # @brief 最新データか確認
    #
    # 現在のバッファ位置に格納されているデータが最新データか確認する。
    #
    # @param self
    #
    # @return 最新データ確認結果
    #            ( true:最新データ．データはまだ読み出されていない
    #             false:過去のデータ．データは既に読み出されている)
    #
    # @else
    #
    # @endif
    #
    # bool isNew()

    def isNew(self, names=None):
        self._rtcout.RTC_TRACE("isNew()")

        guard = OpenRTM_aist.ScopedLock(self._valueMutex)
        if self._directNewData == True:
            self._rtcout.RTC_TRACE(
                "isNew() returns true because of direct write.")
            return True
        del guard

        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return False

        if names is None:
            r = self._connectors[0].getBuffer().readable()
            if r > 0:
                self._rtcout.RTC_DEBUG("isNew() = True, readable data: %d", r)
                return True
            else:
                self._rtcout.RTC_DEBUG("isNew() = False, no readable data")
                return False
        elif isinstance(names, str):
            for con in self._connectors:
                if con.name() == names:
                    r = con.getBuffer().readable()
                    if r > 0:
                        self._rtcout.RTC_DEBUG(
                            "isNew() = True, connector name: %s, readable data: %d", (names, r))
                        return True
                    else:
                        self._rtcout.RTC_DEBUG(
                            "isNew() = False, connector name: %s, no readable data", names)
                        return False
        elif isinstance(names, list):
            del names[:]
            for con in self._connectors:
                r = con.getBuffer().readable()
                if r > 0:
                    self._rtcout.RTC_DEBUG(
                        "isNew() = True, connector name: %s, readable data: %d", (names, r))
                    names.append(con.name())
            if names:
                return True
            else:
                self._rtcout.RTC_DEBUG("isNew() = False, no readable data")
                return False

        self._rtcout.RTC_ERROR("isNew() = False, Unknown Errow")
        return False

    ##
    # @if jp
    #
    # @brief バッファが空かどうか確認する
    #
    # InPortのバッファが空かどうかを bool 値で返す。
    # 空の場合は true, 未読データがある場合は false を返す。
    #
    # @return true  バッファは空
    #         false バッファに未読データがある
    #
    # @else
    #
    # @brief Check whether the data is newest
    #
    # Check whether the data stored at a current buffer position is newest.
    #
    # @return Newest data check result
    #         ( true:Newest data. Data has not been readout yet.
    #          false:Past data．Data has already been readout.)
    #
    # @endif
    #
    # bool isEmpty()

    def isEmpty(self, names=None):
        self._rtcout.RTC_TRACE("isEmpty()")
        if self._directNewData == True:
            return False
        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return True

        if names is None:
            r = self._connectors[0].getBuffer().readable()
            if r == 0:
                self._rtcout.RTC_DEBUG("isEmpty() = true, buffer is empty")
                return True
        elif isinstance(names, str):
            for con in self._connectors:
                if con.name() == names:
                    r = con.getBuffer().readable()
                    if r == 0:
                        self._rtcout.RTC_DEBUG(
                            "isEmpty() = True, connector name: %s, buffer is empty", (names))
                        return True
                    else:
                        self._rtcout.RTC_DEBUG(
                            "isEmpty() = False, connector name: %s, readable data: %d", (names, r))
                        return False
        elif isinstance(names, list):
            del names[:]
            for con in self._connectors:
                r = con.getBuffer().readable()
                if r == 0:
                    self._rtcout.RTC_DEBUG(
                        "isEmpty() = True, connector name: %s", (names))
                    names.append(con.name())
            if names:
                return True
        else:
            self._rtcout.RTC_DEBUG("isEmpty() = False, no readable data")
            return False

        self._rtcout.RTC_DEBUG("isEmpty() = false, data exists in the buffer")
        return False

    ##
    # @if jp
    #
    # @brief DataPort から値を読み出す
    #
    # InPortに書き込まれたデータを読みだす。接続数が0、またはバッファに
    # データが書き込まれていない状態で読みだした場合の戻り値は不定である。
    # バッファが空の状態のとき、
    # 事前に設定されたモード (readback, do_nothing, block) に応じて、
    # 以下のような動作をする。
    #
    # - readback: 最後の値を読みなおす。
    #
    # - do_nothing: 何もしない
    #
    # - block: ブロックする。タイムアウトが設定されている場合は、
    #       タイムアウトするまで待つ。
    #
    # バッファが空の状態では、InPortにバインドされた変数の値が返される。
    # したがって、初回読み出し時には不定値を返す可能性がある。
    # この関数を利用する際には、
    #
    # - isNew(), isEmpty() と併用し、事前にバッファ状態をチェックする。
    #
    # - 初回読み出し時に不定値を返さないようにバインド変数を事前に初期化する
    #
    #
    # 各コールバック関数は以下のように呼び出される。
    # - OnRead: read() 関数が呼ばれる際に必ず呼ばれる。
    #
    # - OnReadConvert: データの読み出しが成功した場合、読みだしたデータを
    #       引数としてOnReadConvertが呼び出され、戻り値をread()が戻り値
    #       として返す。
    #
    # - OnEmpty: バッファが空のためデータの読み出しに失敗した場合呼び出される。
    #        OnEmpty の戻り値を read() の戻り値として返す。
    #
    # - OnBufferTimeout: データフロー型がPush型の場合に、読み出し
    #        タイムアウトのためにデータの読み出しに失敗した場合に呼ばれる。
    #
    # - OnRecvTimeout: データフロー型がPull型の場合に、読み出しタイムアウト
    #        のためにデータ読み出しに失敗した場合に呼ばれる。
    #
    # - OnReadError: 上記以外の理由で読みだしに失敗した場合に呼ばれる。
    #        理由としては、バッファ設定の不整合、例外の発生などが考えられる
    #        が通常は起こりえないためバグの可能性がある。
    #
    # @return 読み出したデータ
    #
    # @else
    #
    # @brief Readout the value from DataPort
    #
    # Readout the value from DataPort
    #
    # - When Callback functor OnRead is already set, OnRead will be invoked
    #   before reading from the buffer held by DataPort.
    # - When the buffer held by DataPort can detect the underflow,
    #   and when it detected the underflow at reading, callback functor
    #   OnUnderflow will be invoked.
    # - When callback functor OnReadConvert is already set, the return value of
    #   operator() of OnReadConvert will be the return value of read().
    # - When timeout of reading is already set by setReadTimeout(),
    #   it waits for only timeout time until the state of the buffer underflow
    #   is reset, and if OnUnderflow is already set, this will be invoked to
    #   return.
    #
    # @return Readout data
    #
    # @endif
    #
    #  DataType read()

    def read(self, name=None):
        self._rtcout.RTC_TRACE("DataType read()")

        if self._OnRead is not None:
            self._OnRead()
            self._rtcout.RTC_TRACE("OnRead called")

        guard = OpenRTM_aist.ScopedLock(self._valueMutex)
        if self._directNewData == True:

            self._rtcout.RTC_TRACE("Direct data transfer")
            if self._OnReadConvert is not None:
                self._value = self._OnReadConvert(self._value)
                self._rtcout.RTC_TRACE("OnReadConvert for direct data called")
            self._directNewData = False
            return self._value
        del guard

        if not self._connectors:
            self._rtcout.RTC_DEBUG("no connectors")
            return self._value

        _val = copy.deepcopy(self._value)

        if name is None:
            ret, _val = self._connectors[0].read(_val)
        else:
            ret = OpenRTM_aist.DataPortStatus.PRECONDITION_NOT_MET
            for con in self._connectors:
                if con.name() == name:
                    ret, _val = con.read(_val)
            if ret == OpenRTM_aist.DataPortStatus.PRECONDITION_NOT_MET:
                self._rtcout.RTC_DEBUG("not found %s", name)
                return self._value

        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            self._rtcout.RTC_DEBUG("data read succeeded")
            self._value = _val

            if self._OnReadConvert is not None:
                self._value = self._OnReadConvert(self._value)
                self._rtcout.RTC_DEBUG("OnReadConvert called")
                return self._value
            return self._value

        elif ret == OpenRTM_aist.DataPortStatus.BUFFER_EMPTY:
            self._rtcout.RTC_WARN("buffer empty")
            return self._value

        elif ret == OpenRTM_aist.DataPortStatus.BUFFER_TIMEOUT:
            self._rtcout.RTC_WARN("buffer read timeout")
            return self._value

        self._rtcout.RTC_ERROR("unknown retern value from buffer.read()")
        return self._value

    ##
    # @if jp
    #
    # @brief バインドされた変数に InPort バッファの最新値を読み込む
    #
    # バインドされたデータに InPort の最新値を読み込む。
    # コンストラクタで変数と InPort がバインドされていなければならない。
    # このメソッドはポリモーフィックに使用される事を前提としているため、
    # 型に依存しない引数、戻り値となっている。
    #
    # @param self
    #
    # @else
    #
    # @brief Read into bound T-type data from current InPort
    #
    # @endif

    def update(self):
        self.read()

    ##
    # @if jp
    #
    # @brief InPort バッファへデータ読み込み時のコールバックの設定
    #
    # InPort が持つバッファからデータが読み込まれる直前に呼ばれるコールバック
    # オブジェクトを設定する。
    #
    # @param self
    # @param on_read 設定対象コールバックオブジェクト
    #
    # @else
    #
    # @endif

    def setOnRead(self, on_read):
        self._OnRead = on_read

    ##
    # @if jp
    #
    # @brief InPort バッファへデータ読み出し時のコールバックの設定
    #
    # InPort が持つバッファからデータが読み出される際に呼ばれるコールバック
    # オブジェクトを設定する。コールバックオブジェクトの戻り値がread()メソッド
    # の呼出結果となる。
    #
    # @param self
    # @param on_rconvert 設定対象コールバックオブジェクト
    #
    # @else
    #
    # @endif

    def setOnReadConvert(self, on_rconvert):
        self._OnReadConvert = on_rconvert

    ##
    # @if jp
    #
    # @brief データをダイレクトに書き込む
    #
    # @param self
    # @param data 書き込むデータ
    #
    # @else
    # @brief
    #
    # @param self
    # @param data
    # @endif
    # void write(const DataType& data)
    def write(self, data):
        guard = OpenRTM_aist.ScopedLock(self._valueMutex)
        self._value = data
        self._directNewData = True
        del guard
