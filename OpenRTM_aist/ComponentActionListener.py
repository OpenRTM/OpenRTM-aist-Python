#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ComponentActionListener.py
# @brief component action listener class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


# ============================================================

##
# @if jp
# @brief PreComponentActionListener のタイプ
#
# - PRE_ON_INITIALIZE:    onInitialize 直前
# - PRE_ON_FINALIZE:      onFinalize 直前
# - PRE_ON_STARTUP:       onStartup 直前
# - PRE_ON_SHUTDOWN:      onShutdown 直前
# - PRE_ON_ACTIVATED:     onActivated 直前
# - PRE_ON_DEACTIVATED:   onDeactivated 直前
# - PRE_ON_ABORTING:      onAborted 直前
# - PRE_ON_ERROR:         onError 直前
# - PRE_ON_RESET:         onReset 直前
# - PRE_ON_EXECUTE:       onExecute 直前
# - PRE_ON_STATE_UPDATE:  onStateUpdate 直前
# - PRE_ON_RATE_CHANGED:  onRateChanged 直前
#
# @else
# @brief The types of PreComponentActionListenerType
#
# @endif
class PreComponentActionListenerType:
    """
    """

    def __init__(self):
        pass

    PRE_ON_INITIALIZE = 0
    PRE_ON_FINALIZE = 1
    PRE_ON_STARTUP = 2
    PRE_ON_SHUTDOWN = 3
    PRE_ON_ACTIVATED = 4
    PRE_ON_DEACTIVATED = 5
    PRE_ON_ABORTING = 6
    PRE_ON_ERROR = 7
    PRE_ON_RESET = 8
    PRE_ON_EXECUTE = 9
    PRE_ON_STATE_UPDATE = 10
    PRE_ON_RATE_CHANGED = 11
    PRE_COMPONENT_ACTION_LISTENER_NUM = 12


##
# @if jp
# @class PreComponentActionListener クラス
# @brief PreComponentActionListener クラス
#
# OMG RTC仕様で定義されている以下のコンポーネントアクショントについ
# て、
#
# - on_initialize()
# - on_finalize()
# - on_startup()
# - on_shutdown()
# - on_activated
# - on_deactivated()
# - on_aborted()
# - on_error()
# - on_reset()
# - on_execute()
# - on_state_update()
# - on_rate_changed()
#
# 各アクションに対応するユーザーコードが呼ばれる直前のタイミング
# でコールされるリスナクラスの基底クラス。
#
# - PRE_ON_INITIALIZE:
# - PRE_ON_FINALIZE:
# - PRE_ON_STARTUP:
# - PRE_ON_SHUTDOWN:
# - PRE_ON_ACTIVATED:
# - PRE_ON_DEACTIVATED:
# - PRE_ON_ABORTING:
# - PRE_ON_ERROR:
# - PRE_ON_RESET:
# - PRE_IN_EXECUTE:
# - PRE_ON_STATE_UPDATE:
# - PRE_ON_RATE_CHANGED:
#
# @else
# @class PreComponentActionListener class
# @brief PreComponentActionListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events in rtobject.
#
# @endif
class PreComponentActionListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief PreComponentActionListenerType を文字列に変換
    #
    # PreComponentActionListenerType を文字列に変換する
    #
    # @param type 変換対象 PreComponentActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert PreComponentActionListenerType into the string.
    #
    # Convert PreComponentActionListenerType into the string.
    #
    # @param type The target PreComponentActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(PreComponentActionListenerType type)
    def toString(status):
        typeString = ["PRE_ON_INITIALIZE",
                      "PRE_ON_FINALIZE",
                      "PRE_ON_STARTUP",
                      "PRE_ON_SHUTDOWN",
                      "PRE_ON_ACTIVATED",
                      "PRE_ON_DEACTIVATED",
                      "PRE_ON_ABORTING",
                      "PRE_ON_ERROR",
                      "PRE_ON_RESET",
                      "PRE_ON_EXECUTE",
                      "PRE_ON_STATE_UPDATE",
                      "PRE_ON_RATE_CHANGED"]
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
    # PreComponentActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for PreComponentActionListener.
    #
    # @endif
    # virtual void operator()(UniqueId ec_id) = 0;
    def __call__(self, ec_id):
        pass


# ============================================================

