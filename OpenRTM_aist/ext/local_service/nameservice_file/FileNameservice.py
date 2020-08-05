#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FileNameservice.py
# @brief FileNameservice
# @date 2012/01/17
# @author n-ando and Shinji Kurihara
#
# Copyright (C) 2011
#     Noriaki Ando
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import shutil
import os.path
import OpenRTM_aist

service_name = "org.openrtm.local_service.nameservice.file_nameservice"
service_uuid = "7288D080-F618-480B-B6D9-A199686F3101"
default_config = ["base_path", "./openrtm_ns/",
                  "file_structure", "tree",
                  "context_delimiter", "|",
                  ""]


##
# @if jp
# @class FileNameservice クラス
# @brief FileNameservice クラス
# @else
# @class FileNameservice class
# @brief FileNameservice class
# @endif
class FileNameservice(OpenRTM_aist.LocalServiceBase):
    """
    """

    ##
    # @if jp
    # @brief FileNameService ctor
    # @else
    # @brief FileNameService ctor
    # @endif
    def __init__(self):
        global service_name
        global service_uuid
        global default_config

        self._profile = OpenRTM_aist.LocalServiceProfile()
        self._profile.name = service_name
        self._profile.uuid = service_uuid
        prop = OpenRTM_aist.Properties(defaults_str=default_config)
        self._profile.properties = prop
        self._profile.service = self
        self._files = []
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("file_nameservice")
        self._rtcout.RTC_DEBUG("FileNameservice was created(")
        self._rtcout.RTC_DEBUG("    name = %s", self._profile.name)
        self._rtcout.RTC_DEBUG("    uuid = %s", self._profile.uuid)
        self._rtcout.RTC_DEBUG("    properties = %s", self._profile.properties)
        self._rtcout.RTC_DEBUG("    service = %s)", self.__class__.__name__)
        return

    ##
    # @if jp
    # @brief FileNameService dtor
    # @else
    # @brief FileNameService dtor
    # @endif

    def __del__(self):
        self._rtcout.RTC_TRACE("FileNameservice.__del__()")
        self.cleanupFiles()
        return

    ##
    # @if jp
    # @brief 初期化関数
    #
    # TODO: Documentation
    #
    # @param profile 外部から与えられた property
    # @return
    #
    # @else
    # @brief Initialization function
    #
    # TODO: Documentation
    #
    # @endif
    # virtual bool
    # init(const ::coil::Properties& profile);

    def init(self, profile):
        self._rtcout.RTC_TRACE("init()")
        self._rtcout.RTC_DEBUG(profile)
        self._profile.properties.mergeProperties(profile)

        manager_ = OpenRTM_aist.Manager.instance()
        manager_.addNamingActionListener(NamingAction(self))
        return True

    ##
    # @if jp
    # @brief 再初期化関数
    #
    # TODO: Documentation
    #
    # @param profile 外部から与えられた property
    # @return
    #
    # @else
    # @brief Reinitialization function
    #
    # TODO: Documentation
    #
    # @endif
    # virtual bool
    # reinit(const ::coil::Properties& profile);

    def reinit(self, profile):
        self._rtcout.RTC_TRACE("reinit()")
        self._rtcout.RTC_DEBUG(profile)
        ret = self.processServiceProfile(profile)
        self._profile.properties.mergeProperties(profile)
        return ret

    ##
    # @if jp
    # @brief LocalServiceProfile を取得する
    #
    # TODO: Documentation
    #
    # @return このオブジェクトが保持している LocalServiceProfile
    #
    # @else
    # @brief Getting LocalServiceProfile
    #
    # TODO: Documentation
    #
    # @return LocalServiceProfile of this service class
    #
    # @endif
    # virtual const LocalServiceProfile& getProfile() const;

    def getProfile(self):
        self._rtcout.RTC_TRACE("getProfile()")
        return self._profile

    ##
    # @if jp
    # @brief 終了関数
    #
    # TODO: Documentation
    #
    # @else
    # @brief Finalization function
    #
    # TODO: Documentation
    #
    # @endif
    # virtual void finalize();

    def finalize(self):
        self.cleanupFiles()
        return

    ##
    # @if jp
    # @brief 名前登録時に呼ばれるコールバック
    #
    # TODO: Documentation
    #
    # @else
    # @brief A call-back at name registration
    #
    # TODO: Documentation
    #
    # @endif
    # void
    # onRegisterNameservice(coil::vstring& path, coil::vstring& ns_info);

    def onRegisterNameservice(self, path, ns_info):
        self._rtcout.RTC_TRACE("onRegisterNameservice(path = %s",
                               OpenRTM_aist.flatten(path))
        self._rtcout.RTC_TRACE(" nsinfo = %s",
                               OpenRTM_aist.flatten(ns_info))

        for p in path:
            filepath_ = self.getFname(p)
            directory_ = os.path.dirname(filepath_)
            self._rtcout.RTC_DEBUG("file path: %s", filepath_)
            self._rtcout.RTC_DEBUG("directory: %s", directory_)
            if not self.createDirectory(directory_):
                continue
            try:
                filename_ = os.path.basename(filepath_)
                self._rtcout.RTC_DEBUG("file name: %s", filename_)
                ofile_ = open(filepath_, 'w')
                ofs_ = []
                for info in ns_info:
                    ofs_.append(info)
                ofile_.writelines(ofs_)
                ofile_.close()
                self._rtcout.RTC_INFO("RTC %s's IOR has been successfully registered: %s",
                                      (filename_, filepath_))
                self._files.append(filepath_)
            except BaseException:
                self._rtcout.RTC_ERROR("Creating file has been failed. %s",
                                       filepath_)
        return

    ##
    # @if jp
    # @brief 名前登録解除に呼ばれるコールバック
    #
    # TODO: Documentation
    #
    # @else
    # @brief A call-back at name runegistration
    #
    # TODO: Documentation
    #
    # @endif
    # void
    # onUnregisterNameservice(coil::vstring& path);

    def onUnregisterNameservice(self, path):
        self._rtcout.RTC_TRACE("onUnregisterNameservice(%s)",
                               OpenRTM_aist.flatten(path))
        for p in path:
            filepath_ = self.getFname(p)
            if not os.path.exists(filepath_):
                self._rtcout.RTC_ERROR("No such file: %s", filepath_)
                continue

            found_path_ = self._files.count(filepath_)
            if not found_path_:
                self._rtcout.RTC_WARN("This file (%s) might not be my file.",
                                      filepath_)
                continue
            found_idx_ = self._files.index(filepath_)
            del self._files[found_idx_]

            try:
                os.remove(filepath_)
                self._rtcout.RTC_DEBUG("Removing file: %s", filepath_)
            except BaseException:
                self._rtcout.RTC_ERROR("Removing a file has been failed. %s",
                                       filepath_)
                continue

            self._rtcout.RTC_PARANOID("Removing a file done: %s", filepath_)

        return

    ##
    # @if jp
    # @brief ディレクトリ作成
    # TODO: Documentation
    # @else
    # @brief Creating directories
    # TODO: Documentation
    # @endif
    # bool createDirectory(fs::path& directory);

    def createDirectory(self, directory):
        self._rtcout.RTC_TRACE("createDirectory(%s)", directory)
        if not os.path.exists(directory):
            self._rtcout.RTC_DEBUG("Directory %s not found", directory)
            try:
                os.makedirs(directory)
                self._rtcout.RTC_DEBUG("Creating directory: %s", directory)
            except BaseException:
                self._rtcout.RTC_ERROR("Creating directory has been failed. %s",
                                       directory)
                return False

            self._rtcout.RTC_PARANOID("Creating directory done: %s",
                                      directory)

        elif os.path.exists(directory) and os.path.isdir(directory):
            self._rtcout.RTC_DEBUG("Directory %s exists.", directory)

        else:
            self._rtcout.RTC_ERROR("File exists instead of base directory %s.",
                                   directory)
            return False

        return True

    ##
    # @if jp
    # @brief ファイル名取得
    # TODO: Documentation
    # @else
    # @brief Getting file name
    # TODO: Documentation
    # @endif
    # std::string getFname(std::string& path) const;

    def getFname(self, path):
        self._rtcout.RTC_TRACE("getFname(%s)", path)

        pathstring_ = self._profile.properties.getProperty("base_path")
        pathstring_ += "/"

        fs_ = self._profile.properties.getProperty("file_structure")
        fs_ = fs_.strip().lower()

        if fs_ == "flat":
            self._rtcout.RTC_DEBUG("file_structure = flat")
            d_ = self._profile.properties.getProperty("context_delimiter")
            ns_path_ = OpenRTM_aist.replaceString(path, "/", d_)
            pathstring_ += ns_path_

        elif fs_ == "tree":
            self._rtcout.RTC_DEBUG("file_structure = tree")
            pathstring_ += path

        self._rtcout.RTC_DEBUG("path string = %s", pathstring_)

        return pathstring_

    ##
    # @if jp
    # @brief 全ファイル削除
    # TODO: Documentation
    # @else
    # @brief Deleting all files
    # TODO: Documentation
    # @endif
    # void cleanupFiles();

    def cleanupFiles(self):
        self._rtcout.RTC_TRACE("cleanupFiles()")
        for file in self._files:
            os.remove(file)

        self._files = []

    ##
    # @if jp
    # @brief プロパティの処理
    # TODO: Documentation
    # @else
    # @brief Processing properties
    # TODO: Documentation
    # @endif
    # bool processServiceProfile(const ::coil::Properties& props);

    def processServiceProfile(self, props):
        return True


