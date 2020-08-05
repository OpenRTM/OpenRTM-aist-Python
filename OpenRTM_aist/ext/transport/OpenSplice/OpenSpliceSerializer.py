#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file OpenSpliceSerializer.py
# @brief OpenSplice Serializer class
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
import OpenSpliceMessageInfo
import RTC
import ddsutil
import os
import site
import sys


##
# @if jp
# @brief omniORBのデータからOpenSpliceのデータに変換
# omniORBのデータ型の情報は_NP_RepositoryIdから取得し、
# 定義された要素名に値を格納していく
#
# @param self
# @param data 変換前のデータ(omniORB)
# @param gen_info OpenSpliceのデータ型Infoオブジェクト
# @return 変換後のデータ(OpenSplice)
#
#
# @else
# @brief
#
# @param self
# @param data
# @param gen_info
# @return
#
# @endif
def OmniDataToDDSData(data, gen_info):
    desc = omniORB.findType(data._NP_RepositoryId)
    if desc[0] == omniORB.tcInternal.tv_struct:
        arg = {}
        for i in range(4, len(desc), 2):
            attr = desc[i]
            attr_type = desc[i + 1]
            if isinstance(attr_type, int):
                arg[attr] = data.__dict__[attr]
            else:
                cdata = data.__dict__[attr]
                data_name = cdata._NP_RepositoryId
                data_name = data_name.split(":")[1]
                data_name = data_name.replace("/", "::")
                datatype = gen_info.get_class(data_name)
                cv = OmniDataToDDSData(cdata, gen_info)
                arg[attr] = datatype(**cv)
        return arg


if sys.version_info[0] == 3:
    long = int


##
# @if jp
# @brief OpenSpliceのデータからomniORBのデータに変換
# OpenSpliceのデータはxml.etree.ElementTreeで定義されており、
# ElementTreeから要素名を取得して値を格納する
#
# @param self
# @param ddsdata 変換前のデータ(OpenSplice)
# @param omnidata 変更対象のデータ(omniORB)
#
#
# @else
# @brief
#
# @param self
# @param ddsdata
# @param omnidata
#
# @endif
def DDSDataToOmniData(ddsdata, omnidata):
    for k in ddsdata._members.keys():
        v = ddsdata.__dict__[k]
        if isinstance(v, int):
            omnidata.__dict__[k] = v
        elif isinstance(v, long):
            omnidata.__dict__[k] = v
        elif isinstance(v, float):
            omnidata.__dict__[k] = v
        elif isinstance(v, str):
            omnidata.__dict__[k] = v
        else:
            DDSDataToOmniData(v, omnidata.__dict__[k])


##
# @if jp
# @class OpenSpliceSerializer
# @brief OpenSplice用シリアライザ
#
# @else
# @class OpenSpliceSerializer
# @brief
#
#
# @endif
class OpenSpliceSerializer(OpenRTM_aist.ByteDataStreamBase):
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
    # @brief データの変換(omniORB->OpenSplice)
    #
    #
    # @param data omniORB定義のデータ
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：OpenSplice定義のデータ
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
        info = OpenSpliceMessageInfo.OpenSpliceMessageInfoList.instance().getInfo(
            data._NP_RepositoryId)
        if info:
            datatype = info.datatype()
            idlFile = info.idlFile()
            try:
                gen_info = ddsutil.get_dds_classes_from_idl(idlFile, datatype)
                osdata = gen_info.topic_data_class(
                    **OmniDataToDDSData(data, gen_info))
                if osdata:
                    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, osdata
                else:
                    return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, osdata
            except BaseException:
                return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, None
        else:
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_NOTFOUND, None

    ##
    # @if jp
    # @brief データの変換(OpenSplice->omniORB)
    #
    # @param bdata OpenSplice定義のデータ
    # @param data_type omniORB定義のデータ型
    # @return ret、value
    # ret：SERIALIZE_OK：成功、SERIALIZE_ERROR：失敗、SERIALIZE_NOTFOUND：指定のシリアライザがない
    # value：omniORB定義のデータ
    #
    # @else
    #
    # @brief
    #
    # @param bdata
    # @param data_type
    # @return
    #
    # @endif
    def deserialize(self, bdata, data_type):
        try:
            DDSDataToOmniData(bdata, data_type)
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_OK, data_type
        except BaseException:
            return OpenRTM_aist.ByteDataStreamBase.SERIALIZE_ERROR, data_type

##
# @if jp
# @brief OpenSpliceで使用するデータ型を追加する
# OpenSpliceとomniORBは同一のIDLファイルで定義したデータ型を使用するが、
# omniORBのデータ型からどのIDLファイルで定義したデータ型なのかを取得することはできないため、
# omniORBのデータ型名、OpenSpliceのデータ型名、IDLファイル名を関連付ける情報を登録する
#
# @param datatype omniORB定義のデータ型名
# @param idlfile IDLファイルのパス
#
# @else
#
# @brief
#
# @param datatype
# @param idlfile
#
# @endif


def addDataType(datatype, idlfile):
    name = datatype._NP_RepositoryId
    data_name = name.split(":")[1]
    data_name = data_name.replace("/", "::")
    OpenSpliceMessageInfo.OpenSpliceMessageInfoList.instance().addInfo(name,
                                                                       OpenSpliceMessageInfo.OpenSpliceMessageInfo(
                                                                           data_name, idlfile))


