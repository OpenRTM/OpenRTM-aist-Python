#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist


class ShortToDoubleSerializer(OpenRTM_aist.CORBA_CdrMemoryStream):
    def __init__(self):
        OpenRTM_aist.CORBA_CdrMemoryStream.__init__(self)
        return

    def serialize(self, data):
        tmp_data = RTC.TimedDouble(data.tm, float(data.data))
        ret, cdr = OpenRTM_aist.CORBA_CdrMemoryStream.serialize(
            self, tmp_data)
        return ret, cdr


def ShortToDoubleSerializerInit(mgr):
    OpenRTM_aist.SerializerFactories.instance().addSerializer(
        "cdr:RTC/TimedDouble:RTC/TimedShort", ShortToDoubleSerializer, RTC.TimedShort)  # addSerializer関数の第1引数で登録名を設定。独自シリアライザを利用するときはこの名前を使用する。
