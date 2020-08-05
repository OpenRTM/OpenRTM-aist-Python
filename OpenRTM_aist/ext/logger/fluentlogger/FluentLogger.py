#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file FluentLogger.py
# @brief File logger stream class
# @date $Date: $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
# Copyright (C) 2017
# 	Nobuhiko Miyamoto
# 	National Institute of
#      Advanced Industrial Science and Technology (AIST), Japan
# 	All rights reserved.
# $Id$

import OpenRTM_aist
import fluent.handler
import logging
import logging.handlers


##
# @if jp
# @class FluentLogger
#
# @brief FluentLogger クラス
#
#  このクラスは ログ出力を fluent-bit へ送信するためのログストリーム
#  用プラグインクラスである。
#
#  fluent-logger-python はログ収集・分配ミドルウェア fluentd へイベントを送信することができる。
#  ログストリームのプラグインを構成する FluentLogger クラスはLogstreamBase クラスの
#  サブクラスであり、実際の fluent-logger-python へのログの出力部分を担うクラスである。
#
#  OpenRTMのログ出力を Fluentd の forward 入力に送信する。
#  forwardプラグインは TCP でイベントの受信、 UDP でハートビートを受信する。
#  elasticsearch、httpプラグインなどにログを送信する場合はfluentdを経由する
#  必要がある。
#  rtc.conf に設定されたホスト、ポートへのログの送信を行い、
#  CPUやメモリ使用量などを送信することも可能である。
#  また yaml ファイルによりfluent-logger-pythonの詳細な設定が可能である。
#
#  以下にrtc.confへのオプションの設定例を示す。
#
#  * Available Output plugins
#  - reference: https://github.com/fluent/fluent-logger-python
#
#  ** forward: fluentd forwarding
#  ______________________________________________________________________
#  |  key   |                  Description                 |   Default  |
#  ----------------------------------------------------------------------
#  | host   | Target host where Fluent-Bit  or Fluentd are |  127.0.0.1 |
#  |        | listening for Forward messages.              |            |
#  ----------------------------------------------------------------------
#  | port   | TCP port of the target service.              |      24224 |
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#  Example:
#  logger.logstream.fluentd.output0.tag:    <tagname>
#  logger.logstream.fluentd.output0.host:   <fluentd_hostname>
#  logger.logstream.fluentd.output0.port:   <fluentd_port>
#
#
#
# @else
# @class FluentLogger
#
# @brief FluentLogger class
#
#
#
# @endif
#
class FluentLogger(OpenRTM_aist.LogstreamBase):
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
    # LogstreamBaseクラスの各種設定を行う。実装クラスでは、与えられた
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
        self.logger = logging.getLogger("fluent")
        self.handlers = []

        if FluentLogger.s_logger is None:
            FluentLogger.s_logger = self

            logging.PARANOID = logging.DEBUG - 3
            logging.VERBOSE = logging.DEBUG - 2
            logging.TRACE = logging.DEBUG - 1
            logging.FATAL = logging.ERROR + 1

            logging.addLevelName(logging.PARANOID, "PARANOID")
            logging.addLevelName(logging.VERBOSE, "VERBOSE")
            logging.addLevelName(logging.TRACE, "TRACE")
            logging.addLevelName(logging.FATAL, "FATAL")

        leaf0 = prop.getLeaf()
        for l in leaf0:
            key = l.getName()
            if key.find("output") != -1:
                formatter = fluent.handler.FluentRecordFormatter()
                tag = l.getProperty("tag")
                if tag == "":
                    return False
                host = l.getProperty("host")
                if host == "":
                    host = "127.0.0.1"
                port = l.getProperty("port")
                try:
                    port = int(port)
                except BaseException:
                    port = 24224

                fhdlr = fluent.handler.FluentHandler(tag, host=host, port=port)
                fhdlr.addFilter(ManagerNameFilter())
                fmt = {
                    "time": "%(asctime)s",
                    "name": "%(name)s",
                    "level": "%(levelname)s",
                    "pid": "%(process)d",
                    "host": "%(hostname)s",
                    "manager": "%(manager)s"
                }
                formatter = fluent.handler.FluentRecordFormatter(fmt=fmt)
                #formatter = logging.Formatter('{Time:%(asctime)s,Name:%(name)s,LEVEL:%(levelname)s,MESSAGE:%(message)s}')
                fhdlr.setFormatter(formatter)
                self.handlers.append(fhdlr)
                self.logger.addHandler(fhdlr)

                self.logger.setLevel(logging.INFO)

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

        FluentLogger.s_logger = None
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
            return logging.getLogger("fluent." + name)
        else:
            return self.logger

##
# @if jp
# @class ManagerNameFilter
#
# @brief ManagerNameFilter クラス
#
# ログのフォーマットの"manager"キーにマネージャ名を設定する
#
# @else
# @class ManagerNameFilter
#
# @brief ManagerNameFilter class
#
#
#
# @endif
#


class ManagerNameFilter(logging.Filter):
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
        logging.Filter.__init__(self)
        conf = OpenRTM_aist.Manager.instance().getConfig()
        self._managername = conf.getProperty("manager.instance_name")
    ##
    # @if jp
    # @brief フィルタリングしてメッセージにマネージャ名を追加する
    #
    #
    # @else
    # @brief
    #
    #
    #
    # @endif
    #

    def filter(self, record):
        record.manager = self._managername
        return True


def FluentLoggerInit(mgr):
    OpenRTM_aist.LogstreamFactory.instance().addFactory("fluentd",
                                                        FluentLogger)
