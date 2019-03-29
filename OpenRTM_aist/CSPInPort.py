#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file CSPInPort.py
# @brief CSPInPort template class
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
class CSPInPort(OpenRTM_aist.InPortBase):
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
  # @param bufsize Buffer length of internal ring buffer of EventInPort
  #                (The default value:64)
  #
  # @endif
  #
  def __init__(self, name, value, manager=None):
    super(CSPInPort, self).__init__(name, "any")
    self._ctrl = OpenRTM_aist.CSPInPort.WorkerThreadCtrl()
    self._name = name
    self._value = value

    self._OnRead = None
    self._OnReadConvert  = None

    self._singlebuffer  = True

    self._channeltimeout = 10
    self._bufferzeromode = False
    self._manager = manager
    if manager:
      manager.addInPort(self)
    self._writingConnector = None


    
    
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
    super(CSPInPort, self).__del__()

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
  # buffer.lengthが0の場合は非リングバッファモードに設定
  # データ読み込み待機状態に移行していないとデータを書き込むことができない
  # buffer.lengthが1以上の場合はリングバッファモードに設定
  # バッファに空きがある場合はデータの書き込みができる
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
  def init(self,prop):
    super(CSPInPort, self).init(prop)

    num = [10]
    if OpenRTM_aist.stringTo(num, self._properties.getProperty("channel_timeout","10")):
      self._channeltimeout = num[0]

    buff_prop = prop.getNode("buffer")
    length = [8]
    OpenRTM_aist.stringTo(length, buff_prop.getProperty("length","8"))

    if length[0] == 0:
      buff_prop.setProperty("length","1")
      self._bufferzeromode = True

    
    self._thebuffer.init(buff_prop)


    if not self._bufferzeromode:
      self._writable_listener = OpenRTM_aist.CSPInPort.IsWritableListener(self._thebuffer, self._ctrl, self._channeltimeout, self, self._manager)
      self._write_listener = OpenRTM_aist.CSPInPort.WriteListener(self._thebuffer,self._ctrl)
    else:
      self._writable_listener = OpenRTM_aist.CSPInPort.IsWritableZeroModeListener(self._thebuffer, self._ctrl, self._channeltimeout, self, self._manager)
      self._write_listener = OpenRTM_aist.CSPInPort.WriteZeroModeListener(self._thebuffer,self._ctrl)

  ##  
  # @if jp
  #
  # @brief 書き込み処理を開始したコネクタを登録
  #
  # @param self
  # @param con InPortConnector
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
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
  # @param self
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
  def notify(self):
    for con in self._connectors:
      guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._thebuffer.full():
        del guard_ctrl
        if con.isReadable():
          ret, cdr = con.readBuff()
          if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            self._thebuffer.write(cdr)
          else:
            self._rtcout.RTC_ERROR("notify read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
          
  ##
  # @if jp
  #
  # @brief コネクタ接続関数
  # InPortBaseの接続処理のほかに、コネクタに書き込み確認時、書き込み時のコールバック関数を設定する
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
    ret, prof = super(CSPInPort, self).notify_connect(connector_profile)
    guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
    for con in self._connectors:
      con.setIsWritableListener(self._writable_listener)
      con.setWriteListener(self._write_listener)
    return (ret, prof)


  ##
  # @if jp
  #
  # @brief リングバッファ使用モード時のデータ読み込み処理
  # バッファがemptyではない場合はバッファから読み込む
  # コネクタの中に読み込み可能なものがある場合は、そのコネクタから読み込む
  # ただし、書き込み中の場合は書き込み終了までブロックする
  #
  # @param self
  # @param connector_profile コネクタプロファイル
  # @return ret, prof
  # ret：True：読み込み成功、False：バッファがemptyでかつ読み込み可能なコネクタが存在しない
  # data：データ
  # 
  #
  # @else
  #
  # @brief 
  #
  # @param self
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
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        if not self._thebuffer.empty():
          value = [None]
          self._thebuffer.read(value)
          del guard_ctrl
          self.notify()
          ret, data = con.deserializeData(value[0])
          if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
            return True, data
          else:
            self._rtcout.RTC_ERROR("deserialize error")
        elif self._ctrl._writing:
          self._ctrl._cond.wait(self._channeltimeout)
          value = [None]
          if not self._thebuffer.empty():
            self._thebuffer.read(value)
            del guard_ctrl
            self.notify()
            ret, data = con.deserializeData(value[0])
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
              return True, data
            else:
              self._rtcout.RTC_ERROR("deserialize error")
              return False, None
          else:
            self._rtcout.RTC_ERROR("read timeout")
            return False, None
        else:
          del guard_ctrl
          readable = con.isReadable()
          if readable:
            value = [None]
            ret = con.read(value)
            if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
              return True, value[0]
            else:
              self._rtcout.RTC_ERROR("empty read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
              return False, None
    else:
      value = [None]
      guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if not self._thebuffer.empty():
        self._thebuffer.read(value)
        del guard_ctrl
        self.notify()
        ret, data = self._connectors[0].deserializeData(value[0])
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
          return True, data
        else:
          self._rtcout.RTC_ERROR("deserialize error")
          return False, None
      else:
        self._rtcout.RTC_ERROR("value read error:%s",(OpenRTM_aist.BufferStatus.toString(ret)))
        del guard_ctrl
        self.notify()
        return False, None
    return False, None


  ##
  # @if jp
  #
  # @brief 非リングバッファ使用モード時のデータ読み込み処理
  # データ読み込み可能なコネクタが存在する場合は、そのコネクタからデータを読み込む
  # 
  #
  # @param self
  # @param connector_profile コネクタプロファイル
  # @return ret, prof
  # ret：True：読み込み成功、False：データ読み込み可能なコネクタが存在しない
  # data：データ(読み込み失敗の場合はNone)
  # 
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
  def dataPullZeroMode(self):
    guard_con = OpenRTM_aist.ScopedLock(self._connector_mutex)
    for con in self._connectors:
      if con.isReadable():
        guard_ctrl = OpenRTM_aist.ScopedLock(self._ctrl._cond)
        value = [None]
        ret = con.read(value)
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
          return True, value[0]
        else:
          self._rtcout.RTC_ERROR("read error:%s",(OpenRTM_aist.DataPortStatus.toString(ret)))
          return False, None
    return False, None

  

  ##
  # @if jp
  #
  # @brief データ読み込み可能なコネクタを選択し、
  # self._valueに読み込んだデータを格納する
  # 
  #
  # @param self
  # @return True：読み込み成功、False：読み込み不可
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
  def select(self):
    self._rtcout.RTC_TRACE("select()")
    if not self._bufferzeromode:
      ret, value = self.dataPullBufferMode()
    else:
      ret, value = self.dataPullZeroMode()
    guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
    if ret:
      self._value = value
    return ret
    
  ##
  # @if jp
  #
  # @brief select関数で格納したデータの取得
  # 
  #
  # @param self
  # @return データ
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
        value = [None]
        self._thebuffer.read(value)
        ret, data = self._connectors[0].deserializeData(value[0])
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
  # @param self
  # @return データ(タイムアウトした場合はNone)
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
  # @param self
  # @return データ(タイムアウトした場合はNone)
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
  def readBufferMode(self):
    ret, data = self.dataPullBufferMode()
    if ret:
      return data
    else:
      value = [None]
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing or self._thebuffer.empty():
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._thebuffer.empty():
        self._thebuffer.read(value)

        ret, data = self._connectors[0].deserializeData(value[0])
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
  # @param self
  # @return データ(タイムアウトした場合はNone)
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
  def readZeroMode(self):
    ret, data = self.dataPullZeroMode()
    if ret:
      return data
    else:
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._ctrl._waiting = True
      self._ctrl._cond.wait(self._channeltimeout)
      self._ctrl._waiting = False
      value = [None]
      if not self._thebuffer.empty():
        self._thebuffer.read(value)
        ret, data = self._connectors[0].deserializeData(value[0])
        if ret == OpenRTM_aist.DataPortStatus.PORT_OK:
          return data
        else:
          self._rtcout.RTC_ERROR("deserialize error")
          return None
      else:
        self._rtcout.RTC_ERROR("read timeout")
        return None

  def setOnRead(self, on_read):
    self._OnRead = on_read

  def setOnReadConvert(self, on_rconvert):
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
  # @brief 
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
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # @param timeout 書き込み待機のタイムアウト時間
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
    # @param buff 
    # @param control 
    # @param timeout 
    # @param manager 
    #
    # @endif
    #
    def __init__(self, buff, control, timeout, port, manager=None):
      self._ctrl = control
      self._buffer = buff
      self._channeltimeout = timeout
      self._manager = manager
      self._port = port
    ##
    # @if jp
    #
    # @brief 書き込み確認時のコールバック関数
    # 他のコネクタがデータ書き込み中の場合は完了まで待機する
    # バッファがフルではない場合は書き込み状態に移行する
    # このため、書き込み可能な場合は必ずデータを書き込む必要がある
    # 
    #
    # @param self
    # @param con InPortConnector
    # @return True：書き込み可能、False：書き込み不可
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param con 
    # @return
    #
    # @endif
    #
    def __call__(self, con):
      if self._manager:
        if self._manager.notify(inport=self._port):
          guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
          self._ctrl._writing = True
          self._port.setWritingConnector(con)
          return True
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if not self._buffer.full():
        self._ctrl._writing = True
        return True
      else:
        self._ctrl._writing = False
        return False

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
  # @brief 
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
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param buff 
    # @param control 
    #
    # @endif
    #
    def __init__(self, buff, control):
      self._ctrl = control
      self._buffer = buff
    ##
    # @if jp
    #
    # @brief 書き込み時のコールバック関数
    # データをバッファに追加し、書き込み状態を解除する
    # 
    #
    # @param self
    # @param data データ
    # @return リターンコード
    # BUFFER_OK：正常完了
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param data 
    # @return
    #
    # @endif
    #
    def __call__(self, data):
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._buffer.write(data)
      self._ctrl._writing = False
      self._ctrl._cond.notify()
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
  # @brief 
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
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # @param timeout 書き込み待機のタイムアウト時間
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
    # @param buff 
    # @param control 
    # @param timeout 
    # @param manager 
    #
    # @endif
    #
    def __init__(self, buff, control, timeout, port, manager=None):
      self._ctrl = control
      self._buffer = buff
      self._channeltimeout = timeout
      self._port = port
      self._manager = manager
    ##
    # @if jp
    #
    # @brief 書き込み確認時のコールバック関数
    # 他のコネクタがデータ書き込み中の場合は完了まで待機する
    # バッファがフルではない場合は書き込み状態に移行する
    # このため、書き込み可能な場合は必ずデータを書き込む必要がある
    # 
    #
    # @param self
    # @param con InPortConnector
    # @return True：書き込み可能、False：書き込み不可
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param con 
    # @return
    #
    # @endif
    #
    def __call__(self, con):
      if self._manager:
        if self._manager.notify(inport=self._port):
          guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
          self._ctrl._writing = True
          self._port.setWritingConnector(con)
          return True
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      if self._ctrl._waiting and self._ctrl._writing:
        self._ctrl._cond.wait(self._channeltimeout)
      if self._ctrl._waiting:
        self._ctrl._writing = True
        return True
      else:
        self._ctrl._writing = False
        return False
        
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
  # @brief 
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
    # @param self
    # @param buff リングバッファ
    # @param control WorkerThreadCtrlオブジェクト
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param buff 
    # @param control 
    #
    # @endif
    #
    def __init__(self, buff, control):
      self._ctrl = control
      self._buffer = buff
    ##
    # @if jp
    #
    # @brief 書き込み時のコールバック関数
    # 書き込み状態を解除しバッファにデータを追加する。
    # 
    #
    # @param self
    # @param data データ
    # @return リターンコード
    # BUFFER_OK：正常完了
    # 
    #
    #
    # @else
    #
    # @brief 
    #
    # @param self
    # @param data 
    # @return
    #
    # @endif
    #
    def __call__(self, data):
      guard = OpenRTM_aist.ScopedLock(self._ctrl._cond)
      self._ctrl._writing = False
      self._buffer.write(data)
      self._ctrl._cond.notify()
      return OpenRTM_aist.BufferStatus.BUFFER_OK
        

  class WorkerThreadCtrl:
    def __init__(self):
      self._mutex = threading.RLock()
      self._cond = threading.Condition(self._mutex)
      self._writing = False
      self._waiting = False

