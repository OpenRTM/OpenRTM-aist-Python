#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file EventPort.py
# @brief EventInPort template class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist
import OpenRTM_aist.Macho
import copy


##
# @if jp
#
# @class Event0
#
# @brief 引数なしのイベントを格納するクラス
# イベント受信時にリスナを格納し、Event0オブジェクトをバッファに格納する
# 実行時は__call__メソッドによりイベントを実行できる
#
# @since 2.0.0
#
# @else
#
# @class Event0
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#
class Event0:
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param eb イベント受信時のリスナ
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param eb
    #
    # @endif
    #
    def __init__(self, eb):
        self._eb = eb
    ##
    # @if jp
    #
    # @brief イベント実行
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

    def __call__(self):
        self._eb.run()

##
# @if jp
#
# @class Event1
#
# @brief 引数1つのイベントを格納するクラス
# イベント受信時にリスナ、引数を格納し、Event1オブジェクトをバッファに格納する
# 実行時は__call__メソッドによりイベントを実行できる
#
# @since 2.0.0
#
# @else
#
# @class Event1
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#


class Event1(Event0):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param eb イベント受信時のリスナ
    # @param data イベント実行時に指定する引数
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param eb
    # @param data
    #
    # @endif
    #
    def __init__(self, eb, data):
        Event0.__init__(self, eb)
        self._data = data
    ##
    # @if jp
    #
    # @brief イベント実行
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

    def __call__(self):
        self._eb.run(self._data)

##
# @if jp
#
# @class EventBinder0
#
# @brief 引数なしのイベント受信時のリスナ
# InPortのON_RECEIVEDコールバックに指定することで、
# イベント受信時にバッファにイベントを格納する
#
#
# @since 2.0.0
#
# @else
#
# @class EventBinder0
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#


class EventBinder0(OpenRTM_aist.ConnectorDataListener):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param fsm 有限状態マシン
    # @param event_name イベント名
    # @param handler イベントハンドラ
    # @param buffer イベントを格納するバッファ
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param fsm
    # @param event_name
    # @param handler
    # @param buffer
    #
    # @endif
    #
    def __init__(self, fsm, event_name, handler, buffer):
        self._fsm = fsm
        self._eventName = event_name
        self._handler = handler
        self._buffer = buffer

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A destructor.
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass
    ##
    # @if jp
    #
    # @brief イベント受信時のコールバック関数
    # コネクタプロファイルのfsm_event_nameの値がイベント名と一致している場合、バッファにイベントを格納する
    #
    # @param self
    # @param info コネクタプロファイル
    # @param data 受信データ
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param info
    # @param data
    # @return
    #
    # @endif
    #

    def __call__(self, info, cdrdata):
        if info.properties.getProperty(
                "fsm_event_name") == self._eventName or info.name == self._eventName:
            self._buffer.write(Event0(self))

            return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, cdrdata
        return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, cdrdata

    ##
    # @if jp
    #
    # @brief イベント実行関数
    # イベントハンドラに指定した処理を実行する
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
    def run(self):
        self._fsm.dispatch(OpenRTM_aist.Macho.Event(self._handler))


##
# @if jp
#
# @class EventBinder1
#
# @brief 引数1つのイベント受信時のリスナ
# InPortのON_RECEIVEDコールバックに指定することで、
# イベント受信時にバッファにイベントを格納する
#
#
# @since 2.0.0
#
# @else
#
# @class EventBinder1
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#
class EventBinder1(OpenRTM_aist.ConnectorDataListener):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param fsm 有限状態マシン
    # @param event_name イベント名
    # @param handler イベントハンドラ
    # @param data_type 入力データ型
    # @param buffer イベントを格納するバッファ
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param fsm
    # @param event_name
    # @param handler
    # @param data_type
    # @param buffer
    #
    # @endif
    #
    def __init__(self, fsm, event_name, handler, data_type, buffer):
        self._fsm = fsm
        self._eventName = event_name
        self._handler = handler
        self._data_type = data_type
        self._buffer = buffer

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A destructor.
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief イベント受信時のコールバック関数
    # コネクタプロファイルのfsm_event_nameの値がイベント名と一致している場合、バッファにイベントを格納する
    #
    # @param self
    # @param info コネクタプロファイル
    # @param data 受信データ
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param info
    # @param data
    # @return
    #
    # @endif
    #
    def __call__(self, info, cdrdata):
        data_ = OpenRTM_aist.ConnectorDataListenerT.__call__(
            self, info, cdrdata, self._data_type, OpenRTM_aist.PortType.InPortType)
        if info.properties.getProperty(
                "fsm_event_name") == self._eventName or info.name == self._eventName:
            self._buffer.write(Event1(self, data_))
            return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, cdrdata
        return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, cdrdata

    ##
    # @if jp
    #
    # @brief イベント実行関数
    # イベントハンドラに指定した処理を実行する
    #
    # @param self
    # @param data 受信データ
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
    def run(self, data):
        self._fsm.dispatch(OpenRTM_aist.Macho.Event(self._handler, data))


