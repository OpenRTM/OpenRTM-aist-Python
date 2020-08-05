#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CORBA_CdrMemoryStream.py
# @brief CORBA Cdr Memory Stream class
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

import sys
import OpenRTM_aist
from omniORB import cdrMarshal
from omniORB import cdrUnmarshal
from omniORB import any

##
# @if jp
# @class CORBA_CdrMemoryStream
#
# @brief CORBAのCDR形式シリアライザ、デシリアライザを定義
#
# @else
# @class CORBA_CdrMemoryStream
#
# @brief
#
# @endif


class CORBA_CdrMemoryStream(OpenRTM_aist.ByteDataStreamBase):
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
        self._endian = None

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
        self._endian = little_endian

    ##
    # @if jp
    # @brief データの符号化
    #
    #
    # @param data 符号化前のデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # cdr：バイト列
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
        if self._endian is not None:
            try:
                cdr = cdrMarshal(
                    any.to_any(data).typecode(), data, self._endian)
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, cdr
            except BaseException:
                if sys.version_info[0] == 3:
                    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, b""
                else:
                    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, ""
        else:
            if sys.version_info[0] == 3:
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, b""
            else:
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, ""

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
        if self._endian is not None:
            try:
                data = cdrUnmarshal(
                    any.to_any(data_type).typecode(), cdr, self._endian)
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data
            except BaseException:
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, data_type
        else:
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type


def CORBA_CdrMemoryStreamInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializerGlobal("cdr",
                                                                    CORBA_CdrMemoryStream)

