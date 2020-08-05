#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
# @file SystemLogger.py
# @brief RT component logger class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2003-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import sys
import traceback

import threading
import logging

import OpenRTM_aist
import copy




##
# @if jp
#
# @class Logg
#
# @brief �����ե����ޥåȥ��ߡ����饹
#
# ���ե����ޥå��ѥ��ߡ����饹��
#
# @else
#
# @endif
class Logger:
  """
  """

  SILENT    = 0  # ()
  FATAL     = 41 # (FATAL)
  ERROR     = 40 # (FATAL, ERROR)
  WARN      = 30 # (FATAL, ERROR, WARN)
  INFO      = 20 # (FATAL, ERROR, WARN, INFO)
  DEBUG     = 10 # (FATAL, ERROR, WARN, INFO, DEBUG)
  TRACE     = 9  # (FATAL, ERROR, WARN, INFO, DEBUG, TRACE)
  VERBOSE   = 8  # (FATAL, ERROR, WARN, INFO, DEBUG, TRACE, VERBOSE)
  PARANOID  = 7  # (FATAL, ERROR, WARN, INFO, DEBUG, TRACE, VERBOSE, PARA)


  ##
  # @if jp
  #
  # @brief ����٥�����
  #
  # Ϳ����줿ʸ������б���������٥�����ꤹ�롣
  #
  # @param self
  # @param lv ����٥�ʸ����
  #
  # @return ���ꤷ������٥�
  #
  # @else
  #
  # @endif
  def strToLogLevel(lv):
    if lv == "SILENT":
      return Logger.SILENT
    elif lv == "FATAL":
      return Logger.FATAL
    elif lv == "ERROR":
      return Logger.ERROR
    elif lv == "WARN":
      return Logger.WARN
    elif lv == "INFO":
      return Logger.INFO
    elif lv == "DEBUG":
      return Logger.DEBUG
    elif lv == "TRACE":
      return Logger.TRACE
    elif lv == "VERBOSE":
      return Logger.VERBOSE
    elif lv == "PARANOID":
      return Logger.PARANOID
    else:
      return Logger.INFO

  strToLogLevel = staticmethod(strToLogLevel)




  ##
  # @if jp
  #
  # @brief printf �ե����ޥåȽ���
  #
  # printf�饤���ʽ񼰤ǥ����Ϥ��롣<br>
  # ���ܼ����Ǥϰ��� fmt ��Ϳ����줿ʸ���򤽤Τޤ��֤���
  #
  # @param self
  # @param fmt ��ʸ����
  #
  # @return ���դ�ʸ�������
  #
  # @else
  #
  # @brief Formatted output like printf
  #
  # @endif
  def printf(fmt):
    return fmt

  printf = staticmethod(printf)


  ##
  # @if jp
  #
  # @brief �㳰�������
  #  �㳰�����ʸ������֤���
  #
  # @return �㳰�����ʸ�������
  #
  # @else
  #
  # @brief Print exception information 
  # @return Return exception information string.
  #
  # @endif
  def print_exception():
    if sys.version_info[0:3] >= (2, 4, 0):
      return traceback.format_exc()
    else:
      _exc_list = traceback.format_exception(*sys.exc_info())
      _exc_str = "".join(_exc_list)
      return _exc_str
    
  print_exception = staticmethod(print_exception)



