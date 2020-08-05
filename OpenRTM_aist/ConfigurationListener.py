#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ConfigurationListener.py
# @brief Configuration related event listener classes
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


##
# @if jp
# @brief ConfigurationParamListener のタイプ
#
# - ON_UPDATE_CONFIG_PARAM,
#
# @else
# @brief The types of ConfigurationParamListenerType
#
# - ON_UPDATE_CONFIG_PARAM,
#
# @endif
#
class ConfigurationParamListenerType:
    """
    """

    def __init__(self):
        pass

    ON_UPDATE_CONFIG_PARAM = 0
    CONFIG_PARAM_LISTENER_NUM = 1


##
# @if jp
# @class ConfigurationParamListener クラス
# @brief ConfigurationParamListener クラス
#
# Configuration パラメータの変更に関するリスナクラス。
# 以下のイベントに対してコールバックされる。
#
# - ON_UPDATE_CONFIG_PARAM: パラメータが変更された
#
# @else
# @class ConfigurationParamListener class
# @brief ConfigurationParamListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events for Configuration parameter.
# The listener will be called on the following event.
#
# - ON_UPDATE_CONFIG_PARAM
#
# @endif
class ConfigurationParamListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief ConfigurationParamListenerType を文字列に変換
    #
    # ConfigurationParamListenerType を文字列に変換する
    #
    # @param type 変換対象 ConfigurationParamListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert ConfigurationParamListenerType into the string.
    #
    # Convert ConfigurationParamListenerType into the string.
    #
    # @param type The target ConfigurationParamListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(ConfigurationParamListenerType type)
    def toString(status):
        typeString = ["ON_UPDATE_CONFIG_PARAM"]

        if status < len(typeString):
            return typeString[status]

        return ""

    toString = staticmethod(toString)

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # ConfigurationParamListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for ConfigurationParamListener.
    #
    # @endif
    # virtual void operator()(const char* config_set_name,
    #                         const char* config_param_name) = 0;

    def __call__(self, config_set_name, config_param_name):
        pass


# ============================================================
##
# @if jp
# @brief ConfigurationSetListener のタイプ
#
# - ON_SET_CONFIG_SET: ConfigurationSet 単位で値がセットされた
# - ON_ADD_CONFIG_SET: ConfigurationSet が追加された
#
# @else
# @brief The types of ConfigurationSetListener
#
# - ON_SET_CONFIG_SET: Value list has been set as a configuration set
# - ON_ADD_CONFIG_SET: A new configuration set has been added
#
# @endif
class ConfigurationSetListenerType:
    """
    """

    def __init__(self):
        pass

    ON_SET_CONFIG_SET = 0
    ON_ADD_CONFIG_SET = 1
    CONFIG_SET_LISTENER_NUM = 2


##
# @if jp
# @class ConfigurationSetListener クラス
# @brief ConfigurationSetListener クラス
#
# Configurationセットが変更されたり追加された場合に呼び出されるリスナクラス。
# 以下のConfigurationセットに関連するイベントに対するリスナ。
#
# - ON_SET_CONFIG_SET: ConfigurationSet 単位で値がセットされた
# - ON_ADD_CONFIG_SET: ConfigurationSet が追加された
#
# @else
# @class ConfigurationSetListener class
# @brief ConfigurationSetListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for configuration set's related events.
#
# - ON_SET_CONFIG_SET: Value list has been set as a configuration set
# - ON_ADD_CONFIG_SET: A new configuration set has been added
#
# @endif
class ConfigurationSetListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief ConfigurationSetListenerType を文字列に変換
    #
    # ConfigurationSetListenerType を文字列に変換する
    #
    # @param type 変換対象 ConfigurationSetListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert ConfigurationSetListenerType into the string.
    #
    # Convert ConfigurationSetListenerType into the string.
    #
    # @param type The target ConfigurationSetListenerType for
    #             transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(ConfigurationSetListenerType type)

    def toString(status):
        typeString = ["ON_SET_CONFIG_SET",
                      "ON_ADD_CONFIG_SET"]
        if status < len(typeString):
            return typeString[status]

        return ""

    toString = staticmethod(toString)

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # ConfigurationSetListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for ConfigurationSetListener
    #
    # @endif
    # virtual void operator()(const coil::Properties& config_set) = 0;

    def __call__(self, config_set):
        pass


