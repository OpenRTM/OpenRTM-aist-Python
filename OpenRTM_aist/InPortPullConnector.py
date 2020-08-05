#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file InPortPullConnector.py
# @brief InPortPull type connector class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2009
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#


import OpenRTM_aist


##
# @if jp
# @class InPortPullConnector
# @brief InPortPullConnector クラス
#
# InPort の pull 型データフローのための Connector クラス。このオブ
# ジェクトは、接続時に dataflow_type に pull が指定された場合、
# InPort によって生成・所有され、OutPortPullConnector と対になって、
# データポートの pull 型のデータフローを実現する。一つの接続に対して、
# 一つのデータストリームを提供する唯一の Connector が対応する。
# Connector は 接続時に生成される UUID 形式の ID により区別される。
#
# InPortPullConnector は以下の三つのオブジェクトを所有し管理する。
#
# - InPortConsumer
# - Buffer
#
# OutPort に書き込まれたデータは OutPortPullConnector::write() に渡
# され Buffer に書き込まれる。InPort::read(),
# InPortPullConnector::read() は結果として、OutPortConsumer::get()
# を呼び出し、OutPortPullConnector の持つバッファからデータを読み出
# し、InPortPullConnector のもつバッファにデータを書き込む。
#
# @since 1.0.0
#
# @else
# @class InPortPullConnector
# @brief InPortPullConnector class
#
# Connector class of InPort for pull type dataflow. When "pull" is
# specified as dataflow_type at the time of establishing
# connection, this object is generated and owned by the InPort.
# This connector and InPortPullConnector make a pair and realize
# pull type dataflow of data ports. One connector corresponds to
# one connection which provides a data stream. Connector is
# distinguished by ID of the UUID that is generated at establishing
# connection.
#
# InPortPullConnector owns and manages the following objects.
#
# - InPortConsumer
# - Buffer
#
# Data written into the OutPort is passed to the
# OutPortPullConnector::write(), and is written into the buffer.
# Consequently, InPort::read() and InPortPullConnector::read() call
# OutPortConsumer::get(), and it reads data from the buffer of
# OutPortPullConnector.  Finally data would be written into the
# InPortPullConnector's buffer.
#
# @since 1.0.0
#
# @endif
#
class InPortPullConnector(OpenRTM_aist.InPortConnector):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # InPortPullConnector のコンストラクタはオブジェクト生成時に下記
    # を引数にとる。ConnectorInfo は接続情報を含み、この情報に従いバッ
    # ファ等を生成する。OutPort インターフェースのプロバイダオブジェク
    # トへのポインタを取り、所有権を持つので、InPortPullConnector は
    # OutPortConsumer の解体責任を持つ。各種イベントに対するコールバッ
    # ク機構を提供する ConnectorListeners を持ち、適切なタイミングでコー
    # ルバックを呼び出す。データバッファがもし InPortBase から提供さ
    # れる場合はそのポインタを取る。
    #
    # @param info ConnectorInfo
    # @param consumer OutPortConsumer
    # @param listeners ConnectorListeners 型のリスナオブジェクトリスト
    # @param buffer CdrBufferBase 型のバッファ
    #
    # @else
    # @brief Constructor
    #
    # InPortPullConnector's constructor is given the following
    # arguments.  According to ConnectorInfo which includes
    # connection information, a buffer is created.  It is also given
    # a pointer to the consumer object for the OutPort interface.
    # The owner-ship of the pointer is owned by this
    # OutPortPullConnector, it has responsibility to destruct the
    # OutPortConsumer.  OutPortPullConnector also has
    # ConnectorListeners to provide event callback mechanisms, and
    # they would be called at the proper timing.  If data buffer is
    # given by OutPortBase, the pointer to the buffer is also given
    # as arguments.
    #
    # @param info ConnectorInfo
    # @param consumer OutPortConsumer
    # @param listeners ConnectorListeners type lsitener object list
    # @param buffer CdrBufferBase type buffer
    #
    # @endif
    #
    # InPortPullConnector(ConnectorInfo info,
    #                     OutPortConsumer* consumer,
    #                     ConnectorListeners& listeners,
    #                     CdrBufferBase* buffer = 0);
    def __init__(self, info, consumer, listeners, buffer=None):
        OpenRTM_aist.InPortConnector.__init__(self, info, buffer)
        self._consumer = consumer
        self._listeners = listeners
        self._directOutPort = None
        self._outPortListeners = None

        if buffer is None:
            self._buffer = self.createBuffer(self._profile)

        if not self._buffer or not self._consumer:
            raise

        self._buffer.init(info.properties.getNode("buffer"))
        self._consumer.init(info.properties)
        self._consumer.setBuffer(self._buffer)
        self._consumer.setListener(info, self._listeners)
        self.onConnect()

        self._marshaling_type = info.properties.getProperty(
            "marshaling_type", "cdr")
        self._marshaling_type = self._marshaling_type.strip()

        self._serializer = None

        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # disconnect() が呼ばれ、consumer, publisher, buffer が解体・削除される。
    #
    # @else
    #
    # @brief Destructor
    #
    # This operation calls disconnect(), which destructs and deletes
    # the consumer, the publisher and the buffer.
    #
    # @endif
    #

    def __del__(self):
        return

    ##
    # @if jp
    # @brief read 関数
    #
    # OutPortConsumer からデータを取得する。正常に読み出せた場合、戻り
    # 値は PORT_OK となり、data に読み出されたデータが格納される。それ
    # 以外の場合には、エラー値として BUFFER_EMPTY, TIMEOUT,
    # PRECONDITION_NOT_MET, UNKNOWN_ERROR, PORT_ERROR が返される。
    #
    # @return PORT_OK              正常終了
    #         BUFFER_EMPTY         バッファは空である
    #         TIMEOUT              タイムアウトした
    #         PRECONDITION_NOT_MET 事前条件を満たさない
    #         UNKNOWN_ERROR        不明のエラー
    #         PORT_ERROR           その他のエラー
    #
    # @else
    # @brief Destructor
    #
    # This function get data from OutPortConsumer.  If data is read
    # properly, this function will return PORT_OK return code. Except
    # normal return, BUFFER_EMPTY, TIMEOUT, PRECONDITION_NOT_MET,
    # UNKNOWN_ERROR and PORT_ERROR will be returned as error codes.
    #
    # @return PORT_OK              Normal return
    #         BUFFER_EMPTY         Buffer empty
    #         TIMEOUT              Timeout
    #         PRECONDITION_NOT_MET Preconditin not met
    #         UNKNOWN_ERROR        Unknown errot
    #         PORT_ERROR           Other error
    #
    # @endif
    #
    # virtual ReturnCode read(cdrMemoryStream& data);

    def read(self, data=None):
        self._rtcout.RTC_TRACE("InPortPullConnector.read()")

        if self._directOutPort is not None:
            if self._directOutPort.isEmpty():
                self._listeners.notify(
                    OpenRTM_aist.ConnectorListenerType.ON_BUFFER_EMPTY, self._profile)
                self._outPortListeners.notify(
                    OpenRTM_aist.ConnectorListenerType.ON_SENDER_EMPTY, self._profile)
                self._rtcout.RTC_TRACE("ON_BUFFER_EMPTY(InPort,OutPort), ")
                self._rtcout.RTC_TRACE("ON_SENDER_EMPTY(InPort,OutPort) ")
                self._rtcout.RTC_TRACE("callback called in direct mode.")

            data = self._directOutPort.read()
            #self._outPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_READ, self._profile, data)
            self._rtcout.RTC_TRACE("ON_BUFFER_READ(OutPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            #self._outPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_SEND, self._profile, data)
            self._rtcout.RTC_TRACE("ON_SEND(OutPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
            self._rtcout.RTC_TRACE("ON_RECEIVED(InPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_SEND, self._profile, data)
            self._rtcout.RTC_TRACE("ON_BUFFER_WRITE(InPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            return self.PORT_OK, data

        if not self._consumer:
            return self.PORT_ERROR, data

        datatype = self._dataType
        if datatype is None:
            if data is None:
                self._rtcout.RTC_ERROR("invalid data type")
                return self.UNKNOWN_ERROR, data
            datatype = data

        ret, cdr_data = self._consumer.get()

        if ret == self.PORT_OK:

            if self._serializer is None:
                self._rtcout.RTC_ERROR("serializer creation failure.")
                return self.UNKNOWN_ERROR, data

            self._serializer.isLittleEndian(self._endian)
            ser_ret, data = self._serializer.deserialize(cdr_data, datatype)

            if ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN:
                self._rtcout.RTC_ERROR("unknown endian from connector")
                return self.UNKNOWN_ERROR, data
            elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR:
                self._rtcout.RTC_ERROR("unknown error")
                return self.UNKNOWN_ERROR, data
            elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOTFOUND:
                self._rtcout.RTC_ERROR("unknown serializer from connector")
                return self.UNKNOWN_ERROR, data

        return ret, data

    ##
    # @if jp
    # @brief 接続解除関数
    #
    # Connector が保持している接続を解除する
    #
    # @else
    # @brief Disconnect connection
    #
    # This operation disconnect this connection
    #
    # @endif
    #
    # virtual ReturnCode disconnect();

    def disconnect(self):
        self._rtcout.RTC_TRACE("disconnect()")
        self.onDisconnect()

        self._consumer = None
        self._serializer = None

        return self.PORT_OK

    ##
    # @if jp
    # @brief アクティブ化
    #
    # このコネクタをアクティブ化する
    #
    # @else
    #
    # @brief Connector activation
    #
    # This operation activates this connector
    #
    # @endif
    #
    # virtual void activate(){}; // do nothing
    def activate(self):  # do nothing
        pass

    ##
    # @if jp
    # @brief 非アクティブ化
    #
    # このコネクタを非アクティブ化する
    #
    # @else
    #
    # @brief Connector deactivation
    #
    # This operation deactivates this connector
    #
    # @endif
    #
    # virtual void deactivate(){}; // do nothing
    def deactivate(self):  # do nothing
        pass

    ##
    # @if jp
    # @brief Bufferの生成
    #
    # 与えられた接続情報に基づきバッファを生成する。
    #
    # @param info 接続情報
    # @return バッファへのポインタ
    #
    # @else
    # @brief create buffer
    #
    # This function creates a buffer based on given information.
    #
    # @param info Connector information
    # @return The poitner to the buffer
    #
    # @endif
    #
    # CdrBufferBase* createBuffer(Profile& profile);
    def createBuffer(self, profile):
        buf_type = profile.properties.getProperty("buffer_type", "ring_buffer")
        return OpenRTM_aist.CdrBufferFactory.instance().createObject(buf_type)

    ##
    # @if jp
    # @brief 接続確立時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is established
    # @endif
    # void onConnect()
    def onConnect(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_CONNECT, self._profile)
        return

    ##
    # @if jp
    # @brief 接続切断時にコールバックを呼ぶ
    # @else
    # @brief Invoke callback when connection is destroied
    # @endif
    # void onDisconnect()
    def onDisconnect(self):
        if self._listeners and self._profile:
            self._listeners.notify(
                OpenRTM_aist.ConnectorListenerType.ON_DISCONNECT, self._profile)
        return

    ##
    # @if jp
    # @brief データをダイレクトに書き込むためのOutPortのサーバントを設定する
    #
    # @param self
    # @param directOutPort OutPortのサーバント
    # @return True: 設定に成功 False: 既に設定済みのため失敗
    # @else
    # @brief
    #
    # @param self
    # @param directOutPort
    # @return
    # @endif
    #
    # bool setOutPort(setOutPort* directOutPort);

    def setOutPort(self, directOutPort):
        if self._directOutPort is not None:
            return False
        self._directOutPort = directOutPort
        self._outPortListeners = self._directOutPort._listeners
        return True

    ##
    # @if jp
    # @brief コンシューマのインターフェースの登録を取り消す
    # @param prop コネクタプロファイルのプロパティ
    # @else
    # @brief
    # @param prop
    # @endif

    def unsubscribeInterface(self, prop):
        if self._consumer:
            self._consumer.unsubscribeInterface(prop)


    def setDataType(self, data):
        OpenRTM_aist.InPortConnector.setDataType(self, data)
        self._serializer = OpenRTM_aist.SerializerFactories.instance().createSerializer(self._marshaling_type, data)