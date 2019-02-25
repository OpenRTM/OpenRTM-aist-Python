#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file ROSSerializer.py
# @brief ROS Serializer class
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

try:
  from cStringIO import StringIO
except ImportError:
  from io import StringIO

import struct
import ROSMessageInfo

from std_msgs.msg import Float32
from std_msgs.msg import Float64
from std_msgs.msg import Int8
from std_msgs.msg import Int16
from std_msgs.msg import Int32
from std_msgs.msg import Int64
from std_msgs.msg import UInt8
from std_msgs.msg import UInt16
from std_msgs.msg import UInt32
from std_msgs.msg import UInt64
from std_msgs.msg import Float32MultiArray
from std_msgs.msg import Float64MultiArray
from std_msgs.msg import Int8MultiArray
from std_msgs.msg import Int16MultiArray
from std_msgs.msg import Int32MultiArray
from std_msgs.msg import Int64MultiArray
from std_msgs.msg import UInt8MultiArray
from std_msgs.msg import UInt16MultiArray
from std_msgs.msg import UInt32MultiArray
from std_msgs.msg import UInt64MultiArray
from std_msgs.msg import String
from geometry_msgs.msg import PointStamped
from geometry_msgs.msg import QuaternionStamped
from geometry_msgs.msg import Vector3Stamped
from sensor_msgs.msg import Image


##
# @if jp
# @brief ROSメッセージを符号化
#
# @param msg ROSメッセージ
# @param buf バッファ
# @return 符号化のデータ
#
# @else
# @brief 
#
# @param msg 
# @param buf 
# @return 
#
# @endif
#
def ros_serialize(msg, buf):
  start = buf.tell()
  buf.seek(start+4)
  msg.serialize(buf)
  
  end = buf.tell()
  size = end - 4 - start
  buf.seek(start)
  buf.write(struct.pack('<I', size))
  buf.seek(end)
  bdata = buf.getvalue()
  buf.truncate(0)
  return bdata


##
# @if jp
# @brief ROSメッセージを復号化
#
# @param bdata 復号化前のデータ
# @param message_type メッセージ型
# @param buf バッファ
# @return 復号化のデータ
#
# @else
# @brief 
#
# @param bdata 
# @param message_type 
# @param buf 
# @return 
#
# @endif
#
def ros_deserialize(bdata, message_type, buf):
  buf.write(bdata)
  buf.seek(0)
  (size,) = struct.unpack('<I', buf.read(4))
  data = buf.read(size)

  message = message_type().deserialize(data)

  return message

##
# @if jp
# @brief 単一データ、配列などの基本メッセージ型のROSシリアライザの生成関数
#
# @param message_type ROSメッセージ型
#
# @else
# @brief 
#
# @param message_type 
#
# @endif
#
def ros_basic_data(message_type):
  ##
  # @if jp
  # @class ROSBasicData
  # @brief 単一データ、配列などの基本メッセージ型
  #
  # @else
  # @class ROSBasicData
  # @brief 
  #
  #
  # @endif
  class ROSBasicData(OpenRTM_aist.ByteDataStreamBase):
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
      self._buff = StringIO()

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
    ## virtual ReturnCode init(coil::Properties& prop) = 0;
    def init(self, prop):
      pass


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
    ## virtual bool serialize(const DataType& data) = 0;
    def serialize(self, data):
      msg = message_type()
      msg.data = data.data

      buf = ros_serialize(msg, self._buff)

      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, buf

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
    def deserialize(self, bdata, data_type):
      try:
        message = ros_deserialize(bdata, message_type, self._buff)
        data_type.data = message.data
        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
      except:
        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type
  return ROSBasicData

##
# @if jp
# @brief 単一データ、配列などの基本メッセージ型のシリアライザの初期化
#
# @param message_type ROSメッセージ型
# @param name シリアライザの名前
#
# @else
# @brief 
#
# @param message_type 
# @param name 
#
#
# @endif
#
def ROSBasicDataInit(message_type, name):
  OpenRTM_aist.SerializerFactory.instance().addFactory(name,
                                                      ros_basic_data(message_type),
                                                      OpenRTM_aist.Delete)
  ROSMessageInfo.ROSMessageInfoFactory.instance().addFactory(name,
                                                      ROSMessageInfo.ros_message_info(message_type),
                                                      OpenRTM_aist.Delete)



