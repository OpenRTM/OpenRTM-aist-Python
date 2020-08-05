#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
# @file NamingManager.py
# @brief naming Service helper class
# @date $Date: 2007/08/27$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2006-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import threading



import OpenRTM_aist
from omniORB import CORBA
import RTM
import RTC
import CosNaming


##
# @if jp
#
# @class NamingBase
# @brief NamingService ��������ݥ��饹
#
# NamingServer ��������ݥ��󥿡��ե��������饹��
# ��ݴ������饹�ϡ��ʲ��δؿ��μ������󶡤��ʤ���Фʤ�ʤ���
# - bindObject() : ���ꤷ�����֥������Ȥ�NamingService�ؤΥХ����
# - unbindObject() : ���ꤷ�����֥������Ȥ�NamingService����Υ���Х����
#
# @since 0.4.0
#
# @else
#
# @endif
class NamingBase:
  """
  """

  ##
  # @if jp
  #
  # @brief NamingService�إХ���ɤ���ؿ�(���֥��饹������)
  #
  # ���ꤷ�����֥������Ȥ�NamingService�إХ���ɤ���<BR>
  # �����֥��饹�Ǥμ���������
  #
  # @param self
  # @param name �Х���ɻ���̾��
  # @param rtobj �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindObject(self, name, rtobj):
    pass

  def bindPortObject(self, name, port):
    pass

  ##
  # @if jp
  #
  # @brief NamingService���饢��Х���ɤ���ؿ�(���֥��饹������)
  #
  # ���ꤷ�����֥������Ȥ�NamingService���饢��Х���ɤ���<BR>
  # �����֥��饹�Ǥμ���������
  #
  # @param self
  # @param name ����Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def unbindObject(self, name):
    pass

  ##
  # @if jp
  #
  # @brief �͡��ॵ���Ф���¸���ǧ���롣
  # 
  # @return true:��¸���Ƥ���, false:��¸���Ƥ��ʤ�
  #
  # @else
  #
  # @brief Check if the name service is alive
  # 
  # @return true: alive, false:non not alive
  #
  # @endif
  #
  # virtual bool isAlive() = 0;
  def isAlive(self):
    return True

  ##
  # @if jp
  #
  # @brief rtcloc������RTC�Υ��֥������ȥ�ե���󥹤��������
  # 
  # @return RTC�Υ��֥������ȥ�ե����
  #
  # @else
  #
  # @brief 
  # 
  # @return 
  #
  # @endif
  #
  # virtual RTCList string_to_component(string name) = 0;
  def string_to_component(self, name):
    return []


