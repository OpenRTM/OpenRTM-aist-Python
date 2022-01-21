#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
import OpenRTM_aist.CORBA_RTCUtil
from omniORB import CORBA
import RTM
import RTC
import CosNaming


##
# @if jp
#
# @class NamingBase
# @brief NamingService 管理用抽象クラス
#
# NamingServer 管理用抽象インターフェースクラス。
# 具象管理クラスは、以下の関数の実装を提供しなければならない。
# - bindObject() : 指定したオブジェクトのNamingServiceへのバインド
# - unbindObject() : 指定したオブジェクトのNamingServiceからのアンバインド
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
    # @brief NamingServiceへバインドする関数(サブクラス実装用)
    #
    # 指定したオブジェクトをNamingServiceへバインドする<BR>
    # ※サブクラスでの実装参照用
    #
    # @param self
    # @param name バインド時の名称
    # @param rtobj バインド対象オブジェクト
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
    # @brief NamingServiceからアンバインドする関数(サブクラス実装用)
    #
    # 指定したオブジェクトをNamingServiceからアンバインドする<BR>
    # ※サブクラスでの実装参照用
    #
    # @param self
    # @param name アンバインド対象オブジェクト
    #
    # @else
    #
    # @endif
    def unbindObject(self, name):
        pass

    ##
    # @if jp
    #
    # @brief ネームサーバの生存を確認する。
    #
    # @return true:生存している, false:生存していない
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
    # @brief rtcloc形式でRTCのオブジェクトリファレンスを取得する
    #
    # @return RTCのオブジェクトリファレンス
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
# @brief CORBA 用 NamingServer 管理クラス
#
# CORBA 用 NamingServer 管理用クラス。
# CORBA コンポーネントのNamingServiceへの登録、解除などを管理する。
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
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param orb ORB
    # @param names NamingServer 名称
    #
    # @else
    #
    # @endif
    def __init__(self, orb, names):
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf('manager.namingoncorba')
        self._cosnaming = OpenRTM_aist.CorbaNaming(orb, names)
        self._endpoint = ""
        self._replaceEndpoint = False

    ##
    # @if jp
    #
    # @brief 指定した CORBA オブジェクトのNamingServiceへバインド
    #
    # 指定した CORBA オブジェクトを指定した名称で CORBA NamingService へ
    # バインドする。
    #
    # @param self
    # @param name バインド時の名称
    # @param rtobj or mgr バインド対象オブジェクト
    #
    # @else
    #
    # @endif
    def bindObject(self, name, rtobj):
        self._rtcout.RTC_TRACE("bindObject(name = %s, rtobj or mgr)", name)
        try:
            self._cosnaming.rebindByString(name, rtobj.getObjRef(), True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        return

    ##
    # @if jp
    #
    # @brief 指定した CORBA オブジェクトのNamingServiceへバインド
    #
    # 指定した CORBA オブジェクトを指定した名称で CORBA NamingService へ
    # バインドする。
    #
    # @param self
    # @param name バインド時の名称
    # @param port バインド対象オブジェクト
    #
    # @else
    #
    # @endif

    def bindPortObject(self, name, port):
        self._rtcout.RTC_TRACE("bindPortObject(name = %s, port)", name)
        try:
            self._cosnaming.rebindByString(name, port.getPortRef(), True)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        return

    ##
    # @if jp
    #
    # @brief 指定した CORBA オブジェクトをNamingServiceからアンバインド
    #
    # 指定した CORBA オブジェクトを CORBA NamingService からアンバインドする。
    #
    # @param self
    # @param name アンバインド対象オブジェクト
    #
    # @else
    #
    # @endif

    def unbindObject(self, name):
        self._rtcout.RTC_TRACE("unbindObject(name  = %s)", name)
        try:
            self._cosnaming.unbind(name)
        except BaseException:
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())

        return

    ##
    # @if jp
    #
    # @brief ネームサーバの生存を確認する。
    #
    # @return true:生存している, false:生存していない
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
    # @brief RTCの検索
    #
    # ネーミングサービスからRTCをインスタンス名から検索し、
    # 一致するRTCのリストを取得する
    #
    # @param self
    # @param context 現在検索中のコンテキスト
    # @param name RTCのインスタンス名
    # @param rtcs RTCのリスト
    #
    # @return
    #
    # @else
    #
    # @endif

    def getComponentByName(self, context, name, rtcs):
        self._rtcout.RTC_TRACE("getComponentByName(name  = %s)", name)
        length = 500
        bl, bi = context.list(length)
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
                    except BaseException:
                        self._rtcout.RTC_ERROR(
                            OpenRTM_aist.Logger.print_exception())

    ##
    # @if jp
    #
    # @brief rtcname形式でRTCのオブジェクトリファレンスを取得する
    #
    # @param name RTC名
    # @return RTCのオブジェクトリファレンスのリスト
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
        self._rtcout.RTC_TRACE("string_to_component(name  = %s)", name)
        rtc_list = []

        rtcuri = OpenRTM_aist.CORBA_RTCUtil.RTCURIObject(name, True, False)

        if not rtcuri.isRTCNameURI():
            self._rtcout.RTC_WARN("syntax error: %s", name)
            return rtc_list
        else:
            self._rtcout.RTC_INFO("URI: %s, Address: %s, Name: %s",
                                  (name, rtcuri.getAddress(),
                                   rtcuri.getRTCName()))
            try:
                cns = None
                if rtcuri.getAddress() == "*":
                    cns = self._cosnaming
                else:
                    orb = OpenRTM_aist.Manager.instance().getORB()
                    cns = OpenRTM_aist.CorbaNaming(orb, rtcuri.getAddress())

                rtcname = rtcuri.getRTCName()
                context = ""
                compname = ""

                pos = rtcname.find("/")
                if pos >= 0:
                    context = rtcname[0:pos]
                    compname = rtcname[pos + 1:]

                if context == "*":
                    root_cxt = cns.getRootContext()
                    self.getComponentByName(
                        root_cxt, compname, rtc_list)
                    return rtc_list
                else:
                    rtcname += ".rtc"
                    obj = cns.resolveStr(rtcname)
                    if CORBA.is_nil(obj):
                        return rtc_list
                    if obj._non_existent():
                        return rtc_list
                    rtc_list.append(obj)
                    return rtc_list
            except BaseException:
                return rtc_list

        return rtc_list


