#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file ManagerConfig.py
# @brief RTC manager configuration
# @date $Date: $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2003-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#    All rights reserved.


import sys
import os
import getopt
import platform

import OpenRTM_aist


##
# @if jp
#
# @class ManagerConfig
# @brief Manager configuration ���饹
#
# Manager �Υ���ե�����졼������Ԥ������ޥ�ɥ饤������������ꡢ
# (���뤤�ϰ����ʤ���)���󥹥��󥹲�����롣
# ���ޥ�ɥ饤������ǻ��ꤵ�줿����ե����롢�Ķ��ѿ��ʤɤ��� Manager ��
# �ץ�ѥƥ���������ꤹ�롣
#
# �������ͥ���٤ϰʲ��ΤȤ���Ǥ��롣
# <OL>
# <LI>���ޥ�ɥ饤�󥪥ץ���� "-f"
# <LI>�Ķ��ѿ� "RTC_MANAGER_CONFIG"
# <LI>�ǥե��������ե����� "./rtc.conf"
# <LI>�ǥե��������ե����� "/etc/rtc.conf"
# <LI>�ǥե��������ե����� "/etc/rtc/rtc.conf"
# <LI>�ǥե��������ե����� "/usr/local/etc/rtc.conf"
# <LI>�ǥե��������ե����� "/usr/local/etc/rtc/rtc.conf"
# <LI>�����ߥ���ե�����졼�������
#</OL>
# �����������ޥ�ɥ饤�󥪥ץ���� "-d" �����ꤵ�줿���ϡ�
# (���Ȥ� -f ������ե��������ꤷ�Ƥ�)�����ߥ���ե�����졼�������
# �����Ѥ���롣
#
# @since 0.4.0
#
# @else
#
# @class ManagerConfig
# @brief Manager configuration class
#
# Modify Manager's configuration. 
# This class receives the command line arguments and will be instantiated.
# Set property information of Manager with the configuration file specified
# by the command line argument or the environment variable etc.
#
# The priorities of each configuration are as follows:
# <OL>
# <LI>Command option "-f"
# <LI>Environment variable "RTC_MANAGER_CONFIG"
# <LI>Default configuration file "./rtc.conf"
# <LI>Default configuration file "/etc/rtc.conf"
# <LI>Default configuration file "/etc/rtc/rtc.conf"
# <LI>Default configuration file "/usr/local/etc/rtc.conf"
# <LI>Default configuration file "/usr/local/etc/rtc/rtc.conf"
# <LI>Embedded configuration value
# </OL>
# If the command option "-d" is specified (even if specify configuration file
# by "-f" option), the embedded configuration values will be used.
#
# @since 0.4.0
#
# @endif
class ManagerConfig :
  """
  """
  ##
  # @if jp
  # @brief Manager ����ե�����졼�����Υǥե���ȡ��ե����롦�ѥ�
  # @else
  # @brief The default configuration file path for manager
  # @endif
  if os.name == 'nt':

    config_file_path = ["./rtc.conf",
                        "${APPDATA}/OpenRTM-aist/rtc.conf"]
  else:
    config_file_path = ["./rtc.conf",
                        "/etc/rtc.conf",
                        "/etc/rtc/rtc.conf",
                        "/usr/local/etc/rtc.conf",
                        "/usr/local/etc/rtc/rtc.conf"]


  ##
  # @if jp
  # @brief �ǥե���ȡ�����ե�����졼�����Υե����롦�ѥ����̤���
  #        �Ķ��ѿ�
  # @else
  # @brief The environment variable to distinguish the default configuration
  #        file path
  # @endif
  config_file_env = "RTC_MANAGER_CONFIG"


  ##
  # @if jp
  #
  # @brief ���󥹥ȥ饯��
  #
  # Ϳ����줿�����ˤ�ꥳ��ե�����졼��������ν������Ԥ���
  #
  # @param self
  # @param argv ���ޥ�ɥ饤�����(�ǥե������:None)
  #
  # @else
  #
  # @brief ManagerConfig constructor
  #
  # The constructor that performs initialization at the same time with
  # given arguments.
  #
  # @param argv The command line arguments
  #
  # @endif
  def __init__(self, argv=None):

    self._configFile = ""
    self._argprop = OpenRTM_aist.Properties()
    self._isMaster   = False
    self._ignoreNoConf = False
    if argv:
      self.init(argv)
    


  ##
  # @if jp
  #
  # @brief �����
  #
  # ���ޥ�ɥ饤������˱����ƽ������¹Ԥ��롣���ޥ�ɥ饤�󥪥ץ�����
  # �ʲ��Τ�Τ����Ѳ�ǽ�Ǥ��롣
  #
  # -a        : �ޥ͡����㥵���ӥ���OFF�ˤ��롣<br>
  # -f file   : ����ե�����졼�����ե��������ꤹ�롣<br>
  # -l module : ���ɤ���⥸�塼�����ꤹ�롣(̤����)<br>
  # -o options: ����¾���ץ�������ꤹ�롣<br>
  # -p        : �ݡ����ֹ����ꤹ�롣<br>
  # -d        : �ޥ������ޥ͡������ư���롣<br>
  #
  # @param self
  # @param argv ���ޥ�ɥ饤�����
  #
  # @else
  #
  # @brief Initialization
  #
  # Initialize with command line options. The following command options
  # are available.
  #
  # -a        : Disable Manager service<br>
  # -f file   : Specify a configuration file. <br>
  # -l module : Specify modules to be loaded at the beginning. <br>
  # -o options: Other options. <br>
  # -p        : Specify a port number. <br>
  # -d        : Run Master Manager. <br>
  #
  # @endif
  def init(self, argv):
    self.parseArgs(argv)
    return

  ##
  # @if jp
  # @brief Configuration ����� Property �����ꤹ��
  # 
  # Manager ��Configuration �������ꤵ�줿 Property �����ꤹ�롣
  #
  # @param self
  # @param prop Configuration �����о� Property
  # 
  # @else
  # @brief Specify the configuration information to the Property
  #
  # Configure to the properties specified by Manager's configuration
  #
  # @endif
  def configure(self, prop):
    prop.setDefaults(OpenRTM_aist.default_config)
    if self.findConfigFile():
      #try:
      with open(self._configFile,"r") as fd:
        prop.load(fd)
        fd.close()
      #except:
      #  print(OpenRTM_aist.Logger.print_exception())


    self.setSystemInformation(prop)
    if self._isMaster:
      prop.setProperty("manager.is_master","YES")

    # Properties from arguments are marged finally
    prop.mergeProperties(self._argprop)
    prop.setProperty("config_file", self._configFile)
    return prop


  #######
  # @if jp
  #
  # @brief ����ե�����졼�������������(̤����)
  #
  # ����ե�����졼������������롣init()�ƤӽФ����˸Ƥ֤ȡ�
  # ��Ū��������줿�ǥե���ȤΥ���ե�����졼�������֤���
  # init() �ƤӽФ���˸Ƥ֤ȡ����ޥ�ɥ饤��������Ķ��ѿ�����
  # ��Ť�����������줿����ե�����졼�������֤���
  #
  # @else
  #
  # @brief Get configuration value.
  #
  # This operation returns default configuration statically defined,
  # when before calling init() function. When after calling init() function,
  # this operation returns initialized configuration value according to
  # command option, environment value and so on.
  #
  # @endif
  #def getConfig(self):
  #pass


  ##
  # @if jp
  #
  # @brief ���ޥ�ɰ�����ѡ�������
  #
  # -a        : �ޥ͡����㥵���ӥ���OFF�ˤ��롣<br>
  # -f file   : ����ե�����졼�����ե��������ꤹ�롣<br>
  # -l module : ���ɤ���⥸�塼�����ꤹ�롣(̤����)<br>
  # -o options: ����¾���ץ�������ꤹ�롣<br>
  # -p        : �ݡ����ֹ����ꤹ�롣<br>
  # -d        : �ޥ������ޥ͡������ư���롣<br>
  #
  # @param self
  # @param argv ���ޥ�ɥ饤�����
  #
  # @else
  #
  # @brief Parse command arguments
  #
  # -a        : Disable Manager service<br>
  # -f file   : Specify a configuration file. <br>
  # -l module : Specify modules to be loaded at the beginning. <br>
  # -o options: Other options. <br>
  # -p        : Specify a port number. <br>
  # -d        : Run Master Manager. <br>
  #
  # @endif
  def parseArgs(self, argv):
    try:
      opts, args = getopt.getopt(argv[1:], "adif:o:p:")
    except getopt.GetoptError:
      print(OpenRTM_aist.Logger.print_exception())
      return

    for opt, arg in opts:
      if opt == "-a":
        self._argprop.setProperty("manager.corba_servant","NO")

      if opt == "-f":
        self._configFile = arg

      if opt == "-o":
        pos = arg.find(":")
        if pos > 0:
          key = arg[:pos]
          value = arg[pos+1:]
          #key = OpenRTM_aist.unescape(key)
          key = key.strip()
          #value = OpenRTM_aist.unescape(value)
          value = value.strip()
          self._argprop.setProperty(key,value)

      if opt == "-p":
        num = [-1]
        ret = OpenRTM_aist.stringTo(num, arg)
        if ret:
          arg_ = ":" + arg
          self._argprop.setProperty("corba.endpoints",arg_)

      if opt == "-d":
        self._isMaster = True
        
      if opt == "-i":
        self._ignoreNoConf = True
        

    return


  ##
  # @if jp
  #
  # @brief Configuration file �θ���
  #
  # Configuration file �򸡺��������ꤹ�롣
  # ���� Configuration file ������Ѥߤξ��ϡ��ե������¸�߳�ǧ��Ԥ���
  #
  # Configuration file ��ͥ����<br>
  # ���ޥ�ɥ��ץ��������Ķ��ѿ���ǥե���ȥե������ǥե��������
  #
  # �ǥե���ȶ������ץ����(-d): �ǥե���ȥե����뤬���äƤ�̵�뤷��
  #                               �ǥե���������Ȥ�
  #
  # @param self
  #
  # @return Configuration file �������
  #
  # @else
  #
  # @brief Find the configuration file
  #
  # Find the configuration file and configure it.
  # Confirm the file existence when the configuration file has 
  # already configured.
  #
  # The priority of the configuration file<br>
  # The command option��the environment variable��the default file��
  # the default configuration
  #
  # Default force option(-d): Ignore any default files and use the default 
  # configuration.
  #
  # @return Configuration file search result
  #
  # @endif
  def findConfigFile(self):
    if self._configFile != "":
      if not self.fileExist(self._configFile):
        #print(OpenRTM_aist.Logger.print_exception())
        print("Configuration file: " + self._configFile + " not found.")
        if not self._ignoreNoConf:
          sys.exit()
        return False
      return True

    env = os.getenv(self.config_file_env)
    if env:
      if self.fileExist(env):
        self._configFile = env
        return True

    for file_path in self.config_file_path:
      file_path = OpenRTM_aist.replaceEnv(file_path)
      if self.fileExist(file_path):
        self._configFile = file_path
        return True

    return False


  ##
  # @if jp
  #
  # @brief �����ƥ��������ꤹ��
  #
  # �����ƥ�����������ץ�ѥƥ��˥��åȤ��롣���ꤵ��륭���ϰʲ����̤ꡣ
  #  - os.name    : OS̾
  #  - os.release : OS��꡼��̾
  #  - os.version : OS�С������̾
  #  - os.arch    : OS�������ƥ�����
  #  - os.hostname: �ۥ���̾
  #  - manager.pid: �ץ���ID
  # 
  # @param self
  # @param prop �����ƥ��������ꤷ���ץ�ѥƥ�
  #
  # @else
  # 
  # @brief Set system information
  # 
  # Get the following system info and set them to Manager's properties.
  #  - os.name    : OS name
  #  - os.release : OS release name
  #  - os.version : OS version
  #  - os.arch    : OS architecture
  #  - os.hostname: Hostname
  #  - manager.pid: process ID
  #
  # @endif
  def setSystemInformation(self, prop):
    if os.name == 'nt':
      sysinfo = platform.uname()
    else:
      sysinfo = os.uname()

    prop.setProperty("os.name",     sysinfo[0])
    prop.setProperty("os.hostname", sysinfo[1])
    prop.setProperty("os.release",  sysinfo[2])
    prop.setProperty("os.version",  sysinfo[3])
    prop.setProperty("os.arch",     sysinfo[4])
    prop.setProperty("manager.pid", os.getpid())

    return prop


  ##
  # @if jp
  # @brief �ե������¸�߳�ǧ
  #
  # ���ꤵ�줿�ե����뤬¸�ߤ��뤫��ǧ���롣
  #
  # @param self
  # @param filename ��ǧ�оݥե�����̾��
  #
  # @return �оݥե������ǧ���(¸�ߤ������true)
  #
  # @else
  # @brief Check the file existence
  #
  # Confirm whether the specified file exists
  #
  # @param filename The target confirmation file
  #
  # @return file existance confirmation (True if the file exists.)
  #
  # @endif
  def fileExist(self, filename):
    try:
      fp = open(filename)
    except:
      return False
    else:
      fp.close()
      return True