##
# @if jp
# @class ROSPoint3DData
# @brief PointStamped型のシリアライザ初期化
#
# @else
# @class ROSPoint3DData
# @brief 
#
#
# @endif
class ROSPoint3DData(OpenRTM_aist.ByteDataStreamBase):
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
    self._buff = StringIO()

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
  ## virtual ReturnCode init(coil::Properties& prop) = 0;
  def init(self, prop):
    pass


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
  ## virtual bool serialize(const DataType& data) = 0;
  def serialize(self, data):
    msg = PointStamped()
    msg.header.stamp.secs = data.tm.sec
    msg.header.stamp.nsecs = data.tm.nsec
    msg.point.x = data.data.x
    msg.point.y = data.data.y
    msg.point.z = data.data.z

    buf = ros_serialize(msg, self._buff)
    

    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, buf

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
  def deserialize(self, bdata, data_type):
    try:
      message = ros_deserialize(bdata, PointStamped, self._buff)
      data_type.tm.sec = message.header.stamp.secs
      data_type.tm.nsec = message.header.stamp.nsecs
      data_type.data.x = message.point.x
      data_type.data.y = message.point.y
      data_type.data.z = message.point.z
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
    except:
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type


##
# @if jp
# @brief PointStamped型のシリアライザの初期化
#
#
# @else
# @brief 
#
#
# @endif
#
def ROSPoint3DInit():
  OpenRTM_aist.SerializerFactory.instance().addFactory("ROSPointStamped",
                                                      ROSPoint3DData,
                                                      OpenRTM_aist.Delete)
  ROSMessageInfo.ROSMessageInfoFactory.instance().addFactory("ROSPointStamped",
                                                      ROSMessageInfo.ros_message_info(PointStamped),
                                                      OpenRTM_aist.Delete)


##
# @if jp
# @class ROSQuaternionData
# @brief QuaternionStamped型のシリアライザ
#
# @else
# @class ROSQuaternionData
# @brief 
#
#
# @endif
class ROSQuaternionData(OpenRTM_aist.ByteDataStreamBase):
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
    self._buff = StringIO()

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
  ## virtual ReturnCode init(coil::Properties& prop) = 0;
  def init(self, prop):
    pass


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
  ## virtual bool serialize(const DataType& data) = 0;
  def serialize(self, data):
    msg = QuaternionStamped()
    msg.header.stamp.secs = data.tm.sec
    msg.header.stamp.nsecs = data.tm.nsec
    msg.quaternion.x = data.data.x
    msg.quaternion.y = data.data.y
    msg.quaternion.z = data.data.z
    msg.quaternion.w = data.data.w

    buf = ros_serialize(msg, self._buff)
    

    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, buf

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
  def deserialize(self, bdata, data_type):
    try:
      message = ros_deserialize(bdata, QuaternionStamped, self._buff)
      data_type.tm.sec = message.header.stamp.secs
      data_type.tm.nsec = message.header.stamp.nsecs
      data_type.data.x = message.quaternion.x
      data_type.data.y = message.quaternion.y
      data_type.data.z = message.quaternion.z
      data_type.data.w = message.quaternion.w
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
    except:
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type


##
# @if jp
# @brief QuaternionStamped型のシリアライザの初期化
#
#
# @else
# @brief 
#
#
# @endif
#
def ROSQuaternionInit():
  OpenRTM_aist.SerializerFactory.instance().addFactory("ROSQuaternionStamped",
                                                      ROSQuaternionData,
                                                      OpenRTM_aist.Delete)
  ROSMessageInfo.ROSMessageInfoFactory.instance().addFactory("ROSQuaternionStamped",
                                                      ROSMessageInfo.ros_message_info(QuaternionStamped),
                                                      OpenRTM_aist.Delete)



##
# @if jp
# @class ROSVector3DData
# @brief Vector3Stamped型のシリアライザ
#
# @else
# @class ROSVector3DData
# @brief 
#
#
# @endif
class ROSVector3DData(OpenRTM_aist.ByteDataStreamBase):
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
    self._buff = StringIO()

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
  ## virtual ReturnCode init(coil::Properties& prop) = 0;
  def init(self, prop):
    pass


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
  ## virtual bool serialize(const DataType& data) = 0;
  def serialize(self, data):
    msg = Vector3Stamped()
    msg.header.stamp.secs = data.tm.sec
    msg.header.stamp.nsecs = data.tm.nsec
    msg.vector.x = data.data.x
    msg.vector.y = data.data.y
    msg.vector.z = data.data.z

    buf = ros_serialize(msg, self._buff)
    

    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, buf

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
  def deserialize(self, bdata, data_type):
    try:
      message = ros_deserialize(bdata, Vector3Stamped, self._buff)
      data_type.tm.sec = message.header.stamp.secs
      data_type.tm.nsec = message.header.stamp.nsecs
      data_type.data.x = message.vector.x
      data_type.data.y = message.vector.y
      data_type.data.z = message.vector.z
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
    except:
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type