##
# @if jp
#
# @class NamingOnManager
# @brief Manager 用 NamingServer 管理クラス
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
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param orb ORB
    # @param mgr マネージャ
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
    # @param name バインド時の名称
    # @param rtobj or mgr バインド対象オブジェクト
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
    # @param name バインド時の名称
    # @param port バインド対象オブジェクト
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
    # @param name アンバインド対象オブジェクト
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
    # @return true:生存している, false:生存していない
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
    # @brief rtcloc形式でRTCのオブジェクトリファレンスを取得する
    #
    # @param name rtcloc形式でのRTC名
    # rtcloc://localhost:2809/example/ConsoleIn
    # @return RTCのオブジェクトリファレンスのリスト
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
        self._rtcout.RTC_TRACE("string_to_component(name  = %s)", name)
        rtc_list = []

        rtcuri = OpenRTM_aist.CORBA_RTCUtil.RTCURIObject(name, False, True)

        if not rtcuri.isRTCLocURI():
            self._rtcout.RTC_WARN("syntax error: %s", name)
            return rtc_list
        else:
            self._rtcout.RTC_INFO("URI: %s, Address: %s, Name: %s",
                                  (name, rtcuri.getAddress(),
                                   rtcuri.getRTCName()))

            mgr = self.getManager(rtcuri.getAddress())
            if not CORBA.is_nil(mgr):
                rtc_list = mgr.get_components_by_name(rtcuri.getRTCName())
                slaves = mgr.get_slave_managers()
                for slave in slaves:
                    try:
                        rtc_list.extend(
                            slave.get_components_by_name(rtcuri.getRTCName()))
                    except BaseException:
                        self._rtcout.RTC_DEBUG(
                            OpenRTM_aist.Logger.print_exception())
                        mgr.remove_slave_manager(slave)
                return rtc_list
        return rtc_list

    ##
    # @if jp
    #
    # @brief 指定ホスト名、ポート名でManagerのオブジェクトリファレンスを取得
    #
    # @param name ホスト名、ポート名
    #
    # @return Managerのオブジェクトリファレンス
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
        self._rtcout.RTC_TRACE("getManager(name = %s)", name)
        if name == "*":
            mgr_sev = self._mgr.getManagerServant()
            mgr = None
            if mgr_sev.is_master():
                mgr = mgr_sev.getObjRef()
            else:
                masters = mgr_sev.get_master_managers()
                if masters:
                    mgr = masters[0]
                else:
                    mgr = mgr_sev.getObjRef()
            return mgr
        try:
            prop = self._mgr.getConfig()
            manager_name = prop.getProperty("manager.name")
            mgrloc = OpenRTM_aist.CORBA_RTCUtil.CorbaURI(name, manager_name).toString()

            mobj = self._orb.string_to_object(mgrloc)
            mgr = mobj._narrow(RTM.Manager)

            self._rtcout.RTC_DEBUG("corbaloc: %s", mgrloc)
            return mgr
        except CORBA.SystemException:
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
        except BaseException:
            self._rtcout.RTC_ERROR("Unknown exception cought.")
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
        return RTM.Manager._nil


