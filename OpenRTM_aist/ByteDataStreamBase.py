#!/usr/bin/env python
# -*- coding: euc-jp -*-

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
# @class 
#
#
# @else
# @brief 
#
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
  ## virtual ReturnCode init(coil::Properties& prop) = 0;
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
  ## virtual void isLittleEndian(bool little_endian) = 0;
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
  ## virtual bool serialize(const DataType& data) = 0;
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
  ## virtual bool deserialize(DataType& data) = 0;
  def deserialize(self, cdr, data_type):
    return ByteDataStreamBase.SERIALIZE_NOTFOUND, data_type




serializerfactory = None

class SerializerFactory(OpenRTM_aist.Factory,ByteDataStreamBase):
  def __init__(self):
    OpenRTM_aist.Factory.__init__(self)
    pass


  def __del__(self):
    pass


  def instance():
    global serializerfactory

    if serializerfactory is None:
      serializerfactory = SerializerFactory()

    return serializerfactory

  instance = staticmethod(instance)
