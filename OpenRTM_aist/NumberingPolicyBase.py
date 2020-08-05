#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file NumberingPolicyBase.py
# @brief Object numbering policy base class
# @date $Date: 2016/02/25$
# @author Nobuhiko Miyamoto
#


import OpenRTM_aist


##
# @if jp
#
# @class NumberingPolicyBase
# @brief オブジェクト生成時ネーミング・ポリシー(命名規則)管理用基底クラス
#
#
#
# @else
#
# @endif
class NumberingPolicyBase:
    def __init__(self):
        pass

    def onCreate(self, obj):
        pass

    def onDelete(self, obj):
        pass


numberingpolicyfactory = None


class NumberingPolicyFactory(OpenRTM_aist.Factory):
    def __init__(self):
        OpenRTM_aist.Factory.__init__(self)

    def instance():
        global numberingpolicyfactory
        if numberingpolicyfactory is None:
            numberingpolicyfactory = NumberingPolicyFactory()
        return numberingpolicyfactory
    instance = staticmethod(instance)
