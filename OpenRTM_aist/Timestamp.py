#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file Timestamp.py
# @brief Timestamp listener class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import OpenRTM_aist


class Timestamp(OpenRTM_aist.ConnectorDataListenerT):
    def __init__(self, ts_type):
        self._ts_type = ts_type

    def __del__(self):
        pass

    def __call__(self, info, data):
        if info.properties.getProperty("timestamp_policy") != self._ts_type:
            return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, data
        tm = OpenRTM_aist.Time().gettimeofday()
        data.tm.sec = tm.sec()
        data.tm.nsec = tm.usec() * 1000
        return OpenRTM_aist.ConnectorListenerStatus.DATA_CHANGED, data