##
# @if jp
# @brief PostCompoenntActionListener のタイプ
#
# - POST_ON_INITIALIZE:
# - POST_ON_FINALIZE:
# - POST_ON_STARTUP:
# - POST_ON_SHUTDOWN:
# - POST_ON_ACTIVATED:
# - POST_ON_DEACTIVATED:
# - POST_ON_ABORTING:
# - POST_ON_ERROR:
# - POST_ON_RESET:
# - POST_ON_EXECUTE:
# - POST_ON_STATE_UPDATE:
# - POST_ON_RATE_CHANGED:
#
# @else
# @brief The types of PostComponentActionListenerType
#
# @endif
class PostComponentActionListenerType:
    """
    """

    def __init__(self):
        pass

    POST_ON_INITIALIZE = 0
    POST_ON_FINALIZE = 1
    POST_ON_STARTUP = 2
    POST_ON_SHUTDOWN = 3
    POST_ON_ACTIVATED = 4
    POST_ON_DEACTIVATED = 5
    POST_ON_ABORTING = 6
    POST_ON_ERROR = 7
    POST_ON_RESET = 8
    POST_ON_EXECUTE = 9
    POST_ON_STATE_UPDATE = 10
    POST_ON_RATE_CHANGED = 11
    POST_COMPONENT_ACTION_LISTENER_NUM = 12


##
# @if jp
# @class PostComponentActionListener クラス
# @brief PostComponentActionListener クラス
#
# OMG RTC仕様で定義されている以下のコンポーネントアクショントについ
# て、
#
# - on_initialize()
# - on_finalize()
# - on_startup()
# - on_shutdown()
# - on_activated
# - on_deactivated()
# - on_aborted()
# - on_error()
# - on_reset()
# - on_execute()
# - on_state_update()
# - on_rate_changed()
#
# 各アクションに対応するユーザーコードが呼ばれる直前のタイミング
# でコールされるリスなクラスの基底クラス。
#
# - POST_ON_INITIALIZE:
# - POST_ON_FINALIZE:
# - POST_ON_STARTUP:
# - POST_ON_SHUTDOWN:
# - POST_ON_ACTIVATED:
# - POST_ON_DEACTIVATED:
# - POST_ON_ABORTING:
# - POST_ON_ERROR:
# - POST_ON_RESET:
# - POST_ON_EXECUTE:
# - POST_ON_STATE_UPDATE:
# - POST_ON_RATE_CHANGED:
#
# @else
# @class PostComponentActionListener class
# @brief PostComponentActionListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events in rtobject.
#
# @endif
class PostComponentActionListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief PostComponentActionListenerType を文字列に変換
    #
    # PostComponentActionListenerType を文字列に変換する
    #
    # @param type 変換対象 PostComponentActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert PostComponentActionListenerType into the string.
    #
    # Convert PostComponentActionListenerType into the string.
    #
    # @param type The target PostComponentActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(PostComponentActionListenerType type)
    def toString(status):
        typeString = ["POST_ON_INITIALIZE",
                      "POST_ON_FINALIZE",
                      "POST_ON_STARTUP",
                      "POST_ON_SHUTDOWN",
                      "POST_ON_ACTIVATED",
                      "POST_ON_DEACTIVATED",
                      "POST_ON_ABORTING",
                      "POST_ON_ERROR",
                      "POST_ON_RESET",
                      "POST_ON_EXECUTE",
                      "POST_ON_STATE_UPDATE",
                      "POST_ON_RATE_CHANGED"]
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
    # PostComponentActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for PostComponentActionListener.
    #
    # @endif
    # virtual void operator()(UniqueId ec_id,
    #                        ReturnCode_t ret) = 0;
    def __call__(self, ec_id, ret):
        pass


# ============================================================
##
# @if jp
# @brief PortActionListener のタイプ
#
# - ADD_PORT:             Port 追加時
# - REMOVE_PORT:          Port 削除時
#
# @else
# @brief The types of PortActionListener
#
# @endif
class PortActionListenerType:
    """
    """

    def __init__(self):
        pass

    ADD_PORT = 0
    REMOVE_PORT = 1
    PORT_ACTION_LISTENER_NUM = 2


##
# @if jp
# @class PortActionListener クラス
# @brief PortActionListener クラス
#
# 各アクションに対応するユーザーコードが呼ばれる直前のタイミング
# でコールされるリスなクラスの基底クラス。
#
# - ADD_PORT:
# - REMOVE_PORT:
#
# @else
# @class PortActionListener class
# @brief PortActionListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events in rtobject.
#
# @endif
class PortActionListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief PortActionListenerType を文字列に変換
    #
    # PortActionListenerType を文字列に変換する
    #
    # @param type 変換対象 PortActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert PortActionListenerType into the string.
    #
    # Convert PortActionListenerType into the string.
    #
    # @param type The target PortActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(PortActionListenerType type)
    def toString(status):
        typeString = ["ADD_PORT",
                      "REMOVE_PORT"]
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
    # virtual ~PortActionListener();
    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # PortActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for PortActionListener
    #
    # @endif
    # virtual void operator()(const ::RTC::PortProfile& pprof) = 0;
    def __call__(self, pprof):
        pass


