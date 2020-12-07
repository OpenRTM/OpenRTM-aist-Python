#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file Timer.py
# @brief Timer class
# @date $Date: $
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2007-2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import time
import threading

import OpenRTM_aist

##
# @if jp
# @class DelayedFunction
# @brief 実行遅延関数呼び出し
#
# @since 2.0.0
#
# @else
#
# @class DelayedFunction
# @brief Delayed function call
#
# @since 2.0.0
#
# @endif


class DelayedFunction(object):
    ##
    # @if jp
    # @brief コンストラクタ
    # @param fn: 実行する関数または関数オブジェクト
    # @param delay: 実行までの遅延時間
    #
    # @else
    # @brief Constructor
    # @param fn: Function or functional object
    # @return delay: the delay until function call
    #
    # @endif
    def __init__(self, function, delay):
        self._fn = function
        self._remains = delay
    ##
    # @if jp
    # @brief 1回の時間経過
    # @param interval: 経過した時間
    # @return bool true:  期限が来た
    #              false: 期限が来ていない
    #
    # interval 分だけ期限を減算し、期限切れの場合に関数を実行する。
    #
    # @else
    # @brief Tick
    # @param interval: Tick interval
    # @return bool true:  The function is expired and executed.
    #              false: The function is unexpired.
    # @endif

    def tick(self, interval):
        self._remains -= interval
        is_expired = (self._remains.toDouble() <= 0.0)
        if is_expired:
            self._fn()
        return is_expired

##
# @if jp
# @class PeriodicFunction
# @brief 周期関数呼び出し
#
# @since 2.0.0
#
# @else
#
# @class PeriodicFunction
# @brief Periodic function call
#
# @since 2.0.0
#
# @endif


class PeriodicFunction(object):
    ##
    # @if jp
    # @brief コンストラクタ
    # @param fn 実行する関数または関数オブジェクト
    # @param period 実行間隔
    #
    # @else
    # @brief Constructor
    # @param fn Function or functional object
    # @param period
    #
    #
    # @endif
    def __init__(self, function, period):
        self._fn = function
        self._remains = period
        self._period = period
        self._lock = threading.RLock()
        self._isRemoved = False
    ##
    # @if jp
    # @brief 1回の時間経過
    # @param interval: 経過した時間
    # @return 停止中の場合は実行せずにTrueを返す
    #
    # interval 分だけ期限を減算し、期限切れの場合に関数を実行する。
    # 関数が実行されると周期が再設定される。
    #
    # @else
    # @brief Tick
    # @param interval: Tick interval
    # @return
    # @endif

    def tick(self, interval):
        guard = OpenRTM_aist.ScopedLock(self._lock)
        if self._isRemoved:
            return True
        self._remains -= interval
        if self._remains.toDouble() <= 0.0:
            self._fn()
            self._remains = self._period
        return False
    ##
    # @if jp
    # @brief 周期実行を停止する
    #
    #
    # @param self
    #
    # @else
    #
    # @brief Stop to execute function
    #
    #
    # @param self
    #
    # @endif

    def stop(self):
        guard = OpenRTM_aist.ScopedLock(self._lock)
        self._isRemoved = True

##
# @if jp
# @class Timer
# @brief Timerクラス
#
# 登録されたリスナーのコールバック関数を、設定された周期で定期的に呼び出す。
#
# @since 0.4.0
#
# @else
#
# @class Timer
# @brief Timer class
#
# Invoke the callback function of registered listener periodically
# at the set cycle.
#
# @since 0.4.0
#
# @endif

# TODO: The "object" class inheritance must be removed in Python3
class Timer(object):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param interval タイマ起動周期
    #
    # @else
    #
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    # @param interval The interval of timer
    #
    # @endif

    def __init__(self):
        self._lock = threading.RLock()
        self._tasks = []
        return

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    # @brief Destructor
    #
    # Destructor
    #
    # @param self
    #
    # @endif
    #
    def __del__(self):
        pass

    ##
    # @if jp
    # @brief 1回の時間経過
    # @param interval: 経過した時間
    # @return bool true 固定
    #
    # interval 分だけ期限を減算し、期限切れの場合に関数を実行する。
    # 関数が実行されると周期が再設定される。
    #
    # @else
    # @brief Tick
    # @param interval: Tick interval
    # @return bool true only
    #
    # @endif
    def tick(self, interval):
        guard = OpenRTM_aist.ScopedLock(self._lock)
        tasks = self._tasks[:]
        del guard
        for task in tasks:
            if task.tick(interval):
                guard = OpenRTM_aist.ScopedLock(self._lock)
                self._tasks.remove(task)
                del guard

##
# @if jp
# @class DelayedTimer
# @brief 実行遅延関数呼び出し用のタイマー
# @since 2.0.0
# @else
# @class DelayedTimer
# @brief Timer of delayed function call
# @since 2.0.0
# @endif
#


class DelayedTimer(Timer):

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    #
    # @endif
    def __init__(self):
        super(DelayedTimer, self).__init__()

    ##
    # @if jp
    # @brief 非同期処理を登録する
    #
    # @param self
    # @param fn 登録関数
    # @return 関数オブジェクト
    #
    # @else
    #
    # @brief Add an async function into list.
    #
    # @param self
    # @param fn 登録関数
    # @return 関数オブジェクト
    #
    # @endif
    def emplace(self, fn, *args):
        guard = OpenRTM_aist.ScopedLock(self._lock)
        funcobj = DelayedFunction(fn, *args)
        self._tasks.append(funcobj)
        return funcobj

##
# @if jp
# @class PeriodicTimer
# @brief 周期関数呼び出し用タイマー
# @since 2.0.0
# @else
# @class PeriodicTimer
# @brief Timer of periodic function call
# @endif
#


class PeriodicTimer(Timer):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief Constructor
    #
    # Constructor
    #
    # @param self
    #
    # @endif
    def __init__(self):
        super(PeriodicTimer, self).__init__()

    ##
    # @if jp
    # @brief 非同期処理を登録する
    #
    # @param self
    # @param fn 登録関数
    # @return 関数オブジェクト
    #
    # @else
    #
    # @brief Add an async function into list.
    #
    # @param self
    # @param fn 登録関数
    # @return 関数オブジェクト
    #
    # @endif
    def emplace(self, fn, *args):
        guard = OpenRTM_aist.ScopedLock(self._lock)
        funcobj = PeriodicFunction(fn, *args)
        self._tasks.append(funcobj)
        return funcobj
