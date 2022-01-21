#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ModuleManager.py
# @brief Loadable modules manager class
# @date $Date: 2007/08/24$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2006-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import sys
import os
import glob
import encodings.aliases
import codecs

import OpenRTM_aist


CONFIG_EXT = "manager.modules.config_ext"
CONFIG_PATH = "manager.modules.config_path"
DETECT_MOD = "manager.modules.detect_loadable"
MOD_LOADPTH = "manager.modules.load_path"
INITFUNC_SFX = "manager.modules.init_func_suffix"
INITFUNC_PFX = "manager.modules.init_func_prefix"
ALLOW_ABSPATH = "manager.modules.abs_path_allowed"
ALLOW_URL = "manager.modules.download_allowed"
MOD_DWNDIR = "manager.modules.download_dir"
MOD_DELMOD = "manager.modules.download_cleanup"
MOD_PRELOAD = "manager.modules.preload"


##
# @if jp
#
# @brief モジュールマネージャクラス
# @class ModuleManager
#
# モジュールのロード、アンロードなどを管理するクラス
#
# @since 0.4.0
#
# @else
#
# @biref ModuleManager class
#
# @endif
class ModuleManager:
    """
    """

    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    # コンストラクタ。
    # 設定された Property オブジェクト内の情報を基に初期化を実行する。
    #
    # @param self
    # @param prop 初期化用プロパティ
    #
    # @else
    #
    # @brief constructor
    #
    # @endif
    def __init__(self, prop):
        self._properties = prop

        self._configPath = prop.getProperty(CONFIG_PATH).split(",")
        for i, cp in enumerate(self._configPath):
            self._configPath[i] = OpenRTM_aist.eraseHeadBlank(
                cp)
        self._loadPath = prop.getProperty(MOD_LOADPTH, "./").split(",")
        for i, lp in enumerate(self._loadPath):
            self._loadPath[i] = OpenRTM_aist.eraseHeadBlank(lp)

        self._absoluteAllowed = OpenRTM_aist.toBool(prop.getProperty(ALLOW_ABSPATH),
                                                    "yes", "no", False)

        self._downloadAllowed = OpenRTM_aist.toBool(prop.getProperty(ALLOW_URL),
                                                    "yes", "no", False)

        self._initFuncSuffix = prop.getProperty(INITFUNC_SFX)
        self._initFuncPrefix = prop.getProperty(INITFUNC_PFX)
        self._modules = OpenRTM_aist.ObjectManager(self.DLLPred)
        self._rtcout = None
        self._mgr = OpenRTM_aist.Manager.instance()
        if not self._rtcout:
            self._rtcout = self._mgr.getLogbuf("ModuleManager")
        self._modprofs = []
        self._loadfailmods = {}
        langs = self._properties.getProperty(
            "manager.supported_languages").split(",")
        for lang in langs:
            lang = lang.strip()
            self._loadfailmods[lang] = []

        self._managerLanguage = self._properties.getProperty(
            "manager.language")

    ##
    # @if jp
    #
    # @brief デストラクタ(未実装)
    #
    # @param self
    #
    # @else
    #
    # @brief destructor
    #
    # @endif
    def __del__(self):
        self.unloadAll()

    ##
    # @if jp
    # @class Error
    # @brief ファイル・オープン失敗例外処理用内部クラス
    # @else
    #
    # @endif

    class Error(Exception):
        def __init__(self, reason_):
            self.reason = reason_

    ##
    # @if jp
    # @class NotFound
    # @brief 未実装部，指定モジュール不明例外処理用内部クラス
    # @else
    #
    # @endif

    class NotFound(Exception):
        def __init__(self, name_):
            self.name = name_

    ##
    # @if jp
    # @class FileNotFound
    # @brief 指定ファイル不明例外処理用内部クラス
    # @else
    #
    # @endif

    class FileNotFound(NotFound):
        def __init__(self, name_):
            ModuleManager.NotFound.__init__(self, name_)

    ##
    # @if jp
    # @class ModuleNotFound
    # @brief 指定モジュール不明例外処理用内部クラス
    # @else
    #
    # @endif

    class ModuleNotFound(NotFound):
        def __init__(self, name_):
            ModuleManager.NotFound.__init__(self, name_)

    ##
    # @if jp
    # @class SymbolNotFound
    # @brief 指定シンボル不明例外処理用内部クラス
    # @else
    #
    # @endif

    class SymbolNotFound(NotFound):
        def __init__(self, name_):
            ModuleManager.NotFound.__init__(self, name_)

    ##
    # @if jp
    # @class NotAllowedOperation
    # @brief 指定操作禁止時例外処理用内部クラス
    # @else
    #
    # @endif

    class NotAllowedOperation(Error):
        def __init__(self, reason_):
            ModuleManager.Error.__init__(self, reason_)

    ##
    # @if jp
    # @class InvalidArguments
    # @brief 指定引数不正時例外処理用内部クラス
    # @else
    #
    # @endif

    class InvalidArguments(Error):
        def __init__(self, reason_):
            ModuleManager.Error.__init__(self, reason_)

    ##
    # @if jp
    # @class InvalidOperation
    # @brief 指定操作不正時例外処理用内部クラス
    # @else
    #
    # @endif

    class InvalidOperation(Error):
        def __init__(self, reason_):
            ModuleManager.Error.__init__(self, reason_)

    ##
    # @if jp
    #
    # @brief モジュールのロード、初期化
    #
    # 指定したファイルを共有ライブラリとしてロードするとともに、
    # 指定した初期化用オペレーションを実行する。
    #
    # @param self
    # @param file_name ロード対象モジュール名 (.pyを除いたファイル名)
    # @param init_func 初期化処理用オペレーション(デフォルト値:None)
    #
    # @return 指定したロード対象モジュール名
    #
    # @else
    #
    # @brief Load module
    #
    #
    # @endif
    # std::string ModuleManager::load(const std::string& file_name,
    #                                 const std::string& init_func)
    def load(self, file_name, init_func=None):

        self._rtcout.RTC_TRACE("load(fname = %s)", file_name)
        if file_name == "":
            raise ModuleManager.InvalidArguments("Invalid file name.")

        if OpenRTM_aist.isURL(file_name):
            if not self._downloadAllowed:
                raise ModuleManager.NotAllowedOperation(
                    "Downloading module is not allowed.")
            else:
                raise ModuleManager.NotFound("Not implemented.")

        import_name = os.path.split(file_name)[-1]
        pathChanged = False
        file_path = None

        name = OpenRTM_aist.replaceEnv(file_name)
        if OpenRTM_aist.isAbsolutePath(name):
            if not self._absoluteAllowed:
                raise ModuleManager.NotAllowedOperation(
                    "Absolute path is not allowed")
            else:
                splitted_name = os.path.split(name)
                save_path = sys.path[:]
                sys.path.append(splitted_name[0])

                pathChanged = True
                import_name = splitted_name[-1]
                file_path = name

        else:
            paths = []
            for path in self._loadPath:
                paths.append(OpenRTM_aist.replaceEnv(path))
            file_path = self.findFile(name, paths)

            if not file_path:
                raise ModuleManager.FileNotFound(file_name)

        if not self.fileExist(file_path):
            raise ModuleManager.FileNotFound(file_name)

        try:
            code = "UTF-8-SIG"
            import chardet
            with open(str(file_path), mode='rb') as f:
                code = chardet.detect(f.read())["encoding"]

            with codecs.open(str(file_path), "r", encoding=code) as f:
                if init_func is not None:
                    s = f.read()
                    if isinstance(s, str):
                        if s.find(init_func) == -1:
                            raise ModuleManager.FileNotFound(file_name)
        except BaseException:
            pass

        if not pathChanged:
            splitted_name = os.path.split(file_path)
            sys.path.append(splitted_name[0])

        ext_pos = import_name.find(".py")
        if ext_pos > 0:
            import_name = import_name[:ext_pos]

        mo = __import__(str(import_name))

        if pathChanged:
            sys.path = save_path

        file_path = file_path.replace("\\", "/")
        file_path = file_path.replace("//", "/")

        dll = self.DLLEntity(mo, OpenRTM_aist.Properties())
        dll.properties.setProperty("file_path", file_path)
        self._modules.registerObject(dll)

        if init_func is None:
            return file_name

        self.symbol(file_path, init_func)(self._mgr)

        return file_name

    ##
    # @if jp
    # @brief モジュールのアンロード
    #
    # 指定したロード済みモジュールをクローズし、アンロードする。
    #
    # @param self
    # @param file_name アンロード対象モジュール名
    #
    # @else
    # @brief Unload module
    # @endif

    def unload(self, file_name):
        dll = self._modules.find(file_name)
        if not dll:
            raise ModuleManager.NotFound(file_name)
        dll_name = dll.dll.__name__
        if dll_name in sys.modules.keys():
            sys.modules.pop(dll_name)
        self._modules.unregisterObject(file_name)
        return

    ##
    # @if jp
    # @brief 全モジュールのアンロード
    #
    # 全てのロード済みモジュールをアンロードする。
    #
    # @param self
    #
    # @else
    # @brief Unload all modules
    # @endif

    def unloadAll(self):
        dlls = self._modules.getObjects()

        for dll in dlls:
            ident = dll.properties.getProperty("file_path")
            self._modules.unregisterObject(ident)
        return

    ##
    # @if jp
    # @brief モジュールのシンボルの参照
    #
    # モジュールのシンボルを取得する
    #
    # @param self
    # @param file_name 取得対象ファイル名
    # @param func_name 取得対象関数名
    #
    # @else
    # @brief Look up a named symbol in the module
    # @endif

    def symbol(self, file_name, func_name):
        dll = self._modules.find(file_name)
        if not dll:
            raise ModuleManager.ModuleNotFound(file_name)

        func = getattr(dll.dll, func_name, None)

        if not func:
            raise ModuleManager.SymbolNotFound(func_name)

        return func

    ##
    # @if jp
    # @brief モジュールロードパスを指定する
    #
    # モジュールロード時に対象モジュールを検索するパスを指定する。
    #
    # @param self
    # @param load_path_list モジュール検索対象パスリスト
    #
    # @else
    # @brief Set default module load path
    # @endif

    def setLoadpath(self, load_path_list):
        self._loadPath = load_path_list
        return

    ##
    # @if jp
    # @brief モジュールロードパスを取得する
    #
    # 設定されているモジュールを検索対象パスリストを取得する。
    #
    # @param self
    #
    # @return load_path モジュール検索対象パスリスト
    #
    # @else
    # @brief Get default module load path
    # @endif

    def getLoadPath(self):
        return self._loadPath

    ##
    # @if jp
    # @brief モジュールロードパスを追加する
    #
    # 指定されたパスリストを検索対象パスリストに追加する。
    #
    # @param self
    # @param load_path 追加モジュール検索対象パスリスト
    #
    # @else
    # @brief Add module load path
    # @endif

    def addLoadpath(self, load_path):
        for path in load_path:
            self._loadPath.append(path)
        return

    ##
    # @if jp
    # @brief ロード済みのモジュールリストを取得する
    #
    # 既にロード済みのモジュールリストを取得する。
    #
    # @param self
    #
    # @return ロード済みモジュールリスト
    #
    # @else
    # @brief Get loaded module names
    # @endif
    # std::vector<coil::Properties> getLoadedModules();

    def getLoadedModules(self):
        dlls = self._modules.getObjects()
        modules = []
        for dll in dlls:
            modules.append(dll.properties)

        return modules

    def __getRtcProfile(self, fname):
        # file name with full path
        fullname = fname
        # directory name
        dirname = os.path.dirname(fullname)
        sys.path.append(dirname)
        # basename
        basename = os.path.basename(fullname)
        # classname
        classname = basename.split(".")[0].lower()

        # loaded profile = old profiles - new profiles
        # for old
        oldp = self._mgr.getFactoryProfiles()

        # for new
        comp_spec_name = classname + "_spec"

        try:
            code = "UTF-8-SIG"
            import chardet
            with open(str(fullname), mode='rb') as f:
                code = chardet.detect(f.read())["encoding"]

            with codecs.open(str(fullname), "r", encoding=code) as f:
                s = f.read()
                if s.find(comp_spec_name) == -1:
                    return None
        except BaseException:
            pass

        imp_file = __import__(basename.split(".")[0])
        comp_spec = getattr(imp_file, comp_spec_name, None)
        if not comp_spec:
            return None
        newp = OpenRTM_aist.Properties(defaults_str=comp_spec)

        profs = []

        exists = False
        for o in oldp:
            if o.getProperty("implementation_id") == newp.getProperty("implementation_id") and \
                    o.getProperty("type_name") == newp.getProperty("type_name") and \
                    o.getProperty("description") == newp.getProperty("description") and \
                    o.getProperty("version") == newp.getProperty("version"):
                exists = True
        if not exists:
            profs.append(newp)

        # loaded component profile have to be one
        if not profs:
            return OpenRTM_aist.Properties()

        # if len(profs) > 1:
        #  return None

        return profs[0]

    ##
    # @if jp
    # @brief 指定言語におけるロードパス上のローダブルなファイルリストを返す
    #
    #
    # @param self
    # @param lang
    # @param modules
    #
    #
    # @else
    # @brief Getting loadable file list on the loadpath for given language
    # @endif

    def getModuleList(self, lang, modules):
        l = "manager.modules." + lang
        lprop = self._properties.getNode(l)

        paths = lprop.getProperty("load_paths").split(",")

        paths.extend(self._loadPath)
        paths = self.deleteSamePath(paths)

        suffixes = lprop.getProperty("suffixes").split(",")

        self._rtcout.RTC_DEBUG("suffixes: %s", OpenRTM_aist.flatten(suffixes))

        for path in paths:
            if not path:
                self._rtcout.RTC_WARN("Given load path is empty")
                continue
            self._rtcout.RTC_DEBUG("Module load path: %s", path)
            flist = []
            path = OpenRTM_aist.replaceEnv(path)
            for suffix in suffixes:
                suffix = OpenRTM_aist.eraseHeadBlank(suffix)

                tmp = []
                OpenRTM_aist.getFileList(path, suffix, tmp)

                if lang == self._managerLanguage:
                    for f in tmp:
                        if f.find("__init__.py") != -1:
                            tmp.remove(f)

                self._rtcout.RTC_DEBUG(
                    "File list (path:%s, ext:%s): %s",
                    (path,
                     suffix,
                     OpenRTM_aist.flatten(suffixes)))
                flist.extend(tmp)

            for f in flist:
                f = f.replace("\\", "/")
                f = f.replace("//", "/")
                self.addNewFile(f, modules, lang)
        modules = list(set(modules))

    ##
    # @if jp
    # @brief キャッシュに無いパスだけmodulesに追加する
    #
    #
    # @param self
    # @param fpath
    # @param modules
    #
    #
    # @else
    # @brief Adding file path not existing cache
    # @endif

    def addNewFile(self, fpath, modules, lang):
        exists = False
        for modprof in self._modprofs:
            if modprof.getProperty("module_file_path") == fpath:
                self._rtcout.RTC_DEBUG(
                    "Module %s already exists in cache.", fpath)
                return

        if not (fpath in self._loadfailmods[lang]):
            self._rtcout.RTC_DEBUG("New module: %s", fpath)
            modules.append(fpath)

    ##
    # @if jp
    # @brief 指定言語、ファイルリストからモジュールのプロパティを返す
    #
    #
    # @param self
    # @param lang
    # @param modules
    # @param modprops
    #
    #
    # @else
    # @brief Getting loadable file list on the loadpath for given language
    # @endif

    def getModuleProfiles(self, lang, modules, modprops):
        l = "manager.modules." + lang
        lprop = self._properties.getNode(l)

        paths = lprop.getProperty("load_paths").split(",")

        for mod_ in modules:

            if lang == self._managerLanguage:
                prop = self.__getRtcProfile(mod_)
                if prop:
                    prop.setProperty(
                        "module_file_name", os.path.basename(mod_))
                    prop.setProperty("module_file_path", mod_)
                    prop.setProperty("language", lang)
                    modprops.append(prop)
            else:
                prop = OpenRTM_aist.Properties()
                cmd = lprop.getProperty("profile_cmd")
                if os.name == "nt":
                    cmd = "cmd /c " + cmd
                cmd = cmd + " \"" + mod_ + "\""

                try:
                    ret = OpenRTM_aist.popen(cmd).split(os.linesep)
                    count = 0
                    for r in ret:
                        pos = r.find(":")
                        if r.find(":") != -1:
                            count += 1
                            key = r[0:pos]
                            key = OpenRTM_aist.eraseHeadBlank(key)

                            value = r[pos + 1:]
                            value = OpenRTM_aist.eraseHeadBlank(value)

                            prop.setProperty(key, value)
                    if count > 0:
                        self._rtcout.RTC_DEBUG("rtcprof cmd sub process done.")
                        prop.setProperty(
                            "module_file_name", os.path.basename(mod_))
                        prop.setProperty("module_file_path", mod_)
                        prop.setProperty("language", lang)
                        modprops.append(prop)
                    else:
                        self._loadfailmods[lang].append(mod_)

                except BaseException:
                    self._rtcout.RTC_ERROR("popen faild")
                    self._loadfailmods[lang].append(mod_)

    ##
    # @if jp
    # @brief 無効なモジュールプロファイルを削除する
    #
    #
    # @param self
    #
    #
    # @else
    # @brief Removing incalid module profiles
    # @endif

    def removeInvalidModules(self):
        for modprof in self._modprofs:
            if not os.path.isfile(modprof.getProperty("module_file_path")):
                self._modprofs.remove(modprof)

    ##
    # @if jp
    # @brief 同じパスを削除
    #
    #
    # @param self
    # @param paths
    #
    #
    # @else
    # @brief
    # @endif

    def deleteSamePath(self, paths):
        tmp_paths = []
        for path in paths:
            if path:
                abs_path = os.path.abspath(path).replace("\\", "/")
                abs_tmp_paths = []
                for tmp_path in tmp_paths:
                    abs_tmp_path = os.path.abspath(tmp_path).replace("\\", "/")
                    abs_tmp_paths.append(abs_tmp_path)
                if abs_path not in abs_tmp_paths:
                    tmp_paths.append(path)
        return tmp_paths

    ##
    # @if jp
    # @brief ロード可能モジュールリストを取得する(未実装)
    #
    # ロード可能なモジュールのリストを取得する。
    #
    # @param self
    #
    # @return ロード可能モジュールリスト
    #
    # @else
    # @brief Get loadable module names
    # @endif

    def getLoadableModules(self):
        self._rtcout.RTC_TRACE("getLoadableModules()")
        # getting loadable module file path list.
        langs = self._properties.getProperty(
            "manager.supported_languages").split(",")
        self._rtcout.RTC_DEBUG(
            "langs: %s",
            self._properties.getProperty("manager.supported_languages"))

        for lang in langs:
            lang = lang.strip()

            modules_ = []
            self.getModuleList(lang, modules_)
            self._rtcout.RTC_DEBUG(
                "%s: %s", (lang, OpenRTM_aist.flatten(modules_)))

            tmpprops = []
            self.getModuleProfiles(lang, modules_, tmpprops)
            self._rtcout.RTC_DEBUG(
                "Modile profile size: %d (newly founded modules)",
                len(tmpprops))

            self._modprofs.extend(tmpprops)

        self._rtcout.RTC_DEBUG("Modile profile size: %d", len(self._modprofs))
        self.removeInvalidModules()
        self._rtcout.RTC_DEBUG(
            "Modile profile size: %d (invalid mod-profiles deleted)", len(self._modprofs))

        return self._modprofs

    ##
    # @if jp
    # @brief モジュールの絶対パス指定許可
    #
    # ロード対象モジュールの絶対パス指定を許可するように設定する。
    #
    # @param self
    #
    # @else
    # @brief Allow absolute load path
    # @endif

    def allowAbsolutePath(self):
        self._absoluteAllowed = True

    ##
    # @if jp
    # @brief モジュールの絶対パス指定禁止
    #
    # ロード対象モジュールの絶対パス指定を禁止するように設定する。
    #
    # @param self
    #
    # @else
    # @brief Forbid absolute load path
    # @endif

    def disallowAbsolutePath(self):
        self._absoluteAllowed = False

    ##
    # @if jp
    # @brief モジュールのURL指定許可
    #
    # ロード対象モジュールのURL指定を許可する。
    # 本設定が許可されている場合、モジュールをダウンロードしてロードすることが
    # 許可される。
    #
    # @param self
    #
    # @else
    # @brief Allow module download
    # @endif

    def allowModuleDownload(self):
        self._downloadAllowed = True

    ##
    # @if jp
    # @brief モジュールのURL指定禁止
    #
    # ロード対象モジュールのURL指定を禁止する。
    #
    # @param self
    #
    # @else
    # @brief Forbid module download
    # @endif

    def disallowModuleDownload(self):
        self._downloadAllowed = False

    ##
    # @if jp
    # @brief LoadPath からのファイルの検索
    #
    # 指定されたパス内に、指定されたファイルが存在するか確認する。
    #
    # @param self
    # @param fname 検索対象ファイル名
    # @param load_path 検索先パスリスト
    #
    # @return 検索されたファイル名
    #
    # @else
    # @brief Search file from load path
    # @endif

    def findFile(self, fname, load_path):
        file_name = fname
        for path in load_path:
            suffix = self._properties.getProperty(
                "manager.modules."+self._managerLanguage+".suffixes")
            if fname.find("." + suffix) == -1:
                f = str(path) + os.sep + str(file_name) + "." + suffix
            else:
                f = str(path) + os.sep + str(file_name)
            if self.fileExist(f):
                f = f.replace("\\", "/")
                f = f.replace("//", "/")
                return f
            filelist = []
            OpenRTM_aist.findFile(path, file_name, filelist)

            if filelist:
                return filelist[0]
        return ""

    ##
    # @if jp
    # @brief ファイルが存在するかどうかのチェック
    #
    # 指定されたファイルが存在するか確認する。
    #
    # @param self
    # @param filename 存在確認対象ファイル名
    #
    # @return ファイル存在確認結果(ファイルあり:true，なし:false)
    #
    # @else
    # @brief Check file existance
    # @endif

    def fileExist(self, filename):
        fname = filename
        suffix = self._properties.getProperty(
            "manager.modules."+self._managerLanguage+".suffixes")
        if fname.find("." + suffix) == -1:
            fname = str(filename) + "." + suffix

        if os.path.isfile(fname):
            return True

        return False

    ##
    # @if jp
    # @brief 初期化関数シンボルを生成する
    #
    # 初期化関数の名称を組み立てる。
    #
    # @param self
    # @param file_path 初期化対象モジュール名称
    #
    # @return 初期化関数名称組み立て結果
    #
    # @else
    # @brief Create initialize function symbol
    # @endif

    def getInitFuncName(self, file_path):
        base_name = os.path.basename(file_path)
        return str(self._initFuncPrefix) + \
            str(base_name) + str(self._initFuncSuffix)

    ##
    # @if jp
    # @class DLL
    # @brief モジュール保持用内部クラス
    # @else
    #
    # @endif

    class DLL:
        def __init__(self, dll):
            self.dll = dll
            return

    class DLLEntity:
        def __init__(self, dll, prop):
            self.dll = dll
            self.properties = prop

    class DLLPred:
        def __init__(self, name=None, factory=None):
            if name is not None:
                self._filepath = name
            else:
                self._filepath = factory.properties.getProperty(
                    "file_path")

        def __call__(self, dll):
            try:
                return os.path.samefile(
                    self._filepath,
                    dll.properties.getProperty("file_path")
                )
            except FileNotFoundError:
                return self._filepath == dll.properties.getProperty("file_path")
            except BaseException:
                return False