# ============================================================
##
# @if jp
# @brief ExecutionContextActionListener のタイプ
#
# - EC_ATTACHED:          ExecutionContext 追加時
# - EC_DETACHED:          ExecutionContext 削除時
#
# @else
# @brief The types of ExecutionContextActionListener
#
# @endif
class ExecutionContextActionListenerType:
    """
    """

    def __init__(self):
        pass

    EC_ATTACHED = 0
    EC_DETACHED = 1
    EC_ACTION_LISTENER_NUM = 2

##
# @if jp
# @class ExecutionContextActionListener クラス
# @brief ExecutionContextActionListener クラス
#
# 各アクションに対応するユーザーコードが呼ばれる直前のタイミング
# でコールされるリスなクラスの基底クラス。
#
# - ADD_PORT:
# - REMOVE_PORT:
#
# @else
# @class ExecutionContextActionListener class
# @brief ExecutionContextActionListener class
#
# This class is abstract base class for listener classes that
# provides callbacks for various events in rtobject.
#
# @endif


class ExecutionContextActionListener:
    """
    """

    def __init__(self):
        pass

    ##
    # @if jp
    #
    # @brief ExecutionContextActionListenerType を文字列に変換
    #
    # ExecutionContextActionListenerType を文字列に変換する
    #
    # @param type 変換対象 ExecutionContextActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert ExecutionContextActionListenerType into the string.
    #
    # Convert ExecutionContextActionListenerType into the string.
    #
    # @param type The target ExecutionContextActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    # static const char* toString(ExecutionContextActionListenerType type)

    def toString(status):
        typeString = ["ATTACH_EC",
                      "DETACH_EC"]
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
    # ExecutionContextActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for ExecutionContextActionListener
    #
    # @endif
    # virtual void operator()(UniqueId ec_id) = 0;
    def __call__(self, ec_id):
        pass


# ============================================================
##
# @if jp
# @class PreComponentActionListenerHolder
# @brief PreComponentActionListener ホルダクラス
#
# 複数の PreComponentActionListener を保持し管理するクラス。
#
# @else
# @class PreComponentActionListenerHolder
# @brief PreComponentActionListener holder class
#
# This class manages one ore more instances of
# PreComponentActionListener class.
#
# @endif
class PreComponentActionListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):
        self._listeners = []
        return

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
    # void addListener(PreComponentActionListener* listener);
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
    # void removeListener(PreComponentActionListener* listener);
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
    # void notify(UniqueId ec_id);
    def notify(self, ec_id):
        for listener in self._listeners:
            listener(ec_id)
        return


##
# @if jp
# @class PostComponentActionListenerHolder
# @brief PostComponentActionListener ホルダクラス
#
# 複数の PostComponentActionListener を保持し管理するクラス。
#
# @else
# @class PostComponentActionListenerHolder
# @brief PostComponentActionListener holder class
#
# This class manages one ore more instances of
# PostComponentActionListener class.
#
# @endif
class PostComponentActionListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):
        self._listeners = []
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
    # void addListener(PostComponentActionListener* listener);
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
    # void removeListener(PostComponentActionListener* listener);
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
    # void notify(UniqueId ec_id, ReturnCode_t ret);

    def notify(self, ec_id, ret):
        for listener in self._listeners:
            listener(ec_id, ret)
        return


# ============================================================
##
# @if jp
# @class PortActionListenerHolder
# @brief PortActionListener ホルダクラス
#
# 複数の PortActionListener を保持し管理するクラス。
#
# @else
# @class PortActionListenerHolder
# @brief PortActionListener holder class
#
# This class manages one ore more instances of
# PortActionListener class.
#
# @endif
class PortActionListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):
        self._listeners = []
        return

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
    # void addListener(PortActionListener* listener);
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
    # void removeListener(PortActionListener* listener);

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
    # void notify(const RTC::PortProfile& pprofile);
    def notify(self, pprofile):
        for listener in self._listeners:
            listener(pprofile)
        return


##
# @if jp
# @class ExecutionContextActionListenerHolder
# @brief ExecutionContextActionListener ホルダクラス
#
# 複数の ExecutionContextActionListener を保持し管理するクラス。
#
# @else
# @class ExecutionContextActionListenerHolder
# @brief ExecutionContextActionListener holder class
#
# This class manages one ore more instances of
# ExecutionContextActionListener class.
#
# @endif
class ExecutionContextActionListenerHolder:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):
        self._listeners = []
        return

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
    # void addListener(ExecutionContextActionListener* listener);

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
    # void removeListener(ExecutionContextActionListener* listener);

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
    # void notify(UniqueId ec_id);

    def notify(self, ec_id):
        for listener in self._listeners:
            listener(ec_id)
        return


