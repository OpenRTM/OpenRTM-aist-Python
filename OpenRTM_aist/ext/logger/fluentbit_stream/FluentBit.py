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
# @brief FluentBit ���饹
#
#  ���Υ��饹�� �����Ϥ� fluent-bit ���������뤿��Υ����ȥ꡼��
#  �ѥץ饰���󥯥饹�Ǥ��롣
# 
#  fluent-bit �ϥ�������ʬ�ۥߥɥ륦���� fluentd ��C��������Ǥ��롣
#  fluent-bit/fluentd ���͡��ʥץ�ȥ���ǥ��μ������ե��륿��󥰡�
#  ������Ԥ����Ȥ��Ǥ��롣���Υ��饹�ϡ������ȥ꡼��Υץ饰�����
#  �������� FluentBit ���饹�� std::stream_buff ���饹�Υ��֥��饹��
#  ���ꡢ�ºݤ� FluentBit �ؤΥ��ν�����ʬ��ô�����饹�Ǥ��롣
# 
#  �ǥե���ȤǤϡ�OpenRTM�Υ����Ϥ����� (input) �Ȥ��Ƽ�ꡢ
#  rtc.conf �����ꤵ�줿���� (output) ���Ф��ƥ������Ф��뤳�Ȥ���
#  ���롣input �� fluent-bit �����ѤǤ���ץ饰����� rtc.conf ����ͭ
#  ���ˤ��뤳�Ȥ��Ǥ���¾�� fluentd/fluent-bit ����Υ����Ϥ������
#  ���ꡢCPU���������̤ʤɤ�����ϤȤ��Ƽ������뤳�Ȥ��ǽ�Ǥ�
#  �롣�¼�Ū�ˡ����ޥ�ɥ饤��ץ����� fluent-bit �Ȥۤ�Ʊ������
#  ���¸���ǽ�ˤʤäƤ��롣
# 
#  ���ץ����ϡ�����Ū�ˤ� fluent-bit �� key-value ���Υץ�ѥƥ���
#  rtc.conf �ǻ��ꤹ�뤳�ȤǤ��٤ƤΥץ饰��������ѤǤ��뤬���ʲ��ˡ�
#  ��ɽŪ�ʥץ饰����Ȥ��Υ��ץ����򼨤���
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
	# @brief ���󥹥ȥ饯��
	#
	# ���󥹥ȥ饯��
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
	# @brief �ǥ��ȥ饯��
	#
	# �ǥ��ȥ饯��
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
	# @brief ��������
	#
	#Logstream���饹�γƼ������Ԥ����������饹�Ǥϡ�Ϳ����줿
	#Properties����ɬ�פʾ����������ƳƼ������Ԥ���
	#
	# @param self 
	# @param prop �������
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
	# @brief ����ʸ���������Ϥ���
	#
	#
	# @param self
	# @param msg�������Ϥ���ʸ����
	# @param level ����٥�
	# @param name ���ν���̾
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
	# @brief ����٥�����
	#
	#
	# @param self
	# @param level ����٥�
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
	# @brief ��λ����
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
	# @brief �����μ���
	#
	#
	# @param self
	# @param name ���ν���̾
	# @return������
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

