#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ComponentObserverProvider.py
# @brief test for ComponentObserverConsumer
# @date $Date$
# @author Shinji Kurihara
#
# Copyright (C) 2011
#     Noriaki Ando
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#

import sys

from omniORB import CORBA, PortableServer
import RTC
import RTC__POA
import OpenRTM
import OpenRTM__POA
import SDOPackage
import OpenRTM_aist
import OpenRTM_aist.NVUtil


class ExtendedFsmServiceProvider(
        RTC__POA.ExtendedFsmService, OpenRTM_aist.SdoServiceProviderBase):
    def __init__(self):
        self._rtobj = None
        self._profile = None
        self._fsmState = ""
        structure = """
<scxml xmlns=\"http://www.w3.org/2005/07/scxml\
           version=\"1.0\"
           initial=\"airline-ticket\">
  <state id=\"state0\">
    <datamodel>
      <data id=\"data0\">
      </data>
    </datamodel>
    <transition event=\"toggle\" target=\"state1\" />
  </state>
  <state id=\"state1\">
    <datamodel>"
      <data id=\"data1\">
      </data>
    </datamodel>
    <transition event=\"toggle\" target=\"state0\" />
  </state>
</scxml>
    """
        event_profile = RTC.FsmEventProfile("toggle", "TimedShort")
        nv = OpenRTM_aist.NVUtil.newNV("fsm_structure.format", "scxml")
        self._fsmStructure = RTC.FsmStructure(
            "dummy_name", "", [event_profile], [nv])

    ##
    # @if jp
    # @brief 初期化
    # @else
    # @brief Initialization
    # @endif
    #
    def init(self, rtobj, profile):
        self._rtobj = rtobj
        self._profile = profile
        return True

    ##
    # @if jp
    # @brief 再初期化
    # @else
    # @brief Re-initialization
    # @endif
    #
    def reinit(self, profile):
        self._profile = profile
        return True

    ##
    # @if jp
    # @brief ServiceProfile を取得する
    # @else
    # @brief getting ServiceProfile
    # @endif
    #
    def getProfile(self):
        return self._profile

    ##
    # @if jp
    # @brief 終了処理
    # @else
    # @brief Finalization
    # @endif
    #
    def finalize(self):
        pass

    ##
    # @if jp
    # @brief FSMの現在の状態を取得
    #
    # このオペレーションはFSMコンポーネントのFSMの現在の状態を返す。
    # (FSM4RTC spec. p.20)
    #
    # @return 現在の状態を表す文字列
    #
    # @else
    # @brief Get Current FSM State
    #
    # This operation returns the current state of an FSM in the
    # target FSM component. (FSM4RTC spec. p.20)
    #
    # @return A string which represent the current status
    #
    # @endif
    #
    def get_current_state(self):
        return self._fsmState

    ##
    # @if jp
    # @brief FSMの構造を設定する
    #
    # このオペレーションは対象のコンポーネントに対して、FSMの構造を保
    # 持する FsmStruccture を設定する。対象コンポーネントは
    # fsm_structure に与えられた値を基に状態遷移ルール等のFSM構造を再
    # 設定する。このオペレーションが未実装の場合は、UNSUPPORTED を返す。
    #
    # @param fsm_structure FSMの構造を表すFsmStructure構造体。
    # @return RTC_OK 正常終了
    #         RTC_ERROR その他のエラー
    #         BAD_PARAMETER 不正なパラメータ
    #         UNSUPPORTED 未サポート
    #
    # @else
    # @brief Set FSM Structure
    #
    # This operation sets an FsmStructure to the target
    # component. Then the target component reconfigures its FSM
    # structure such as transition rules according to the values of
    # the given fsm_structure. RTCs may return UNSUPPORTED if this
    # operation is not implemented.
    #
    # @param fsm_structure FsmStructure structure which represents
    #        FSM structure
    # @return RTC_OK normal return
    #         RTC_ERROR other error
    #         BAD_PARAMETER invalid parameter
    #         UNSUPPORTED unsupported or not implemented
    #
    # @endif
    #
    def set_fsm_structure(self, fsm_structure):
        self._fsmStructure = fsm_structure
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief FSMの構造を取得する
    #
    # このオペレーションは対象のコンポーネントに対して、現在保持してい
    # るFSMの構造を取得する。ExtendedFsmService 構造体はフィールド
    # name (FSMの名称), structure (FSMの構造) 、EventProfile などを返
    # す。structure のフォーマットは、フィールド properties 内に格納さ
    # れたキー "fsm_structure.format" に指定される。このオペレーション
    # が未実装の場合は、UNSUPPORTED を返す。
    #
    # ref: SCXML https://www.w3.org/TR/scxml/
    #
    # @param fsm_structure FSMの構造を表すFsmStructure構造体。
    # @return RTC_OK 正常終了
    #         RTC_ERROR その他のエラー
    #         BAD_PARAMETER 不正なパラメータ
    #         UNSUPPORTED 未サポート
    #
    # @else
    # @brief Set FSM Structure
    #
    # This operation returns the structure of an FSM in the target
    # FSM component. ExtendedFsmService returns the name, structure
    # with format specified by fsm_structure.format and
    # EventProfiles. RTCs may return UNSUPPORTED if this operation is
    # not implemented.
    #
    # @param fsm_structure FsmStructure structure which represents
    #        FSM structure
    # @return RTC_OK normal return
    #         RTC_ERROR other error
    #         BAD_PARAMETER invalid parameter
    #         UNSUPPORTED unsupported or not implemented
    #
    # @endif
    #

    def get_fsm_structure(self):
        return (RTC.RTC_OK, self._fsmStructure)

    ##
    # @if jp
    # @brief RTObjectへのリスナ接続処理
    # @else
    # @brief Connectiong listeners to RTObject
    # @endif
    #

    def setListeners(self, prop):
        pass

    ##
    # @if jp
    # @brief FSM状態遷移
    # @else
    # @brief FSM status change
    # @endif
    #
    def changeStatus(self, state):
        self._fsmState = state

    ##
    # @if jp
    # @brief ハートビートを解除する
    # @else
    # @brief Unsetting heartbeat
    # @endif
    #
    def changeStructure(self, fsm_structure):
        self._fsmStructure.structure = fsm_structure

    ##
    # @if jp
    # @brief FSM状態変化リスナの設定処理
    # @else
    # @brief Setting FSM status listeners
    # @endif
    #
    def setFSMStatusListeners(self):
        pass

    ##
    # @if jp
    # @brief FSM状態変化リスナの解除処理
    # @else
    # @brief Unsetting FSM status listeners
    # @endif
    #
    def unsetFSMStatusListeners(self):
        pass

    ##
    # @if jp
    # @brief FsmProfile状態変化リスナの設定
    # @else
    # @brief Setting FsmProfile listener
    # @endif
    #
    def setFSMProfileListeners(self):
        pass

    ##
    # @if jp
    # @brief FsmProfile状態変化リスナの解除
    # @else
    # @brief Unsetting FsmProfile listener
    # @endif
    #
    def unsetFSMProfileListeners(self):
        pass

    ##
    # @if jp
    # @brief FsmStructure状態変化リスナの設定
    # @else
    # @brief Setting FsmStructure listener
    # @endif
    #
    def setFSMStructureListeners(self):
        pass

    ##
    # @if jp
    # @brief FsmStructure状態変化リスナの解除
    # @else
    # @brief Unsetting FsmStructure listener
    # @endif
    #
    def unsetFSMStructureListeners(self):
        pass


def ExtendedFsmServiceProviderInit(mgr=None):
    factory = OpenRTM_aist.SdoServiceProviderFactory.instance()
    factory.addFactory(RTC.ExtendedFsmService._NP_RepositoryId,
                       ExtendedFsmServiceProvider)
    return
