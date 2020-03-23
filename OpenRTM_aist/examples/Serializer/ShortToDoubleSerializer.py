#!/usr/bin/env python
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

    def deserialize(self, cdr, data_type):
        ret, tmp_data = OpenRTM_aist.CORBA_CdrMemoryStream.deserialize(
            self, cdr, RTC.TimedShort)
        data = RTC.TimedDouble(tmp_data.tm, float(tmp_data.data))
        return ret, data


def ShortToDoubleSerializerInit(mgr):
    OpenRTM_aist.SerializerFactory.instance().addFactory("corba:RTC/TimedDouble:RTC/TimedShort",  # addFactory関数の第1引数で登録名を設定。以下で独自シリアライザを利用するときはこの名前を使用する。
                                                         ShortToDoubleSerializer)
