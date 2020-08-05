#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROS2Serializer.py
# @brief ROS2 Serializer class
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
import omniORB

import struct
import array
import ROS2MessageInfo
import RTC
import rclpy
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
# @brief 単一データ、配列などの基本メッセージ型のROS2シリアライザの生成関数
#
# @param message_type ROS2メッセージ型
#
# @else
# @brief
#
# @param message_type
#
# @endif
#
def ros2_basic_data(message_type):
    ##
    # @if jp
    # @class ROS2BasicData
    # @brief 単一データ、配列などの基本メッセージ型
    #
    # @else
    # @class ROS2BasicData
    # @brief
    #
    #
    # @endif
    class ROS2BasicData(OpenRTM_aist.ByteDataStreamBase):
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
        # @brief データの変換(omniORB->ROS2)
        #
        #
        # @param data omniORBのデータ
        # @return ret、value
        # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
        # value：ROS2のデータ
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

        def serialize(self, data):
            msg = message_type()
            field_type = msg.get_fields_and_field_types()["data"]
            if field_type == "int" or field_type == "int8" or field_type == "int16" or field_type == "int32" or field_type == "int64":
                msg.data = int(data.data)
            elif field_type == "uint" or field_type == "uint8" or field_type == "uint16" or field_type == "uint32" or field_type == "uint64":
                msg.data = int(data.data)
            elif field_type == "float" or field_type == "double" or field_type == "float32" or field_type == "float64":
                msg.data = float(data.data)
            elif field_type == "sequence<int8>" or field_type == "sequence<int16>" or field_type == "sequence<int32>" or field_type == "sequence<int64>" or field_type == "int8[]" or field_type == "int16[]" or field_type == "int32[]" or field_type == "int64[]":
                msg.data = list(map(int, data.data))
            elif field_type == "sequence<uint8>" or field_type == "sequence<uint16>" or field_type == "sequence<uint32>" or field_type == "sequence<uint64>" or field_type == "uint8[]" or field_type == "uint16[]" or field_type == "uint32[]" or field_type == "uint64[]":
                msg.data = list(map(int, data.data))
            elif field_type == "sequence<float>" or field_type == "sequence<double>" or field_type == "float32[]" or field_type == "float64[]":
                msg.data = list(map(float, data.data))
            elif field_type == "string":
                msg.data = str(data.data)
            else:
                msg.data = data.data

            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, msg

        ##
        # @if jp
        # @brief データの変換(ROS2->omniORB)
        #
        # @param self
        # @param bdata ROS2のデータ
        # @param data_type omniORBのデータ
        # @return ret、value
        # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
        # value：変換後のデータ
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
        def deserialize(self, bdata, data_type):
            try:
                if isinstance(data_type.data, bytes):
                    if isinstance(bdata.data, array.array):
                        data_type.data = bdata.data.tobytes()
                    else:
                        data_type.data = bytes(bdata.data)
                elif isinstance(data_type.data, str):
                    if isinstance(bdata.data, array.array):
                        data_type.data = bdata.data.tostring()
                    else:
                        data_type.data = str(bdata.data)
                elif isinstance(data_type.data, list):
                    data_type.data = list(bdata.data)
                elif isinstance(data_type.data, tuple):
                    data_type.data = tuple(bdata.data)
                elif isinstance(data_type.data, int):
                    data_type.data = int(bdata.data)
                elif isinstance(data_type.data, float):
                    data_type.data = float(bdata.data)
                else:
                    data_type.data = bdata.data
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
            except BaseException:
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOT_SUPPORT_ENDIAN, data_type
    return ROS2BasicData

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


def ROS2BasicDataInit(message_type, name):
    datatypes = [RTC.TimedState, RTC.TimedShort, RTC.TimedLong,
                 RTC.TimedUShort, RTC.TimedULong, RTC.TimedFloat,
                 RTC.TimedDouble, RTC.TimedChar, RTC.TimedWChar,
                 RTC.TimedBoolean, RTC.TimedOctet, RTC.TimedString,
                 RTC.TimedWString, RTC.TimedShortSeq, RTC.TimedLongSeq,
                 RTC.TimedUShortSeq, RTC.TimedULongSeq, RTC.TimedFloatSeq,
                 RTC.TimedDoubleSeq, RTC.TimedCharSeq, RTC.TimedWCharSeq,
                 RTC.TimedBooleanSeq, RTC.TimedOctetSeq, RTC.TimedStringSeq,
                 RTC.TimedWStringSeq]
    for datatype in datatypes:
        OpenRTM_aist.SerializerFactories.instance().addSerializer(name,
                                                         ros2_basic_data(
                                                             message_type), datatype)
    ROS2MessageInfo.ROS2MessageInfoList.instance().addInfo(name,
                                                           ROS2MessageInfo.ROS2MessageInfo(
                                                               message_type))


