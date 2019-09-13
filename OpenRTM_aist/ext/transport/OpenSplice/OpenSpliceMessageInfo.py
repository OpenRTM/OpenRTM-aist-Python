#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file OpenSpliceMessageInfo.py
# @brief OpenSplice Message Info class
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
# @class OpenSpliceMessageInfoBase
# @brief OpenSpliceメッセージ情報格納オブジェクトの基底クラス
# OpenSpliceデータ型名、IDLファイルパスを登録する
#
# @else
# @class OpenSpliceOutPort
# @brief
#
#
# @endif


class OpenSpliceMessageInfoBase(object):
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
        return ""

    ##
    # @if jp
    # @brief IDLファイルのパスを取得
    #
    # @param self
    # @return IDLファイルのパス
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
    def idlFile(self):
        return ""


##
# @if jp
# @brief メッセージの情報格納オブジェクト生成関数
#
# @param data_class OpenSpliceデータ型
# @return メッセージの情報格納オブジェクト
#
# @else
# @brief
#
# @param data_class
# @return
#
# @endif
#
def opensplice_message_info(datatype, idlfile):
    ##
    # @if jp
    # @class OpenSpliceMessageInfo
    # @brief メッセージの情報格納クラス
    #
    #
    # @else
    # @class OpenSpliceMessageInfo
    # @brief
    #
    #
    # @endif
    class OpenSpliceMessageInfo(OpenSpliceMessageInfoBase):
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
        def __init__(self):
            super(OpenSpliceMessageInfo, self).__init__()

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
            return datatype

        ##
        # @if jp
        # @brief IDLファイルのパスを取得
        #
        # @param self
        # @return IDLファイルのパス
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
        def idlFile(self):
            return idlfile

    return OpenSpliceMessageInfo


opensplicemessageinfofactory = None


##
# @if jp
# @class OpenSpliceMessageInfoFactory
# @brief OpenSpliceメッセージ情報格納オブジェクト生成ファクトリ
#
# @else
# @class OpenSpliceMessageInfoFactory
# @brief
#
#
# @endif
class OpenSpliceMessageInfoFactory(
        OpenRTM_aist.Factory, OpenSpliceMessageInfoBase):
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
        OpenRTM_aist.Factory.__init__(self)

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
        global opensplicemessageinfofactory

        if opensplicemessageinfofactory is None:
            opensplicemessageinfofactory = OpenSpliceMessageInfoFactory()

        return opensplicemessageinfofactory

    instance = staticmethod(instance)
