#!/usr/bin/env python
# -*- coding: euc-jp -*-

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


class EventBinder0(OpenRTM_aist.ConnectorDataListener):
  def __init__(self, fsm, event_name, handler):
    self._fsm = fsm
    self._eventName = event_name
    self._handler = handler
  def __del__(self):
    pass
  def __call__(self, info, data):
    if info.properties.getProperty("fsm_event_name") == self._eventName or info.name == self._eventName:
      self._fsm.dispatch(OpenRTM_aist.Macho.Event0(self._handler))
      return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE
    return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE

    

class EventBinder1(OpenRTM_aist.ConnectorDataListenerT):
  def __init__(self, fsm, event_name, handler, data_type):
    self._fsm = fsm
    self._eventName = event_name
    self._handler = handler
    self._data_type = data_type
  def __del__(self):
    pass
  def __call__(self, info, data):
    data_ = OpenRTM_aist.ConnectorDataListenerT.__call__(self, info, data, self._data_type)
    
    if info.properties.getProperty("fsm_event_name") == self._eventName or info.name == self._eventName:
      self._fsm.dispatch(OpenRTM_aist.Macho.Event1(self._handler, data_))
      return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE
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
# このリングバッファに格納する。リングバッファのサイズはデフォルトで64と
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
# @since 0.2.0
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
# is 64. Unread data and data which is already read are managed
# with the flag, and the data can be handled by the isNew(),
# write(), read(), isFull() and isEmpty() method etc.
#
# @since 0.2.0
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
  # @param bufsize EventInPort 内部のリングバッファのバッファ長(デフォルト値:64)
  # @param read_block 読込ブロックフラグ。
  #        データ読込時に未読データがない場合、次のデータ受信までブロックする
  #        かどうかを設定(デフォルト値:false)
  # @param write_block 書込ブロックフラグ。
  #        データ書込時にバッファがフルであった場合、バッファに空きができる
  #        までブロックするかどうかを設定(デフォルト値:false)
  # @param read_timeout 読込ブロックを指定していない場合の、データ読取タイム
  #        アウト時間(ミリ秒)(デフォルト値:0)
  # @param write_timeout 書込ブロックを指定していない場合の、データ書込タイム
  #        アウト時間(ミリ秒)(デフォルト値:0)
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
  # @param bufsize Buffer length of internal ring buffer of EventInPort
  #                (The default value:64)
  # @param read_block Flag of reading block.
  #                   When there are not unread data at reading data,
  #                   set whether to block data until receiving the next 
  #                   data. (The default value:false)
  # @param write_block Flag of writing block.
  #                    If the buffer was full at writing data, set whether 
  #                    to block data until the buffer has space. 
  #                    (The default value:false)
  # @param read_timeout Data reading timeout time (millisecond) 
  #                     when not specifying read blocking.
  #                     (The default value:0)
  # @param write_timeout Data writing timeout time (millisecond)
  #                      when not specifying writing block.
  #                      (The default value:0)
  #
  # @endif
  #
  def __init__(self, name, fsm, bufsize=64, read_block=False, write_block=False, read_timeout=0, write_timeout=0):
    super(EventInPort, self).__init__(name, "any")
    self._name = name
    self._fsm = fsm
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

  def bindEvent0(self, name, handler):
    self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                  EventBinder0(self._fsm, name, handler))
    
  def bindEvent1(self, name, handler, data_type):
    self.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED,
                                  EventBinder1(self._fsm, name, handler, data_type))
  




