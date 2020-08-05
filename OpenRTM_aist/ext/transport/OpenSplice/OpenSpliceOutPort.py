#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OpenSpliceOutPort.py
# @brief OpenSplice OutPort class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist
from OpenSpliceTopicManager import OpenSpliceTopicManager
import OpenSpliceMessageInfo
import RTC


##
# @if jp
# @class OpenSpliceOutPort
# @brief OpenSplice Publisherに対応するクラス
# InPortConsumerオブジェクトとして使用する
#
# @else
# @class OpenSpliceOutPort
# @brief
#
#
# @endif
class OpenSpliceOutPort(OpenRTM_aist.InPortConsumer):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # @param self
    #
    # @endif
    def __init__(self):
        OpenRTM_aist.InPortConsumer.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OpenSpliceOutPort")
        self._properties = None
        self._dataType = RTC.TimedLong._NP_RepositoryId
        self._topic = "chatter"
        self._writer = None

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    #
    # @endif
    #

    def __del__(self):
        self._rtcout.RTC_PARANOID("~OpenSpliceOutPort()")

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    #
    # @param self
    # @param prop 接続設定
    # marshaling_type シリアライザの種類 デフォルト：OpenSplice
    # topic トピック名 デフォルト chatter
    #
    # @else
    # @brief Initializing configuration
    #
    # This operation would be called to configure this consumer
    # in initialization.
    #
    # @param self
    # @param prop
    #
    # @endif
    #
    # virtual void init(coil::Properties& prop);
    def init(self, prop):
        self._rtcout.RTC_PARANOID("init()")

        if not prop.propertyNames():
            self._rtcout.RTC_DEBUG("Property is empty.")
            return

        self._properties = prop

        qosxml = prop.getProperty("QOSXML")
        qosprofile = prop.getProperty("QOSPrfile")
        self._topicmgr = OpenSpliceTopicManager.instance(qosxml, qosprofile)

        self._dataType = prop.getProperty("data_type", self._dataType)

        self._topic = prop.getProperty("opensplice.topic", "chatter")

        topic = self._topicmgr.createTopic(self._dataType, self._topic)

        self._rtcout.RTC_VERBOSE("data type: %s", self._dataType)
        self._rtcout.RTC_VERBOSE("topic name: %s", self._topic)

        self._writer = self._topicmgr.createWriter(topic)

    ##
    # @if jp
    # @brief 接続先へのデータ送信
    #
    # 接続先のポートへデータを送信するための純粋仮想関数。
    #
    # この関数は、以下のリターンコードを返す。
    #
    # - PORT_OK:       正常終了。
    # - PORT_ERROR:    データ送信の過程で何らかのエラーが発生した。
    # - SEND_FULL:     データを送信したが、相手側バッファがフルだった。
    # - SEND_TIMEOUT:  データを送信したが、相手側バッファがタイムアウトした。
    # - UNKNOWN_ERROR: 原因不明のエラー
    #
    # @param data 送信するデータ
    # @return リターンコード
    #
    # @else
    # @brief Send data to the destination port
    #
    # Pure virtual function to send data to the destination port.
    #
    # This function might the following return codes
    #
    # - PORT_OK:       Normal return
    # - PORT_ERROR:    Error occurred in data transfer process
    # - SEND_FULL:     Buffer full although OutPort tried to send data
    # - SEND_TIMEOUT:  Timeout although OutPort tried to send data
    # - UNKNOWN_ERROR: Unknown error
    #
    # @endif
    #
    # virtual ReturnCode put(const cdrMemoryStream& data);
    def put(self, data):
        self._rtcout.RTC_PARANOID("put()")

        if self._writer:
            try:
                self._writer.write(data)
                return self.PORT_OK
            except BaseException:
                self._rtcout.RTC_ERROR("write error")
                return self.CONNECTION_LOST
        else:
            return self.CONNECTION_LOST

    ##
    # @if jp
    # @brief InterfaceProfile情報を公開する
    #
    # InterfaceProfile情報を公開する。
    # 引数で指定するプロパティ情報内の NameValue オブジェクトの
    # dataport.interface_type 値を調べ、当該ポートに設定されている
    # インターフェースタイプと一致する場合のみ情報を取得する。
    #
    # @param properties InterfaceProfile情報を受け取るプロパティ
    #
    # @else
    # @brief Publish InterfaceProfile information
    #
    # Publish interfaceProfile information.
    # Check the dataport.interface_type value of the NameValue object
    # specified by an argument in property information and get information
    # only when the interface type of the specified port is matched.
    #
    # @param properties Properties to get InterfaceProfile information
    #
    # @endif
    #
    # virtual void publishInterfaceProfile(SDOPackage::NVList& properties);

    def publishInterfaceProfile(self, properties):
        pass

    ##
    # @if jp
    # @brief データ送信通知への登録
    #
    # 指定されたプロパティに基づいて、データ送出通知の受け取りに登録する。
    #
    # @param properties 登録情報
    #
    # @return 登録処理結果(登録成功:true、登録失敗:false)
    #
    # @else
    # @brief Subscribe to the data sending notification
    #
    # Subscribe to the data sending notification based on specified
    # property information.
    #
    # @param properties Information for subscription
    #
    # @return Subscription result (Successful:true, Failed:false)
    #
    # @endif
    #
    # virtual bool subscribeInterface(const SDOPackage::NVList& properties);
    def subscribeInterface(self, properties):
        return True

    ##
    # @if jp
    # @brief データ送信通知からの登録解除
    #
    # データ送出通知の受け取りから登録を解除する。
    #
    # @param properties 登録解除情報
    #
    # @else
    # @brief Unsubscribe the data send notification
    #
    # Unsubscribe the data send notification.
    #
    # @param properties Information for unsubscription
    #
    # @endif
    #
    # virtual void unsubscribeInterface(const SDOPackage::NVList& properties);
    def unsubscribeInterface(self, properties):
        if self._writer:
            self._writer.close()
            self._rtcout.RTC_VERBOSE("remove writer")


##
# @if jp
# @brief モジュール登録関数
#
#
# @else
# @brief
#
#
# @endif
#
def OpenSpliceOutPortInit():
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("opensplice",
                       OpenSpliceOutPort)