##
# @if jp
# @class NamingAction class
# TODO: Documentation
# @else
# @class NamingActin class
# TODO: Documentation
# @endif
class NamingAction:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    def __init__(self, fns):
        self._fns = fns
        return

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif

    def __del__(self):
        return

    ##
    # @if jp
    # @brief preBind コールバック関数
    # TODO: Documentation
    # @else
    # @brief preBind callback function
    # TODO: Documentation
    # @endif
    # virtual void preBind(RTC::RTObject_impl* rtobj,
    #                      coil::vstring& name);

    def preBind(self, rtobj, name):
        objref_ = rtobj.getObjRef()
        ior_ = OpenRTM_aist.Manager.instance().getORB().object_to_string(objref_)
        ns_info_ = [ior_]
        self._fns.onRegisterNameservice(name, ns_info_)
        return

    ##
    # @if jp
    # @brief postBind コールバック関数
    # TODO: Documentation
    # @else
    # @brief postBind callback function
    # TODO: Documentation
    # @endif
    # virtual void postBind(RTC::RTObject_impl* rtobj,
    #                       coil::vstring& name);

    def postBind(self, rtobj, name):
        return

    ##
    # @if jp
    # @brief preUnbind コールバック関数
    # TODO: Documentation
    # @else
    # @brief preUnbind callback function
    # TODO: Documentation
    # @endif
    # virtual void preUnbind(RTC::RTObject_impl* rtobj,
    #                        coil::vstring& name);

    def preUnbind(self, rtobj, name):
        return

    ##
    # @if jp
    # @brief postUnbind コールバック関数
    # TODO: Documentation
    # @else
    # @brief postUnbind callback function
    # TODO: Documentation
    # @endif
    # virtual void postUnbind(RTC::RTObject_impl* rtobj,
    #                         coil::vstring& name);

    def postUnbind(self, rtobj, name):
        self._fns.onUnregisterNameservice(name)
        return


##
# @if jp
# @brief モジュール初期化関数
#
# FileNameserviceをファクトリに登録する初期化関数。
#
# @else
# @brief Module initialization
#
# This initialization function registers FileNameservice to the factory.
#
# @endif
def FileNameserviceInit(manager):
    global service_name
    factory_ = OpenRTM_aist.LocalServiceFactory.instance()
    factory_.addFactory(service_name,
                        FileNameservice)
    return
