#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file LogstreamBase.py
# @brief Logger stream buffer base class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
# Copyright (C) 2017
#   Nobuhiko Miyamoto
#   National Institute of
#      Advanced Industrial Science and Technology (AIST), Japan
#   All rights reserved.
# $Id$


import OpenRTM_aist


##
# @if jp
# @class LogstreamBase
#
# @brief LogstreamBase クラス
#
#
#
#
# @else
# @class LogstreamBase
#
# @brief LogstreamBase class
#
#
# @endif
#
class LogstreamBase:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @endif
    #
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    # @brief 設定初期化
    #
    # Logstreamクラスの各種設定を行う。実装クラスでは、与えられた
    # Propertiesから必要な情報を取得して各種設定を行う。
    #
    # @param self
    # @param prop 設定情報
    # @return
    #
    # @else
    # @brief Initializing configuration
    #
    # This operation would be called to configure in initialization.
    # In the concrete class, configuration should be performed
    # getting appropriate information from the given Properties data.
    #
    # @param self
    # @param prop Configuration information
    # @return
    #
    # @endif
    #

    def init(self, prop):
        return False

    ##
    # @if jp
    # @brief 指定文字列をログ出力する
    #
    #
    # @param self
    # @param msg　ログ出力する文字列
    # @param level ログレベル
    # @return
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @param msg
    # @param level
    # @return
    #
    # @endif
    #

    def log(self, msg, level, name):
        return False

    ##
    # @if jp
    # @brief ログレベル設定
    #
    #
    # @param self
    # @param level ログレベル
    # @return
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @param level
    # @return
    #
    # @endif
    #

    def setLogLevel(self, level):
        pass

    ##
    # @if jp
    # @brief 終了処理
    #
    #
    # @param self
    # @return
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

    def shutdown(self):
        return True


logstreamfactory = None


class LogstreamFactory(OpenRTM_aist.Factory):
    def __init__(self):
        OpenRTM_aist.Factory.__init__(self)

    def instance():
        global logstreamfactory
        if logstreamfactory is None:
            logstreamfactory = LogstreamFactory()
        return logstreamfactory
    instance = staticmethod(instance)
