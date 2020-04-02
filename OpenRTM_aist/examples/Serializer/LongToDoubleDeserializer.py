#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist


class LongToDoubleDeserializer(OpenRTM_aist.CORBA_CdrMemoryStream):
    def __init__(self):
        OpenRTM_aist.CORBA_CdrMemoryStream.__init__(self)
        return

    def serialize(self, data):
        tmp_data = RTC.TimedLong(data.tm, data.data)
        ret, cdr = OpenRTM_aist.CORBA_CdrMemoryStream.serialize(
            self, tmp_data)
        return ret, cdr

    def deserialize(self, cdr, data_type):
        ret, tmp_data = OpenRTM_aist.CORBA_CdrMemoryStream.deserialize(
            self, cdr, RTC.TimedLong)
        data = RTC.TimedDouble(tmp_data.tm, float(tmp_data.data))
        return ret, data


def LongToDoubleDeserializerInit(mgr):
    OpenRTM_aist.SerializerFactories.instance().addSerializer(
        "cdr:RTC/TimedLong:RTC/TimedDouble", LongToDoubleDeserializer, RTC.TimedDouble)  # addSerializer関数の第1引数で登録名を設定。独自シリアライザを利用するときはこの名前を使用する。
