#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  CdrBufferBase.py
# @brief CdrBufferBase class
# @date  $Date: 2007-12-31 03:08:03 $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2006-2008
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import OpenRTM_aist


class CdrBufferBase(OpenRTM_aist.BufferBase):
    def __init__(self):
        pass


cdrbufferfactory = None


class CdrBufferFactory(OpenRTM_aist.Factory):
    def __init__(self):
        OpenRTM_aist.Factory.__init__(self)
        pass

    def instance():
        global cdrbufferfactory

        if cdrbufferfactory is None:
            cdrbufferfactory = CdrBufferFactory()

        return cdrbufferfactory

    instance = staticmethod(instance)
