#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file LogstreamFile.py
# @brief File logger stream class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
# Copyright (C) 2017
#   Nobuhiko Miyamoto
#   National Institute of
#      Advanced Industrial Science and Technology (AIST), Japan
#   All rights reserved.
# $Id$


import OpenRTM_aist
import OpenRTM_aist.StringUtil
import logging
import logging.handlers


##
# @if jp
# @class LogstreamFile
#
# @brief LogstreamFile クラス
#
#
#
#
# @else
# @class LogstreamFile
#
# @brief LogstreamFile class
#
#
# @endif
#
class LogstreamFile(OpenRTM_aist.LogstreamBase):
    """
    """
    s_logger = None
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
        OpenRTM_aist.LogstreamBase.__init__(self)
        self.handlers = []

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
        self.logger = logging.getLogger("file")

        if LogstreamFile.s_logger is None:
            LogstreamFile.s_logger = self

            logging.PARANOID = logging.DEBUG - 3
            logging.VERBOSE = logging.DEBUG - 2
            logging.TRACE = logging.DEBUG - 1
            logging.FATAL = logging.ERROR + 1

            logging.addLevelName(logging.PARANOID, "PARANOID")
            logging.addLevelName(logging.VERBOSE, "VERBOSE")
            logging.addLevelName(logging.TRACE, "TRACE")
            logging.addLevelName(logging.FATAL, "FATAL")

        files = prop.getProperty("file_name")
        files = [s.strip() for s in files.split(",")]

        for f in files:
            self.addHandler(f)

        if not self.handlers:
            return False

        return True

    ##
    # @if jp
    # @brief ログ出力ハンドラ追加
    #
    #
    # @param self
    # @param f ログ出力ファイル名、もしくはstdout
    # @return
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @param f
    # @return
    #
    # @endif
    #

    def addHandler(self, f):
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
        f = OpenRTM_aist.eraseHeadBlank(f)
        f = OpenRTM_aist.eraseTailBlank(f)
        handlers = self.logger.handlers
        for h in handlers:
            if h.get_name() == f:
                return False

        fname = OpenRTM_aist.StringUtil.normalize(f)

        if fname == "stdout":
            ch = logging.StreamHandler()
            ch.setLevel(logging.NOTSET)
            ch.setFormatter(formatter)
            ch.set_name(f)
            self.logger.addHandler(ch)
            self.handlers.append(ch)
            return True

        else:
            try:
                fhdlr = logging.FileHandler(fname)
                mhdlr = logging.handlers.MemoryHandler(
                    1024, logging.NOTSET, fhdlr)
                fhdlr.setFormatter(formatter)
                mhdlr.set_name(f)
                self.logger.addHandler(mhdlr)
                self.handlers.append(mhdlr)
                self.logger.setLevel(logging.NOTSET)
            except BaseException:
                pass

            return True

    ##
    # @if jp
    # @brief 指定文字列をログ出力する
    #
    #
    # @param self
    # @param msg　ログ出力する文字列
    # @param level ログレベル
    # @param name ログの出力名
    # @return
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @param msg
    # @param level
    # @param name
    # @return
    #
    # @endif
    #
    def log(self, msg, level, name):
        log = self.getLogger(name)
        if level == OpenRTM_aist.Logger.FATAL:
            log.log(logging.FATAL, msg)
        elif level == OpenRTM_aist.Logger.ERROR:
            log.error(msg)
        elif level == OpenRTM_aist.Logger.WARN:
            log.warning(msg)
        elif level == OpenRTM_aist.Logger.INFO:
            log.info(msg)
        elif level == OpenRTM_aist.Logger.DEBUG:
            log.debug(msg)
        elif level == OpenRTM_aist.Logger.TRACE:
            log.log(logging.TRACE, msg)
        elif level == OpenRTM_aist.Logger.VERBOSE:
            log.log(logging.VERBOSE, msg)
        elif level == OpenRTM_aist.Logger.PARANOID:
            log.log(logging.PARANOID, msg)
        else:
            return False
        return True

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
        if level == OpenRTM_aist.Logger.INFO:
            self.logger.setLevel(logging.INFO)
        elif level == OpenRTM_aist.Logger.FATAL:
            self.logger.setLevel(logging.FATAL)
        elif level == OpenRTM_aist.Logger.ERROR:
            self.logger.setLevel(logging.ERROR)
        elif level == OpenRTM_aist.Logger.WARN:
            self.logger.setLevel(logging.WARNING)
        elif level == OpenRTM_aist.Logger.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        elif level == OpenRTM_aist.Logger.SILENT:
            self.logger.setLevel(logging.NOTSET)
        elif level == OpenRTM_aist.Logger.TRACE:
            self.logger.setLevel(logging.TRACE)
        elif level == OpenRTM_aist.Logger.VERBOSE:
            self.logger.setLevel(logging.VERBOSE)
        elif level == OpenRTM_aist.Logger.PARANOID:
            self.logger.setLevel(logging.PARANOID)
        else:
            self.logger.setLevel(logging.INFO)

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
        for h in self.handlers:
            logging.Handler.close(h)
            self.logger.removeHandler(h)

        LogstreamFile.s_logger = None
        self.handlers = []
        return True

    ##
    # @if jp
    # @brief ロガーの取得
    #
    #
    # @param self
    # @param name ログの出力名
    # @return　ロガー
    #
    # @else
    # @brief
    #
    #
    # @param self
    # @param name
    # @return
    #
    # @endif
    #
    def getLogger(self, name):
        if name:
            return logging.getLogger("file." + name)
        else:
            return self.logger


def LogstreamFileInit():
    OpenRTM_aist.LogstreamFactory.instance().addFactory("file",
                                                        OpenRTM_aist.LogstreamFile)