##
# @if jp
#
# @class NamingOnCorba
# @brief CORBA �� NamingServer �������饹
#
# CORBA �� NamingServer �����ѥ��饹��
# CORBA ����ݡ��ͥ�Ȥ�NamingService�ؤ���Ͽ������ʤɤ�������롣
#
# @since 0.4.0
#
# @else
#
# @biref ModuleManager class
#
# @endif
class NamingOnCorba(NamingBase):
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
  # @param orb ORB
  # @param names NamingServer ̾��
  #
  # @else
  #
  # @endif
  def __init__(self, orb, names):
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf('manager.namingoncorba')
    self._cosnaming = OpenRTM_aist.CorbaNaming(orb,names)
    self._endpoint = ""
    self._replaceEndpoint = False

  ##
  # @if jp
  #
  # @brief ���ꤷ�� CORBA ���֥������Ȥ�NamingService�إХ����
  # 
  # ���ꤷ�� CORBA ���֥������Ȥ���ꤷ��̾�Τ� CORBA NamingService ��
  # �Х���ɤ��롣
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param rtobj or mgr �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindObject(self, name, rtobj):
    self._rtcout.RTC_TRACE("bindObject(name = %s, rtobj or mgr)", name)
    try:
      self._cosnaming.rebindByString(name, rtobj.getObjRef(), True)
    except:
      self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

    return


  ##
  # @if jp
  #
  # @brief ���ꤷ�� CORBA ���֥������Ȥ�NamingService�إХ����
  # 
  # ���ꤷ�� CORBA ���֥������Ȥ���ꤷ��̾�Τ� CORBA NamingService ��
  # �Х���ɤ��롣
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param port �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindPortObject(self, name, port):
    self._rtcout.RTC_TRACE("bindPortObject(name = %s, port)", name)
    try:
      self._cosnaming.rebindByString(name, port.getPortRef(), True)
    except:
      self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

    return


  ##
  # @if jp
  #
  # @brief ���ꤷ�� CORBA ���֥������Ȥ�NamingService���饢��Х����
  # 
  # ���ꤷ�� CORBA ���֥������Ȥ� CORBA NamingService ���饢��Х���ɤ��롣
  # 
  # @param self
  # @param name ����Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def unbindObject(self, name):
    self._rtcout.RTC_TRACE("unbindObject(name  = %s)", name)
    try:
      self._cosnaming.unbind(name)
    except:
      self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

    return


  ##
  # @if jp
  #
  # @brief �͡��ॵ���Ф���¸���ǧ���롣
  # 
  # @return true:��¸���Ƥ���, false:��¸���Ƥ��ʤ�
  #
  # @else
  #
  # @brief Check if the name service is alive
  # 
  # @return true: alive, false:non not alive
  #
  # @endif
  #
  # virtual bool isAlive();
  def isAlive(self):
    self._rtcout.RTC_TRACE("isAlive()")
    return self._cosnaming.isAlive()

  def getCorbaNaming(self):
    self._rtcout.RTC_TRACE("getCorbaNaming()")
    return self._cosnaming


  ##
  # @if jp
  #
  # @brief RTC�θ���
  #
  # �͡��ߥ󥰥����ӥ�����RTC�򥤥󥹥���̾���鸡������
  # ���פ���RTC�Υꥹ�Ȥ��������
  # 
  # @param self
  # @param context ���߸�����Υ���ƥ�����
  # @param name RTC�Υ��󥹥���̾
  # @param rtcs RTC�Υꥹ��
  #
  # @return
  #
  # @else
  #
  # @endif
  def getComponentByName(self, context, name, rtcs):
    length = 500
    bl,bi = context.list(length)
    for i in bl:
      if i.binding_type == CosNaming.ncontext:
        next_context = context.resolve(i.binding_name)
        self.getComponentByName(next_context, name, rtcs)
      elif i.binding_type == CosNaming.nobject:
        
        if i.binding_name[0].id == name and i.binding_name[0].kind == "rtc":
          try:
            cc = OpenRTM_aist.CorbaConsumer()
            cc.setObject(context.resolve(i.binding_name))
            obj = cc.getObject()._narrow(RTC.RTObject)
            if not obj._non_existent():
              rtcs.append(obj)
          except:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
    

  ##
  # @if jp
  #
  # @brief rtcname������RTC�Υ��֥������ȥ�ե���󥹤��������
  #
  # @param name RTC̾
  # @return RTC�Υ��֥������ȥ�ե���󥹤Υꥹ��
  #
  # @else
  #
  # @brief 
  # 
  # @return 
  #
  # @endif
  #
  # virtual RTCList string_to_component(string name) = 0;
  def string_to_component(self, name):
    rtc_list = []
    tmp = name.split("://")
    if len(tmp) > 1:
      if tmp[0] == "rtcname":
        #tag = tmp[0]
        url = tmp[1]
        r = url.split("/")
        if len(r) > 1:
          host = r[0]
          
          rtc_name = url[len(host)+1:]
          
          try:
            cns = None
            if host == "*":
              cns = self._cosnaming
            else:
              orb = OpenRTM_aist.Manager.instance().getORB()
              cns = OpenRTM_aist.CorbaNaming(orb,host)
            names = rtc_name.split("/")
            
            if len(names) == 2 and names[0] == "*":
              root_cxt = cns.getRootContext()
              self.getComponentByName(root_cxt, names[1], rtc_list)
              return rtc_list
            else:
              rtc_name += ".rtc"
              obj = cns.resolveStr(rtc_name)
              if CORBA.is_nil(obj):
                return []
              if obj._non_existent():
                return []
              rtc_list.append(obj)
              return rtc_list
          except:
            return []


      
    return rtc_list



