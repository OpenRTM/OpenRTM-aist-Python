#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  InPortCorbaConsumerBase.py
# @brief InPortCorbaConsumer base class
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
from omniORB import CORBA
import OpenRTM_aist
import OpenRTM

##
# @if jp
#
# @class InPortCorbaConsumerBase
#
# @brief InPortCorbaConsumerBase クラス
#
#
# @param DataType 本ポートにて扱うデータ型
#
# @since 2.0.0
#
# @else
# @class InPortCorbaConsumerBase
#
# @brief InPortCorbaConsumerBase class
#
#
#
# @since 2.0.0
#
# @endif
#


class InPortCorbaConsumerBase(OpenRTM_aist.InPortConsumer, OpenRTM_aist.CorbaConsumer):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param buffer 当該コンシューマに割り当てるバッファオブジェクト
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param buffer The buffer object that is attached to this Consumer
    #
    # @endif
    #
    def __init__(self, interfaceType, interfacetypestr):
        OpenRTM_aist.InPortConsumer.__init__(self)
        OpenRTM_aist.CorbaConsumer.__init__(self, interfaceType)
        self._rtcout = OpenRTM_aist.Manager.instance(
        ).getLogbuf("InPortCorbaConsumerBase")
        self._properties = None
        self._interfacetypestr = interfacetypestr
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
        self._rtcout.RTC_PARANOID("~InPortCorbaConsumerBase()")
        OpenRTM_aist.CorbaConsumer.__del__(self)
        return

    ##
    # @if jp
    # @brief 設定初期化
    #
    # InPortConsumerの各種設定を行う
    #
    # @else
    # @brief Initializing configuration
    #
    # This operation would be called to configure this consumer
    # in initialization.
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
        return

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
        self._rtcout.RTC_TRACE("subscribeInterface()")
        # self._rtcout.RTC_DEBUG_STR(OpenRTM_aist.NVUtil.toString(properties))

        # getting InPort's ref from IOR string
        if self.subscribeFromIor(properties):
            return True

        # getting InPort's ref from Object reference
        if self.subscribeFromRef(properties):
            return True

        return False

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
        self._rtcout.RTC_TRACE("unsubscribeInterface()")
        # self._rtcout.RTC_DEBUG_STR(OpenRTM_aist.NVUtil.toString(properties))

        if self.unsubscribeFromIor(properties):
            return

        self.unsubscribeFromRef(properties)
        return

    ##
    # @if jp
    # @brief IOR文字列からオブジェクト参照を取得する
    #
    # @return true: 正常取得, false: 取得失敗
    #
    # @else
    # @brief Getting object reference fromn IOR string
    #
    # @return true: succeeded, false: failed
    #
    # @endif
    #
    # bool subscribeFromIor(const SDOPackage::NVList& properties);
    def subscribeFromIor(self, properties):
        self._rtcout.RTC_TRACE("subscribeFromIor()")

        index = OpenRTM_aist.NVUtil.find_index(properties,
                                               "dataport."+self._interfacetypestr+".inport_ior")
        if index < 0:
            self._rtcout.RTC_ERROR("inport_ior not found")
            return False

        ior = ""
        try:
            ior = any.from_any(properties[index].value, keep_structs=True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        if not ior:
            self._rtcout.RTC_ERROR("inport_ior has no string")
            return False

        orb = OpenRTM_aist.Manager.instance().getORB()
        obj = orb.string_to_object(ior)

        if CORBA.is_nil(obj):
            self._rtcout.RTC_ERROR("invalid IOR string has been passed")
            return False

        if not self.setObject(obj):
            self._rtcout.RTC_WARN("Setting object to consumer failed.")
            return False

        return True

    ##
    # @if jp
    # @brief Anyから直接オブジェクト参照を取得する
    #
    # @return true: 正常取得, false: 取得失敗
    #
    # @else
    # @brief Getting object reference fromn Any directry
    #
    # @return true: succeeded, false: failed
    #
    # @endif
    #
    # bool subscribeFromRef(const SDOPackage::NVList& properties);
    def subscribeFromRef(self, properties):
        self._rtcout.RTC_TRACE("subscribeFromRef()")
        index = OpenRTM_aist.NVUtil.find_index(properties,
                                               "dataport."+self._interfacetypestr+".inport_ref")
        if index < 0:
            self._rtcout.RTC_ERROR("inport_ref not found")
            return False

        obj = None
        try:
            obj = any.from_any(properties[index].value, keep_structs=True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        if not obj:
            self._rtcout.RTC_ERROR("prop[inport_ref] is not objref")
            return False

        if CORBA.is_nil(obj):
            self._rtcout.RTC_ERROR("prop[inport_ref] is not objref")
            return False

        if not self.setObject(obj):
            self._rtcout.RTC_ERROR("Setting object to consumer failed.")
            return False

        return True

    ##
    # @if jp
    # @brief 接続解除(IOR版)
    #
    # @return true: 正常取得, false: 取得失敗
    #
    # @else
    # @brief ubsubscribing (IOR version)
    #
    # @return true: succeeded, false: failed
    #
    # @endif
    #
    # bool unsubscribeFromIor(const SDOPackage::NVList& properties);
    def unsubscribeFromIor(self, properties):
        self._rtcout.RTC_TRACE("unsubscribeFromIor()")
        index = OpenRTM_aist.NVUtil.find_index(properties,
                                               "dataport."+self._interfacetypestr+".inport_ior")
        if index < 0:
            self._rtcout.RTC_ERROR("inport_ior not found")
            return False

        ior = ""
        try:
            ior = any.from_any(properties[index].value, keep_structs=True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        if not ior:
            self._rtcout.RTC_ERROR("prop[inport_ior] is not string")
            return False

        orb = OpenRTM_aist.Manager.instance().getORB()
        var = orb.string_to_object(ior)
        ptr = self._ptr(True)
        if ptr:
            if not ptr._is_equivalent(var):
                self._rtcout.RTC_ERROR("connector property inconsistency")
                return False

        self.releaseObject()
        return True

    ##
    # @if jp
    # @brief 接続解除(Object reference版)
    #
    # @return true: 正常取得, false: 取得失敗
    #
    # @else
    # @brief ubsubscribing (Object reference version)
    #
    # @return true: succeeded, false: failed
    #
    # @endif
    #
    # bool unsubscribeFromRef(const SDOPackage::NVList& properties);
    def unsubscribeFromRef(self, properties):
        self._rtcout.RTC_TRACE("unsubscribeFromRef()")
        index = OpenRTM_aist.NVUtil.find_index(properties,
                                               "dataport."+self._interfacetypestr+".inport_ref")

        if index < 0:
            return False

        obj = None
        try:
            obj = any.from_any(properties[index].value, keep_structs=True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        if not obj:
            return False

        obj_ptr = self._ptr(True)

        if obj_ptr is None or not obj_ptr._is_equivalent(obj):
            return False

        self.releaseObject()
        return True
