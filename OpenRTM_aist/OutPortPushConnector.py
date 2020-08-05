#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file OutPortPushConnector.py
# @brief Push type connector class
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
# @class OutPortPushConnector
# @brief OutPortPushConnector クラス
#
# OutPort の push 型データフローのための Connector クラス。このオブ
# ジェクトは、接続時に dataflow_type に push が指定された場合、
# OutPort によって生成・所有され、InPortPushConnector と対になって、
# データポートの push 型のデータフローを実現する。一つの接続に対して、
# 一つのデータストリームを提供する唯一の Connector が対応する。
# Connector は 接続時に生成される UUID 形式の ID により区別される。
#
# OutPortPushConnector は以下の三つのオブジェクトを所有し管理する。
#
# - InPortConsumer
# - Buffer
# - Publisher
#
# OutPort に書き込まれたデータは OutPortPushConnector::write() に渡
# され、Connector は Publisher にデータを書き込む。Publisher はその
# 特性に従ってデータを Buffer から取得し InPortConsumer に対して
# push することで InPort にデータが転送される。
#
# @since 1.0.0
#
# @else
# @class OutPortPushConnector
# @brief OutPortPushConnector class
#
# Connector class of OutPort for push type dataflow.  When "push"
# is specified as dataflow_type at the time of establishing
# connection, this object is generated and owned by the OutPort.
# This connector and InPortPushConnector make a pair and realize
# push type dataflow of data ports.  One connector corresponds to
# one connection which provides a data stream.  Connector is
# distinguished by ID of the UUID that is generated at establishing
# connection.
#
# OutPortPushConnector owns and manages the following objects.
#
# - InPortConsumer
# - Buffer
# - Publisher
#
# @since 1.0.0
#
# Data written into the OutPort is passed to
# OutPortPushConnector::write(), and the connector writes into the
# publisher.  The publisher gets data from the buffer based on the
# policy and it is transferred to InPort by pushing it into the
# InPortConsumer.
#
# @endif
#
class OutPortPushConnector(OpenRTM_aist.OutPortConnector):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # OutPortPushConnector のコンストラクタはオブジェクト生成時に下記
    # を引数にとる。ConnectorInfo は接続情報を含み、この情報に従いパブ
    # リッシャやバッファ等を生成する。InPort インターフェースに対する
    # コンシューマオブジェクトへのポインタを取り、所有権を持つので、
    # OutPortPushConnector は InPortConsumer の解体責任を持つ。各種イ
    # ベントに対するコールバック機構を提供する ConnectorListeners を持
    # ち、適切なタイミングでコールバックを呼び出す。データバッファがも
    # し OutPortBase から提供される場合はそのポインタを取る。
    #
    # @param info ConnectorInfo
    # @param consumer InPortConsumer
    # @param listeners ConnectorListeners 型のリスナオブジェクトリスト
    # @param buffer CdrBufferBase 型のバッファ
    #
    # @else
    # @brief Constructor
    #
    # OutPortPushConnector's constructor is given the following
    # arguments.  According to ConnectorInfo which includes
    # connection information, a publisher and a buffer are created.
    # It is also given a pointer to the consumer object for the
    # InPort interface.  The owner-ship of the pointer is owned by
    # this OutPortPushConnector, it has responsibility to destruct
    # the InPortConsumer.  OutPortPushConnector also has
    # ConnectorListeners to provide event callback mechanisms, and
    # they would be called at the proper timing.  If data buffer is
    # given by OutPortBase, the pointer to the buffer is also given
    # as arguments.
    #
    # @param info ConnectorInfo
    # @param consumer InPortConsumer
    # @param listeners ConnectorListeners type lsitener object list
    # @param buffer CdrBufferBase type buffer
    #
    # @endif
    #
    # OutPortPushConnector(ConnectorInfo info,
    #                      InPortConsumer* consumer,
    #                      ConnectorListeners& listeners,
    #                      CdrBufferBase* buffer = 0);
    def __init__(self, info, consumer, listeners, buffer=None):
        OpenRTM_aist.OutPortConnector.__init__(self, info)

        self._buffer = buffer
        self._consumer = consumer
        self._listeners = listeners

        self._directInPort = None
        self._inPortListeners = None

        # publisher/buffer creation. This may throw std::bad_alloc;
        self._publisher = self.createPublisher(info)
        if not self._buffer:
            self._buffer = self.createBuffer(info)

        if not self._publisher or not self._buffer or not self._consumer:
            raise

        if self._publisher.init(info.properties) != self.PORT_OK:
            raise

        if self._profile.properties.hasKey("serializer"):
            endian = self._profile.properties.getProperty(
                "serializer.cdr.endian")
            if not endian:
                self._rtcout.RTC_ERROR("write(): endian is not set.")
                raise

            # Maybe endian is ["little","big"]
            endian = OpenRTM_aist.split(endian, ",")
            # Maybe self._endian is "little" or "big"
            endian = OpenRTM_aist.normalize(endian[0])
            if endian == "little":
                self._endian = True
            elif endian == "big":
                self._endian = False
            else:
                self._endian = None

        else:
            self._endian = True  # little endian

        self._buffer.init(info.properties.getNode("buffer"))
        self._consumer.init(info.properties)
        self._publisher.setConsumer(self._consumer)
        self._publisher.setBuffer(self._buffer)
        self._publisher.setListener(self._profile, self._listeners)

        self._marshaling_type = info.properties.getProperty(
            "marshaling_type", "cdr")
        self._marshaling_type = self._marshaling_type.strip()

        self._serializer = None

        self.onConnect()
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    #
    #
    # @else
    #
    # @brief Destructor
    #
    #
    # @endif
    #

    def __del__(self):
        return

    ##
    # @if jp
    # @brief データの書き込み
    #
    # Publisherに対してデータを書き込み、これにより対応するInPortへデー
    # タが転送される。正常終了した場合 PORT_OK が返される。それ以外の
    # 場合、エラー値として、CONNECTION_LOST, BUFFER_FULL,
    # BUFFER_ERROR, PORT_ERROR, BUFFER_TIMEOUT, PRECONDITION_NO_MET が
    # 返される。
    #
    # @return PORT_OK              正常終了
    #         CONNECTION_LOST      接続がロストした
    #         BUFFER_FULL          バッファが一杯である
    #         BUFFER_ERROR         バッファエラー
    #         BUFFER_TIMEOUT       バッファへの書き込みがタイムアウトした
    #         PRECONDITION_NOT_MET 事前条件を満たさない
    #         PORT_ERROR           その他のエラー
    #
    # @else
    #
    # @brief Writing data
    #
    # This operation writes data into publisher and then the data
    # will be transferred to correspondent InPort. If data is written
    # properly, this function will return PORT_OK return code. Except
    # normal return, CONNECTION_LOST, BUFFER_FULL, BUFFER_ERROR,
    # PORT_ERROR, BUFFER_TIMEOUT and PRECONDITION_NO_MET will be
    # returned as error codes.
    #
    # @return PORT_OK              Normal return
    #         CONNECTION_LOST      Connectin lost
    #         BUFFER_FULL          Buffer full
    #         BUFFER_ERROR         Buffer error
    #         BUFFER_TIMEOUT       Timeout
    #         PRECONDITION_NOT_MET Precondition not met
    #         PORT_ERROR           Other error
    #
    # @endif
    #
    # template<class DataType>
    # virtual ReturnCode write(const DataType& data);
    def write(self, data):
        self._rtcout.RTC_TRACE("write()")

        if self._directInPort is not None:
            if self._directInPort.isNew():
                #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
                #self._inPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_OVERWRITE, self._profile, data)
                #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
                #self._inPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVER_FULL, self._profile, data)
                self._rtcout.RTC_TRACE("ONBUFFER_OVERWRITE(InPort,OutPort), ")
                self._rtcout.RTC_TRACE("ON_RECEIVER_FULL(InPort,OutPort) ")
                self._rtcout.RTC_TRACE("callback called in direct mode.")
            #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
            #self._inPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE, self._profile, data)
            self._rtcout.RTC_TRACE("ON_BUFFER_WRITE(InPort,OutPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            self._directInPort.write(data)
            #self._listeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
            #self._inPortListeners.notifyData(OpenRTM_aist.ConnectorDataListenerType.ON_RECEIVED, self._profile, data)
            self._rtcout.RTC_TRACE("ON_RECEIVED(InPort,OutPort), ")
            self._rtcout.RTC_TRACE("callback called in direct mode.")
            return self.PORT_OK
        # data -> (conversion) -> CDR stream
        if self._serializer is None:
            self._rtcout.RTC_ERROR("serializer creation failure.")
            return self.UNKNOWN_ERROR

        self._serializer.isLittleEndian(self._endian)
        ser_ret, cdr_data = self._serializer.serialize(data)
        if ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN:
            self._rtcout.RTC_ERROR(
                "write(): endian %s is not support.", self._endian)
            return self.UNKNOWN_ERROR
        elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR:
            self._rtcout.RTC_ERROR("unkown error.")
            return self.UNKNOWN_ERROR
        elif ser_ret == OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOTFOUND:
            self._rtcout.RTC_ERROR(
                "write(): serializer %s is not support.",
                self._marshaling_type)
            return self.UNKNOWN_ERROR

        return self._publisher.write(cdr_data, -1, 0)

    ##
    # @if jp
    # @brief 接続解除
    #
    # consumer, publisher, buffer が解体・削除される。
    #
    # @else
    #
    # @brief disconnect
    #
    # This operation destruct and delete the consumer, the publisher
    # and the buffer.
    #
    # @endif
    #
    # virtual ReturnCode disconnect();

    def disconnect(self):
        self._rtcout.RTC_TRACE("disconnect()")
        self.onDisconnect()
        # delete publisher
        if self._publisher:
            self._rtcout.RTC_DEBUG("delete publisher")
            self._publisher.exit()
            pfactory = OpenRTM_aist.PublisherFactory.instance()

        self._publisher = None

        # delete consumer
        if self._consumer:
            self._rtcout.RTC_DEBUG("delete consumer")
            cfactory = OpenRTM_aist.InPortConsumerFactory.instance()

        self._consumer = None

        # delete buffer
        if self._buffer:
            self._rtcout.RTC_DEBUG("delete buffer")
            bfactory = OpenRTM_aist.CdrBufferFactory.instance()

        self._buffer = None

        if self._serializer:
            self._rtcout.RTC_DEBUG("delete serializer")
        self._serializer = None

        self._rtcout.RTC_TRACE("disconnect() done")

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
    # virtual void activate();

    def activate(self):
        self._publisher.activate()
        return

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
    # virtual void deactivate();

    def deactivate(self):
        self._publisher.deactivate()
        return

    ##
    # @if jp
    # @brief Buffer を取得する
    #
    # Connector が保持している Buffer を返す
    #
    # @else
    # @brief Getting Buffer
    #
    # This operation returns this connector's buffer
    #
    # @endif
    #
    # virtual CdrBufferBase* getBuffer();

    def getBuffer(self):
        return self._buffer

    ##
    # @if jp
    # @brief Publisherの生成
    #
    # 与えられた接続情報に基づきパブリッシャを生成する。
    #
    # @param info 接続情報
    # @return パブリッシャへのポインタ
    #
    # @else
    # @brief create buffer
    #
    # This function creates a publisher based on given information.
    #
    # @param info Connector information
    # @return The poitner to the publisher
    #
    # @endif
    #
    # virtual PublisherBase* createPublisher(ConnectorInfo& info);

    def createPublisher(self, info):
        pub_type = info.properties.getProperty("io_mode")
        if not pub_type:
            pub_type = info.properties.getProperty(
                "subscription_type", "flush")
            pub_type = OpenRTM_aist.normalize(pub_type)
            if pub_type == "flush":
                info.properties.setProperty("io_mode", "block")
            elif pub_type == "new":
                info.properties.setProperty("io_mode", "nonblock")
            else:
                info.properties.setProperty("io_mode", "pub_type")

        return OpenRTM_aist.PublisherFactory.instance().createObject(pub_type)

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
    # virtual CdrBufferBase* createBuffer(ConnectorInfo& info);

    def createBuffer(self, info):
        buf_type = info.properties.getProperty("buffer_type",
                                               "ring_buffer")

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
    # @brief データをダイレクトに書き込むためのInPortのサーバントを設定する
    #
    # @param self
    # @param directInPort InPortのサーバント
    # @return True: 設定に成功 False: 既に設定済みのため失敗
    # @else
    # @brief
    #
    # @param self
    # @param directInPort
    # @return
    # @endif
    #
    # bool setInPort(InPortBase* directInPort);
    def setInPort(self, directInPort):
        if self._directInPort is not None:
            return False
        self._directInPort = directInPort
        self._inPortListeners = self._directInPort._listeners
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
        OpenRTM_aist.OutPortConnector.setDataType(self, data)
        self._serializer = OpenRTM_aist.SerializerFactories.instance().createSerializer(self._marshaling_type, data)
