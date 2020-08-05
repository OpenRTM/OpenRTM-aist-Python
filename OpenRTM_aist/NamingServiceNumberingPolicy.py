#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file NamingServiceNumberingPolicy.py
# @brief Object numbering policy class
# @date $Date: 2016/02/25$
# @author Nobuhiko Miyamoto
#


import OpenRTM_aist


##
# @if jp
#
# @class NamingServiceNumberingPolicy
# @brief オブジェクト生成時ネーミング・ポリシー(命名規則)管理用クラス
#　ネーミングサービスからRTCを検索してナンバリングを行う
#
#
# @else
#
# @endif
class NamingServiceNumberingPolicy(OpenRTM_aist.NumberingPolicy):
    """
    """

    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief virtual destractor
    #
    # @endif
    def __init__(self):
        self._num = 0
        self._objects = []
        self._mgr = OpenRTM_aist.Manager.instance()

    ##
    # @if jp
    #
    # @brief オブジェクト生成時の名称作成
    #
    #
    #
    # @param self
    # @param obj 名称生成対象オブジェクト
    #
    # @return 生成したオブジェクト名称
    #
    # @else
    #
    # @endif

    def onCreate(self, obj):
        num = 0
        while True:
            num_str = OpenRTM_aist.otos(num)

            name = obj.getTypeName() + num_str
            if not self.find(name):
                return num_str
            else:
                num += 1
        return OpenRTM_aist.otos(num)

    ##
    # @if jp
    #
    # @brief オブジェクト削除時の名称解放
    #
    #
    #
    # @param self
    # @param obj 名称解放対象オブジェクト
    #
    # @else
    #
    # @endif
    def onDelete(self, obj):
        pass

    ##
    # @if jp
    #
    # @brief オブジェクトの検索
    #
    # 指定名のインスタンス名のRTCを検索し、
    # 一致するRTCが存在する場合はTrueを返す
    #
    # @param self
    # @param name RTCのインスタンス名
    #
    # @return 判定
    #
    # @else
    #
    # @endif

    def find(self, name):
        rtcs = []
        rtc_name = "rtcname://*/*/"
        rtc_name += name
        rtcs = self._mgr.getNaming().string_to_component(rtc_name)

        if rtcs:
            return True
        else:
            return False


def NamingServiceNumberingPolicyInit():
    OpenRTM_aist.NumberingPolicyFactory.instance().addFactory("ns_unique",
                                                              OpenRTM_aist.NamingServiceNumberingPolicy)