##
# @if jp
# @class ROS2Point3DData
# @brief PointStamped型のシリアライザ初期化
#
# @else
# @class ROS2Point3DData
# @brief
#
#
# @endif
class ROS2Point3DData(OpenRTM_aist.ByteDataStreamBase):
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
    # @brief データの変換(omniORB->ROS2)
    #
    #
    # @param data omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：ROS2のデータ
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

    def serialize(self, data):
        msg = PointStamped()
        msg.header.stamp.sec = data.tm.sec
        msg.header.stamp.nanosec = data.tm.nsec
        msg.point.x = float(data.data.x)
        msg.point.y = float(data.data.y)
        msg.point.z = float(data.data.z)

        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, msg

    ##
    # @if jp
    # @brief データの変換(ROS2->omniORB)
    #
    # @param self
    # @param bdata ROS2のデータ
    # @param data_type omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：変換後のデータ
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
    def deserialize(self, bdata, data_type):
        try:
            data_type.tm.sec = bdata.header.stamp.sec
            data_type.tm.nsec = bdata.header.stamp.nanosec
            data_type.data.x = bdata.point.x
            data_type.data.y = bdata.point.y
            data_type.data.z = bdata.point.z
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
        except BaseException:
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
def ROS2Point3DInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializer("ros2:geometry_msgs/PointStamped",
                                                              ROS2Point3DData, RTC.TimedPoint3D)
    ROS2MessageInfo.ROS2MessageInfoList.instance().addInfo("ros2:geometry_msgs/PointStamped",
                                                           ROS2MessageInfo.ROS2MessageInfo(
                                                               PointStamped))


##
# @if jp
# @class ROS2QuaternionData
# @brief QuaternionStamped型のシリアライザ
#
# @else
# @class ROS2QuaternionData
# @brief
#
#
# @endif
class ROS2QuaternionData(OpenRTM_aist.ByteDataStreamBase):
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
    # @brief データの変換(omniORB->ROS2)
    #
    #
    # @param data omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：ROS2のデータ
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

    def serialize(self, data):
        msg = QuaternionStamped()
        msg.header.stamp.sec = data.tm.sec
        msg.header.stamp.nanosec = data.tm.nsec
        msg.quaternion.x = float(data.data.x)
        msg.quaternion.y = float(data.data.y)
        msg.quaternion.z = float(data.data.z)
        msg.quaternion.w = float(data.data.w)

        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, msg

    ##
    # @if jp
    # @brief データの変換(ROS2->omniORB)
    #
    # @param self
    # @param bdata ROS2のデータ
    # @param data_type omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：変換後のデータ
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
    def deserialize(self, bdata, data_type):
        try:
            data_type.tm.sec = bdata.header.stamp.sec
            data_type.tm.nsec = bdata.header.stamp.nanosec
            data_type.data.x = bdata.quaternion.x
            data_type.data.y = bdata.quaternion.y
            data_type.data.z = bdata.quaternion.z
            data_type.data.w = bdata.quaternion.w
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
        except BaseException:
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
def ROS2QuaternionInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializer("ros2:geometry_msgs/QuaternionStamped",
                                                              ROS2QuaternionData, RTC.TimedQuaternion)
    ROS2MessageInfo.ROS2MessageInfoList.instance().addInfo("ros2:geometry_msgs/QuaternionStamped",
                                                           ROS2MessageInfo.ROS2MessageInfo(
                                                               QuaternionStamped))


##
# @if jp
# @class ROS2Vector3DData
# @brief Vector3Stamped型のシリアライザ
#
# @else
# @class ROS2Vector3DData
# @brief
#
#
# @endif
class ROS2Vector3DData(OpenRTM_aist.ByteDataStreamBase):
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
    # @brief データの変換(omniORB->ROS2)
    #
    #
    # @param data omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：ROS2のデータ
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

    def serialize(self, data):
        msg = Vector3Stamped()
        msg.header.stamp.sec = data.tm.sec
        msg.header.stamp.nanosec = data.tm.nsec
        msg.vector.x = float(data.data.x)
        msg.vector.y = float(data.data.y)
        msg.vector.z = float(data.data.z)

        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, msg

    ##
    # @if jp
    # @brief データの変換(ROS2->omniORB)
    #
    # @param self
    # @param bdata ROS2のデータ
    # @param data_type omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：変換後のデータ
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
    def deserialize(self, bdata, data_type):
        try:
            data_type.tm.sec = bdata.header.stamp.sec
            data_type.tm.nsec = bdata.header.stamp.nanosec
            data_type.data.x = bdata.vector.x
            data_type.data.y = bdata.vector.y
            data_type.data.z = bdata.vector.z
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
        except BaseException:
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
def ROS2Vector3DInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializer("ros2:geometry_msgs/Vector3Stamped",
                                                              ROS2Vector3DData, RTC.TimedVector3D)
    ROS2MessageInfo.ROS2MessageInfoList.instance().addInfo("ros2:geometry_msgs/Vector3Stamped",
                                                           ROS2MessageInfo.ROS2MessageInfo(
                                                               Vector3Stamped))