##
# @if jp
# @class ComponentActionListeners
# @brief ComponentActionListeners クラス
#
#
# @else
# @class ComponentActionListeners
# @brief ComponentActionListeners class
#
#
# @endif
class ComponentActionListeners:
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
        # @brief PreComponentActionListenerTypeリスナ配列
        # PreComponentActionListenerTypeリスナを格納
        # @else
        # @brief PreComponentActionListenerType listener array
        # The PreComponentActionListenerType listener is stored.
        # @endif
        self.preaction_num = PreComponentActionListenerType.PRE_COMPONENT_ACTION_LISTENER_NUM
        self.preaction_ = [PreComponentActionListenerHolder()
                           for i in range(self.preaction_num)]

        ##
        # @if jp
        # @brief PostComponentActionListenerTypeリスナ配列
        # PostComponentActionListenerTypeリスナを格納
        # @else
        # @brief PostComponentActionListenerType listener array
        # The PostComponentActionListenerType listener is stored.
        # @endif
        self.postaction_num = PostComponentActionListenerType.POST_COMPONENT_ACTION_LISTENER_NUM
        self.postaction_ = [PostComponentActionListenerHolder()
                            for i in range(self.postaction_num)]

        ##
        # @if jp
        # @brief PortActionListenerTypeリスナ配列
        # PortActionListenerTypeリスナを格納
        # @else
        # @brief PortActionListenerType listener array
        # The PortActionListenerType listener is stored.
        # @endif
        self.portaction_num = PortActionListenerType.PORT_ACTION_LISTENER_NUM
        self.portaction_ = [PortActionListenerHolder()
                            for i in range(self.portaction_num)]

        ##
        # @if jp
        # @brief ExecutionContextActionListenerTypeリスナ配列
        # ExecutionContextActionListenerTypeリスナを格納
        # @else
        # @brief ExecutionContextActionListenerType listener array
        # The ExecutionContextActionListenerType listener is stored.
        # @endif
        self.ecaction_num = ExecutionContextActionListenerType.EC_ACTION_LISTENER_NUM
        self.ecaction_ = [ExecutionContextActionListenerHolder()
                          for i in range(self.ecaction_num)]

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のPreComponentActionListenerを追加する。
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
    def addPreActionListener(self, ltype, listener):
        if ltype < len(self.preaction_):
            self.preaction_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のPostComponentActionListenerを追加する。
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
    def addPostActionListener(self, ltype, listener):
        if ltype < len(self.postaction_):
            self.postaction_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のPortActionListenerを追加する。
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
    def addPortActionListener(self, ltype, listener):
        if ltype < len(self.portaction_):
            self.portaction_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のExecutionContextActionListenerを追加する。
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
    def addECActionListener(self, ltype, listener):
        if ltype < len(self.ecaction_):
            self.ecaction_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のPreComponentActionListenerを削除する。
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
    def removePreActionListener(self, ltype, listener):
        if ltype < len(self.preaction_):
            self.preaction_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のPostComponentActionListenerを削除する。
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
    def removePostActionListener(self, ltype, listener):
        if ltype < len(self.postaction_):
            self.postaction_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のPortActionListenerを削除する。
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
    def removePortActionListener(self, ltype, listener):
        if ltype < len(self.portaction_):
            self.portaction_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のExecutionContextActionListenerを削除する。
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
    def removeECActionListener(self, ltype, listener):
        if ltype < len(self.ecaction_):
            self.ecaction_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のPreComponentActionListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param ec_id 実行コンテキストのID
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param ec_id
    #
    # @endif
    def notifyPreAction(self, ltype, ec_id):
        if ltype < len(self.preaction_):
            self.preaction_[ltype].notify(ec_id)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のPostComponentActionListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param ec_id 実行コンテキストのID
    # @param ret リターンコード
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param ec_id
    # @param ret
    #
    # @endif
    def notifyPostAction(self, ltype, ec_id, ret):
        if ltype < len(self.postaction_):
            self.postaction_[ltype].notify(ec_id, ret)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のPortActionListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param pprofile ポートプロファイル
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param pprofile
    #
    # @endif
    def notifyPortAction(self, ltype, pprofile):
        if ltype < len(self.portaction_):
            self.portaction_[ltype].notify(pprofile)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のExecutionContextActionListenerのコールバック関数を呼び出す。
    #
    # @param self
    # @param ltype リスナの種類
    # @param ec_id 実行コンテキストのID
    #
    # @else
    #
    # @param self
    # @param ltype
    # @param ec_id
    #
    # @endif
    def notifyECAction(self, ltype, ec_id):
        if ltype < len(self.ecaction_):
            self.ecaction_[ltype].notify(ec_id)
