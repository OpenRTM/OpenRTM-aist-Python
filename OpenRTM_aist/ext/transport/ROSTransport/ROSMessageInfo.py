#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ROSMessageInfo.py
# @brief ROS Message Info class
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
# @class ROSMessageInfoBase
# @brief ROSメッセージ情報格納オブジェクトの基底クラス
#
# @else
# @class ROSOutPort
# @brief
#
#
# @endif


class ROSMessageInfoBase(object):
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
        return ""

    ##
    # @if jp
    # @brief メッセージのMD5チェックサムを取得
    #
    # @param self
    # @return MD5チェックサム
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
    def md5sum(self):
        return ""

    ##
    # @if jp
    # @brief メッセージの詳細説明を取得
    #
    # @param self
    # @return 詳細説明
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
    def message_definition(self):
        return ""


##
# @if jp
# @class ROSMessageInfo
# @brief メッセージの情報格納クラス
#
#
# @else
# @class ROSMessageInfo
# @brief
#
#
# @endif
class ROSMessageInfo(ROSMessageInfoBase):
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

    def __init__(self, data_class):
        super(ROSMessageInfo, self).__init__()
        self._data_class = data_class
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
        return self._data_class._type
    ##
    # @if jp
    # @brief メッセージのMD5チェックサムを取得
    #
    # @param self
    # @return MD5チェックサム
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

    def md5sum(self):
        return self._data_class._md5sum
    ##
    # @if jp
    # @brief メッセージのMD5チェックサムを取得
    #
    # @param self
    # @return MD5チェックサム
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

    def message_definition(self):
        return self._data_class._full_text


rosmessageinfolist = None


##
# @if jp
# @class ROSMessageInfoList
# @brief ROSメッセージ情報格納オブジェクト生成ファクトリ
#
# @else
# @class ROSMessageInfoList
# @brief
#
#
# @endif
class ROSMessageInfoList:
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
        global rosmessageinfolist

        if rosmessageinfolist is None:
            rosmessageinfolist = ROSMessageInfoList()

        return rosmessageinfolist

    instance = staticmethod(instance)

    ##
    # @if jp
    # @brief ROSMessageInfoの追加
    #
    # @param self
    # @param id 名前
    # @param info ROSMessageInfo
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
    # @brief ROSMessageInfoの削除
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
    # @brief 指定名のROSMessageInfoの取得
    #
    # @param id 名前
    # @return ROSMessageInfo
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
