#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FsmObject.py
# @brief Fsm Object Base class
# @date  $Date: 2017-06-09 07:49:59 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
import RTC
import RTC__POA


##
# @if jp
# @brief
# FiniteStateMachineのベースクラス。
# ユーザが新たなRTコンポーネントを作成する場合は、このクラスを拡張する。
# 各RTコンポーネントのベースとなるクラス。}
#
#
# @else
# @brief
# This is a class to be a base of each RT-Component.
# This is a implementation class of lightweightRTComponent in Robotic
# Technology Component specification
#
# @endif
class FsmObject_impl(RTC__POA.FsmObject):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief Consructor
    #
    #
    # @endif
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief
    #
    #
    #
    # @param self
    #
    # @else
    # Send a stimulus to an FSM that realizes this interface.
    # If the stimulus corresponds to any outgoing transition of the
    # current state, that transition shall be taken and the state
    # shall change. Any FSM participants associated with the exit of
    # the current state, the transition to the new state, or the
    # entry to the new state shall be invoked. If the stimulus does
    # not correspond to any such transition, this operation shall
    # succeed but have no effect.
    #
    # If the given execution context is a non-nil reference to a
    # context in which this FSM participates, the transition shall be
    # executed in that context. If the argument is nil, the FSM shall
    # choose an EVENT_DRIVEN context in which to execute the
    # transition. If the argument is non-nil, but this FSM does not
    # participate in the given context, this operation shall fail
    # with * ReturnCode_t::BAD_PARAMETER.
    #
    # @brief Consructor
    #
    #
    # @endif
    def send_stimulus(self, ids, id):
        return RTC.RTC_OK
