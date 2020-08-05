#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ByteDataStreamBase.py
# @brief ByteData Stream Base class
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


##
# @if jp
# @class ByteDataStreamBase
#
# @brief シリアライザの基底クラス
#
# @else
# @class ByteDataStreamBase
#
# @brief
#
# @endif
class ByteDataStreamBase:
    """
    """
    SERIALIZE_OK = 0
    SERIALIZE_ERROR = 1
    SERIALIZE_NOTFOUND = 2
    SERIALIZE_NOT_SUPPORT_ENDIAN = 3

    ##
    # @if jp
    # @brief 設定初期化
    #
    #
    # @param prop 設定情報
    #
    # @else
    #
    # @brief Initializing configuration
    #
    #
    # @param prop Configuration information
    #
    # @endif
    # virtual ReturnCode init(coil::Properties& prop) = 0;

    def init(self, prop):
        pass

    ##
    # @if jp
    # @brief エンディアンの設定
    #
    #
    # @param little_endian リトルエンディアン(True)、ビッグエンディアン(False)
    #
    # @else
    #
    # @brief
    #
    #
    # @param little_endian
    #
    # @endif
    # virtual void isLittleEndian(bool little_endian) = 0;

    def isLittleEndian(self, little_endian):
        pass

    ##
    # @if jp
    # @brief データの符号化
    #
    #
    # @param data 符号化前のデータ
    # @return SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    #
    # @else
    #
    # @brief
    #
    #
    # @param data
    # @return
    #
    # @endif
    # virtual bool serialize(const DataType& data) = 0;

    def serialize(self, data):
        return ByteDataStreamBase.SERIALIZE_NOTFOUND, ""

    ##
    # @if jp
    # @brief データの復号化
    #
    # @param cdr バイト列
    # @param data_type データ型
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：復号化後のデータ
    #
    # @else
    #
    # @brief
    #
    # @param cdr
    # @param data_type
    # @return
    #
    # @endif
    # virtual bool deserialize(DataType& data) = 0;

    def deserialize(self, cdr, data_type):
        return ByteDataStreamBase.SERIALIZE_NOTFOUND, data_type


serializerfactories = None
globalserializerfactories = None

##
# @if jp
# @class SerializerFactory
#
# @brief シリアライザを生成するファクトリ
#
# @else
# @class SerializerFactory
#
# @brief
#
# @endif


class SerializerFactory(OpenRTM_aist.Factory, ByteDataStreamBase):

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
        OpenRTM_aist.Factory.__init__(self)
        pass

    ##
    # @if jp
    # @brief デストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif
    def __del__(self):
        pass

##
# @if jp
# @class SerializerFactories
#
# @brief シリアライザ生成ファクトリの一覧を操作するクラス
#
# @else
# @class SerializerFactories
#
# @brief
#
# @endif


class SerializerFactories:
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
        self._factories = {}

    ##
    # @if jp
    # @brief デストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif
    def __del__(self):
        pass

    ##
    # @if jp
    # @brief シリアライザの登録(データ型ごと)
    #
    # @param self
    # @param marshalingtype シリアライザの種類(文字列)
    # @param serializer シリアライザを定義したクラス
    # @param datatype 対象のデータ型のインスタンス、もしくはクラス
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param marshalingtype
    # @param serializer
    # @param datatype
    #
    # @endif
    def addSerializer(self, marshalingtype, serializer, datatype):
        mtype = OpenRTM_aist.toTypename(datatype)
        if not (mtype in self._factories):
            self._factories[mtype] = SerializerFactory()
        self._factories[mtype].addFactory(marshalingtype,
                                          serializer)

    ##
    # @if jp
    # @brief シリアライザの登録(グローバル)
    # 基本的にシリアライザはデータ型ごとに追加するが、
    # CORBA CDR形式のシリアライザのように全てのデータ型で共通の
    # 処理を行う場合はグローバルにシリアライザを登録できる。
    # 特定のデータ型から特定のROSメッセージ型への変換が必要などという
    # 場合はデータ型ごとの登録が必要である。
    #
    #
    #
    # @param self
    # @param marshalingtype シリアライザの種類(文字列)
    # @param serializer シリアライザを定義したクラス
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param marshalingtype
    # @param serializer
    #
    # @endif
    def addSerializerGlobal(self, marshalingtype, serializer):
        globalserializerfactories.addFactory(marshalingtype,
                                             serializer)
    ##
    # @if jp
    # @brief シリアライザの登録解除(データ型ごと)
    #
    # @param self
    # @param marshalingtype シリアライザの種類(文字列)
    # @param datatype 対象のデータ型のインスタンス、もしくはクラス
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param marshalingtype
    # @param datatype
    #
    # @endif

    def removeSerializer(self, marshalingtype, datatype):
        mtype = OpenRTM_aist.toTypename(datatype)
        if mtype in self._factories:
            self._factories[mtype].removeFactory(marshalingtype)

    ##
    # @if jp
    # @brief シリアライザの登録解除(グローバル)
    #
    # @param self
    # @param marshalingtype シリアライザの種類(文字列)
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param marshalingtype
    #
    # @endif
    def removeSerializerGlobal(self, marshalingtype):
        globalserializerfactories.removeFactory(marshalingtype)

    ##
    # @if jp
    # @brief シリアライザの生成
    #
    # @param self
    # @param marshalingtype シリアライザの種類(文字列)
    # @param datatype 対象のデータ型のインスタンス、もしくはクラス
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param marshalingtype
    # @param datatype
    #
    # @endif
    def createSerializer(self, marshalingtype, datatype=None):
        if datatype is not None:
            mtype = OpenRTM_aist.toTypename(datatype)
            if mtype in self._factories:
                obj = self._factories[mtype].createObject(marshalingtype)
                if obj is not None:
                    return obj
        obj = globalserializerfactories.createObject(marshalingtype)
        if obj is not None:
            return obj
        return None

    ##
    # @if jp
    # @brief 使用可能なシリアライザ一覧の取得
    #
    # @param self
    # @param datatype 対象のデータ型のインスタンス、もしくはクラス
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    # @param datatype
    #
    # @endif
    def getSerializerList(self, datatype):
        if datatype is not None:
            available_types = []
            mtype = OpenRTM_aist.toTypename(datatype)
            if mtype in self._factories:
                factory = self._factories[mtype]
                available_types.extend(factory.getIdentifiers())

        available_types.extend(globalserializerfactories.getIdentifiers())

        return available_types

    def instance():
        global serializerfactories
        global globalserializerfactories

        if serializerfactories is None:
            serializerfactories = SerializerFactories()
        if globalserializerfactories is None:
            globalserializerfactories = SerializerFactory()

        return serializerfactories

    instance = staticmethod(instance)