##
# @if jp
#
# @class Logg
#
# @brief �����ե����ޥåȥ��ߡ����饹
#
# ���ե����ޥå��ѥ��ߡ����饹��
#
# @else
#
# @endif
class LogStream:
  """
  """

  ##
  # @if jp
  #
  # @brief ���󥹥ȥ饯��
  #
  # ���󥹥ȥ饯��
  #
  # @param self
  # @param (mode,file_name,address)
  #
  # @else
  #
  # @brief constructor.
  #
  # @endif
  def __init__(self, *args):
    self._LogLock = False
    self._log_enable = False
    


    self._logger_name = ""
    self._mutex = threading.RLock()
    self._loggerObj = []
    self._log_enable = True
    self.guard = None


  def __del__(self):
    return

  def shutdown(self):
    for log in self._loggerObj:
      log.shutdown()
    self._loggerObj = []
    return

  def addLogger(self, loggerObj):
    self.acquire()
    self._loggerObj.append(loggerObj)
    self.release()

  ##
  # @if jp
  #
  # @brief ����٥�����
  #
  # ����٥�����ꤹ�롣
  #
  # @param self
  # @param level ����٥�
  #
  # @else
  #
  # @endif
  def setLogLevel(self, level):
    lvl = Logger.strToLogLevel(level)
    for log in self._loggerObj:
      log.setLogLevel(lvl)
    
    


  ##
  # @if jp
  #
  # @brief ��å��⡼������
  #
  # ���Υ�å��⡼�ɤ����ꤹ�롣
  #
  # @param self
  # @param lock ����å��ե饰
  #
  # @else
  #
  # @endif
  def setLogLock(self, lock):
    if lock == 1:
      self._LogLock = True
    elif lock == 0:
      self._LogLock = False


  ##
  # @if jp
  #
  # @brief ��å��⡼��ͭ����
  #
  # @param self
  #
  # ��å��⡼�ɤ�ͭ���ˤ��롣
  #
  # @else
  #
  # @endif
  def enableLogLock(self):
    self._LogLock = True


  ##
  # @if jp
  #
  # @brief ��å��⡼�ɲ��
  #
  # @param self
  #
  # ��å��⡼�ɤ�̵���ˤ��롣
  #
  # @else
  #
  # @endif
  def disableLogLock(self):
    self._LogLock = False


  ##
  # @if jp
  #
  # @brief ����å�����
  # ��å��⡼�ɤ����ꤵ��Ƥ����硢���Υ�å���������롣
  #
  # @param self
  #
  # @else
  #
  # @endif
  def acquire(self):
    if self._LogLock:
      self.guard = OpenRTM_aist.ScopedLock(self._mutex)


  ##
  # @if jp
  #
  # @brief ����å�����
  # ��å��⡼�ɤ����ꤵ��Ƥ�����ˡ����Υ�å���������롣
  #
  # @param self
  #
  # @else
  #
  # @endif
  def release(self):
    if self._LogLock and self.guard:
      del self.guard


  ##
  # @if jp
  #
  # @brief ���ѥ�����
  #
  # ����٥뤪��ӽ��ϥե����ޥå�ʸ���������Ȥ��ƤȤꡤ
  # ���ѥ�����Ϥ��롣
  #
  # @param self
  # @param LV ����٥�
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Log output macro
  #
  # @endif
  def RTC_LOG(self, LV, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_LOG : argument error")
          return
      for log in self._loggerObj:
        log.log(messages, LV, self._logger_name)
      

      self.release()


  ##
  # @if jp
  #
  # @brief FATAL���顼������
  #
  # FATAL���顼��٥�Υ�����Ϥ��롣<BR>����٥뤬
  # FATAL, ERROR, WARN, INFO, DEBUG, TRACE, VERBOSE, PARANOID
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Error log output macro.
  #
  # @endif
  def RTC_FATAL(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_FATAL : argument error")
          return

      for log in self._loggerObj:
        log.log(messages, Logger.FATAL, self._logger_name)

      self.release()


  ##
  # @if jp
  #
  # @brief ���顼������
  #
  # ���顼��٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ERROR, WARN, INFO, DEBUG, TRACE, VERBOSE, PARANOID
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Error log output macro.
  #
  # @endif
  def RTC_ERROR(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_ERROR : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.ERROR, self._logger_name)

      self.release()


  ##
  # @if jp
  #
  # @brief ��˥󥰥�����
  #
  # ��˥󥰥�٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( WARN, INFO, DEBUG, TRACE, VERBOSE, PARANOID )
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Warning log output macro.
  #
  # If logging levels are
  # ( WARN, INFO, DEBUG, TRACE, VERBOSE, PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_WARN(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_WARN : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.WARN, self._logger_name)

      self.release()


  ##
  # @if jp
  #
  # @brief ����ե�������
  #
  # ����ե���٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( INFO, DEBUG, TRACE, VERBOSE, PARANOID )
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Infomation level log output macro.
  #
  #  If logging levels are
  # ( INFO, DEBUG, TRACE, VERBOSE, PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_INFO(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_INFO : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.INFO, self._logger_name)
    
      self.release()


  ##
  # @if jp
  #
  # @brief �ǥХå�������
  #
  # �ǥХå���٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( DEBUG, TRACE, VERBOSE, PARANOID )
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Debug level log output macro.
  #
  # If logging levels are
  # ( DEBUG, TRACE, VERBOSE, PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_DEBUG(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_DEBUG : argument error")
          return
        
      
      for log in self._loggerObj:
        log.log(messages, Logger.DEBUG, self._logger_name)
      
      self.release()


  ##
  # @if jp
  #
  # @brief �ȥ졼��������
  #
  # �ȥ졼����٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( TRACE, VERBOSE, PARANOID )
  # �ξ��˥����Ϥ���롣
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Trace level log output macro.
  #
  # If logging levels are
  # ( TRACE, VERBOSE, PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_TRACE(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg

      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_TRACE : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.TRACE, self._logger_name)
    
      self.release()


  ##
  # @if jp
  #
  # @brief �٥�ܡ���������
  #
  # �٥�ܡ�����٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( VERBOSE, PARANOID )
  # �ξ��˥����Ϥ���롣<br>
  # �������Ǥ�̤����
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Verbose level log output macro.
  #
  # If logging levels are
  # ( VERBOSE, PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_VERBOSE(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_VERBOSE : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.VERBOSE, self._logger_name)
    
      self.release()



  ##
  # @if jp
  #
  # @brief �ѥ�Υ��ɥ�����
  #
  # �ѥ�Υ��ɥ�٥�Υ�����Ϥ��롣<BR>����٥뤬
  # ( PARANOID )
  # �ξ��˥����Ϥ���롣<br>
  # �������Ǥ�̤����
  #
  # @param self
  # @param msg ����å�����
  # @param opt ���ץ����(�ǥե������:None)
  #
  # @else
  #
  # @brief Paranoid level log output macro.
  #
  # If logging levels are
  # ( PARANOID ),
  # message will be output to log.
  #
  # @endif
  def RTC_PARANOID(self, msg, opt=None):
    if self._log_enable:
      self.acquire()

      if opt is None:
        messages = msg
      else:
        try:
          messages = msg%(opt)
        except:
          print("RTC_PARANOID : argument error")
          return

      
      for log in self._loggerObj:
        log.log(messages, Logger.PARANOID, self._logger_name)
    
      self.release()


  def getLogger(self, name):
    syslogger = copy.copy(self)
    syslogger._logger_name = name
    return syslogger
    



