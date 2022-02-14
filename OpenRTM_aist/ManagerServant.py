#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ManagerServant.py
# @brief RTComponent manager servant implementation class
# @date $Date: 2007-12-31 03:08:04 $
# @author Noriaki Ando <n-ando@aist.go.jp>
#
# Copyright (C) 2008
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import copy
import threading
import time
from omniORB import CORBA
import OpenRTM_aist
import OpenRTM_aist.CORBA_RTCUtil
import RTC
import RTM
import RTM__POA
import re
import os


##
# @if jp
# @class CompParam
# @brief CompParam クラス
#
# RTCのベンダ名、カテゴリ名、ID、言語、バージョンを格納する構造体
#
# @since 1.2.0
#
# @else
# @class CompParam
# @brief CompParam class
# @endif
class CompParam:
    prof_list = [
        "RTC",
        "vendor",
        "category",
        "implementation_id",
        "language",
        "version"]
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param module_name モジュール名
    #
    # @else
    # @brief Constructor
    #
    # @param self
    # @param module_name
    #
    # @endif

    def __init__(self, module_name):
        module_name = module_name.split("?")[0]
        param_list = module_name.split(":")
        if len(param_list) < len(CompParam.prof_list):
            self._type = "RTC"
            self._vendor = ""
            self._category = ""
            self._impl_id = module_name
            self._language = "Python"
            self._version = ""
        else:
            self._type = param_list[0]
            self._vendor = param_list[1]
            self._category = param_list[2]
            self._impl_id = param_list[3]
            if param_list[4]:
                self._language = param_list[4]
            else:
                self._language = "Python"
            self._version = param_list[5]

    ##
    # @if jp
    # @brief ベンダ名取得
    #
    #
    #
    # @param self
    # @return ベンダ名
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif

    def vendor(self):
        return self._vendor
    ##
    # @if jp
    # @brief カテゴリ名取得
    #
    #
    #
    # @param self
    # @return カテゴリ名
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif

    def category(self):
        return self._category
    ##
    # @if jp
    # @brief ID取得
    #
    #
    #
    # @param self
    # @return ID
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif

    def impl_id(self):
        return self._impl_id
    ##
    # @if jp
    # @brief 言語取得
    #
    #
    #
    # @param self
    # @return 言語
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif

    def language(self):
        return self._language
    ##
    # @if jp
    # @brief バージョン取得
    #
    #
    #
    # @param self
    # @return バージョン
    #
    # @else
    # @brief
    #
    # @param self
    # @return
    #
    # @endif

    def version(self):
        return self._version