# ============================================================
##
# @if jp
# @brief ConfigurationSetNameListenerType
#
# @else
# @brief The types of ConfigurationSetNameListener
#
# @endif
class ConfigurationSetNameListenerType:
    """
    """

    def __init__(self):
        pass

    ON_UPDATE_CONFIG_SET = 0
    ON_REMOVE_CONFIG_SET = 1
    ON_ACTIVATE_CONFIG_SET = 2
    CONFIG_SET_NAME_LISTENER_NUM = 3


##
# @if jp
# @class ConfigurationSetNameListener クラス
# @brief ConfigurationSetNameListener クラス
#
# ConfigurationSetに関するイベントに関するリスナークラス。
#
# - ON_UPDATE_CONFIG_SET:
# - ON_REMOVE_CONFIG_SET:
# - ON_ACTIVATE_CONFIG_SET:
#
# @else
# @class ConfigurationSetNameListener class
# @brief ConfigurationSetNameListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events for ConfigurationSet.
#
# - ON_UPDATE_CONFIG_SET:
# - ON_REMOVE_CONFIG_SET:
# - ON_ACTIVATE_CONFIG_SET:
#
# @endif
class ConfigurationSetNameListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief ConfigurationSetNameListenerType を文字列に変換
    #
    # ConfigurationSetNameListenerType を文字列に変換する
    #
    # @param type 変換対象 ConfigurationSetNameListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert ConfigurationSetNameListenerType into the string.
    #
    # Convert ConfigurationSetNameListenerType into the string.
    #
    # @param type The target ConfigurationSetNameListenerType for
    #             transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(ConfigurationSetNameListenerType type)

    def toString(status):
        typeString = ["ON_UPDATE_CONFIG_SET",
                      "ON_REMOVE_CONFIG_SET",
                      "ON_ACTIVATE_CONFIG_SET"]
        if status < len(typeString):
            return typeString[status]

        return ""

    toString = staticmethod(toString)

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # ConfigurationSetNameListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for ConfigurationSetNameListener.
    #
    # @endif
    # virtual void operator()(const char* config_set_name) = 0;

    def __call__(self, config_set_name):
        pass


##
# @if jp
# @class ConfigurationParamListenerHolder
# @brief ConfigurationParamListener ホルダクラス
#
# 複数の ConfigurationParamListener を保持し管理するクラス。
#
# @else
# @class ConfigurationParamListenerHolder
# @brief ConfigurationParamListener holder class
#
# This class manages one ore more instances of
# ConfigurationParamListener class.
#
# @endif
class ConfigurationParamListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    # ConfigurationParamListenerHolder();
    def __init__(self):
        self._listeners = []
        pass

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif

    def __del__(self):
        for (idx, listener) in enumerate(self._listeners):
            del self._listeners[idx]
        return

    ##
    # @if jp
    #
    # @brief リスナーの追加
    #
    # リスナーを追加する。
    #
    # @param listener 追加するリスナ
    # @else
    #
    # @brief Add the listener.
    #
    # This method adds the listener.
    #
    # @param listener Added listener
    # @endif
    # void addListener(ConfigurationParamListener* listener);

    def addListener(self, listener):
        self._listeners.append(listener)
        return

    ##
    # @if jp
    #
    # @brief リスナーの削除
    #
    # リスナを削除する。
    #
    # @param listener 削除するリスナ
    # @else
    #
    # @brief Remove the listener.
    #
    # This method removes the listener.
    #
    # @param listener Removed listener
    # @endif
    # void removeListener(ConfigurationParamListener* listener);

    def removeListener(self, listener):
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
                return
        return

    ##
    # @if jp
    #
    # @brief リスナーへ通知する
    #
    # 登録されているリスナのコールバックメソッドを呼び出す。
    #
    # @param info ConnectorInfo
    # @param cdrdata データ
    # @else
    #
    # @brief Notify listeners.
    #
    # This calls the Callback method of the registered listener.
    #
    # @param info ConnectorInfo
    # @param cdrdata Data
    # @endif
    # void notify(const char* config_set_name, const char* config_param_name);

    def notify(self, config_set_name, config_param_name):
        for listener in self._listeners:
            listener(config_set_name, config_param_name)
        return