##
# @if jp
# @class ROS2CameraImageData
# @brief Image型のシリアライザ
#
# @else
# @class ROS2CameraImageData
# @brief
#
#
# @endif
class ROS2CameraImageData(OpenRTM_aist.ByteDataStreamBase):
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
    # @brief データの変換(omniORB->ROS2)
    #
    #
    # @param data omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：ROS2のデータ
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

    def serialize(self, data):
        msg = Image()
        msg.header.stamp.sec = data.tm.sec
        msg.header.stamp.nanosec = data.tm.nsec
        msg.height = data.height
        msg.width = data.width
        if not data.format:
            msg.encoding = "rgb8"
        else:
            msg.encoding = data.format
        msg.step = 1920
        msg.data = data.pixels

        return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, msg

    ##
    # @if jp
    # @brief データの変換(ROS2->omniORB)
    #
    # @param self
    # @param bdata ROS2のデータ
    # @param data_type omniORBのデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：変換後のデータ
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
    def deserialize(self, bdata, data_type):
        try:
            data_type.tm.sec = bdata.header.stamp.sec
            data_type.tm.nsec = bdata.header.stamp.nanosec
            data_type.height = bdata.height
            data_type.width = bdata.width
            data_type.format = bdata.encoding
            data_type.pixels = bdata.data.tobytes()
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
        except BaseException:
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
def ROS2CameraImageInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializer("ros2:sensor_msgs/Image",
                                                              ROS2CameraImageData, RTC.CameraImage)
    ROS2MessageInfo.ROS2MessageInfoList.instance().addInfo("ros2:sensor_msgs/Image",
                                                           ROS2MessageInfo.ROS2MessageInfo(
                                                               Image))


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
def ROS2SerializerInit():
    ROS2BasicDataInit(Float32, "ros2:std_msgs/Float32")
    ROS2BasicDataInit(Float64, "ros2:std_msgs/Float64")
    ROS2BasicDataInit(Int8, "ros2:std_msgs/Int8")
    ROS2BasicDataInit(Int16, "ros2:std_msgs/Int16")
    ROS2BasicDataInit(Int32, "ros2:std_msgs/Int32")
    ROS2BasicDataInit(Int64, "ros2:std_msgs/Int64")
    ROS2BasicDataInit(UInt8, "ros2:std_msgs/UInt8")
    ROS2BasicDataInit(UInt16, "ros2:std_msgs/UInt16")
    ROS2BasicDataInit(UInt32, "ros2:std_msgs/UInt32")
    ROS2BasicDataInit(UInt64, "ros2:std_msgs/UInt64")
    ROS2BasicDataInit(String, "ros2:std_msgs/String")

    ROS2BasicDataInit(Float32MultiArray, "ros2:std_msgs/Float32MultiArray")
    ROS2BasicDataInit(Float64MultiArray, "ros2:std_msgs/Float64MultiArray")
    ROS2BasicDataInit(Int8MultiArray, "ros2:std_msgs/Int8MultiArray")
    ROS2BasicDataInit(Int16MultiArray, "ros2:std_msgs/Int16MultiArray")
    ROS2BasicDataInit(Int32MultiArray, "ros2:std_msgs/Int32MultiArray")
    ROS2BasicDataInit(Int64MultiArray, "ros2:std_msgs/Int64MultiArray")
    ROS2BasicDataInit(UInt8MultiArray, "ros2:std_msgs/UInt8MultiArray")
    ROS2BasicDataInit(UInt16MultiArray, "ros2:std_msgs/UInt16MultiArray")
    ROS2BasicDataInit(UInt32MultiArray, "ros2:std_msgs/UInt32MultiArray")
    ROS2BasicDataInit(UInt64MultiArray, "ros2:std_msgs/UInt64MultiArray")

    ROS2Point3DInit()
    ROS2QuaternionInit()
    ROS2Vector3DInit()
    ROS2CameraImageInit()