##
# @if jp
# @brief シリアライザ初期化、データ型情報登録
#
#
# @else
# @brief
#
#
# @endif
#
def OpenSpliceSerializerInit():
    OpenRTM_aist.SerializerFactories.instance().addSerializerGlobal("opensplice",
                                                                    OpenSpliceSerializer)

    OpenRTM_dir = OpenRTM_aist.__path__[0]

    idl_dir = os.path.join(OpenRTM_dir, "RTM_IDL")
    basicdatatypefile = os.path.join(idl_dir, "BasicDataType.idl")
    extendeddatatypes = os.path.join(idl_dir, "ExtendedDataTypes.idl")
    interfacedataTypes = os.path.join(idl_dir, "InterfaceDataTypes.idl")
    addDataType(RTC.TimedState, basicdatatypefile)
    addDataType(RTC.TimedShort, basicdatatypefile)
    addDataType(RTC.TimedLong, basicdatatypefile)
    addDataType(RTC.TimedUShort, basicdatatypefile)
    addDataType(RTC.TimedULong, basicdatatypefile)
    addDataType(RTC.TimedFloat, basicdatatypefile)
    addDataType(RTC.TimedDouble, basicdatatypefile)
    addDataType(RTC.TimedChar, basicdatatypefile)
    addDataType(RTC.TimedWChar, basicdatatypefile)
    addDataType(RTC.TimedBoolean, basicdatatypefile)
    addDataType(RTC.TimedOctet, basicdatatypefile)
    addDataType(RTC.TimedString, basicdatatypefile)
    addDataType(RTC.TimedWString, basicdatatypefile)
    addDataType(RTC.TimedShortSeq, basicdatatypefile)
    addDataType(RTC.TimedLongSeq, basicdatatypefile)
    addDataType(RTC.TimedUShortSeq, basicdatatypefile)
    addDataType(RTC.TimedULongSeq, basicdatatypefile)
    addDataType(RTC.TimedFloatSeq, basicdatatypefile)
    addDataType(RTC.TimedDoubleSeq, basicdatatypefile)
    addDataType(RTC.TimedCharSeq, basicdatatypefile)
    addDataType(RTC.TimedWCharSeq, basicdatatypefile)
    addDataType(RTC.TimedBooleanSeq, basicdatatypefile)
    addDataType(RTC.TimedOctetSeq, basicdatatypefile)
    addDataType(RTC.TimedStringSeq, basicdatatypefile)
    addDataType(RTC.TimedWStringSeq, basicdatatypefile)
    addDataType(RTC.TimedRGBColour, extendeddatatypes)
    addDataType(RTC.TimedPoint2D, extendeddatatypes)
    addDataType(RTC.TimedVector2D, extendeddatatypes)
    addDataType(RTC.TimedPose2D, extendeddatatypes)
    addDataType(RTC.TimedVelocity2D, extendeddatatypes)
    addDataType(RTC.TimedAcceleration2D, extendeddatatypes)
    addDataType(RTC.TimedPoseVel2D, extendeddatatypes)
    addDataType(RTC.TimedSize2D, extendeddatatypes)
    addDataType(RTC.TimedGeometry2D, extendeddatatypes)
    addDataType(RTC.TimedCovariance2D, extendeddatatypes)
    addDataType(RTC.TimedPointCovariance2D, extendeddatatypes)
    addDataType(RTC.TimedCarlike, extendeddatatypes)
    addDataType(RTC.TimedSpeedHeading2D, extendeddatatypes)
    addDataType(RTC.TimedPoint3D, extendeddatatypes)
    addDataType(RTC.TimedVector3D, extendeddatatypes)
    addDataType(RTC.TimedOrientation3D, extendeddatatypes)
    addDataType(RTC.TimedPose3D, extendeddatatypes)
    addDataType(RTC.TimedVelocity3D, extendeddatatypes)
    addDataType(RTC.TimedAngularVelocity3D, extendeddatatypes)
    addDataType(RTC.TimedAcceleration3D, extendeddatatypes)
    addDataType(RTC.TimedAngularAcceleration3D, extendeddatatypes)
    addDataType(RTC.TimedPoseVel3D, extendeddatatypes)
    addDataType(RTC.TimedSize3D, extendeddatatypes)
    addDataType(RTC.TimedGeometry3D, extendeddatatypes)
    addDataType(RTC.TimedCovariance3D, extendeddatatypes)
    addDataType(RTC.TimedSpeedHeading3D, extendeddatatypes)
    addDataType(RTC.TimedOAP, extendeddatatypes)
    addDataType(RTC.TimedQuaternion, extendeddatatypes)
    addDataType(RTC.ActArrayActuatorPos, interfacedataTypes)
    addDataType(RTC.ActArrayActuatorSpeed, interfacedataTypes)
    addDataType(RTC.ActArrayActuatorCurrent, interfacedataTypes)
    addDataType(RTC.ActArrayState, interfacedataTypes)
    addDataType(RTC.CameraImage, interfacedataTypes)
    addDataType(RTC.Fiducials, interfacedataTypes)
    addDataType(RTC.GPSData, interfacedataTypes)
    addDataType(RTC.GripperState, interfacedataTypes)
    addDataType(RTC.INSData, interfacedataTypes)
    addDataType(RTC.LimbState, interfacedataTypes)
    addDataType(RTC.Hypotheses2D, interfacedataTypes)
    addDataType(RTC.Hypotheses3D, interfacedataTypes)
    addDataType(RTC.Features, interfacedataTypes)
    addDataType(RTC.MultiCameraImages, interfacedataTypes)
    addDataType(RTC.Path2D, interfacedataTypes)
    addDataType(RTC.Path3D, interfacedataTypes)
    addDataType(RTC.PointCloud, interfacedataTypes)
    addDataType(RTC.PanTiltAngles, interfacedataTypes)
    addDataType(RTC.PanTiltState, interfacedataTypes)
    addDataType(RTC.RangeData, interfacedataTypes)
    addDataType(RTC.IntensityData, interfacedataTypes)