##
# @if jp
# @brief Vector3Stamped型のシリアライザの初期化
#
#
# @else
# @brief 
#
#
# @endif
#
def ROSVector3DInit():
  OpenRTM_aist.SerializerFactory.instance().addFactory("ROSVector3Stamped",
                                                      ROSVector3DData,
                                                      OpenRTM_aist.Delete)
  ROSMessageInfo.ROSMessageInfoFactory.instance().addFactory("ROSVector3Stamped",
                                                      ROSMessageInfo.ros_message_info(Vector3Stamped),
                                                      OpenRTM_aist.Delete)


##
# @if jp
# @class ROSCameraImageData
# @brief Image型のシリアライザ
#
# @else
# @class ROSCameraImageData
# @brief 
#
#
# @endif
class ROSCameraImageData(OpenRTM_aist.ByteDataStreamBase):
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
    self._buff = StringIO()

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
  ## virtual ReturnCode init(coil::Properties& prop) = 0;
  def init(self, prop):
    pass


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
  ## virtual bool serialize(const DataType& data) = 0;
  def serialize(self, data):
    msg = Image()
    msg.header.stamp.secs = data.tm.sec
    msg.header.stamp.nsecs = data.tm.nsec
    msg.height = data.height
    msg.width = data.width
    if not data.format:
      msg.encoding = "rgb8"
    else:
      msg.encoding = data.format
    msg.step = 1920
    msg.data = data.pixels

    buf = ros_serialize(msg, self._buff)
    

    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, buf

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
  def deserialize(self, bdata, data_type):
    try:
      message = ros_deserialize(bdata, Image, self._buff)

      data_type.tm.sec = message.header.stamp.secs
      data_type.tm.nsec = message.header.stamp.nsecs
      data.height = message.height
      data_type.width = message.width
      data_type.format = message.encoding 
      data_type.pixels = message.data
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
    except:
      return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type


##
# @if jp
# @brief Image型のシリアライザの初期化
#
#
# @else
# @brief 
#
#
# @endif
#
def ROSCameraImageInit():
  OpenRTM_aist.SerializerFactory.instance().addFactory("ROSImage",
                                                      ROSCameraImageData,
                                                      OpenRTM_aist.Delete)
  ROSMessageInfo.ROSMessageInfoFactory.instance().addFactory("ROSImage",
                                                      ROSMessageInfo.ros_message_info(Image),
                                                      OpenRTM_aist.Delete)


##
# @if jp
# @brief 各種シリアライザの初期化関数
#
#
# @else
# @brief 
#
#
# @endif
#
def ROSSerializerInit():
  ROSBasicDataInit(Float32, "ROSFloat32")
  ROSBasicDataInit(Float64, "ROSFloat64")
  ROSBasicDataInit(Int8, "ROSInt8")
  ROSBasicDataInit(Int16, "ROSInt16")
  ROSBasicDataInit(Int32, "ROSInt32")
  ROSBasicDataInit(Int64, "ROSInt64")
  ROSBasicDataInit(UInt8, "ROSUInt8")
  ROSBasicDataInit(UInt16, "ROSUInt16")
  ROSBasicDataInit(UInt32, "ROSUInt32")
  ROSBasicDataInit(UInt64, "ROSUInt64")
  ROSBasicDataInit(String, "ROSString")

  ROSBasicDataInit(Float32MultiArray, "ROSFloat32MultiArray")
  ROSBasicDataInit(Float64MultiArray, "ROSFloat64MultiArray")
  ROSBasicDataInit(Int8MultiArray, "ROSInt8MultiArray")
  ROSBasicDataInit(Int16MultiArray, "ROSInt16MultiArray")
  ROSBasicDataInit(Int32MultiArray, "ROSInt32MultiArray")
  ROSBasicDataInit(Int64MultiArray, "ROSInt64MultiArray")
  ROSBasicDataInit(UInt8MultiArray, "ROSUInt8MultiArray")
  ROSBasicDataInit(UInt16MultiArray, "ROSUInt16MultiArray")
  ROSBasicDataInit(UInt32MultiArray, "ROSUInt32MultiArray")
  ROSBasicDataInit(UInt64MultiArray, "ROSUInt64MultiArray")

  ROSPoint3DInit()
  ROSQuaternionInit()
  ROSVector3DInit()
  ROSCameraImageInit()
  
