#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FactoryInit.py
# @brief factory initialization function
# @date $Date: 2008-03-06 06:58:40 $
# @author Noriaki Ando <n-ando@aist.go.jp>
#
# Copyright (C) 2009
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import OpenRTM_aist
from OpenRTM_aist.ext.sdo.observer import ComponentObserverConsumer


def FactoryInit():
    # Buffers
    OpenRTM_aist.CdrRingBufferInit()

    # Threads
    OpenRTM_aist.DefaultPeriodicTaskInit()

    # Publishers
    OpenRTM_aist.PublisherFlushInit()
    OpenRTM_aist.PublisherNewInit()
    OpenRTM_aist.PublisherPeriodicInit()

    # Providers/Consumer
    OpenRTM_aist.InPortCorbaCdrProviderInit()
    OpenRTM_aist.InPortCorbaCdrConsumerInit()
    OpenRTM_aist.OutPortCorbaCdrConsumerInit()
    OpenRTM_aist.OutPortCorbaCdrProviderInit()
    OpenRTM_aist.InPortDirectProviderInit()
    OpenRTM_aist.InPortDirectConsumerInit()
    OpenRTM_aist.OutPortDirectProviderInit()
    OpenRTM_aist.OutPortDirectConsumerInit()
    OpenRTM_aist.InPortSHMProviderInit()
    OpenRTM_aist.InPortSHMConsumerInit()
    OpenRTM_aist.OutPortSHMProviderInit()
    OpenRTM_aist.OutPortSHMConsumerInit()
    OpenRTM_aist.ProcessUniquePolicyInit()
    OpenRTM_aist.NodeNumberingPolicyInit()
    OpenRTM_aist.NamingServiceNumberingPolicyInit()
    OpenRTM_aist.LogstreamFileInit()
    OpenRTM_aist.OutPortDSProviderInit()
    OpenRTM_aist.OutPortDSConsumerInit()
    OpenRTM_aist.InPortDSProviderInit()
    OpenRTM_aist.InPortDSConsumerInit()
    OpenRTM_aist.InPortCSPProviderInit()
    OpenRTM_aist.InPortCSPConsumerInit()
    OpenRTM_aist.OutPortCSPProviderInit()
    OpenRTM_aist.OutPortCSPConsumerInit()
    OpenRTM_aist.CORBA_CdrMemoryStreamInit()
    ComponentObserverConsumer.ComponentObserverConsumerInit()
