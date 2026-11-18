#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file  OutPortCorbaConsumerBase.py
# @brief OutPortCorbaConsumer base class
# @date  $Date: 2020-04-08 03:08:03 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright(C) 2020
#     Nobuhiko Miyamoto
#     Software Platform Research Team,
#     Industrial Cyber-Physical System Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology(AIST), Jap
#     All rights reserved.
#


from omniORB import any
import OpenRTM_aist
import OpenRTM

##
# @if jp
# @class OutPortCorbaConsumerBase
#
# @brief OutPortCorbaConsumerBase クラス
#
# 通信手段に CORBA を利用した出力ポートコンシューマの実装クラス。
#
# @param DataType 本ポートにて扱うデータ型
#
# @since 2.0.0
#
# @else
# @class OutPortCorbaConsumerBase
#
# @brief OutPortCorbaConsumerBase class
#
# This is an implementation class of the output Consumer
# that uses CORBA for means of communication.
#
# @param DataType Data type for this port
#
# @since 2.0.0
#
# @endif
#


class OutPortCorbaConsumerBase(OpenRTM_aist.OutPortConsumer, OpenRTM_aist.CorbaConsumer):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param buffer 本ポートに割り当てるバッファ
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param buffer Buffer that is attached to this port
    #
    # @endif
    #
    def __init__(self, interfaceType, interfacetypestr):
        OpenRTM_aist.OutPortConsumer.__init__(self)
        OpenRTM_aist.CorbaConsumer.__init__(self, interfaceType)
        self._rtcout = OpenRTM_aist.Manager.instance(
        ).getLogbuf("OutPortCorbaConsumerBase")
        self._interfacetypestr = interfacetypestr
        self._properties = None
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @endif
    #
    def __del__(self):
        self._rtcout.RTC_PARANOID("~OutPortCorbaConsumerBase()")
        OpenRTM_aist.CorbaConsumer.__del__(self)
        pass

    ##
    # @if jp
    # @brief 設定初期化
    #
    # OutPortConsumerの各種設定を行う。実装クラスでは、与えられた
    # Propertiesから必要な情報を取得して各種設定を行う。この init() 関
    # 数は、OutPortProvider生成直後および、接続時にそれぞれ呼ばれる可
    # 能性がある。したがって、この関数は複数回呼ばれることを想定して記
    # 述されるべきである。
    #
    # @param prop 設定情報
    #
    # @else
    #
    # @brief Initializing configuration
    #
    # This operation would be called to configure in initialization.
    # In the concrete class, configuration should be performed
    # getting appropriate information from the given Properties data.
    # This function might be called right after instantiation and
    # connection sequence respectivly.  Therefore, this function
    # should be implemented assuming multiple call.
    #
    # @param prop Configuration information
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
    # @brief データ受信通知への登録
    #
    # 指定されたプロパティに基づいて、データ受信通知の受け取りに登録する。
    #
    # @param properties 登録情報
    #
    # @return 登録処理結果(登録成功:true、登録失敗:false)
    #
    # @else
    # @brief Subscribe the data receive notification
    #
    # Subscribe the data receive notification based on specified property
    # information
    #
    # @param properties Subscription information
    #
    # @return Subscription result (Successful:true, Failed:false)
    #
    # @endif
    #
    # virtual bool subscribeInterface(const SDOPackage::NVList& properties);

    def subscribeInterface(self, properties):
        self._rtcout.RTC_TRACE("subscribeInterface()")
        index = OpenRTM_aist.NVUtil.find_index(
            properties, "dataport."+self._interfacetypestr+".outport_ior")

        if index < 0:
            self._rtcout.RTC_DEBUG(
                "dataport."+self._interfacetypestr+".outport_ior not found.")
            return False

        if OpenRTM_aist.NVUtil.isString(
                properties, "dataport."+self._interfacetypestr+".outport_ior"):
            self._rtcout.RTC_DEBUG(
                "dataport."+self._interfacetypestr+".outport_ior found.")
            ior = ""
            # try:
            ior = any.from_any(properties[index].value, keep_structs=True)
            # except:
            #  self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

            orb = OpenRTM_aist.Manager.instance().getORB()
            obj = orb.string_to_object(ior)
            ret = self.setObject(obj)
            if ret:
                self._rtcout.RTC_DEBUG("CorbaConsumer was set successfully.")
            else:
                self._rtcout.RTC_ERROR("Invalid object reference.")

            return ret

        return False

    ##
    # @if jp
    # @brief データ受信通知からの登録解除
    #
    # データ受信通知の受け取りから登録を解除する。
    #
    # @param properties 登録解除情報
    #
    # @else
    # @brief Unsubscribe the data receive notification
    #
    # Unsubscribe the data receive notification.
    #
    # @param properties Unsubscription information
    #
    # @endif
    #
    # virtual void unsubscribeInterface(const SDOPackage::NVList& properties);

    def unsubscribeInterface(self, properties):
        self._rtcout.RTC_TRACE("unsubscribeInterface()")
        index = OpenRTM_aist.NVUtil.find_index(properties,
                                               "dataport."+self._interfacetypestr+".outport_ior")
        if index < 0:
            self._rtcout.RTC_DEBUG(
                "dataport."+self._interfacetypestr+".outport_ior not found.")
            return

        ior = ""

        try:
            ior = any.from_any(properties[index].value, keep_structs=True)

            if ior:
                self._rtcout.RTC_DEBUG(
                    "dataport."+self._interfacetypestr+".outport_ior found.")
                orb = OpenRTM_aist.Manager.instance().getORB()
                obj = orb.string_to_object(ior)
                if self._ptr(True)._is_equivalent(obj):
                    self.releaseObject()
                    self._rtcout.RTC_DEBUG(
                        "CorbaConsumer's reference was released.")
                    return

                self._rtcout.RTC_ERROR("hmm. Inconsistent object reference.")

        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        return
