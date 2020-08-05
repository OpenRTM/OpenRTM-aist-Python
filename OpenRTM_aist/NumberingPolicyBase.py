#!/usr/bin/env python3
# -*- coding: euc-jp -*-

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
# @brief ���֥��������������͡��ߥ󥰡��ݥꥷ��(̿̾��§)�����Ѵ��쥯�饹
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

