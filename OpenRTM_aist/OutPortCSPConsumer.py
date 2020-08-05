#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  OutPortCSPConsumer.py
# @brief OutPortCSPConsumer class
# @date  $Date: 2016/01/08 $
# @author Nobuhiko Miyamoto


import OpenRTM_aist
import OpenRTM
import CSP


##
# @if jp
# @class OutPortCSPConsumer
# @brief OutPortCSPConsumer クラス
#
# CSPモデルのチャネルを模擬した出力ポートプロバイダーの実装クラス。
#
#
# @else
# @class OutPortCSPConsumer
# @brief OutPortCSPConsumer class
#
#
#
# @endif
#
class OutPortCSPConsumer(OpenRTM_aist.OutPortCorbaCdrConsumer):

    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # Interface Typeにはshared_memoryを指定する
    # 共有メモリの空間名はUUIDで作成し、コネクタプロファイルのdataport.shared_memory.addressに保存する
    #
    # self
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # self
    # @endif
    #
    def __init__(self):
        OpenRTM_aist.OutPortCorbaCdrConsumer.__init__(self)
        OpenRTM_aist.CorbaConsumer.__init__(self, CSP.OutPortCsp)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("OutPortCSPConsumer")
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
    def __del__(self, CorbaConsumer=OpenRTM_aist.CorbaConsumer):
        self._rtcout.RTC_PARANOID("~OutPortCSPConsumer()")
        CorbaConsumer.__del__(self)

    # void init(coil::Properties& prop)

    def init(self, prop):
        self._rtcout.RTC_TRACE("init()")
        self._properties = prop

    ##
    # @if jp
    # @brief バッファをセットする
    #
    #
    # @param buffer OutPortProviderがデータを取り出すバッファへのポインタ
    #
    # @else
    # @brief Setting outside buffer's pointer
    #
    # @param buffer A pointer to a data buffer to be used by OutPortProvider
    #
    # @endif
    #
    # virtual void setBuffer(CdrBufferBase* buffer);

    def setBuffer(self, buffer):
        pass

    # void OutPortCorbaCdrConsumer::setListener(ConnectorInfo& info,
    #                                           ConnectorListeners* listeners)

    def setListener(self, info, listeners):
        self._rtcout.RTC_TRACE("setListener()")
        self._listeners = listeners
        self._profile = info
        return

    def setConnector(self, connector):
        self._connector = connector
        return

    ##
    # @if jp
    # @brief 接続先のProviderからデータを取得する
    #
    # @param data データの格納先
    # @return リターンコード
    # PORT_OK：正常終了
    # PORT_ERROR：バッファの読み込みエラー、通常は発生しない
    # BUFFER_FULL：バッファフル、通常は発生しない
    # BUFFER_EMPTY：バッファが空
    # BUFFER_TIMEOUT：一定時間以内にバッファにデータが追加されなかった
    # CONNECTION_LOST：通信エラー
    # UNKNOWN_ERROR：その他のエラー
    #
    # @else
    # @brief
    #
    #
    # @param data
    # @return
    #
    # @endif
    #
    # ::OpenRTM::PortStatus put()
    #  throw (CORBA::SystemException);
    def get(self):
        self._rtcout.RTC_PARANOID("get()")

        try:
            data = None
            outportcsp = self._ptr()
            ret, cdr_data = outportcsp.get()

            if ret == OpenRTM.PORT_OK:
                self._rtcout.RTC_DEBUG("get() successful")
                data = cdr_data
                self.onReceived(data)
                self.onBufferWrite(data)

                return self.PORT_OK, data
            return self.convertReturn(ret, data)

        except BaseException:
            self._rtcout.RTC_WARN("Exception caught from OutPort.get().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return self.CONNECTION_LOST, None

    ##
    # @if jp
    # @brief データ読み込み可能かを接続先のproviderに確認
    #
    #
    # @param self
    # @param retry True：再検索、False：通常の読み込み確認
    # @return True：読み込み可能、False：読み込み不可
    # 通信エラーが発生した場合はFalseを返す
    #
    # @else
    # @brief
    #
    # @param self
    # @param retry
    # @return
    #
    # @endif
    #
    def isReadable(self, retry=False):
        self._rtcout.RTC_PARANOID("isReadable()")
        try:
            outportcsp = self._ptr()
            return outportcsp.is_readable(retry)
        except BaseException:
            self._rtcout.RTC_WARN(
                "Exception caught from OutPort.isReadable().")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return False


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
def OutPortCSPConsumerInit():
    factory = OpenRTM_aist.OutPortConsumerFactory.instance()
    factory.addFactory("csp_channel",
                       OpenRTM_aist.OutPortCSPConsumer)
