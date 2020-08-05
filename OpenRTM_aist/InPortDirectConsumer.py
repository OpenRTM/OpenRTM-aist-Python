#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
#  @file InPortDirectConsumer.py
#  @brief InPortDirectConsumer class
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
#


import OpenRTM_aist


##
# @if jp
#
# @class InPortDirectConsumer
#
# @brief InPortDirectConsumer クラス
#
# データをダイレクトに書き込むpush型通信を実現するInPortコンシュマークラス
#
# @else
# @class InPortDirectConsumer
#
# @brief InPortDirectConsumer class
#
#
#
# @endif
#
class InPortDirectConsumer(OpenRTM_aist.InPortConsumer):
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
    # Constructor
    #
    # @param self
    #
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.InPortConsumer.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("InPortDirectConsumer")
        self._properties = None
        return

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
        self._rtcout.RTC_PARANOID("~InPortDirectConsumer()")

        return

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    #
    # @self
    #
    #
    # @else
    # @brief Initializing configuration
    #
    #
    # @endif
    #
    # virtual void init(coil::Properties& prop);
    def init(self, prop):
        self._rtcout.RTC_TRACE("init()")
        self._properties = prop
        return

    ##
    # @if jp
    # @brief
    #
    # @param self
    # @param data
    # @return
    #
    # @else
    # @brief
    #
    # @param self
    # @param data
    # @return
    #
    # @endif
    #
    # virtual ReturnCode put(const cdrMemoryStream& data);
    def put(self, data):
        self._rtcout.RTC_PARANOID("put()")

        return self.UNKNOWN_ERROR

    ##
    # @if jp
    # @brief InterfaceProfile情報を公開する
    #
    #
    # @param self
    # @param properties InterfaceProfile情報を受け取るプロパティ
    #
    # @else
    # @brief Publish InterfaceProfile information
    #
    #
    # @param self
    # @param properties Properties to get InterfaceProfile information
    #
    # @endif
    #
    # virtual void publishInterfaceProfile(SDOPackage::NVList& properties);
    def publishInterfaceProfile(self, properties):
        return

    ##
    # @if jp
    # @brief データ送信通知への登録
    #
    # @param self
    # @param properties 登録情報
    #
    # @return 登録処理結果(登録成功:true、登録失敗:false)
    #
    # @else
    # @brief Subscribe to the data sending notification
    #
    # @param self
    # @param properties Information for subscription
    #
    # @return Subscription result (Successful:true, Failed:false)
    #
    # @endif
    #
    # virtual bool subscribeInterface(const SDOPackage::NVList& properties);
    def subscribeInterface(self, properties):
        self._rtcout.RTC_TRACE("subscribeInterface()")

        return True

    ##
    # @if jp
    # @brief データ送信通知からの登録解除
    #
    # @param self
    # @param properties 登録解除情報
    #
    # @else
    # @brief Unsubscribe the data send notification
    #
    #
    # @param self
    # @param properties Information for unsubscription
    #
    # @endif
    #
    # virtual void unsubscribeInterface(const SDOPackage::NVList& properties);
    def unsubscribeInterface(self, properties):
        self._rtcout.RTC_TRACE("unsubscribeInterface()")

        return


def InPortDirectConsumerInit():
    factory = OpenRTM_aist.InPortConsumerFactory.instance()
    factory.addFactory("direct",
                       OpenRTM_aist.InPortDirectConsumer)