##
# @if jp
#
# @class NamingOnManager
# @brief Manager �� NamingServer �������饹
#
#
# @since 1.2.0
#
# @else
#
# @biref 
#
# @endif
class NamingOnManager(NamingBase):
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
  # @param orb ORB
  # @param mgr �ޥ͡�����
  #
  # @else
  #
  # @param self
  # @param orb ORB
  # @param mgr 
  #
  # @endif
  def __init__(self, orb, mgr):
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf('manager.namingonmanager')
    self._cosnaming = None
    self._orb = orb
    self._mgr = mgr
    

  ##
  # @if jp
  #
  # @brief 
  # 
  # 
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param rtobj or mgr �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindObject(self, name, rtobj):
    self._rtcout.RTC_TRACE("bindObject(name = %s, rtobj or mgr)", name)
    """print(isinstance(rtobj, OpenRTM.ManagerServant))
    if isinstance(rtobj, OpenRTM.ManagerServant):
      
      self.manager = rtobj"""
    return


  ##
  # @if jp
  #
  # @brief 
  # 
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param port �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindPortObject(self, name, port):
    self._rtcout.RTC_TRACE("bindPortObject(name = %s, port)", name)
    
    return


  ##
  # @if jp
  #
  # @brief 
  # 
  # 
  # @param self
  # @param name ����Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def unbindObject(self, name):
    self._rtcout.RTC_TRACE("unbindObject(name  = %s)", name)
    
    return


  ##
  # @if jp
  #
  # @brief 
  # 
  # @return true:��¸���Ƥ���, false:��¸���Ƥ��ʤ�
  #
  # @else
  #
  # @brief Check if the name service is alive
  # 
  # @return true: alive, false:non not alive
  #
  # @endif
  #
  # virtual bool isAlive();
  def isAlive(self):
    self._rtcout.RTC_TRACE("isAlive()")
    return True

  ##
  # @if jp
  #
  # @brief rtcloc������RTC�Υ��֥������ȥ�ե���󥹤��������
  #
  # @param name rtcloc�����Ǥ�RTC̾
  # rtcloc://localhost:2809/example/ConsoleIn
  # @return RTC�Υ��֥������ȥ�ե���󥹤Υꥹ��
  #
  # @else
  #
  # @brief 
  # 
  # @return 
  #
  # @endif
  #
  # virtual RTCList string_to_component();
  def string_to_component(self, name):
    rtc_list = []
    tmp = name.split("://")
    
    if len(tmp) > 1:
      if tmp[0] == "rtcloc":
        #tag = tmp[0]
        url = tmp[1]
        r = url.split("/")
        if len(r) > 1:
          host = r[0]
          rtc_name = url[len(host)+1:]
          
          mgr = self.getManager(host)
          if not CORBA.is_nil(mgr):
            rtc_list = mgr.get_components_by_name(rtc_name)

            slaves = mgr.get_slave_managers()
            for slave in slaves:
              try:
                rtc_list.extend(slave.get_components_by_name(rtc_name))
              except:
                self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
                mgr.remove_slave_manager(slave)

          return rtc_list
    return rtc_list

  ##
  # @if jp
  #
  # @brief ����ۥ���̾���ݡ���̾��Manager�Υ��֥������ȥ�ե���󥹤����
  #
  # @param name �ۥ���̾���ݡ���̾
  # 
  # @return Manager�Υ��֥������ȥ�ե����
  #
  # @else
  #
  # @brief 
  # 
  # @return 
  #
  # @endif
  #
  # virtual Manager_ptr getManager(string name);
  def getManager(self, name):
    if name == "*":
      mgr_sev = self._mgr.getManagerServant()
      mgr = None
      if mgr_sev.is_master():
        mgr = mgr_sev.getObjRef()
      else:
        masters = mgr_sev.get_master_managers()
        if len(masters) > 0:
          mgr = masters[0]
        else:
          mgr = mgr_sev.getObjRef()
      return mgr
    try:
      mgrloc = "corbaloc:iiop:"
      prop = self._mgr.getConfig()
      manager_name = prop.getProperty("manager.name")
      mgrloc += name
      mgrloc += "/" + manager_name
      
      mobj = self._orb.string_to_object(mgrloc)
      mgr = mobj._narrow(RTM.Manager)
      
      self._rtcout.RTC_DEBUG("corbaloc: %s", mgrloc)
      return mgr
    except CORBA.SystemException:
      self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
    except:
      self._rtcout.RTC_ERROR("Unknown exception cought.")
      self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
    return RTM.Manager._nil
        


