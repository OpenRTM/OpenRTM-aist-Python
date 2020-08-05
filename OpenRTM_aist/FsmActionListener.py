#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FsmActionListener.py
# @brief FSM Action listener class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist
import threading
import OpenRTM_aist.Guard

##
# @if jp
# @brief
#
# FSMコンポーネントに関する種々の振る舞いをフックするためのリスナ定
# 義。リスナには大きく分けると、
#
# - FSMそのものの動作をフックするためのリスナ
# - FSMに関するメタデータ変更等の動作をフックするためのリスナ
#
# の2種類に分けられる。さらに前者は、FSMの状態遷移等のアクションの前
# 後それぞれをフックするための PreFsmActionListener と
# PostFsmActionListener の二つがあり、後者は、FSMのProfileの変更をフッ
# クする FsmProfileListener と FSMの構造 (Structure) の変更をフック
# する FsmStructureListener の二つに分けられる。以上、以下のFSMに関
# する以下の4種類のリスナークラス群が提供されている。
#
# - PreFsmActionListener
# - PostFsmActionListener
# - FsmProfileListner
# - FsmStructureListener
#
#
# @else
#
#
# @endif
#

##
# @if jp
# @brief PreFsmActionListener のタイプ
#
# PreFsmActionListener には以下のフックポイントが定義されている。こ
# れらが呼び出されるかどうかは、FSMの実装に依存する。
#
# - PRE_ON_INIT:          init 直前
# - PRE_ON_ENTRY:         entry 直前
# - PRE_ON_DO:            do 直前
# - PRE_ON_EXIT:          exit 直前
# - PRE_ON_STATE_CHANGE:  状態遷移直前
#
# @else
# @brief The types of PreFsmActionListenerType
#
# PreFsmActionListener has the following hook points. If these
# listeners are actually called or not called are depends on FSM
# implementations.
#
# - PRE_ON_INIT:          just before "init" action
# - PRE_ON_ENTRY:         just before "entry" action
# - PRE_ON_DO:            just before "do" action
# - PRE_ON_EXIT:          just before "exit" action
# - PRE_ON_STATE_CHANGE:  just before state transition action
#
# @endif
#


class PreFsmActionListenerType:
    """
    """

    def __init__(self):
        pass
    PRE_ON_INIT = 0
    PRE_ON_ENTRY = 1
    PRE_ON_DO = 2
    PRE_ON_EXIT = 3
    PRE_ON_STATE_CHANGE = 4
    PRE_FSM_ACTION_LISTENER_NUM = 5


