#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

from __future__ import print_function
import sys

import RTC
import OpenRTM_aist


class TestSerializer1(OpenRTM_aist.CORBA_CdrMemoryStream):
    def __init__(self):
        OpenRTM_aist.CORBA_CdrMemoryStream.__init__(self)
        return

    def serialize(self, data):
        tmp_data = RTC.TimedLong(data.tm, data.data)
        ret, cdr = OpenRTM_aist.CORBA_CdrMemoryStream.serialize(
            self, tmp_data)
        return ret, cdr

    def deserialize(self, cdr, data_type):
        ret, data = OpenRTM_aist.CORBA_CdrMemoryStream.deserialize(
            self, cdr, RTC.TimedLong)
        return ret, data


def TestSerializer1Init(mgr):
    OpenRTM_aist.SerializerFactories.instance().addSerializer("test1:dummydata",  # addFactory関数の第1引数で登録名を設定。以下で独自シリアライザを利用するときはこの名前を使用する。
                                                              TestSerializer1, RTC.TimedDouble)
    OpenRTM_aist.SerializerFactories.instance().addSerializer("test1:dummydata",  # addFactory関数の第1引数で登録名を設定。以下で独自シリアライザを利用するときはこの名前を使用する。
                                                              TestSerializer1, RTC.TimedShort)