##
# @if jp
#
# @class NamingManager
# @brief NamingServer �������饹
#
# NamingServer �����ѥ��饹��
# ����ݡ��ͥ�Ȥ�NamingService�ؤ���Ͽ������ʤɤ�������롣
#
# @since 0.4.0
#
# @else
#
# @biref ModuleManager class
#
# @endif
class NamingManager:
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
  # @param manager �ޥ͡����㥪�֥�������
  #
  # @else
  #
  # @endif
  def __init__(self, manager):
    self._manager = manager
    self._rtcout = manager.getLogbuf('manager.namingmanager')
    #self._rtcout.setLogLevel(manager.getConfig().getProperty("logger.log_level"))
    #self._rtcout.setLogLock(OpenRTM_aist.toBool(manager.getConfig().getProperty("logger.stream_lock"), "enable", "disable", False))
    self._names = []
    self._namesMutex = threading.RLock()
    self._compNames = []
    self._mgrNames  = []
    self._portNames = []
    self._compNamesMutex = threading.RLock()
    self._mgrNamesMutex = threading.RLock()
    self._portNamesMutex = threading.RLock()


  ##
  # @if jp
  #
  # @brief NameServer ����Ͽ
  #
  # ���ꤷ�������� NameServer ����Ͽ���롣
  # CORBA��Manager�������ǽ
  #
  # @param self
  # @param method NamingService �η���
  # @param name_server ��Ͽ���� NameServer ��̾��
  #
  # @else
  #
  # @endif
  def registerNameServer(self, method, name_server):
    self._rtcout.RTC_TRACE("NamingManager::registerNameServer(%s, %s)",
                           (method, name_server))
    name = self.createNamingObj(method, name_server)
    self._names.append(self.NameServer(method, name_server, name))
    

  ##
  # @if jp
  #
  # @brief ���ꤷ�����֥������Ȥ�NamingService�إХ����
  # 
  # ���ꤷ�����֥������Ȥ���ꤷ��̾�Τ� CORBA NamingService �إХ���ɤ��롣
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param rtobj �Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def bindObject(self, name, rtobj):
    self._rtcout.RTC_TRACE("NamingManager::bindObject(%s)", name)
    guard = OpenRTM_aist.ScopedLock(self._namesMutex)
    for i in range(len(self._names)):
      if self._names[i].ns:
        try:
          self._names[i].ns.bindObject(name, rtobj)
        except:
          del self._names[i].ns
          self._names[i].ns = 0

    self.registerCompName(name, rtobj)


  def bindManagerObject(self, name, mgr):
    self._rtcout.RTC_TRACE("NamingManager::bindManagerObject(%s)", name)
    guard = OpenRTM_aist.ScopedLock(self._namesMutex)
    for i in range(len(self._names)):
      if self._names[i].ns:
        try:
          self._names[i].ns.bindObject(name, mgr)
        except:
          del self._names[i].ns
          self._names[i].ns = 0

    self.registerMgrName(name, mgr)

  ##
  # @if jp
  #
  # @brief ���ꤷ���ݡ��Ȥ�NamingService�إХ����
  # 
  # @param self
  # @param name �Х���ɻ���̾��
  # @param port �Х�����оݤΥݡ���
  #
  # @else
  #
  # @param self
  # @param name 
  # @param port 
  #
  # @endif
  # void bindPortObject(const char* name, PortBase* port)
  def bindPortObject(self, name, port):
    self._rtcout.RTC_TRACE("NamingManager::bindPortObject(%s)", name)
    guard = OpenRTM_aist.ScopedLock(self._namesMutex)
    for i in range(len(self._names)):
      if self._names[i].ns:
        try:
          self._names[i].ns.bindPortObject(name, port)
        except:
          del self._names[i].ns
          self._names[i].ns = 0
    self.registerPortName(name, port)


  ##
  # @if jp
  #
  # @brief NamingServer �ξ���ι���
  # 
  # ���ꤵ��Ƥ��� NameServer �����Ͽ����Ƥ��륪�֥������Ȥξ����
  # �������롣
  # 
  # @param self
  # 
  # @else
  #
  # @endif
  def update(self):
    self._rtcout.RTC_TRACE("NamingManager::update()")
    guard = OpenRTM_aist.ScopedLock(self._namesMutex)
    rebind = OpenRTM_aist.toBool(self._manager.getConfig().getProperty("naming.update.rebind"),
                                 "YES","NO",False)
    for i in range(len(self._names)):
      if self._names[i].ns is None:
        self._rtcout.RTC_DEBUG("Retrying connection to %s/%s",
                               (self._names[i].method,
                                self._names[i].nsname))
        self.retryConnection(self._names[i])

      else:
        try:
          if rebind:
            self.bindCompsTo(self._names[i].ns)
          if not self._names[i].ns.isAlive():
            self._rtcout.RTC_INFO("Name server: %s (%s) disappeared.",
                                  (self._names[i].nsname,
                                   self._names[i].method))
            del self._names[i].ns
            self._names[i].ns = None
        except:
          self._rtcout.RTC_INFO("Name server: %s (%s) disappeared.",
                                (self._names[i].nsname,
                                 self._names[i].method))
          del self._names[i].ns
          self._names[i].ns = None


    return


  ##
  # @if jp
  #
  # @brief ���ꤷ�����֥������Ȥ�NamingService���饢��Х����
  # 
  # ���ꤷ�����֥������Ȥ� NamingService ���饢��Х���ɤ��롣
  # 
  # @param self
  # @param name ����Х�����оݥ��֥�������
  #
  # @else
  #
  # @endif
  def unbindObject(self, name):
    self._rtcout.RTC_TRACE("NamingManager::unbindObject(%s)", name)
    guard = OpenRTM_aist.ScopedLock(self._namesMutex)
    for i in range(len(self._names)):
      if self._names[i].ns:
        self._names[i].ns.unbindObject(name)
    self.unregisterCompName(name)
    self.unregisterMgrName(name)
    self.unregisterPortName(name)


  ##
  # @if jp
  #
  # @brief ���ƤΥ��֥������Ȥ�NamingService���饢��Х����
  # 
  # ���ƤΥ��֥������Ȥ� CORBA NamingService ���饢��Х���ɤ��롣
  # 
  # @param self
  # 
  # @else
  #
  # @endif
  def unbindAll(self):
    self._rtcout.RTC_TRACE("NamingManager::unbindAll(): %d names.", len(self._compNames))

    guard = OpenRTM_aist.ScopedLock(self._compNamesMutex)
    len_ = len(self._compNames)
    
    for i in range(len_):
      idx = (len_ - 1) - i
      self.unbindObject(self._compNames[idx].name)

    guard = OpenRTM_aist.ScopedLock(self._mgrNamesMutex)
    len_ = len(self._mgrNames)
    for i in range(len_):
      idx = (len_ - 1) - i
      self.unbindObject(self._mgrNames[idx].name)


    guard = OpenRTM_aist.ScopedLock(self._portNamesMutex)
    len_ = len(self._portNames)
    for i in range(len_):
      idx = (len_ - 1) - i
      self.unbindObject(self._portNames[idx].name)


  ##
  # @if jp
  #
  # @brief �Х���ɤ���Ƥ������ƤΥ��֥������Ȥ����
  # 
  # �Х���ɤ���Ƥ������ƤΥ��֥������Ȥ� �������롣
  # 
  # @param self
  #
  # @return �Х���ɺѤߥ��֥������� �ꥹ��
  # 
  # @else
  #
  # @endif
  def getObjects(self):
    comps = []
    guard = OpenRTM_aist.ScopedLock(self._compNamesMutex)
    for i in range(len(self._compNames)):
      comps.append(self._compNames[i].rtobj)
    return comps


  ##
  # @if jp
  #
  # @brief NameServer �����ѥ��֥������Ȥ�����
  # 
  # ���ꤷ������NameServer �����ѥ��֥������Ȥ��������롣
  #
  # @param self
  # @param method NamingService ����
  # @param name_server NameServer ̾��
  # 
  # @return �������� NameServer ���֥�������
  # 
  # @else
  #
  # @endif
  def createNamingObj(self, method, name_server):
    self._rtcout.RTC_TRACE("createNamingObj(method = %s, nameserver = %s)",
                           (method, name_server))
    mth = method
    if mth == "corba":
      try:
        name = OpenRTM_aist.NamingOnCorba(self._manager.getORB(),name_server)
        
        self._rtcout.RTC_INFO("NameServer connection succeeded: %s/%s",
                              (method, name_server))
        return name
      except:
        self._rtcout.RTC_INFO("NameServer connection failed: %s/%s",
                              (method, name_server))
        return None


    elif mth == "manager":
      name = OpenRTM_aist.NamingOnManager(self._manager.getORB(), self._manager)
      return name
    return None


  ##
  # @if jp
  #
  # @brief ����Ѥߥ���ݡ��ͥ�Ȥ� NameServer ����Ͽ
  # 
  # ����Ѥߥ���ݡ��ͥ�Ȥ���ꤷ�� NameServer ����Ͽ���롣
  #
  # @param self
  # @param ns ��Ͽ�о� NameServer
  # 
  # @else
  #
  # @endif
  def bindCompsTo(self, ns):
    for i in range(len(self._compNames)):
      ns.bindObject(self._compNames[i].name, self._compNames[i].rtobj)


  ##
  # @if jp
  #
  # @brief NameServer ����Ͽ���륳��ݡ��ͥ�Ȥ�����
  # 
  # NameServer ����Ͽ���륳��ݡ��ͥ�Ȥ����ꤹ�롣
  #
  # @param self
  # @param name ����ݡ��ͥ�Ȥ���Ͽ��̾��
  # @param rtobj ��Ͽ�оݥ��֥�������
  # 
  # @else
  #
  # @endif
  def registerCompName(self, name, rtobj):
    for i in range(len(self._compNames)):
      if self._compNames[i].name == name:
        self._compNames[i].rtobj = rtobj
        return

    self._compNames.append(self.Comps(name, rtobj))
    return


  def registerMgrName(self, name, mgr):
    for i in range(len(self._mgrNames)):
      if self._mgrNames[i].name == name:
        self._mgrNames[i].mgr = mgr
        return

    self._mgrNames.append(self.Mgr(name, mgr))
    return

  ##
  # @if jp
  #
  # @brief NameServer ����Ͽ����ݡ��Ȥ�����
  # 
  #
  # @param self
  # @param name �ݡ��Ȥ���Ͽ��̾��
  # @param port ��Ͽ�оݥ��֥�������
  # 
  # @else
  # @param self
  # @param name 
  # @param port 
  #
  # @endif
  def registerPortName(self, name, port):
    for i in range(len(self._portNames)):
      if self._portNames[i].name == name:
        self._portNames[i].port = port
        return

    self._portNames.append(self.Port(name, port))
    return
  
  ##
  # @if jp
  #
  # @brief NameServer ����Ͽ���륳��ݡ��ͥ�Ȥ�������
  # 
  # NameServer ����Ͽ���륳��ݡ��ͥ�Ȥ�����������롣
  #
  # @param self
  # @param name �������оݥ���ݡ��ͥ�Ȥ�̾��
  # 
  # @else
  #
  # @endif
  def unregisterCompName(self, name):
    len_ = len(self._compNames)
    for i in range(len_):
      idx = (len_-1) - i
      if self._compNames[idx].name == name:
        del self._compNames[idx]
        return
    return
    

  def unregisterMgrName(self, name):
    len_ = len(self._mgrNames)
    for i in range(len_):
      idx = (len_ -1) - i
      if self._mgrNames[idx].name == name:
        del self._mgrNames[idx]
        return
    return


  ##
  # @if jp
  #
  # @brief NameServer ����Ͽ����ݡ��Ȥ�������
  # 
  #
  # @param self
  # @param name �������оݥݡ��Ȥ�̾��
  # 
  # @else
  #
  # @param self
  # @param name
  #
  # @endif
  def unregisterPortName(self, name):
    len_ = len(self._portNames)
    for i in range(len_):
      idx = (len_ -1) - i
      if self._portNames[idx].name == name:
        del self._portNames[idx]
        return
    return


  ##
  # @if jp
  #
  # @brief ����ݥͥ�Ȥ��Х���ɤ���
  # 
  # �͡��ॵ���Ф���³���ƥ���ݥͥ�Ȥ��Х���ɤ��롣
  #
  # @param ns NameServer
  # 
  # @else
  #
  # @brief Rebind the component to NameServer
  # 
  # Connect with the NameServer and rebind the component. 
  #
  # @param ns NameServer
  # 
  # @endif
  #
  # void retryConnection(Names* ns);
  def retryConnection(self, ns):
    # recreate NamingObj
    nsobj = 0
    try:
      nsobj = self.createNamingObj(ns.method, ns.nsname)
      if nsobj is not None: # if succeed
        self._rtcout.RTC_INFO("Connected to a name server: %s/%s",
                              (ns.method, ns.nsname))
        ns.ns = nsobj
        self.bindCompsTo(nsobj) # rebind all comps to new NS
        return
      else:
        self._rtcout.RTC_DEBUG("Name service: %s/%s still not available.",
                               (ns.method, ns.nsname))

    except:
      self._rtcout.RTC_DEBUG("Name server: %s/%s disappeared again.",
                             (ns.method, ns.nsname))
      if nsobj is not None:
        del ns.ns
        ns.ns = 0

    return


  ##
  # @if jp
  #
  # @brief ��Ͽ�����͡��ॵ���ӥ��Υꥹ�Ȥ��������
  # 
  # @return �͡��ॵ���ӥ��Υꥹ��
  # 
  # @else
  #
  # @brief 
  # 
  # @return
  # 
  # @endif
  #
  # std::vector<NamingService*>& getNameServices();
  def getNameServices(self):
    return self._names

  ##
  # @if jp
  #
  # @brief rtcloc������RTC�Υ��֥������ȥ�ե���󥹤����
  #
  # @param name rtcloc�����Ǥ�RTC̾
  # rtcloc://localhost:2809/example/ConsoleIn
  # @return RTC�Υ��֥������ȥ�ե���󥹤Υꥹ��
  # 
  # @else
  #
  # @brief 
  # 
  # @return
  # 
  # @endif
  #
  # RTCList string_to_component(string name);
  def string_to_component(self, name):
    for n in self._names:
      if n.ns:
        comps = n.ns.string_to_component(name)
        if len(comps) > 0:
          return comps
    return []

  # Name Servers' method/name and object
  ##
  # @if jp
  # @class NameServer
  # @brief NameServer �����ѥ��饹
  # @else
  #
  # @endif
  class NameServer:
    def __init__(self, meth, name, naming):
      self.method = meth
      self.nsname = name
      self.ns     = naming


  # Components' name and object
  ##
  # @if jp
  # @class Comps
  # @brief ����ݡ��ͥ�ȴ����ѥ��饹
  # @else
  #
  # @endif
  class Comps:
    def __init__(self, n, obj):
      self.name = n
      self.rtobj = obj


  class Mgr:
    def __init__(self, n, obj):
      self.name = n
      self.mgr = obj


  ##
  # @if jp
  # @class Port
  # @brief �ݡ��ȴ����ѥ��饹
  # @else
  #
  # @endif
  class Port:
    def __init__(self, n, obj):
      self.name = n
      self.port = obj
