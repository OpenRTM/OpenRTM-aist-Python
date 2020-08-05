#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROS2MessageInfo.py
# @brief ROS2 Message Info class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist

##
# @if jp
# @class ROS2MessageInfoBase
# @brief ROS2メッセージ情報格納オブジェクトの基底クラス
# ROS2データ型名、IDLファイルパスを登録する
#
# @else
# @class ROS2OutPort
# @brief
#
#
# @endif


class ROS2MessageInfoBase(object):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # @param self
    #
    # @endif
    def __init__(self):
        pass
    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    #
    # @endif
    #

    def __del__(self):
        pass

    ##
    # @if jp
    # @brief データの型名を取得
    #
    # @param self
    # @return 型名
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @return
    #
    # @endif
    #
    def datatype(self):
        return None


##
# @if jp
# @class ROS2MessageInfo
# @brief メッセージの情報格納クラス
#
#
# @else
# @class ROS2MessageInfo
# @brief
#
#
# @endif
class ROS2MessageInfo(ROS2MessageInfoBase):
    """
    """
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # @param self
    #
    # @endif

    def __init__(self, datatype):
        super(ROS2MessageInfo, self).__init__()
        self._datatype = datatype
    ##
    # @if jp
    # @brief デストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif

    def __del__(self):
        pass
    ##
    # @if jp
    # @brief メッセージの型名を取得
    #
    # @param self
    # @return 型名
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @return
    #
    # @endif
    #

    def datatype(self):
        return self._datatype


ros2messageinfolist = None


##
# @if jp
# @class ROS2MessageInfoList
# @brief ROS2メッセージ情報格納オブジェクト生成ファクトリ
#
# @else
# @class ROS2MessageInfoList
# @brief
#
#
# @endif
class ROS2MessageInfoList:
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    # @brief Constructor
    #
    # @param self
    #
    # @endif
    def __init__(self):
        self._data = {}

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    # @brief インスタンス取得
    #
    #
    # @return インスタンス
    #
    # @else
    # @brief
    #
    #
    # @return
    #
    # @endif
    #
    def instance():
        global ros2messageinfolist

        if ros2messageinfolist is None:
            ros2messageinfolist = ROS2MessageInfoList()

        return ros2messageinfolist

    instance = staticmethod(instance)

    ##
    # @if jp
    # @brief ROS2MessageInfoの追加
    #
    # @param self
    # @param id 名前
    # @param info ROS2MessageInfo
    #
    # @else
    # @brief
    #
    # @param self
    # @param id
    # @param info
    #
    # @endif
    #
    def addInfo(self, id, info):
        self._data[id] = info

    ##
    # @if jp
    # @brief ROS2MessageInfoの削除
    #
    # @param self
    # @param id 名前
    # @return 削除に成功した場合はTrue
    #
    # @else
    # @brief
    #
    # @param self
    # @param id
    # @return
    #
    # @endif
    #
    def removeInfo(self, id):
        if id in self._data:
            del self._data[id]
            return True
        return False

    ##
    # @if jp
    # @brief 指定名のROS2MessageInfoの取得
    #
    # @param id 名前
    # @return ROS2MessageInfo
    #
    # @else
    # @brief
    #
    # @param id
    # @return
    #
    # @endif
    #
    def getInfo(self, id):
        if id in self._data:
            return self._data[id]
        return None