class ManagerServant(RTM__POA.Manager):
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
        self._mgr = OpenRTM_aist.Manager.instance()
        self._owner = None
        self._rtcout = self._mgr.getLogbuf("ManagerServant")
        self._isMaster = False
        self._masters = []
        self._slaves = []
        self._masterMutex = threading.RLock()
        self._slaveMutex = threading.RLock()
        self._objref = RTM.Manager._nil

        config = copy.deepcopy(self._mgr.getConfig())

        if (not self.createINSManager()):
            self._rtcout.RTC_WARN("Manager CORBA servant creation failed.")
            return
        self._rtcout.RTC_TRACE(
            "Manager CORBA servant was successfully created.")

        if OpenRTM_aist.toBool(config.getProperty(
                "manager.is_master"), "YES", "NO", True):
            # this is master manager
            self._rtcout.RTC_TRACE("This manager is master.")
            self._isMaster = True
            return
        else:
            # this is slave manager
            self._rtcout.RTC_TRACE("This manager is slave.")
            try:
                owner = self.findManager(
                    config.getProperty("corba.master_manager"))
                if not owner:
                    self._rtcout.RTC_INFO("Master manager not found")
                    return
                self.add_master_manager(owner)
                owner.add_slave_manager(self._objref)
                return
            except BaseException:
                self._rtcout.RTC_ERROR("Unknown exception cought.")
                self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
        return

    ##
    # @if jp
    #
    # @brief 仮想デストラクタ
    #
    # @else
    #
    # @brief Virtual destructor
    #
    # @endif

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 終了関数
    #
    # @else
    #
    # @brief
    #
    # @endif

    def exit(self):
        guard_master = OpenRTM_aist.ScopedLock(self._masterMutex)
        for master in self._masters:
            try:
                if CORBA.is_nil(master):
                    continue
                master.remove_slave_manager(self._objref)
            except BaseException:
                pass
        self._masters = []

        guard_slave = OpenRTM_aist.ScopedLock(self._slaveMutex)
        for slave in self._slaves:
            try:
                if CORBA.is_nil(slave):
                    continue
                slave.remove_master_manager(self._objref)
            except BaseException:
                pass
        self._slaves = []

        del guard_slave
        del guard_master
        if not CORBA.is_nil(self._objref):
            poa = self._mgr.getORB().resolve_initial_references("omniINSPOA")
            poa.deactivate_object(poa.servant_to_id(self))
            # self._objref._release()

        return

    ##
    # @if jp
    # @brief モジュールをロードする
    #
    # 当該マネージャに指定されたモジュールをロードし、指定された初期化
    # 関数で初期化を行う。
    #
    # @param pathname モジュールへのパス
    # @param initfunc モジュールの初期化関数
    # @return リターンコード
    #
    # @else
    # @brief Loading a module
    #
    # This operation loads a specified loadable module、and perform
    # initialization with the specified function.
    #
    # @param pathname A path to a loading module.
    # @param initfunc Module initialization function.
    # @return The return code.
    #
    # @endif
    #
    # ReturnCode_t load_module(const char* pathname, const char* initfunc)
    def load_module(self, pathname, initfunc):
        self._rtcout.RTC_TRACE(
            "ManagerServant::load_module(%s, %s)", (pathname, initfunc))
        self._mgr.load(pathname, initfunc)
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief モジュールをアンロードする
    #
    # 当該マネージャに指定されたモジュールをアンロードする。
    #
    # @param pathname モジュールへのパス
    # @return リターンコード
    #
    # @else
    # @brief Unloading a module
    #
    # This operation unloads a specified loadable module.
    #
    # @param pathname A path to a loading module.
    # @return The return code.
    #
    # @endif
    #
    # ReturnCode_t unload_module(const char* pathname)

    def unload_module(self, pathname):
        self._rtcout.RTC_TRACE("ManagerServant::unload_module(%s)", pathname)
        self._mgr.unload(pathname)
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief ロード可能なモジュールのプロファイルを取得する
    #
    # ロード可能なモジュールのプロファイルを取得する。
    #
    # @return モジュールプロファイル
    #
    # @else
    # @brief Getting loadable module profiles
    #
    # This operation returns loadable module profiles.
    #
    # @return A module profile list.
    #
    # @endif
    #
    # ModuleProfileList* get_loadable_modules()

    def get_loadable_modules(self):
        self._rtcout.RTC_TRACE("get_loadable_modules()")

        # copy local module profiles
        prof = self._mgr.getLoadableModules()
        cprof = [RTM.ModuleProfile([]) for i in prof]

        for i, p in enumerate(prof):
            OpenRTM_aist.NVUtil.copyFromProperties(
                cprof[i].properties, p)

        return cprof

    ##
    # @if jp
    # @brief ロード済みのモジュールのプロファイルを取得する
    #
    # ロード済みのモジュールのプロファイルを取得する。
    #
    # @return モジュールプロファイル
    #
    # @else
    # @brief Getting loaded module profiles
    #
    # This operation returns loaded module profiles.
    #
    # @return A module profile list.
    #
    # @endif
    #
    # ModuleProfileList* get_loaded_modules()

    def get_loaded_modules(self):
        self._rtcout.RTC_TRACE("get_loaded_modules()")
        prof = self._mgr.getLoadedModules()
        cprof = [RTM.ModuleProfile([]) for i in prof]

        for i, p in enumerate(prof):
            OpenRTM_aist.NVUtil.copyFromProperties(
                cprof[i].properties, p)

        if self._isMaster:
            guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
            for slave in self._slaves[:]:
                try:
                    profs = slave.get_loaded_modules()
                    cprof.extend(profs)
                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_DEBUG(
                        OpenRTM_aist.Logger.print_exception())
                    self._slaves.remove(slave)

        return cprof

    ##
    # @if jp
    # @brief コンポーネントファクトリのプロファイルを取得する
    #
    # ロード済みのモジュールのうち、RTコンポーネントのモジュールが持つ
    # ファクトリのプロファイルのリストを取得する。
    #
    # @return コンポーネントファクトリのプロファイルリスト
    #
    # @else
    # @brief Getting component factory profiles
    #
    # This operation returns component factory profiles from loaded
    # RT-Component module factory profiles.
    #
    # @return An RT-Component factory profile list.
    #
    # @endif
    #
    # ModuleProfileList* get_factory_profiles()

    def get_factory_profiles(self):
        self._rtcout.RTC_TRACE("get_factory_profiles()")
        prof = self._mgr.getFactoryProfiles()
        cprof = [RTM.ModuleProfile([]) for i in prof]

        for i, p in enumerate(prof):
            OpenRTM_aist.NVUtil.copyFromProperties(
                cprof[i].properties, p)

        if self._isMaster:
            guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
            for slave in self._slaves[:]:
                try:
                    profs = slave.get_factory_profiles()
                    cprof.extend(profs)
                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_DEBUG(
                        OpenRTM_aist.Logger.print_exception())
                    self._slaves.remove(slave)

        return cprof

    ##
    # @if jp
    # @brief コンポーネントを生成する
    #
    # 引数に指定されたコンポーネントを生成する。
    #
    # @return 生成されたRTコンポーネント
    #
    # @else
    # @brief Creating an RT-Component
    #
    # This operation creates RT-Component according to the string
    # argument.
    #
    # @return A created RT-Component
    #
    # @endif
    #
    # RTObject_ptr create_component(const char* module_name)
    def create_component(self, module_name):

        self._rtcout.RTC_TRACE("create_component(%s)", module_name)

        rtc = self.createComponentByAddress(module_name)
        if not CORBA.is_nil(rtc):
            return rtc

        rtc = self.createComponentByManagerName(module_name)

        if not CORBA.is_nil(rtc):
            return rtc

        #module_name = module_name.split("&")[0]
        _, module_name = self.getParameterByModulename(
            "manager_address", module_name)
        manager_name, module_name = self.getParameterByModulename(
            "manager_name", module_name)

        comp_param = CompParam(module_name)

        if self._isMaster:
            guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
            for slave in self._slaves[:]:
                try:
                    prof = slave.get_configuration()
                    prop = OpenRTM_aist.Properties()
                    OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                    slave_lang = prop.getProperty("manager.language")
                    if slave_lang == comp_param.language():
                        rtc = slave.create_component(module_name)
                        if not CORBA.is_nil(rtc):
                            return rtc
                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_DEBUG(
                        OpenRTM_aist.Logger.print_exception())
                    self._slaves.remove(slave)
            del guard
            if not manager_name:
                module_name = module_name + "&manager_name=manager_%p"

                rtc = self.createComponentByManagerName(module_name)
                return rtc

        else:
            # create on this manager
            rtc = self._mgr.createComponent(module_name)
            if rtc:
                return rtc.getObjRef()

        return RTC.RTObject._nil

    ##
    # @if jp
    # @brief コンポーネントを削除する
    #
    # 引数に指定されたコンポーネントを削除する。
    #
    # @return リターンコード
    #
    # @else
    # @brief Deleting an RT-Component
    #
    # This operation delete an RT-Component according to the string
    # argument.
    #
    # @return Return code
    #
    # @endif
    #
    # ReturnCode_t delete_component(const char* instance_name)

    def delete_component(self, instance_name):
        self._rtcout.RTC_TRACE("delete_component(%s)", instance_name)
        comp_ = self._mgr.getComponent(instance_name)
        if not comp_:
            self._rtcout.RTC_WARN(
                "No such component exists: %s",
                instance_name)
            return RTC.BAD_PARAMETER

        try:
            comp_.exit()
        except BaseException:
            self._rtcout.RTC_ERROR(
                "Unknown exception was raised, when RTC was finalized.")
            return RTC.RTC_ERROR

        return RTC.RTC_OK

    ##
    # @if jp
    # @brief 起動中のコンポーネントのリストを取得する
    #
    # 現在当該マネージャ上で起動中のコンポーネントのリストを返す。
    #
    # @return RTコンポーネントのリスト
    #
    # @else
    # @brief Getting RT-Component list running on this manager
    #
    # This operation returns RT-Component list running on this manager.
    #
    # @return A list of RT-Components
    #
    # @endif
    #
    # RTCList* get_components()

    def get_components(self):
        self._rtcout.RTC_TRACE("get_components()")

        # get local component references
        rtcs = self._mgr.getComponents()
        crtcs = []

        for rtc in rtcs:
            crtcs.append(rtc.getObjRef())

        # get slaves' component references
        self._rtcout.RTC_DEBUG("%d slave managers exists.", len(self._slaves))
        for slave in self._slaves[:]:
            try:
                if not CORBA.is_nil(slave):
                    srtcs = slave.get_components()
                    OpenRTM_aist.CORBA_SeqUtil.push_back_list(crtcs, srtcs)

            except BaseException:
                self._rtcout.RTC_ERROR("Unknown exception cought.")
                self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
                self._slaves.remove(slave)
                #self._rtcout.RTC_INFO("slave (%d) has disappeared.", i)
                #self._slaves[i] = RTM.Manager._nil

                #OpenRTM_aist.CORBA_SeqUtil.erase(self._slaves, i)
                #i -= 1

        return crtcs

    ##
    # @if jp
    # @brief 起動中のコンポーネントプロファイルのリストを取得する
    #
    # 現在当該マネージャ上で起動中のコンポーネントのプロファイルのリス
    # トを返す。
    #
    # @return RTコンポーネントプロファイルのリスト
    #
    # @else
    # @brief Getting RT-Component's profile list running on this manager
    #
    # This operation returns RT-Component's profile list running on
    # this manager.
    #
    # @return A list of RT-Components' profiles
    #
    # @endif
    #
    # ComponentProfileList* get_component_profiles()

    def get_component_profiles(self):
        rtcs = self._mgr.getComponents()
        cprofs = [rtc.get_component_profile() for rtc in rtcs]

        # copy slaves' component profiles
        guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
        self._rtcout.RTC_DEBUG("%d slave managers exists.", len(self._slaves))

        for slave in self._slaves[:]:
            try:
                if not CORBA.is_nil(slave):
                    sprofs = slave.get_component_profiles()
                    OpenRTM_aist.CORBA_SeqUtil.push_back_list(cprofs, sprofs)
            except BaseException:
                self._rtcout.RTC_ERROR("Unknown exception cought.")
                self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
                self._slaves.remove(slave)
                #self._rtcout.RTC_INFO("slave (%d) has disappeared.", i)
                #self._slaves[i] = RTM.Manager._nil

                #OpenRTM_aist.CORBA_SeqUtil.erase(self._slaves, i)
                #i -= 1

        del guard
        return cprofs

    ##
    # @if jp
    # @brief マネージャのプロファイルを取得する
    #
    # 現在当該マネージャのプロファイルを取得する。
    #
    # @return マネージャプロファイル
    #
    # @else
    # @brief Getting this manager's profile.
    #
    # This operation returns this manager's profile.
    #
    # @return Manager's profile
    #
    # @endif
    #
    # ManagerProfile* get_profile()

    def get_profile(self):
        self._rtcout.RTC_TRACE("get_profile()")
        prof = RTM.ModuleProfile([])
        OpenRTM_aist.NVUtil.copyFromProperties(
            prof.properties, self._mgr.getConfig().getNode("manager"))

        return prof

    ##
    # @if jp
    # @brief マネージャのコンフィギュレーションを取得する
    #
    # 現在当該マネージャのコンフィギュレーションを取得する。
    #
    # @return マネージャコンフィギュレーション
    #
    # @else
    # @brief Getting this manager's configuration.
    #
    # This operation returns this manager's configuration.
    #
    # @return Manager's configuration
    #
    # @endif
    #
    # NVList* get_configuration()

    def get_configuration(self):
        self._rtcout.RTC_TRACE("get_configuration()")
        nvlist = []
        OpenRTM_aist.NVUtil.copyFromProperties(nvlist, self._mgr.getConfig())
        return nvlist

    ##
    # @if jp
    # @brief マネージャのコンフィギュレーションを設定する
    #
    # 現在当該マネージャのコンフィギュレーションを設定する。
    #
    # @param name セットするコンフィギュレーションのキー名
    # @param value セットするコンフィギュレーションの値
    # @return リターンコード
    #
    # @else
    # @brief Setting manager's configuration
    #
    # This operation sets managers configuration.
    #
    # @param name A configuration key name to be set
    # @param value A configuration value to be set
    # @return Return code
    #
    # @endif
    #
    # ReturnCode_t set_configuration(const char* name, const char* value)

    def set_configuration(self, name, value):
        self._rtcout.RTC_TRACE(
            "set_configuration(name = %s, value = %s)", (name, value))
        self._mgr.getConfig().setProperty(name, value)
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief マネージャがマスターかどうか
    #
    # この関数はマネージャがマスターかどうかを返す。Trueならば、当該マ
    # ネージャはマスターであり、それ以外は False を返す。
    #
    # @return マスターマネージャかどうかのbool値
    #
    # @else
    # @brief Whether this manager is master or not
    #
    # It returns "True" if this manager is a master, and it returns
    # "False" in other cases.
    #
    # @return A boolean value that means it is master or not.
    #
    # @endif
    #
    # bool is_master();

    def is_master(self):
        # since Python2.5
        # self._rtcout.RTC_TRACE("is_master(): %s", (lambda x: "YES" if x else "NO")(self._isMaster))
        ret = ""
        if self._isMaster:
            ret = "YES"
        else:
            ret = "NO"
        self._rtcout.RTC_TRACE("is_master(): %s", ret)
        return self._isMaster

    ##
    # @if jp
    # @brief マスターマネージャの取得
    #
    # このマネージャがスレーブマネージャの場合、マスターとなっているマ
    # ネージャのリストを返す。このマネージャがマスターの場合、空のリス
    # トが返る。
    #
    # @return マスターマネージャのリスト
    #
    # @else
    # @brief Getting master managers
    #
    # This operation returns master manager list if this manager is
    # slave. If this manager is master, an empty sequence would be
    # returned.
    #
    # @return Master manager list
    #
    # @endif
    #
    # RTM::ManagerList* get_master_managers();

    def get_master_managers(self):
        self._rtcout.RTC_TRACE("get_master_managers()")
        guard = OpenRTM_aist.ScopedLock(self._masterMutex)

        return self._masters

    ##
    # @if jp
    # @brief マスターマネージャの追加
    #
    # このマネージャのマスタとしてマネージャを一つ追加する。戻り値には、
    # 当該マネージャ上で追加されたマスターマネージャを識別するユニーク
    # なIDが返される。このマネージャがマスタの場合、当該IDで指定された
    # マスターマネージャを返す。IDで指定されたマスターマネージャがない
    # 場合、nilオブジェクトが返る。
    #
    # @return マスターマネージャ
    #
    # @else
    # @brief Getting a master manager
    #
    # This operation returns a master manager with specified id. If
    # the manager with the specified id does not exist, nil object
    # reference would be returned.
    #
    # @return A master manager
    #
    # @endif
    #
    # RTC::ReturnCode_t add_master_manager(RTM::Manager_ptr mgr);

    def add_master_manager(self, mgr):
        guard = OpenRTM_aist.ScopedLock(self._masterMutex)
        self._rtcout.RTC_TRACE(
            "add_master_manager(), %d masters", len(
                self._masters))
        index = OpenRTM_aist.CORBA_SeqUtil.find(
            self._masters, self.is_equiv(mgr))

        if not (index < 0):  # found in my list
            self._rtcout.RTC_ERROR("Already exists.")
            return RTC.BAD_PARAMETER

        OpenRTM_aist.CORBA_SeqUtil.push_back(self._masters, mgr)
        self._rtcout.RTC_TRACE(
            "add_master_manager() done, %d masters", len(
                self._masters))
        del guard
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief マスターマネージャの削除
    #
    # このマネージャが保持するマスタのうち、指定されたものを削除する。
    #
    # @param mgr マスターマネージャ
    # @return ReturnCode_t
    #
    # @else
    # @brief Removing a master manager
    #
    # This operation removes a master manager from this manager.
    #
    # @param mgr A master manager
    # @return ReturnCode_t
    #
    # @endif
    #
    # RTC::ReturnCode_t remove_master_manager(RTM::Manager_ptr mgr);

    def remove_master_manager(self, mgr):
        guard = OpenRTM_aist.ScopedLock(self._masterMutex)
        self._rtcout.RTC_TRACE(
            "remove_master_manager(), %d masters", len(
                self._masters))

        index = OpenRTM_aist.CORBA_SeqUtil.find(
            self._masters, self.is_equiv(mgr))

        if index < 0:  # not found in my list
            self._rtcout.RTC_ERROR("Not found.")
            return RTC.BAD_PARAMETER

        OpenRTM_aist.CORBA_SeqUtil.erase(self._masters, index)
        self._rtcout.RTC_TRACE(
            "remove_master_manager() done, %d masters", len(
                self._masters))
        del guard
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief スレーブマネージャの取得
    #
    # このマネージャがスレーブマネージャの場合、スレーブとなっているマ
    # ネージャのリストを返す。このマネージャがスレーブの場合、空のリス
    # トが返る。
    #
    # @return スレーブマネージャのリスト
    #
    # @else
    # @brief Getting slave managers
    #
    # This operation returns slave manager list if this manager is
    # slave. If this manager is slave, an empty sequence would be
    # returned.
    #
    # @return Slave manager list
    #
    # @endif
    #
    # RTM::ManagerList* get_slave_managers();

    def get_slave_managers(self):
        guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
        self._rtcout.RTC_TRACE(
            "get_slave_managers(), %d slaves", len(
                self._slaves))
        return self._slaves

    ##
    # @if jp
    # @brief スレーブマネージャの追加
    #
    # このマネージャのマスタとしてマネージャを一つ追加する。
    #
    # @param mgr スレーブマネージャ
    # @return ReturnCode_t
    #
    # @else
    # @brief Getting a slave manager
    #
    # This operation add a slave manager to this manager.
    #
    # @param mgr A slave manager
    # @return ReturnCode_t
    #
    # @endif
    #
    # RTC::ReturnCode_t add_slave_manager(RTM::Manager_ptr mgr);

    def add_slave_manager(self, mgr):
        guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
        self._rtcout.RTC_TRACE(
            "add_slave_manager(), %d slaves", len(
                self._slaves))

        index = OpenRTM_aist.CORBA_SeqUtil.find(
            self._slaves, self.is_equiv(mgr))

        if not (index < 0):  # found in my list
            self._rtcout.RTC_ERROR("Already exists.")
            return RTC.BAD_PARAMETER

        OpenRTM_aist.CORBA_SeqUtil.push_back(self._slaves, mgr)
        self._rtcout.RTC_TRACE(
            "add_slave_manager() done, %d slaves", len(
                self._slaves))
        del guard
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief スレーブマネージャの削除
    #
    # このマネージャが保持するマスタのうち、指定されたものを削除する。
    #
    # @param mgr スレーブマネージャ
    # @return ReturnCode_t
    #
    # @else
    # @brief Removing a slave manager
    #
    # This operation removes a slave manager from this manager.
    #
    # @param mgr A slave manager
    # @return ReturnCode_t
    #
    # @endif
    #
    # RTC::ReturnCode_t remove_slave_manager(RTM::Manager_ptr mgr);

    def remove_slave_manager(self, mgr):
        guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
        self._rtcout.RTC_TRACE(
            "remove_slave_manager(), %d slaves", len(
                self._slaves))
        index = OpenRTM_aist.CORBA_SeqUtil.find(
            self._slaves, self.is_equiv(mgr))

        if index < 0:  # not found in my list
            self._rtcout.RTC_ERROR("Not found.")
            return RTC.BAD_PARAMETER

        OpenRTM_aist.CORBA_SeqUtil.erase(self._slaves, index)
        self._rtcout.RTC_TRACE(
            "remove_slave_manager() done, %d slaves", len(
                self._slaves))
        del guard
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief プロセスのコピーを生成する
    # @return ReturnCode_t
    # @else
    # @brief The copy of the process is generated.
    # @return ReturnCode_t
    # @endif
    #
    # ReturnCode_t fork()

    def fork(self):
        # self._mgr.fork()
        pid = OpenRTM_aist.fork()
        if pid >= 0:
            return RTC.RTC_OK
        else:
            return RTC.RTC_ERROR

    ##
    # @if jp
    # @brief shutdownする
    # @return ReturnCode_t
    # @else
    # @brief This method shutdowns RTC.
    # @return ReturnCode_t
    # @endif
    #
    # ReturnCode_t shutdown()

    def shutdown(self):
        guard_master = OpenRTM_aist.ScopedLock(self._masterMutex)
        for master in self._masters:
            try:
                if CORBA.is_nil(master):
                    continue
                master.remove_slave_manager(self._objref)
            except BaseException:
                pass
        self._masters = []

        guard_slave = OpenRTM_aist.ScopedLock(self._slaveMutex)
        for slaves in self._slaves:
            try:
                if CORBA.is_nil(slaves):
                    continue
                slaves.remove_master_manager(self._objref)
            except BaseException:
                pass
        self._slaves = []

        wait_time = 1.0
        if self._mgr.getConfig().findNode("manager.termination_waittime"):
            s = self._mgr.getConfig().getProperty("manager.termination_waittime")
            ret, wait_time = OpenRTM_aist.stringTo(wait_time, s)

        self._mgr.terminate()

        return RTC.RTC_OK

    ##
    # @if jp
    # @brief 再起動する。
    # @return ReturnCode_t
    # @else
    # @brief This method restarts RTC.
    # @return ReturnCode_t
    # @endif
    #
    # ReturnCode_t restart()

    def restart(self):
        # self._mgr.restart()
        return RTC.RTC_OK

    ##
    # @if jp
    # @brief RTCのリファレンスを取得する。
    # @return RTCのリファレンス
    # @else
    # @brief Get the reference of RTC.
    # @return RTC reference
    # @endif
    #
    # Object_ptr get_service(const char* name)

    def get_service(self, name):
        return CORBA.Object._nil

    ##
    # @if jp
    # @brief Managerのリファレンスを取得する。
    # @return Managerのリファレンス
    # @else
    # @brief Get the reference of Manager.
    # @return Manager reference
    # @endif
    #
    # Manager_ptr getObjRef() const

    def getObjRef(self):
        return self._objref

    ##
    # @if jp
    # @brief INSManagerの生成
    # @return
    # @else 成功:true, 失敗:false
    # @brief Generate INSManager.
    # @return Successful:true, Failed:false
    # @endif
    #
    # bool createINSManager();

    def createINSManager(self):
        try:
            poa = self._mgr.getORB().resolve_initial_references("omniINSPOA")
            poa._get_the_POAManager().activate()
            id = self._mgr.getConfig().getProperty("manager.name")
            poa.activate_object_with_id(id, self)
            mgrobj = poa.id_to_reference(id)
            self._objref = mgrobj._narrow(RTM.Manager)
        except BaseException:
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
            return False

        return True

    ##
    # @if jp
    # @brief Managerのリファレンスを検索する。
    # @return Managerのリファレンス
    # @else
    # @brief Find the reference of Manager.
    # @return Manager reference
    # @endif
    #
    # RTM::Manager_ptr findManager(const char* host_port);

    def findManager(self, host_port):
        self._rtcout.RTC_TRACE("findManager(host_port = %s)", host_port)
        try:
            config = copy.deepcopy(self._mgr.getConfig())
            mgrloc = OpenRTM_aist.CORBA_RTCUtil.CorbaURI(host_port, config.getProperty("manager.name")).toString()

            self._rtcout.RTC_DEBUG("corbaloc: %s", mgrloc)

            mobj = self._mgr.getORB().string_to_object(mgrloc)
            mgr = mobj._narrow(RTM.Manager)

            return mgr

        except CORBA.SystemException:
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())

        except BaseException:
            self._rtcout.RTC_ERROR("Unknown exception cought.")
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())

        return RTM.Manager._nil

    ##
    # @if jp
    # @brief 指定名のRTCを取得
    # @param self
    # @param name RTC名
    # @return RTCのリスト
    # @else
    #
    # @brief
    # @param self
    # @param name
    # @return
    # @endif
    # RTCList get_components_by_name(string name)
    def get_components_by_name(self, name):
        self._rtcout.RTC_TRACE("get_components_by_name()")
        rtcs = self._mgr.getComponents()
        crtcs = []
        name = OpenRTM_aist.eraseHeadBlank(name)
        rtc_name = name.split("/")
        for rtc in rtcs:
            if len(rtc_name) == 1:
                if rtc.getInstanceName() == rtc_name[0]:
                    crtcs.append(rtc.getObjRef())
            else:
                if rtc_name[0] == "*":
                    if rtc.getInstanceName() == rtc_name[1]:
                        crtcs.append(rtc.getObjRef())
                else:
                    if rtc.getCategory() == rtc_name[0]:
                        if rtc.getInstanceName() == rtc_name[1]:
                            crtcs.append(rtc.getObjRef())

        return crtcs

    ##
    # @if jp
    # @brief 指定名のマネージャを取得
    # マネージャがマスターの場合は登録されているスレーブマネージャから検索する
    # マネージャがスレーブの場合は登録されているマスターマネージャからスレーブマネージャを検索する
    # @param self
    # @param manager_name マネージャ名
    # @return マネージャ
    # @else
    #
    # @brief
    # @param self
    # @param manager_name
    # @return
    # @endif
    # RTC::Manager_ptr findManagerByName(string manager_name)
    def findManagerByName(self, manager_name):
        self._rtcout.RTC_TRACE(
            "findManagerByName(manager_name = %s)",
            manager_name)
        prop = self._mgr.getConfig()
        name = prop.getProperty("manager.instance_name")
        if name == manager_name:
            return self.getObjRef()
        if self._isMaster:
            guard = OpenRTM_aist.ScopedLock(self._slaveMutex)
            for slave in self._slaves[:]:
                try:
                    prof = slave.get_configuration()
                    prop = OpenRTM_aist.Properties()
                    OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                    name = prop.getProperty("manager.instance_name")
                    if name == manager_name:
                        return slave

                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_DEBUG(
                        OpenRTM_aist.Logger.print_exception())
                    self._slaves.remove(slave)
            del guard
        else:
            guard = OpenRTM_aist.ScopedLock(self._masterMutex)
            for master in self._masters:
                try:
                    prof = master.get_configuration()
                    prop = OpenRTM_aist.Properties()
                    OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                    name = prop.getProperty("manager.instance_name")
                    if name == manager_name:
                        return master
                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_DEBUG(
                        OpenRTM_aist.Logger.print_exception())
                    continue

                slaves = master.get_slave_managers()
                for slave in slaves[:]:
                    try:
                        prof = slave.get_configuration()
                        prop = OpenRTM_aist.Properties()
                        OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                        name = prop.getProperty("manager.instance_name")
                        if name == manager_name:
                            return slave
                    except BaseException:
                        self._rtcout.RTC_ERROR("Unknown exception cought.")
                        self._rtcout.RTC_DEBUG(
                            OpenRTM_aist.Logger.print_exception())
                        master.remove_slave_manager(slave)

            del guard

        return RTM.Manager._nil

    ##
    # @if jp
    # @brief モジュール名からパラメータを取り出す
    # &param_name=value　もしくは ?param_name=value
    #　のvalueを取り出す
    #
    # @param self
    # @param param_name パラメータ名
    # @param module_name モジュール名
    # @return パラメータ
    # @else
    #
    # @brief
    # @param self
    # @param param_name
    # @param module_name
    # @return
    # @endif
    # std::string getParameterByModulename(string param_name, string
    # &module_name)
    def getParameterByModulename(self, param_name, module_name):
        arg = module_name
        pos0 = arg.find("&" + param_name + "=")
        pos1 = arg.find("?" + param_name + "=")

        if pos0 == -1 and pos1 == -1:
            return "", module_name

        pos = 0
        if pos0 == -1:
            pos = pos1
        else:
            pos = pos0

        paramstr = ""
        endpos = arg.find('&', pos + 1)
        if endpos == -1:
            endpos = arg.find('?', pos + 1)
            if endpos == -1:
                paramstr = arg[(pos + 1):]
            else:
                paramstr = arg[(pos + 1): endpos]
        else:
            paramstr = arg[(pos + 1): endpos]
        self._rtcout.RTC_VERBOSE("%s arg: %s", (param_name, paramstr))

        eqpos = paramstr.find("=")
        # if eqpos == -1:
        #  self._rtcout.RTC_WARN("Invalid argument: %s", module_name)
        #  return ""

        paramstr = paramstr[eqpos + 1:]
        self._rtcout.RTC_DEBUG("%s is %s", (param_name, paramstr))

        if endpos == -1:
            arg = arg[:pos]
        else:
            arg = arg[:pos] + arg[endpos:]

        module_name = arg

        return paramstr, module_name

    ##
    # @if jp
    # @brief 指定のマネージャでRTCを起動する
    # comp&manager_name=mgr
    # のようにRTC名&manager_name=マネージャ名と指定する
    # @param self
    # @param module_name 起動するRTC、マネージャ名
    # @return RTC
    # @else
    #
    # @brief
    # @param self
    # @param module_name
    # @return
    # @endif
    # RTC::RTObject_ptr createComponentByManagerName(string module_name)
    def createComponentByManagerName(self, module_name):

        arg = module_name

        mgrstr, arg = self.getParameterByModulename("manager_name", arg)

        if not mgrstr:
            return RTC.RTObject._nil

        if mgrstr == "manager_%p":
            mgrobj = RTM.Manager._nil
        else:
            mgrobj = self.findManagerByName(mgrstr)

        comp_param = CompParam(arg)

        if CORBA.is_nil(mgrobj):
            self._rtcout.RTC_WARN("%s cannot be found.", mgrstr)
            config = copy.deepcopy(self._mgr.getConfig())
            rtcd_cmd = config.getProperty(
                "manager.modules." +
                comp_param.language() +
                ".manager_cmd")

            if not rtcd_cmd:
                lang = config.getProperty("manager.language")
                rtcd_cmd = config.getProperty(
                    "manager.modules." +
                    lang +
                    ".manager_cmd")

            load_path = config.getProperty("manager.modules.load_path")
            load_path_language = config.getProperty(
                "manager.modules." + comp_param.language() + ".load_paths")
            load_path = load_path + "," + load_path_language

            if os.name == "nt":
                cmd = "cmd /c " + rtcd_cmd
                load_path = load_path.replace("\\", "\\\\")
                load_path = load_path.replace("\\", "\\\\")
            else:
                cmd = rtcd_cmd
            cmd += " -o " + "manager.is_master:NO"
            cmd += " -o " + "manager.corba_servant:YES"
            cmd += " -o " + "corba.master_manager:" + \
                config.getProperty("corba.master_manager")
            cmd += " -o " + "manager.name:" + \
                config.getProperty("manager.name")
            cmd += " -o " + "manager.instance_name:" + mgrstr
            cmd += " -o " + "\"manager.modules.load_path:" + load_path + "\""
            cmd += " -o " + "manager.supported_languages:" + comp_param.language()
            cmd += " -o " + "manager.shutdown_auto:NO"

            self._rtcout.RTC_DEBUG("Invoking command: %s.", cmd)

            slaves_names = []
            regex = r'manager_[0-9]+'
            if mgrstr == "manager_%p":
                guard_slave = OpenRTM_aist.ScopedLock(self._slaveMutex)
                for slave in self._slaves[:]:
                    try:
                        prof = slave.get_configuration()
                        prop = OpenRTM_aist.Properties()
                        OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                        name = prop.getProperty("manager.instance_name")
                        if re.match(regex, name):
                            slaves_names.append(name)
                    except BaseException:
                        self._rtcout.RTC_ERROR("Unknown exception cought.")
                        self._rtcout.RTC_DEBUG(
                            OpenRTM_aist.Logger.print_exception())
                        self._slaves.remove(slave)

                del guard_slave

            ret = OpenRTM_aist.launch_shell(cmd)

            if ret == -1:
                self._rtcout.RTC_DEBUG("%s: failed", cmd)
                return RTC.RTObject._nil
            time.sleep(0.01)
            count = 0

            t0_ = OpenRTM_aist.Time()

            while CORBA.is_nil(mgrobj):
                if mgrstr == "manager_%p":

                    guard_slave = OpenRTM_aist.ScopedLock(self._slaveMutex)

                    for slave in self._slaves[:]:
                        try:
                            prof = slave.get_configuration()
                            prop = OpenRTM_aist.Properties()
                            OpenRTM_aist.NVUtil.copyToProperties(prop, prof)
                            name = prop.getProperty("manager.instance_name")

                            if re.match(regex, name) and not (
                                    name in slaves_names):
                                mgrobj = slave
                        except BaseException:
                            self._rtcout.RTC_ERROR("Unknown exception cought.")
                            self._rtcout.RTC_DEBUG(
                                OpenRTM_aist.Logger.print_exception())
                            self._slaves.remove(slave)
                    del guard_slave

                else:
                    mgrobj = self.findManagerByName(mgrstr)
                count += 1
                if count > 1000:
                    break

                t1_ = OpenRTM_aist.Time()
                if (t1_ - t0_).getTime().toDouble() > 10.0 and count > 10:
                    break
                time.sleep(0.01)

        if CORBA.is_nil(mgrobj):
            self._rtcout.RTC_WARN("Manager cannot be found.")
            return RTC.RTObject._nil

        self._rtcout.RTC_DEBUG("Creating component on %s", mgrstr)
        self._rtcout.RTC_DEBUG("arg: %s", arg)

        try:
            rtobj = mgrobj.create_component(arg)

            return rtobj
        except CORBA.SystemException:
            self._rtcout.RTC_DEBUG(
                "Exception was caught while creating component.")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return RTC.RTObject._nil
        except BaseException:
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
            return RTC.RTObject._nil

    ##
    # @if jp
    # @brief 指定のマネージャでRTCを起動する
    # comp&manager_address=localhost:2810
    # のようにRTC名&manager_address=マネージャのホスト名、ポート番号を指定する
    # @param self
    # @param module_name 起動するRTC、マネージャのホストアドレス
    # @return RTC
    # @else
    #
    # @brief
    # @param self
    # @param module_name
    # @return
    # @endif
    # RTC::RTObject_ptr createComponentByAddress(string module_name)
    def createComponentByAddress(self, module_name):

        arg = module_name
        mgrstr, arg = self.getParameterByModulename("manager_address", arg)

        if not mgrstr:
            return RTC.RTObject._nil

        mgrvstr = mgrstr.split(":")
        if len(mgrvstr) != 2:
            self._rtcout.RTC_WARN("Invalid manager address: %s", mgrstr)
            return RTC.RTObject._nil

        # find manager
        mgrobj = self.findManager(mgrstr)

        comp_param = CompParam(arg)

        if CORBA.is_nil(mgrobj):
            config = copy.deepcopy(self._mgr.getConfig())
            rtcd_cmd = config.getProperty(
                "manager.modules." +
                comp_param.language() +
                ".manager_cmd")
            if not rtcd_cmd:
                lang = config.getProperty("manager.language")
                rtcd_cmd = config.getProperty(
                    "manager.modules." +
                    lang +
                    ".manager_cmd")

            load_path = config.getProperty("manager.modules.load_path")
            load_path_language = config.getProperty(
                "manager.modules." + comp_param.language() + ".load_path")
            load_path = load_path + "," + load_path_language

            if os.name == "nt":
                cmd = "cmd /c " + rtcd_cmd
                load_path = load_path.replace("\\", "\\\\")
            else:
                cmd = rtcd_cmd
            cmd += " -o corba.master_manager:"
            cmd += mgrstr  # port number
            cmd += " -o \"manager.modules.load_path:"
            cmd += load_path + "\""
            cmd += " -d "

            self._rtcout.RTC_DEBUG("Invoking command: %s.", cmd)
            ret = OpenRTM_aist.launch_shell(cmd)

            if ret == -1:
                self._rtcout.RTC_DEBUG("%s: failed", cmd)
                return RTC.RTObject._nil

            # find manager
            time.sleep(0.01)
            count = 0
            t0_ = OpenRTM_aist.Time()
            while CORBA.is_nil(mgrobj):
                mgrobj = self.findManager(mgrstr)
                count += 1
                if count > 1000:
                    break

                t1_ = OpenRTM_aist.Time()
                if (t1_ - t0_).getTime().toDouble() > 10.0 and count > 10:
                    break
                time.sleep(0.01)

        if CORBA.is_nil(mgrobj):
            self._rtcout.RTC_WARN("Manager cannot be found.")
            return RTC.RTObject._nil

        self._rtcout.RTC_DEBUG("Creating component on %s", mgrstr)
        self._rtcout.RTC_DEBUG("arg: %s", arg)
        try:
            rtobj = mgrobj.create_component(arg)
            self._rtcout.RTC_DEBUG("Component created %s", arg)
            return rtobj
        except CORBA.SystemException:
            self._rtcout.RTC_DEBUG(
                "Exception was caught while creating component.")
            self._rtcout.RTC_ERROR(OpenRTM_aist.Logger.print_exception())
            return RTC.RTObject._nil
        except BaseException:
            self._rtcout.RTC_DEBUG(OpenRTM_aist.Logger.print_exception())
            return RTC.RTObject._nil

    ##
    # @if jp
    # @brief マスターマネージャの有無を確認してリストを更新する
    #
    # @param self
    # @else
    #
    # @brief
    # @param self
    # @endif
    # void updateMasterManager()
    def updateMasterManager(self):
        if not self._isMaster and self._objref:
            guard = OpenRTM_aist.ScopedLock(self._masterMutex)
            if self._masters:
                for master in self._masters[:]:
                    try:
                        if master._non_existent():
                            self._masters.remove(master)
                    except BaseException:
                        self._rtcout.RTC_ERROR("Unknown exception cought.")
                        self._rtcout.RTC_ERROR(
                            OpenRTM_aist.Logger.print_exception())
                        self._masters.remove(master)
            del guard

            if not self._masters:
                try:
                    config = self._mgr.getConfig()
                    owner = self.findManager(
                        config.getProperty("corba.master_manager"))
                    if not owner:
                        self._rtcout.RTC_INFO("Master manager not found")
                        return
                    self.add_master_manager(owner)
                    owner.add_slave_manager(self._objref)

                    return
                except BaseException:
                    self._rtcout.RTC_ERROR("Unknown exception cought.")
                    self._rtcout.RTC_ERROR(
                        OpenRTM_aist.Logger.print_exception())

    class is_equiv:
        def __init__(self, mgr):
            self._mgr = mgr

        def __call__(self, mgr):
            if not self._mgr or not mgr:
                return self._mgr == mgr

            return self._mgr._is_equivalent(mgr)