# ============================================================
##
# @if jp
# @class ConfigurationSetListenerHolder
# @brief ConfigurationSetListener ホルダクラス
#
# 複数の ConfigurationSetListener を保持し管理するクラス。
#
# @else
# @class ConfigurationSetListenerHolder
# @brief ConfigurationSetListener holder class
#
# This class manages one ore more instances of
# ConfigurationSetListener class.
#
# @endif
class ConfigurationSetListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    # ConfigurationSetListenerHolder();
    def __init__(self):
        self._listeners = []
        pass

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
    #
    # @brief リスナーの追加
    #
    # リスナーを追加する。
    #
    # @param listener 追加するリスナ
    # @else
    #
    # @brief Add the listener.
    #
    # This method adds the listener.
    #
    # @param listener Added listener
    # @endif
    # void addListener(ConfigurationSetListener* listener);

    def addListener(self, listener):
        self._listeners.append(listener)
        return

    ##
    # @if jp
    #
    # @brief リスナーの削除
    #
    # リスナを削除する。
    #
    # @param listener 削除するリスナ
    # @else
    #
    # @brief Remove the listener.
    #
    # This method removes the listener.
    #
    # @param listener Removed listener
    # @endif
    # void removeListener(ConfigurationSetListener* listener);

    def removeListener(self, listener):
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
                return
        return

    ##
    # @if jp
    #
    # @brief リスナーへ通知する
    #
    # 登録されているリスナのコールバックメソッドを呼び出す。
    #
    # @param info ConnectorInfo
    # @param cdrdata データ
    # @else
    #
    # @brief Notify listeners.
    #
    # This calls the Callback method of the registered listener.
    #
    # @param info ConnectorInfo
    # @param cdrdata Data
    # @endif
    # void notify(const coil::Properties& config_set);

    def notify(self, config_set):
        for listener in self._listeners:
            listener(config_set)
        return


# ============================================================
##
# @if jp
# @class ConfigurationSetNameListenerHolder
# @brief ConfigurationSetNameListener ホルダクラス
#
# 複数の ConfigurationSetNameListener を保持し管理するクラス。
#
# @else
# @class ConfigurationSetNameListenerHolder
# @brief ConfigurationSetNameListener holder class
#
# This class manages one ore more instances of
# ConfigurationSetNameListener class.
#
# @endif
class ConfigurationSetNameListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    # ConfigurationSetNameListenerHolder();
    def __init__(self):
        self._listeners = []
        pass

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
    #
    # @brief リスナーの追加
    #
    # リスナーを追加する。
    #
    # @param listener 追加するリスナ
    # @else
    #
    # @brief Add the listener.
    #
    # This method adds the listener.
    #
    # @param listener Added listener
    # @endif
    # void addListener(ConfigurationSetNameListener* listener);

    def addListener(self, listener):
        self._listeners.append(listener)
        return

    ##
    # @if jp
    #
    # @brief リスナーの削除
    #
    # リスナを削除する。
    #
    # @param listener 削除するリスナ
    # @else
    #
    # @brief Remove the listener.
    #
    # This method removes the listener.
    #
    # @param listener Removed listener
    # @endif
    # void removeListener(ConfigurationSetNameListener* listener);

    def removeListener(self, listener):
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
                return
        return

    ##
    # @if jp
    #
    # @brief リスナーへ通知する
    #
    # 登録されているリスナのコールバックメソッドを呼び出す。
    #
    # @param info ConnectorInfo
    # @else
    #
    # @brief Notify listeners.
    #
    # This calls the Callback method of the registered listener.
    #
    # @param info ConnectorInfo
    # @endif
    # void notify(const char* config_set_name);

    def notify(self, config_set_name):
        for listener in self._listeners:
            listener(config_set_name)
        return