##
# @if jp
#
# @class EventConnListener
#
# @brief コネクタ接続時のリスナ
# InPortのON_CONNECTコールバックに指定する
# ポートが保持するバッファのwrite.full_policy、read.empty_policyをdo_nothingに設定することで、
# ポートが保持するバッファのデータ読み込み、書き込み時にブロックやエラー等を発生させないようにする
# 有限状態マシンが保持するバッファの初期化を行う
# このため、後で接続したコネクタの設定でバッファの設定が上書きされる
#
#
# @since 2.0.0
#
# @else
#
# @class EventConnListener
#
# @brief
#
# @since 2.0.0
#
#
# @endif
#
class EventConnListener(OpenRTM_aist.ConnectorListener):
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # @param self
    # @param buffer
    # @param thebuffer
    #
    # @else
    #
    # @brief A constructor.
    #
    # @param self
    # @param buffer
    # @param thebuffer
    #
    # @endif
    #
    def __init__(self, buffer, thebuffer):
        self._buffer = buffer
        self._thebuffer = thebuffer

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief A destructor.
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief コネクタ接続時のコールバック関数
    #
    # @param self
    # @param info コネクタプロファイル
    # @return リターンコード
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param info
    # @return
    #
    # @endif
    #
    def __call__(self, info):
        prop = OpenRTM_aist.Properties()
        prop.setProperty("write.full_policy", "do_nothing")
        prop.setProperty("read.empty_policy", "do_nothing")
        self._thebuffer.init(prop)

        prop_ = copy.copy(info.properties.getNode("buffer"))

        self._buffer.init(prop_)
        return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE


##
# @if jp
#
# @class EventInPort
#
# @brief EventInPort テンプレートクラス
#
# EventInPort の実装である EventInPort<T> のテンプレートクラス。
# <T> はBasicDataType.idl にて定義されている型で、メンバとして
# Time 型の tm , および T型の data を持つ構造体でなくてはならない。
# EventInPort は内部にリングバッファを持ち、外部から送信されたデータを順次
# このリングバッファに格納する。リングバッファのサイズはデフォルトで8と
# なっているが、コンストラクタ引数によりサイズを指定することができる。
# データはフラグによって未読、既読状態が管理され、isNew(), write(), read(),
# isFull(), isEmpty() 等のメソッドによりハンドリングすることができる。
#
# OnRead系コールバック (読み出しに起因するイベントによりコールされる)
#
# - void OnRead::operator():
#     EventInPort::read() を呼び出し読み出しを行う際にコールされる。
#
# - DataType OnReadConvert::operator(DataType):
#     EventInPort::read() を呼び出し、データをバッファから読みだす際に呼ばれ
#     データの変換を行う。引数にはバッファから読み出された値が与えられ、
#     変換後のデータを戻り値として返す。この値がread()の返す値となる。
#
# @since 2.0.0
#
# @else
#
# @class EventInPort
#
# @brief EventInPort template class
#
# This is a template class that implements EventInPort.  <T> is the type
# defined in BasicDataType.idl and must be the structure which has
# both Time type tm and type-T data as a member. EventInPort has a ring
# buffer internally, and stores the received data externally in
# this buffer one by one. The size of ring buffer can be specified
# according to the argument of constructor, though the default size
# is 8. Unread data and data which is already read are managed
# with the flag, and the data can be handled by the isNew(),
# write(), read(), isFull() and isEmpty() method etc.
#
# @since 2.0.0
#
# @endif
#
class EventInPort(OpenRTM_aist.InPortBase):
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
    def __init__(self, name, fsm):
        super(EventInPort, self).__init__(name, "any")
        self._name = name
        self._fsm = fsm
        self._buffer = self._fsm.getBuffer()

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
        super(EventInPort, self).__del__()
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
    # @brief 初期化
    # InPortBaseの初期化のほかにバッファ初期化のためのコネクタコールバック関数の登録を行う
    #
    # @param prop 設定情報
    #
    #
    # @else
    #
    # @brief
    #
    #
    # @param prop
    #
    # @endif
    #

    def init(self, prop):
        OpenRTM_aist.InPortBase.init(self, prop)
        self.addConnectorListener(OpenRTM_aist.ConnectorListenerType.ON_CONNECT,
                                  EventConnListener(self._buffer, self._thebuffer))
    ##
    # @if jp
    #
    # @brief 引数なしのイベントハンドラを登録する
    # コネクタのON_RECEIVEDコールバック実行時にバッファに実行予定のイベントとして格納する
    # バッファに格納したイベントはMachineのrun_event関数で実行する
    #
    # @param name イベント名
    # @param handler イベントハンドラ
    #
    #
    # @else
    #
    # @brief
    #
    # @param name
    # @param handler
    #
    # @endif
    #

    def bindEvent0(self, name, handler):
        self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                      EventBinder0(self._fsm, name, handler, self._buffer))
    ##
    # @if jp
    #
    # @brief 引数1つのイベントハンドラを登録する
    # コネクタのON_RECEIVEDコールバック実行時にバッファに実行予定のイベントとして格納する
    # バッファに格納したイベントはMachineのrun_event関数で実行する
    #
    # @param name イベント名
    # @param handler イベントハンドラ
    # @param data_type データ型
    #
    #
    # @else
    #
    # @brief
    #
    #
    # @param name
    # @param handler
    # @param data_type
    #
    # @endif
    #

    def bindEvent1(self, name, handler, data_type):
        self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                      EventBinder1(self._fsm, name, handler, data_type, self._buffer))