##
# @if jp
# @class PreFsmActionListener クラス
# @brief PreFsmActionListener クラス
#
# PreFsmActionListener クラスは、Fsmのアクションに関するコールバック
# を実現するリスナーオブジェクトの基底クラスである。FSMのアクション
# の直前の動作をフックしたい場合、以下の例のように、このクラスを継承
# したコールバックオブジェクトを定義し、適切なコールバック設定関数か
# らRTObjectに対してコールバックオブジェクトをセットする必要がある。
#
# <pre>
# class MyListener
#   : public PreFsmActionListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const char* state_name)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#     std::cout << "Current state: " state_name << std::endl;
#   };
# };
# </pre>
#
# このようにして定義されたリスナクラスは、以下のようにRTObjectに対し
# て、セットされる。
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addPreFsmActionListener(PRE_ON_STATE_CHANGE,
#                             new MyListener("init listener"),
#                             true);
#    :
# </pre>
#
# 第1引数の "PRE_ON_STATE_CHANGE" は、コールバックをフックするポイン
# トであり、以下の値を取ることが可能である。なお、すべてのコールバッ
# クポイントが実装されているとは限らず、これらが呼び出されるかどうか
# は、FSMの実装に依存する。
#
# - PRE_ON_INIT:          init 直前
# - PRE_ON_ENTRY:         entry 直前
# - PRE_ON_DO:            do 直前
# - PRE_ON_EXIT:          exit 直前
# - PRE_ON_STATE_CHANGE:  状態遷移直前
#
# 第2引数はリスナオブジェクトのポインタである。第3引数はオブジェクト
# 自動削除フラグであり、true の場合は、RTObject削除時に自動的にリス
# ナオブジェクトが削除される。falseの場合は、オブジェクトの所有権は
# 呼び出し側に残り、削除は呼び出し側の責任で行わなければならない。
# RTObject のライフサイクル中にコールバックが必要ならば上記のような
# 呼び出し方で第3引数を true としておくとよい。逆に、コールバックを
# 状況等に応じてセットしたりアンセットしたりする必要がある場合は
# falseとして置き、リスナオブジェクトのポインタをメンバ変数などに保
# 持しておき、
# RTObject_impl::addPreFsmActionListener()/removePreFsmActionListener()
# により、セットとアンセットを管理するといった使い方も可能である。
#
# @else
# @class PreFsmActionListener class
# @brief PreFsmActionListener class
#
# PreFsmActionListener class is a base class for the listener
# objects which realize callback to hook FSM related pre-actions.
# To hook execution just before a FSM action, the callback object
# should be defined as follows, and set to RTObject through
# appropriate callback set function.
#
# <pre>
# class MyListener
#   : public PreFsmActionListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const char* state_name)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#     std::cout << "Current state: " state_name << std::endl;
#   };
# };
# </pre>
#
# The listener class defined above is set to RTObject as follows.
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addPreFsmActionListener(PRE_ON_STATE_CHANGE,
#                             new MyListener("init listener"),
#                             true);
#    :
# </pre>
#
# The first argument "PRE_ON_STATE_CHANGE" specifies callback hook
# point, and the following values are available. Not all the
# callback points are implemented. It depends on the FSM
# implementations.
#
# - PRE_ON_INIT:          just before "init" action
# - PRE_ON_ENTRY:         just before "entry" action
# - PRE_ON_DO:            just before "do" action
# - PRE_ON_EXIT:          just before "exit" action
# - PRE_ON_STATE_CHANGE:  just before state transition action
#
# The second argument is a pointers to the listener object. The
# third argument is a flag for automatic object destruction. When
# "true" is given to the third argument, the given object in second
# argument is automatically destructed with RTObject. In the "false
# " case, the ownership of the object is left in the caller side,
# and then destruction of the object must be done by users'
# responsibility.
#
# It is good for setting "true" as third argument, if the listener
# object life span is equals to the RTObject's life cycle.  On the
# otehr hand, if callbacks are required to set/unset depending on
# its situation, the third argument could be "false".  In that
# case, listener objects pointers must be stored to member
# variables, and set/unset of the listener objects shoud be
# paerformed throguh
# RTObject_impl::addPreFsmActionListener()/removePreFsmActionListener()
# functions.
#
# @endif
#
class PreFsmActionListener:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # PreFsmActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for PreFsmActionListener.
    #
    # @endif
    # virtual void operator()(const char*) = 0;

    def __call__(self, state):
        pass

    ##
    # @if jp
    #
    # @brief PreFsmActionListenerType を文字列に変換
    #
    # PreFsmActionListenerType を文字列に変換する
    #
    # @param type 変換対象 PreFsmActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert PreFsmActionListenerType into the string.
    #
    # Convert PreFsmActionListenerType into the string.
    #
    # @param type The target PreFsmActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    #
    def toString(status):
        typeString = ["PRE_ON_INIT",
                      "PRE_ON_ENTRY",
                      "PRE_ON_DO",
                      "PRE_ON_EXIT",
                      "PRE_ON_STATE_CHANGE"]
        if status < len(typeString):
            return typeString[status]

        return ""
    toString = staticmethod(toString)


##
# @if jp
# @brief PreFsmActionListener のタイプ
#
# PreFsmActionListener には以下のフックポイントが定義されている。こ
# れらが呼び出されるかどうかは、FSMの実装に依存する。
#
# - POST_ON_INIT:          init 直後
# - POST_ON_ENTRY:         entry 直後
# - POST_ON_DO:            do 直後
# - POST_ON_EXIT:          exit 直後
# - POST_ON_STATE_CHANGE:  状態遷移直後
#
# @else
# @brief The types of PostFsmActionListenerType
#
# PreFsmActionListener has the following hook points. If these
# listeners are actually called or not called are depends on FSM
# implementations.
#
# - POST_ON_INIT:          just after "init" action
# - POST_ON_ENTRY:         just after "entry" action
# - POST_ON_DO:            just after "do" action
# - POST_ON_EXIT:          just after "exit" action
# - POST_ON_STATE_CHANGE:  just after state transition action
#
# @endif
#
class PostFsmActionListenerType:
    """
    """

    def __init__(self):
        pass
    POST_ON_INIT = 0
    POST_ON_ENTRY = 1
    POST_ON_DO = 2
    POST_ON_EXIT = 3
    POST_ON_STATE_CHANGE = 4
    POST_FSM_ACTION_LISTENER_NUM = 5


##
# @if jp
# @class PostFsmActionListener クラス
# @brief PostFsmActionListener クラス
#
# PostFsmActionListener クラスは、Fsmのアクションに関するコールバック
# を実現するリスナーオブジェクトの基底クラスである。FSMのアクション
# の直後の動作をフックしたい場合、以下の例のように、このクラスを継承
# したコールバックオブジェクトを定義し、適切なコールバック設定関数か
# らRTObjectに対してコールバックオブジェクトをセットする必要がある。
#
# <pre>
# class MyListener
#   : public PostFsmActionListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const char* state_name, ReturnCode_t ret)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#     std::cout << "Current state: " state_name << std::endl;
#   };
# };
# </pre>
#
# このようにして定義されたリスナクラスは、以下のようにRTObjectに対し
# て、セットされる。
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addPostFsmActionListener(POST_ON_STATE_CHANGE,
#                             new MyListener("init listener"),
#                             true);
#    :
# </pre>
#
# 第1引数の "POST_ON_STATE_CHANGE" は、コールバックをフックするポイン
# トであり、以下の値を取ることが可能である。なお、すべてのコールバッ
# クポイントが実装されているとは限らず、これらが呼び出されるかどうか
# は、FSMの実装に依存する。
#
# - POST_ON_INIT:          init 直後
# - POST_ON_ENTRY:         entry 直後
# - POST_ON_DO:            do 直後
# - POST_ON_EXIT:          exit 直後
# - POST_ON_STATE_CHANGE:  状態遷移直後
#
# 第2引数はリスナオブジェクトのポインタである。第3引数はオブジェクト
# 自動削除フラグであり、true の場合は、RTObject削除時に自動的にリス
# ナオブジェクトが削除される。falseの場合は、オブジェクトの所有権は
# 呼び出し側に残り、削除は呼び出し側の責任で行わなければならない。
# RTObject のライフサイクル中にコールバックが必要ならば上記のような
# 呼び出し方で第3引数を true としておくとよい。逆に、コールバックを
# 状況等に応じてセットしたりアンセットしたりする必要がある場合は
# falseとして置き、リスナオブジェクトのポインタをメンバ変数などに保
# 持しておき、
# RTObject_impl::addPostFsmActionListener()/removePostFsmActionListener()
# により、セットとアンセットを管理するといった使い方も可能である。
#
# @else
# @class PostFsmActionListener class
# @brief PostFsmActionListener class
#
# PostFsmActionListener class is a base class for the listener
# objects which realize callback to hook FSM related post-actions.
# To hook execution just before a FSM action, the callback object
# should be defined as follows, and set to RTObject through
# appropriate callback set function.
#
# <pre>
# class MyListener
#   : public PostFsmActionListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const char* state_name, ReturnCode\t ret)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#     std::cout << "Current state: " state_name << std::endl;
#   };
# };
# </pre>
#
# The listener class defined above is set to RTObject as follows.
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addPostFsmActionListener(POST_ON_STATE_CHANGE,
#                             new MyListener("init listener"),
#                             true);
#    :
# </pre>
#
# The first argument "POST_ON_STATE_CHANGE" specifies callback hook
# point, and the following values are available. Not all the
# callback points are implemented. It depends on the FSM
# implementations.
#
# - POST_ON_INIT:          just after "init" action
# - POST_ON_ENTRY:         just after "entry" action
# - POST_ON_DO:            just after "do" action
# - POST_ON_EXIT:          just after "exit" action
# - POST_ON_STATE_CHANGE:  just after state transition action
#
# The second argument is a pointers to the listener object. The
# third argument is a flag for automatic object destruction. When
# "true" is given to the third argument, the given object in second
# argument is automatically destructed with RTObject. In the "false
# " case, the ownership of the object is left in the caller side,
# and then destruction of the object must be done by users'
# responsibility.
#
# It is good for setting "true" as third argument, if the listener
# object life span is equals to the RTObject's life cycle.  On the
# otehr hand, if callbacks are required to set/unset depending on
# its situation, the third argument could be "false".  In that
# case, listener objects pointers must be stored to member
# variables, and set/unset of the listener objects shoud be
# paerformed throguh
# RTObject_impl::addPostFsmActionListener()/removePostFsmActionListener()
# functions.
#
# @endif
#
class PostFsmActionListener:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # PostFsmActionListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for PostFsmActionListener.
    #
    # @endif
    # virtual void operator()(const char* state, ReturnCode_t ret) = 0;

    def __call__(self, state, ret):
        pass

    ##
    # @if jp
    #
    # @brief PostFsmActionListenerType を文字列に変換
    #
    # PostFsmActionListenerType を文字列に変換する
    #
    # @param type 変換対象 PostFsmActionListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert PostFsmActionListenerType into the string.
    #
    # Convert PostFsmActionListenerType into the string.
    #
    # @param type The target PostFsmActionListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    #
    def toString(status):
        typeString = ["POST_ON_INIT",
                      "POST_ON_ENTRY",
                      "POST_ON_DO",
                      "POST_ON_EXIT",
                      "POST_ON_STATE_CHANGE"]
        if status < len(typeString):
            return typeString[status]

        return ""
    toString = staticmethod(toString)


##
# @if jp
# @brief FsmProfileListener のタイプ
#
# - SET_FSM_PROFILE       : FSM Profile設定時
# - GET_FSM_PROFILE       : FSM Profile取得時
# - ADD_FSM_STATE         : FSMにStateが追加された
# - REMOVE_FSM_STATE      : FSMからStateが削除された
# - ADD_FSM_TRANSITION    : FSMに遷移が追加された
# - REMOVE_FSM_TRANSITION : FSMから遷移が削除された
# - BIND_FSM_EVENT        : FSMにイベントがバインドされた
# - UNBIND_FSM_EVENT      : FSMにイベントがアンバインドされた
#
# @else
# @brief The types of FsmProfileListener
#
# - SET_FSM_PROFILE       : Setting FSM Profile
# - GET_FSM_PROFILE       : Getting FSM Profile
# - ADD_FSM_STATE         : A State added to the FSM
# - REMOVE_FSM_STATE      : A State removed from FSM
# - ADD_FSM_TRANSITION    : A transition added to the FSM
# - REMOVE_FSM_TRANSITION : A transition removed from FSM
# - BIND_FSM_EVENT        : An event bounded to the FSM
# - UNBIND_FSM_EVENT      : An event unbounded to the FSM
#
# @endif
#
class FsmProfileListenerType:
    """
    """

    def __init__(self):
        pass
    SET_FSM_PROFILE = 0
    GET_FSM_PROFILE = 1
    ADD_FSM_STATE = 2
    REMOVE_FSM_STATE = 3
    ADD_FSM_TRANSITION = 4
    REMOVE_FSM_TRANSITION = 5
    BIND_FSM_EVENT = 6
    UNBIND_FSM_EVENT = 7
    FSM_PROFILE_LISTENER_NUM = 8


##
# @if jp
# @class FsmProfileListener クラス
# @brief FsmProfileListener クラス
#
# FsmProfileListener クラスは、FSMのProfileに関連したアクションのコー
# ルバックを実現するリスナーオブジェクトの基底クラスである。FSM
# Profileのアクションの動作をフックしたい場合、以下の例のように、こ
# のクラスを継承したコールバックオブジェクトを定義し、適切なコールバッ
# ク設定関数からRTObjectに対してコールバックオブジェクトをセットする
# 必要がある。
#
# <pre>
# class MyListener
#   : public FsmProfileListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const ::RTC::FsmProfile& fsmprof)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#   };
# };
# </pre>
#
# このようにして定義されたリスナクラスは、以下のようにRTObjectに対し
# て、セットされる。
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addFsmProfileListener(SET_FSM_PROFILE,
#                           new MyListener("prof listener"),
#                           true);
#    :
# </pre>
#
# 第1引数の "SET_FSM_PROFILE" は、コールバックをフックするポイン
# トであり、以下の値を取ることが可能である。なお、すべてのコールバッ
# クポイントが実装されているとは限らず、これらが呼び出されるかどうか
# は、FSMサービスの実装に依存する。
#
# - SET_FSM_PROFILE       : FSM Profile設定時
# - GET_FSM_PROFILE       : FSM Profile取得時
# - ADD_FSM_STATE         : FSMにStateが追加された
# - REMOVE_FSM_STATE      : FSMからStateが削除された
# - ADD_FSM_TRANSITION    : FSMに遷移が追加された
# - REMOVE_FSM_TRANSITION : FSMから遷移が削除された
# - BIND_FSM_EVENT        : FSMにイベントがバインドされた
# - UNBIND_FSM_EVENT      : FSMにイベントがアンバインドされた
#
# 第2引数はリスナオブジェクトのポインタである。第3引数はオブジェクト
# 自動削除フラグであり、true の場合は、RTObject削除時に自動的にリス
# ナオブジェクトが削除される。falseの場合は、オブジェクトの所有権は
# 呼び出し側に残り、削除は呼び出し側の責任で行わなければならない。
# RTObject のライフサイクル中にコールバックが必要ならば上記のような
# 呼び出し方で第3引数を true としておくとよい。逆に、コールバックを
# 状況等に応じてセットしたりアンセットしたりする必要がある場合は
# falseとして置き、リスナオブジェクトのポインタをメンバ変数などに保
# 持しておき、addFsmProfileListener()/removeFsmProfileListener() に
# より、セットとアンセットを管理するといった使い方も可能である。
#
# @else
# @class FsmProfileListener class
# @brief FsmProfileListener class
#
# FsmProfileListener class is a base class for the listener
# objects which realize callback to hook FSM Profile related actions.
# To hook execution just before a FSM profile action, the callback object
# should be defined as follows, and set to RTObject through
# appropriate callback set function.
#
# <pre>
# class MyListener
#   : public FsmProfileListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#
#   virtual void operator()(const ::RTC::FsmProfile& fsmprof)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#   };
# };
# </pre>
#
# The listener class defined above is set to RTObject as follows.
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addFsmProfileListener(SET_FSM_PROFILE,
#                           new MyListener("prof listener"),
#                           true);
#    :
# </pre>
#
# The first argument "SET_FSM_PROFILE" specifies callback hook
# point, and the following values are available. Not all the
# callback points are implemented. It depends on the FSM service
# implementations.
#
# - SET_FSM_PROFILE       : Setting FSM Profile
# - GET_FSM_PROFILE       : Getting FSM Profile
# - ADD_FSM_STATE         : A State added to the FSM
# - REMOVE_FSM_STATE      : A State removed from FSM
# - ADD_FSM_TRANSITION    : A transition added to the FSM
# - REMOVE_FSM_TRANSITION : A transition removed from FSM
# - BIND_FSM_EVENT        : An event bounded to the FSM
# - UNBIND_FSM_EVENT      : An event unbounded to the FSM
#
# The second argument is a pointers to the listener object. The
# third argument is a flag for automatic object destruction. When
# "true" is given to the third argument, the given object in second
# argument is automatically destructed with RTObject. In the "false
# " case, the ownership of the object is left in the caller side,
# and then destruction of the object must be done by users'
# responsibility.
#
# It is good for setting "true" as third argument, if the listener
# object life span is equals to the RTObject's life cycle.  On the
# otehr hand, if callbacks are required to set/unset depending on
# its situation, the third argument could be "false".  In that
# case, listener objects pointers must be stored to member
# variables, and set/unset of the listener objects shoud be
# paerformed throguh
# addFsmProfileListener()/removeFsmProfileListener() functions.
#
# @endif
#
class FsmProfileListener:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # FsmProfileListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for FsmProfileListener.
    #
    # @endif
    # virtual void operator()(const ::RTC::FsmProfile& fsmprof) = 0;

    def __call__(self, fsmprof):
        pass

    ##
    # @if jp
    #
    # @brief FsmProfileListenerType を文字列に変換
    #
    # FsmProfileListenerType を文字列に変換する
    #
    # @param type 変換対象 FsmProfileListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert FsmProfileListenerType into the string.
    #
    # Convert FsmProfileListenerType into the string.
    #
    # @param type The target FsmProfileListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    #
    def toString(status):
        typeString = ["SET_FSM_PROFILE",
                      "GET_FSM_PROFILE",
                      "ADD_FSM_STATE",
                      "REMOVE_FSM_STATE",
                      "ADD_FSM_TRANSITION",
                      "REMOVE_FSM_TRANSITION",
                      "BIND_FSM_EVENT",
                      "UNBIND_FSM_EVENT"]
        if status < len(typeString):
            return typeString[status]

        return ""
    toString = staticmethod(toString)


##
# @if jp
# @brief FsmStructureListener のタイプ
#
# - SET_FSM_STRUCTURE: FSM構造の設定
# - GET_FSM_STRUCTURE: FSM構造の取得
#
# @else
# @brief The types of FsmStructureListener
#
# - SET_FSM_STRUCTURE: Setting FSM structure
# - GET_FSM_STRUCTURE: Getting FSM structure
#
# @endif
#
class FsmStructureListenerType:
    """
    """

    def __init__(self):
        pass
    SET_FSM_STRUCTURE = 0
    GET_FSM_STRUCTURE = 1
    FSM_STRUCTURE_LISTENER_NUM = 2


##
# @if jp
# @class FsmStructureListener クラス
# @brief FsmStructureListener クラス
#
# FsmStructureListener クラスは、FSM Structureのアクションに関するコー
# ルバックを実現するリスナーオブジェクトの基底クラスである。FSM
# Structure のアクションの直後の動作をフックしたい場合、以下の例のよ
# うに、このクラスを継承したコールバックオブジェクトを定義し、適切な
# コールバック設定関数からRTObjectに対してコールバックオブジェクトを
# セットする必要がある。
#
# <pre>
# class MyListener
#   : public FsmStructureListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#   virtual void operator()(::RTC::FsmStructure& pprof)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#   };
# };
# </pre>
#
# このようにして定義されたリスナクラスは、以下のようにRTObjectに対し
# て、セットされる。
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addFsmStructureListener(SET_FSM_STRUCTURE,
#                             new MyListener("set structure listener"),
#                             true);
#    :
# </pre>
#
# 第1引数の "SET_FSM_STRUCTURE" は、コールバックをフックするポイン
# トであり、以下の値を取ることが可能である。なお、すべてのコールバッ
# クポイントが実装されているとは限らず、これらが呼び出されるかどうか
# は、FSMの実装に依存する。
#
# - SET_FSM_STRUCTURE: FSM構造の設定
# - GET_FSM_STRUCTURE: FSM構造の取得
#
# 第2引数はリスナオブジェクトのポインタである。第3引数はオブジェクト
# 自動削除フラグであり、true の場合は、RTObject削除時に自動的にリス
# ナオブジェクトが削除される。falseの場合は、オブジェクトの所有権は
# 呼び出し側に残り、削除は呼び出し側の責任で行わなければならない。
# RTObject のライフサイクル中にコールバックが必要ならば上記のような
# 呼び出し方で第3引数を true としておくとよい。逆に、コールバックを
# 状況等に応じてセットしたりアンセットしたりする必要がある場合は
# falseとして置き、リスナオブジェクトのポインタをメンバ変数などに保
# 持しておき、
# RTObject_impl::addPostFsmActionListener()/removePostFsmActionListener()
# により、セットとアンセットを管理するといった使い方も可能である。
#
# @else
# @class FsmStructureListener class
# @brief FsmStructureListener class
#
# PostFsmActionListener class is a base class for the listener
# objects which realize callback to hook FSM structure profile
# related actions. To hook execution just before a FSM action, the
# callback object should be defined as follows, and set to RTObject
# through appropriate callback set function.
#
# <pre>
# class MyListener
#   : public FsmStructureListener
# {
#   std::string m_name;
# public:
#   MyListener(const char* name) : m_name(name) {}
#   virtual ~MyListener() {}
#   virtual void operator()(::RTC::FsmStructure& pprof)
#   {
#     std::cout << "Listner name:  " m_name << std::endl;
#   };
# };
# </pre>
#
# The listener class defined above is set to RTObject as follows.
#
# <pre>
# RTC::ReturnCode_t ConsoleIn::onInitialize()
# {
#     addFsmStructureListener(SET_FSM_STRUCTURE,
#                             new MyListener("set structure listener"),
#                             true);
#    :
# </pre>
#
# The first argument "SET_FSM_STRUCTURE" specifies callback hook
# point, and the following values are available. Not all the
# callback points are implemented. It depends on the FSM
# implementations.
#
# - SET_FSM_STRUCTURE: Setting FSM structure
# - GET_FSM_STRUCTURE: Getting FSM structure
#
# The second argument is a pointers to the listener object. The
# third argument is a flag for automatic object destruction. When
# "true" is given to the third argument, the given object in second
# argument is automatically destructed with RTObject. In the "false
# " case, the ownership of the object is left in the caller side,
# and then destruction of the object must be done by users'
# responsibility.
#
# It is good for setting "true" as third argument, if the listener
# object life span is equals to the RTObject's life cycle.  On the
# otehr hand, if callbacks are required to set/unset depending on
# its situation, the third argument could be "false".  In that
# case, listener objects pointers must be stored to member
# variables, and set/unset of the listener objects shoud be
# paerformed throguh
# RTObject_impl::addPostFsmActionListener()/removePostFsmActionListener()
# functions.
#
# @endif
#
class FsmStructureListener:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        pass

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #

    def __del__(self):
        pass

    ##
    # @if jp
    #
    # @brief 仮想コールバック関数
    #
    # FsmStructureListener のコールバック関数
    #
    # @else
    #
    # @brief Virtual Callback function
    #
    # This is a the Callback function for FsmStructureListener.
    #
    # @endif
    # virtual void operator()(const ::RTC::FsmStructure& fsmprof) = 0;

    def __call__(self, pprof):
        pass

    ##
    # @if jp
    #
    # @brief FsmStructureListenerType を文字列に変換
    #
    # FsmStructureListenerType を文字列に変換する
    #
    # @param type 変換対象 FsmStructureListenerType
    #
    # @return 文字列変換結果
    #
    # @else
    #
    # @brief Convert FsmStructureListenerType into the string.
    #
    # Convert FsmStructureListenerType into the string.
    #
    # @param type The target FsmStructureListenerType for transformation
    #
    # @return Trnasformation result of string representation
    #
    # @endif
    #
    def toString(status):
        typeString = ["SET_FSM_STRUCTURE",
                      "GET_FSM_STRUCTURE"]
        if status < len(typeString):
            return typeString[status]

        return ""
    toString = staticmethod(toString)


##
# @if jp
# @class PreFsmActionListenerHolder
# @brief PreFsmActionListener ホルダクラス
#
# 複数の PreFsmActionListener を保持し管理するクラス。
#
# @else
# @class PreFsmActionListenerHolder
# @brief PreFsmActionListener holder class
#
# This class manages one ore more instances of
# PreFsmActionListener class.
#
# @endif
#
class PreFsmActionListenerHolder:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        self._listeners = []
        self._mutex = threading.RLock()

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #
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
    #

    def addListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        self._listeners.append(listener)

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
    #
    def removeListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
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
    #
    def notify(self, state):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        for listener in self._listeners:
            listener(state)
        return


##
# @if jp
# @class PostFsmActionListenerHolder
# @brief PostFsmActionListener ホルダクラス
#
# 複数の PostFsmActionListener を保持し管理するクラス。
#
# @else
# @class PostFsmActionListenerHolder
# @brief PostFsmActionListener holder class
#
# This class manages one ore more instances of
# PostFsmActionListener class.
#
# @endif
#
class PostFsmActionListenerHolder:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        self._listeners = []
        self._mutex = threading.RLock()

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #
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
    #
    def addListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        self._listeners.append(listener)

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
    #
    def removeListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
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
    #
    def notify(self, state, ret):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        for listener in self._listeners:
            listener(state, ret)
        return


##
# @if jp
# @class FsmProfileListenerHolder
# @brief FsmProfileListener ホルダクラス
#
# 複数の FsmProfileListener を保持し管理するクラス。
#
# @else
# @class FsmProfileListenerHolder
# @brief FsmProfileListener holder class
#
# This class manages one ore more instances of
# FsmProfileListener class.
#
# @endif
#
class FsmProfileListenerHolder:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        self._listeners = []
        self._mutex = threading.RLock()

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #
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
    #

    def addListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        self._listeners.append(listener)

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
    #
    def removeListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
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
    #
    def notify(self, state):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        for listener in self._listeners:
            listener(state)
        return

##
# @if jp
# @class FsmStructureListenerHolder
# @brief FsmStructureListener ホルダクラス
#
# 複数の FsmStructureListener を保持し管理するクラス。
#
# @else
# @class FsmStructureListenerHolder
# @brief FsmStructureListener holder class
#
# This class manages one ore more instances of
# FsmStructureListener class.
#
# @endif
#


class FsmStructureListenerHolder:
    ##
    # @if jp
    # @brief コンストラクタ
    # @else
    # @brief Constructor
    # @endif
    #
    def __init__(self):
        self._listeners = []
        self._mutex = threading.RLock()

    ##
    # @if jp
    # @brief デストラクタ
    # @else
    # @brief Destructor
    # @endif
    #
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
    #

    def addListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        self._listeners.append(listener)

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
    #
    def removeListener(self, listener):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        len_ = len(self._listeners)
        for i in range(len_):
            idx = (len_ - 1) - i
            if self._listeners[idx] == listener:
                del self._listeners[idx]
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
    #
    def notify(self, state):
        guard = OpenRTM_aist.Guard.ScopedLock(self._mutex)
        for listener in self._listeners:
            listener(state)
        return


##
# @if jp
# @class FsmActionListeners
# @brief FsmActionListeners クラス
#
#
# @else
# @class FsmActionListeners
# @brief FsmActionListeners class
#
#
# @endif
class FsmActionListeners:
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
        # @brief PreFsmActionListenerType
        # PreFsmActionListenerTypeリスナを格納
        # @else
        # @brief PreFsmActionListenerType listener array
        # The PreFsmActionListenerType listener is stored.
        # @endif
        self.preaction_num = PreFsmActionListenerType.PRE_FSM_ACTION_LISTENER_NUM
        self.preaction_ = [PreFsmActionListenerHolder()
                           for i in range(self.preaction_num)]

        ##
        # @if jp
        # @brief PostFsmActionTypeリスナ配列
        # PostFsmActionTypeリスナを格納
        # @else
        # @brief PostFsmActionType listener array
        # The PostFsmActionType listener is stored.
        # @endif
        self.postaction_num = PostFsmActionListenerType.POST_FSM_ACTION_LISTENER_NUM
        self.postaction_ = [PostFsmActionListenerHolder()
                            for i in range(self.postaction_num)]

        ##
        # @if jp
        # @brief FsmProfileType
        # FsmProfileTypeリスナを格納
        # @else
        # @brief FsmProfileType listener array
        # The FsmProfileType listener is stored.
        # @endif
        self.profile_num = FsmProfileListenerType.FSM_PROFILE_LISTENER_NUM
        self.profile_ = [FsmProfileListenerHolder()
                         for i in range(self.profile_num)]

        ##
        # @if jp
        # @brief FsmStructureTypeリスナ配列
        # FsmStructureTypeリスナを格納
        # @else
        # @brief FsmStructureTypelistener array
        # The FsmStructureType listener is stored.
        # @endif
        self.structure_num = FsmStructureListenerType.FSM_STRUCTURE_LISTENER_NUM
        self.structure_ = [FsmStructureListenerHolder()
                           for i in range(self.structure_num)]

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のPreFsmActionListenerを追加する。
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
    # 指定の種類のPostFsmActionListenerを追加する。
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
    # 指定の種類のFsmProfileListenerを追加する。
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
    def addProfileListener(self, ltype, listener):
        if ltype < len(self.profile_):
            self.profile_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの追加
    #
    # 指定の種類のFsmStructureListenerを追加する。
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
    def addStructureListener(self, ltype, listener):
        if ltype < len(self.structure_):
            self.structure_[ltype].addListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のPreFsmActionListenerを削除する。
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
    # 指定の種類のPostFsmActionListenerを削除する。
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
    # 指定の種類のFsmProfileListenerを削除する。
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
    def removeProfileListener(self, ltype, listener):
        if ltype < len(self.profile_):
            self.profile_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーの削除
    #
    # 指定の種類のFsmStructureListenerを削除する。
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
    def removeStructureListener(self, ltype, listener):
        if ltype < len(self.structure_):
            self.structure_[ltype].removeListener(listener)
            return True
        return False

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のPreFsmActionListenerのコールバック関数を呼び出す。
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
    # 指定の種類のPostFsmActionListenerのコールバック関数を呼び出す。
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
    # 指定の種類のFsmStructureListenerのコールバック関数を呼び出す。
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
    def notifyProfile(self, ltype, pprofile):
        if ltype < len(self.profile_):
            self.profile_[ltype].notify(pprofile)

    ##
    # @if jp
    # @brief リスナーへ通知する
    #
    # 指定の種類のFsmStructureListenerのコールバック関数を呼び出す。
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
    def notifyStructure(self, ltype, ec_id):
        if ltype < len(self.structure_):
            self.structure_[ltype].notify(ec_id)