##
# @if jp
#
# @class NamingManager
# @brief NamingServer 管理クラス
#
# NamingServer 管理用クラス。
# コンポーネントのNamingServiceへの登録、解除などを管理する。
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
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param manager マネージャオブジェクト
    #
    # @else
    #
    # @endif
    def __init__(self, manager):
        self._manager = manager
        self._rtcout = manager.getLogbuf('manager.namingmanager')
        # self._rtcout.setLogLevel(manager.getConfig().getProperty("logger.log_level"))
        #self._rtcout.setLogLock(OpenRTM_aist.toBool(manager.getConfig().getProperty("logger.stream_lock"), "enable", "disable", False))
        self._names = []
        self._namesMutex = threading.RLock()
        self._compNames = []
        self._mgrNames = []
        self._portNames = []
        self._compNamesMutex = threading.RLock()
        self._mgrNamesMutex = threading.RLock()
        self._portNamesMutex = threading.RLock()

    ##
    # @if jp
    #
    # @brief NameServer の登録
    #
    # 指定した形式の NameServer を登録する。
    # CORBAとManagerが指定可能
    #
    # @param self
    # @param method NamingService の形式
    # @param name_server 登録する NameServer の名称
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
    # @brief 指定したオブジェクトのNamingServiceへバインド
    #
    # 指定したオブジェクトを指定した名称で CORBA NamingService へバインドする。
    #
    # @param self
    # @param name バインド時の名称
    # @param rtobj バインド対象オブジェクト
    #
    # @else
    #
    # @endif

    def bindObject(self, name, rtobj):
        self._rtcout.RTC_TRACE("NamingManager::bindObject(%s)", name)
        guard = OpenRTM_aist.ScopedLock(self._namesMutex)
        for n in self._names:
            if n.ns:
                try:
                    n.ns.bindObject(name, rtobj)
                except BaseException:
                    del n.ns
                    n.ns = None

        self.registerCompName(name, rtobj)

    def bindManagerObject(self, name, mgr):
        self._rtcout.RTC_TRACE("NamingManager::bindManagerObject(%s)", name)
        guard = OpenRTM_aist.ScopedLock(self._namesMutex)
        for n in self._names:
            if n.ns:
                try:
                    n.ns.bindObject(name, mgr)
                except BaseException:
                    del n.ns
                    n.ns = None

        self.registerMgrName(name, mgr)

    ##
    # @if jp
    #
    # @brief 指定したポートのNamingServiceへバインド
    #
    # @param self
    # @param name バインド時の名称
    # @param port バインド対象のポート
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
        for n in self._names:
            if n.ns:
                try:
                    n.ns.bindPortObject(name, port)
                except BaseException:
                    del n.ns
                    n.ns = None
        self.registerPortName(name, port)

    ##
    # @if jp
    #
    # @brief NamingServer の情報の更新
    #
    # 設定されている NameServer 内に登録されているオブジェクトの情報を
    # 更新する。
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
                                     "YES", "NO", False)
        for i, name in enumerate(self._names):
            if name.ns is None:
                self._rtcout.RTC_DEBUG("Retrying connection to %s/%s",
                                       (name.method,
                                        name.nsname))
                self.retryConnection(name)

            else:
                try:
                    if rebind:
                        self.bindCompsTo(name.ns)
                    if not name.ns.isAlive():
                        self._rtcout.RTC_INFO("Name server: %s (%s) disappeared.",
                                              (name.nsname,
                                               name.method))
                        del name.ns
                        name.ns = None
                except BaseException:
                    self._rtcout.RTC_INFO("Name server: %s (%s) disappeared.",
                                          (name.nsname,
                                           name.method))
                    del name.ns
                    name.ns = None

        return

    ##
    # @if jp
    #
    # @brief 指定したオブジェクトをNamingServiceからアンバインド
    #
    # 指定したオブジェクトを NamingService からアンバインドする。
    #
    # @param self
    # @param name アンバインド対象オブジェクト
    #
    # @else
    #
    # @endif

    def unbindObject(self, name):
        self._rtcout.RTC_TRACE("NamingManager::unbindObject(%s)", name)
        guard = OpenRTM_aist.ScopedLock(self._namesMutex)
        for n in self._names:
            if n.ns:
                try:
                    n.ns.unbindObject(name)
                except BaseException:
                    del n.ns
                    n.ns = None


        self.unregisterCompName(name)
        self.unregisterMgrName(name)
        self.unregisterPortName(name)

    ##
    # @if jp
    #
    # @brief 全てのオブジェクトをNamingServiceからアンバインド
    #
    # 全てのオブジェクトを CORBA NamingService からアンバインドする。
    #
    # @param self
    #
    # @else
    #
    # @endif

    def unbindAll(self):
        self._rtcout.RTC_TRACE(
            "NamingManager::unbindAll(): %d names.", len(
                self._compNames))

        guard = OpenRTM_aist.ScopedLock(self._compNamesMutex)

        for comp in self._compNames[::-1]:
            self.unbindObject(comp.name)

        guard = OpenRTM_aist.ScopedLock(self._mgrNamesMutex)

        for mgr in self._mgrNames[::-1]:
            self.unbindObject(mgr.name)

        guard = OpenRTM_aist.ScopedLock(self._portNamesMutex)

        for port in self._portNames[::-1]:
            self.unbindObject(port.name)

    ##
    # @if jp
    #
    # @brief バインドされている全てのオブジェクトを取得
    #
    # バインドされている全てのオブジェクトを 取得する。
    #
    # @param self
    #
    # @return バインド済みオブジェクト リスト
    #
    # @else
    #
    # @endif

    def getObjects(self):
        comps = []
        guard = OpenRTM_aist.ScopedLock(self._compNamesMutex)
        for comp in self._compNames:
            comps.append(comp.rtobj)
        return comps

    ##
    # @if jp
    #
    # @brief NameServer 管理用オブジェクトの生成
    #
    # 指定した型のNameServer 管理用オブジェクトを生成する。
    #
    # @param self
    # @param method NamingService 形式
    # @param name_server NameServer 名称
    #
    # @return 生成した NameServer オブジェクト
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
                name = OpenRTM_aist.NamingOnCorba(
                    self._manager.getORB(), name_server)

                self._rtcout.RTC_INFO("NameServer connection succeeded: %s/%s",
                                      (method, name_server))
                return name
            except BaseException:
                self._rtcout.RTC_INFO("NameServer connection failed: %s/%s",
                                      (method, name_server))
                return None

        elif mth == "manager":
            name = OpenRTM_aist.NamingOnManager(
                self._manager.getORB(), self._manager)
            return name
        return None

    ##
    # @if jp
    #
    # @brief 設定済みコンポーネントを NameServer に登録
    #
    # 設定済みコンポーネントを指定した NameServer に登録する。
    #
    # @param self
    # @param ns 登録対象 NameServer
    #
    # @else
    #
    # @endif

    def bindCompsTo(self, ns):
        for comp in self._compNames:
            try:
                ns.bindObject(comp.name, comp.rtobj)
            except BaseException:
                pass

    ##
    # @if jp
    #
    # @brief NameServer に登録するコンポーネントの設定
    #
    # NameServer に登録するコンポーネントを設定する。
    #
    # @param self
    # @param name コンポーネントの登録時名称
    # @param rtobj 登録対象オブジェクト
    #
    # @else
    #
    # @endif

    def registerCompName(self, name, rtobj):
        for c in self._compNames:
            if c.name == name:
                c.rtobj = rtobj
                return

        self._compNames.append(self.Comps(name, rtobj))
        return

    def registerMgrName(self, name, mgr):
        for m in self._mgrNames:
            if m.name == name:
                m.mgr = mgr
                return

        self._mgrNames.append(self.Mgr(name, mgr))
        return

    ##
    # @if jp
    #
    # @brief NameServer に登録するポートの設定
    #
    #
    # @param self
    # @param name ポートの登録時名称
    # @param port 登録対象オブジェクト
    #
    # @else
    # @param self
    # @param name
    # @param port
    #
    # @endif
    def registerPortName(self, name, port):
        for p in self._portNames:
            if p.name == name:
                p.port = port
                return

        self._portNames.append(self.Port(name, port))
        return

    ##
    # @if jp
    #
    # @brief NameServer に登録するコンポーネントの設定解除
    #
    # NameServer に登録するコンポーネントの設定を解除する。
    #
    # @param self
    # @param name 設定解除対象コンポーネントの名称
    #
    # @else
    #
    # @endif
    def unregisterCompName(self, name):
        len_ = len(self._compNames)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._compNames[idx].name == name:
                del self._compNames[idx]
                return
        return

    def unregisterMgrName(self, name):
        len_ = len(self._mgrNames)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._mgrNames[idx].name == name:
                del self._mgrNames[idx]
                return
        return

    ##
    # @if jp
    #
    # @brief NameServer に登録するポートの設定解除
    #
    #
    # @param self
    # @param name 設定解除対象ポートの名称
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
            idx = (len_ - 1) - i
            if self._portNames[idx].name == name:
                del self._portNames[idx]
                return
        return

    ##
    # @if jp
    #
    # @brief コンポネントをリバインドする
    #
    # ネームサーバと接続してコンポネントをリバインドする。
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
        nsobj = None
        try:
            nsobj = self.createNamingObj(ns.method, ns.nsname)
            if nsobj is not None:  # if succeed
                self._rtcout.RTC_INFO("Connected to a name server: %s/%s",
                                      (ns.method, ns.nsname))
                ns.ns = nsobj
                self.bindCompsTo(nsobj)  # rebind all comps to new NS
                return
            else:
                self._rtcout.RTC_DEBUG("Name service: %s/%s still not available.",
                                       (ns.method, ns.nsname))

        except BaseException:
            self._rtcout.RTC_DEBUG("Name server: %s/%s disappeared again.",
                                   (ns.method, ns.nsname))
            if nsobj is not None:
                del ns.ns
                ns.ns = None

        return

    ##
    # @if jp
    #
    # @brief 登録したネームサービスのリストを取得する
    #
    # @return ネームサービスのリスト
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
    # @brief rtcloc形式でRTCのオブジェクトリファレンスを取得
    #
    # @param name rtcloc形式でのRTC名
    # rtcloc://localhost:2809/example/ConsoleIn
    # @return RTCのオブジェクトリファレンスのリスト
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
                if comps:
                    return comps
        return []

    # Name Servers' method/name and object
    ##
    # @if jp
    # @class NameServer
    # @brief NameServer 管理用クラス
    # @else
    #
    # @endif
    class NameServer:
        def __init__(self, meth, name, naming):
            self.method = meth
            self.nsname = name
            self.ns = naming

    # Components' name and object
    ##
    # @if jp
    # @class Comps
    # @brief コンポーネント管理用クラス
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
    # @brief ポート管理用クラス
    # @else
    #
    # @endif

    class Port:
        def __init__(self, n, obj):
            self.name = n
            self.port = obj
