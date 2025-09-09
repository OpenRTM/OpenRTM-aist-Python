#!/usr/bin/env python
# -*- coding: utf-8 -*-


##
# @file ESLogger.py
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
from elasticsearch import Elasticsearch
import ecs_logging
import logging
import logging.handlers


##
# @if jp
# @class ECS_Handler
#
# @brief ECS_Handler クラス
#
#  Elasticsearch用ロギングハンドラクラス
#
#
# @else
# @class ESLogger
#
# @brief ESLogger class
#
#
#
# @endif
#

class ECS_Handler(logging.Handler):

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # @param self
    # @param host ElasticSearchサーバーのアドレス
    # @param index 登録するデータのインデックス
    # @param **kwargs
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    # @param host
    # @param index
    # @param **kwargs
    #
    # @endif
    #
    def __init__(self, hosts="http://localhost:9200", index="fluentbit", **kwargs):
        self._index = index
        logging.Handler.__init__(self)
        self._es = Elasticsearch(hosts, **kwargs)
    ##
    # @if jp
    # @brief データをElasticsearchに登録する
    #
    # @param self
    # @param record ログデータ
    #
    # @else
    # @brief
    #
    #
    #
    # @param self
    # @param record
    #
    # @endif
    #

    def emit(self, record):
        data = self.format(record)
        self._es.index(index=self._index, body=data)


##
# @if jp
# @class ECS_Formatter
#
# @brief ECS_Formatter クラス
#
#  Elastic Common Schema(ECS)に独自の要素を追加する
#  ロギングフォーマッタクラス
#
#
# @else
# @class ECS_Formatter
#
# @brief ECS_Formatter class
#
#
#
# @endif
#
class ECS_Formatter(ecs_logging.StdlibFormatter):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # @param self
    # @param fmt
    # @param datefmt
    # @param style
    # @param validate
    # @param stack_trace_limit
    # @param exclude_fields
    #
    # @else
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    # @param fmt
    # @param datefmt
    # @param style
    # @param validate
    # @param stack_trace_limit
    # @param exclude_fields
    #
    # @endif
    #
    def __init__(self, fmt=None, datefmt=None, style="%", validate=None, stack_trace_limit=None, exclude_fields=()):
        ecs_logging.StdlibFormatter.__init__(
            self, fmt, datefmt, style, validate, stack_trace_limit, exclude_fields)

    ##
    # @if jp
    # @brief loggingのレコードをECSフォーマットに変換する
    #
    # @param self
    # @param record ログデータ
    #
    # @else
    # @brief
    #
    #
    #
    # @param self
    # @param record
    #
    # @endif
    #
    def format_to_ecs(self, record):
        result = ecs_logging.StdlibFormatter.format_to_ecs(self, record)
        result["level"] = result["log"]["level"]
        return result


##
# @if jp
# @class ESLogger
#
# @brief ESLogger クラス
#
#  このクラスは ログ出力を ElasticSearch へ送信するためのログストリーム
#  用プラグインクラスである。
#
#
# @else
# @class ESLogger
#
# @brief ESLogger class
#
#
#
# @endif
#


class ESLogger(OpenRTM_aist.LogstreamBase):
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
        self.logger = logging.getLogger("esrtm")
        self.handlers = []

        if ESLogger.s_logger is None:
            ESLogger.s_logger = self

            logging.PARANOID = logging.DEBUG - 3
            logging.VERBOSE = logging.DEBUG - 2
            logging.TRACE = logging.DEBUG - 1
            logging.FATAL = logging.ERROR + 1

            logging.addLevelName(logging.PARANOID, "PARANOID")
            logging.addLevelName(logging.VERBOSE, "VERBOSE")
            logging.addLevelName(logging.TRACE, "TRACE")
            logging.addLevelName(logging.FATAL, "FATAL")

        leaf0 = prop.getLeaf()
        for param in leaf0:
            key = param.getName()
            if key.find("output") != -1:

                host = param.getProperty("host", "127.0.0.1")

                port = param.getProperty("port", "9200")

                hosts = host + ":" + port

                index = param.getProperty("index", "fluentbit")

                opt = {}
                try:
                    opt.timeout = int(param.getProperty("timeout"))
                except ValueError:
                    pass

                opt["use_ssl"] = OpenRTM_aist.toBool(
                    param.getProperty("use_ssl"), "YES", "NO", False)

                opt["verify_certs"] = OpenRTM_aist.toBool(
                    param.getProperty("verify_certs"), "YES", "NO", True)

                opt["ca_certs"] = param.getProperty("ca_certs")
                opt["cert_file_path"] = param.getProperty("cert_file_path")
                opt["key_file_path"] = param.getProperty("key_file_path")

                ehdlr = ECS_Handler(hosts=hosts, index=index, **opt)
                # ehdlr.addFilter(ManagerNameFilter())

                formatter = ECS_Formatter()
                ehdlr.setFormatter(formatter)
                self.handlers.append(ehdlr)
                self.logger.addHandler(ehdlr)

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

        ESLogger.s_logger = None
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
            return logging.getLogger("esrtm." + name)
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


def ESLoggerInit(mgr):
    OpenRTM_aist.LogstreamFactory.instance().addFactory("elasticsearch",
                                                        ESLogger)
