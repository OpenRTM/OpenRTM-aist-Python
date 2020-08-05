#!/usr/bin/env python3
# -*- coding: euc-jp -*-


##
# @file FluentBit.py
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
from fluent import sender
from fluent import event
from fluent import handler
import logging
import logging.handlers


			




##
# @if jp
# @class FluentBit
#
# @brief FluentBit クラス
#
#  このクラスは ログ出力を fluent-bit へ送信するためのログストリーム
#  用プラグインクラスである。
# 
#  fluent-bit はログ収集・分配ミドルウェア fluentd のC言語実装である。
#  fluent-bit/fluentd は様々なプロトコルでログの受信、フィルタリング、
#  送信を行うことができる。このクラスは、ログストリームのプラグインを
#  構成する FluentBit クラスの std::stream_buff クラスのサブクラスで
#  あり、実際の FluentBit へのログの出力部分を担うクラスである。
# 
#  デフォルトでは、OpenRTMのログ出力を入力 (input) として取り、
#  rtc.conf に設定された出力 (output) に対してログを送出することがで
#  きる。input も fluent-bit で利用できるプラグインを rtc.conf から有
#  効にすることができ、他の fluentd/fluent-bit からのログ出力を受信し
#  たり、CPUやメモリ使用量などをログ入力として取得することも可能であ
#  る。実質的に、コマンドラインプログラムの fluent-bit とほぼ同じこと
#  が実現可能になっている。
# 
#  オプションは、基本的には fluent-bit の key-value 型のプロパティを
#  rtc.conf で指定することですべてのプラグインを利用できるが、以下に、
#  代表的なプラグインとそのオプションを示す。
#    
#  * Available Output plugins
#  - reference: http://fluentbit.io/documentation/0.8/output/index.html
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
#  logger.logstream.fluentd.output0.plugin: forward
#  logger.logstream.fluentd.output0.tag:    <tagname>
#  logger.logstream.fluentd.output0.host:   <fluentd_hostname>
#  logger.logstream.fluentd.output0.port:   <fluentd_port>
# 
#  ** es: Elasticsearch
#  ______________________________________________________________________
#  |  key   |                  Description                 |   Default  |
#  ----------------------------------------------------------------------
#  | host   | IP address or hostname of the target         |  127.0.0.1 |
#  |        | Elasticsearch instance.                      |            |
#  ----------------------------------------------------------------------
#  | port   | TCP port of the target Elasticsearch         |       9200 |
#  |        | instance.                                    |            |
#  ----------------------------------------------------------------------
#  | index  | Elastic index.                               | fluentbit  |
#  ----------------------------------------------------------------------
#  | type   | Elastic type.                                | test       |
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#  Example:
#  logger.logstream.fluentd.output0.plugin: es
#  logger.logstream.fluentd.output0.tag:    <tagname>
#  logger.logstream.fluentd.output0.host:   <es_hostname>
#  logger.logstream.fluentd.output0.port:   <es_port>
#  logger.logstream.fluentd.output0.index:  <es_index>
#  logger.logstream.fluentd.output0.type:   <es_type>
# 
#  ** http: HTTP POST request in MessagePack format
#  ______________________________________________________________________
#  |   key  |            Description                       |   Default  |
#  ----------------------------------------------------------------------
#  |  Host  | IP address or hostname of the target HTTP    |  127.0.0.1 |
#  |        | Server.                                      |            |
#  ----------------------------------------------------------------------
#  |  Port  | TCP port of the target HTTP Server.          |         80 |
#  ----------------------------------------------------------------------
#  |  Proxy | Specify an HTTP Proxy. The expected format   |            |
#  |        | of this value is http://host:port.           |            |
#  |        | Note that https is not supported yet.        |            |
#  ----------------------------------------------------------------------
#  |  URI   | Specify an optional HTTP URI for the target  |          / |
#  |        | web server, e.g: /something                  |            |
#  ----------------------------------------------------------------------
#  | Format | Specify the data format to be used in the    |    msgpack |
#  |        | HTTP request body, by default it uses        |            |
#  |        | msgpack, optionally it can be set to json.   |            |
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#  Example:
#  logger.logstream.fluentd.output0.plugin: http
#  logger.logstream.fluentd.output0.tag:    <tagname>
#  logger.logstream.fluentd.output0.host:   127.0.0.1
#  logger.logstream.fluentd.output0.port:   80
#  logger.logstream.fluentd.output0.proxy:
#  logger.logstream.fluentd.output0.uri:     /openrtm/
#  logger.logstream.fluentd.output0.format:  msgpack
# 
#  ** nats: NATS output plugin
#  ______________________________________________________________________
#  |  key   |                  Description                 |   Default  |
#  ----------------------------------------------------------------------
#  | host   | IP address or hostname of the NATS Server.   |  127.0.0.1 |
#  ----------------------------------------------------------------------
#  | port   | TCP port of the target NATS Server.          |       4222 |
#  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
#  Example:
#  logger.logstream.fluentd.output0.plugin: nats
#  logger.logstream.fluentd.output0.tag:    <tagname>
#  logger.logstream.fluentd.output0.host:   <nats_host>
#  logger.logstream.fluentd.output0.port:   <nats_port>
# 
#  * stdout: Standard Output plugin
# 
#  Example:
#  logger.logstream.fluentd.output0.plugin: stdin
#
#
# @else
# @class FluentBit
#
# @brief FluentBit class
#
#
#
# @endif
#
class FluentBit(OpenRTM_aist.LogstreamBase):
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
	#Logstreamクラスの各種設定を行う。実装クラスでは、与えられた
	#Propertiesから必要な情報を取得して各種設定を行う。
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
		
		if FluentBit.s_logger is None:
			FluentBit.s_logger = self
			
			logging.PARANOID  = logging.DEBUG - 3
			logging.VERBOSE   = logging.DEBUG - 2
			logging.TRACE     = logging.DEBUG - 1
			logging.FATAL     = logging.ERROR + 1

			logging.addLevelName(logging.PARANOID,  "PARANOID")
			logging.addLevelName(logging.VERBOSE,   "VERBOSE")
			logging.addLevelName(logging.TRACE,     "TRACE")
			logging.addLevelName(logging.FATAL,     "FATAL")


		leaf0 = prop.getLeaf()
		for l in leaf0:
			key = l.getName()
			if key.find("output") != -1:
				formatter = handler.FluentRecordFormatter()
				tag = l.getProperty("tag")
				if tag == "":
					return False
				host = l.getProperty("host")
				if host == "":
					host = "127.0.0.1"
				port = l.getProperty("port")
				try:
					port = int(port)
				except:
					port = 24224
				
				fhdlr = handler.FluentHandler(tag, host=host, port=port)
				fmt = {
					"time": "%(asctime)s",
					"name": "%(name)s",
					"level": "%(levelname)s",
				}
				formatter = handler.FluentRecordFormatter(fmt=fmt)
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
			log.log(logging.FATAL,msg)
		elif level == OpenRTM_aist.Logger.ERROR:
			log.error(msg)
		elif level == OpenRTM_aist.Logger.WARN:
			log.warning(msg)
		elif level == OpenRTM_aist.Logger.INFO:
			log.info(msg)
		elif level == OpenRTM_aist.Logger.DEBUG:
			log.debug(msg)
		elif level == OpenRTM_aist.Logger.TRACE:
			log.log(logging.TRACE,msg)
		elif level == OpenRTM_aist.Logger.VERBOSE:
			log.log(logging.VERBOSE,msg)
		elif level == OpenRTM_aist.Logger.PARANOID:
			log.log(logging.PARANOID,msg)
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
		
		FluentBit.s_logger = None
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
			return logging.getLogger("fluent."+name)
		else:
			return self.logger


def FluentBitInit(mgr):
	OpenRTM_aist.LogstreamFactory.instance().addFactory("fluentd",
													FluentBit,
													OpenRTM_aist.Delete)