# ------------------------------------------------------------
##
# @if jp
# @class ConfigurationActionListeners
# @brief ConfigurationActionListeners クラス
#
#
# @else
# @class ConfigurationActionListeners
# @brief ConfigurationActionListeners class
#
#
# @endif
class ConfigurationListeners:
    """
    """
    ##
    # @if jp
    # @brief コンストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    #
    # @endif
    def __init__(self):
        ##
        # @if jp
        # @brief ConfigurationParamListenerTypeリスナ配列
        # ConfigurationParamTypeリスナを格納
        # @else
        # @brief ConfigurationParamListenerType listener array
        # The ConfigurationParamListenerType listener is stored.
        # @endif
        self.configparam_num = ConfigurationParamListenerType.CONFIG_PARAM_LISTENER_NUM
        self.configparam_ = [ConfigurationParamListenerHolder()
                             for i in range(self.configparam_num)]

        ##
        # @if jp
        # @brief ConfigurationSetListenerTypeリスナ配列
        # ConfigurationSetListenerTypeリスナを格納
        # @else
        # @brief ConfigurationSetListenerType listener array
        # The ConfigurationSetListenerType listener is stored.
        # @endif
        self.configset_num = ConfigurationSetListenerType.CONFIG_SET_LISTENER_NUM
        self.configset_ = [ConfigurationSetListenerHolder()
                           for i in range(self.configset_num)]

        ##
        # @if jp
        # @brief ConfigurationSetNameListenerTypeリスナ配列
        # ConfigurationSetNameListenerTypeリスナを格納
        # @else
        # @brief ConfigurationSetNameListenerType listener array
        # The ConfigurationSetNameListenerType listener is stored.
        # @endif
        self.configsetname_num = ConfigurationSetNameListenerType.CONFIG_SET_NAME_LISTENER_NUM
        self.configsetname_ = [ConfigurationSetNameListenerHolder()
                               for i in range(self.configsetname_num)]

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のConfigurationParamListenerを追加する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 追加するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def addConfigParamListener(self, ltype, listener):
        if ltype < len(self.configparam_):
            self.configparam_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のConfigurationSetListenerを追加する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 追加するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def addConfigurationSetListener(self, ltype, listener):
        if ltype < len(self.configset_):
            self.configset_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のConfigurationSetNameListenerを追加する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 追加するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def addConfigurationSetNameListener(self, ltype, listener):
        if ltype < len(self.configsetname_):
            self.configsetname_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のConfigParamListenerを削除する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 削除するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def removeConfigParamListener(self, ltype, listener):
        if ltype < len(self.configparam_):
            self.configparam_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のConfigurationSetListenerを削除する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 削除するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def removeConfigurationSetListener(self, ltype, listener):
        if ltype < len(self.configset_):
            self.configset_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のConfigurationSetNameListenerを削除する。
    #
    # @param self
    # @param ltype リスナの種類
    # @param listener 削除するリスナ
    # @return False：指定の種類のリスナが存在しない
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param listener
    # @return
    #
    # @endif
    def removeConfigurationSetNameListener(self, ltype, listener):
        if ltype < len(self.configsetname_):
            self.configsetname_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のConfigurationParamListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param config_set_name コンフィギュレーションセット名
    # @param config_param_name コンフィギュレーションパラメータ名
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param config_set_name
    # @param config_param_name
    # @return
    #
    # @endif
    def notifyConfigParam(self, ltype, config_set_name, config_param_name):
        if ltype < len(self.configparam_):
            self.configparam_[ltype].notify(config_set_name, config_param_name)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のConfigurationSetListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param config_set コンフィギュレーションセット
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param config_set
    # @return
    #
    # @endif
    def notifyConfigurationSet(self, ltype, config_set):
        if ltype < len(self.configset_):
            self.configset_[ltype].notify(config_set)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のConfigurationSetNameListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param config_set_name コンフィギュレーションセット名
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param config_set_name
    # @return
    #
    # @endif
    def notifyConfigurationSetName(self, ltype, config_set_name):
        if ltype < len(self.configsetname_):
            self.configsetname_[ltype].notify(config_set_name)
