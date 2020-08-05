#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ClockManager.py
# @brief Global clock management class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp>
#
# Copyright (C) 2012
#     Noriaki Ando
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import threading
import OpenRTM_aist


##
# @if jp
# @class 時刻設定・取得オブジェクトのインターフェース
#
# このクラスは ClockManager によって管理されるクロックオブジェクトの
# ためのインターフェースである。ClockManager は複数のクロックオブジェ
# クトを管理し、必要に応じて適切なクロックオブジェクトを IClock イン
# ターフェースをもつオブジェクトとして返す。クロックオブジェクトは単
# にシステム時刻を返すものや、独自の論理時刻を持つクロックオブジェク
# ト等が考えられる。
#
# @else
# @brief An interface to set and get time
#
# This class is a interface for clock objects managed by
# ClockManager. ClockManager manages one or more clocks, and it
# returns appropriate clock objects according to demands. The clock
# object might be clock which just returns system time, or a clock
# which returns individual logical time.
#
# @endif
class IClock:
    """
    """

    ##
    # @if jp
    # @brief 時刻を取得する
    # @return 現在の時刻
    # @else
    # @brief Getting time
    # @return Current time
    # @endif
    # virtual coil::TimeValue gettime() const = 0;
    def gettime(self):
        pass

    ##
    # @if jp
    # @brief 時刻を設定する
    # @param clocktime 現在の時刻
    # @else
    # @brief Setting time
    # @param clocktime Current time
    # @endif
    # virtual bool settime(coil::TimeValue clocktime) = 0;

    def settime(self, clocktime):
        pass


##
# @if jp
# @class システム時刻を扱うクロックオブジェクト
#
# このクラスはシステムクロックを設定または取得するクラスである。
#
# @else
# @brief clock object to handle system clock
#
# This class sets and gets system clock.
#
# @endif
class SystemClock(IClock):
    """
    """

    # virtual coil::TimeValue gettime() const;
    def gettime(self):
        return OpenRTM_aist.Time().getTime()

    # virtual bool settime(coil::TimeValue clocktime);
    def settime(self, clocktime):
        return OpenRTM_aist.Time().settimeofday(clocktime, 0)


##
# @if jp
# @class 論理時間を扱うクロックオブジェクト
#
# このクラスは論理時間を設定または取得するクラスである。
# 単純に settime() によって設定された時刻を gettime() によって取得する。
#
# @else
# @brief Clock object to handle logical clock
#
# This class sets and gets system clock.
# It just sets time by settime() and gets time by gettime().
#
# @endif
class LogicalClock(IClock):
    """
    """

    def __init__(self):
        self._currentTime = OpenRTM_aist.TimeValue(0.0)
        self._currentTimeMutex = threading.RLock()
        return

    # virtual coil::TimeValue gettime() const;
    def gettime(self):
        guard = OpenRTM_aist.ScopedLock(self._currentTimeMutex)
        return self._currentTime

    # virtual bool settime(coil::TimeValue clocktime);
    def settime(self, clocktime):
        guard = OpenRTM_aist.ScopedLock(self._currentTimeMutex)
        self._currentTime = clocktime
        return True


##
# @if jp
# @class 調整済み時刻を扱うクロックオブジェクト
#
# settime() 呼び出し時に現在時刻との差をオフセットとして保持し、
# gettime() によってオフセット調整済みの時刻を返す。
#
# @else
# @brief Clock object to handle adjusted clock
#
# This class stores a offset time with current system clock when
# settime(), and gettime() returns adjusted clock by the offset.
#
# @endif
class AdjustedClock(IClock):
    """
    """

    def __init__(self):
        self._offset = OpenRTM_aist.TimeValue(0.0)
        self._offsetMutex = threading.RLock()
        return

    # virtual coil::TimeValue gettime() const;

    def gettime(self):
        guard = OpenRTM_aist.ScopedLock(self._offsetMutex)
        return OpenRTM_aist.Time().getTime() - self._offset

    # virtual bool settime(coil::TimeValue clocktime);
    def settime(self, clocktime):
        guard = OpenRTM_aist.ScopedLock(self._offsetMutex)
        self._offset = OpenRTM_aist.Time().getTime() - clocktime
        return True


clockmgr = None
clockmgr_mutex = threading.RLock()

##
# @if jp
# @class グローバルなクロック管理クラス。
#
# このクラスはグローバルにクロックオブジェクトを提供するシングルトン
# クラスである。getClocK(クロック名) により IClock 型のクロックオブ
# ジェクトを返す。利用可能なクロックは "system", "logical" および
# "adjusted" の３種類である。
#
# @else
# @brief A global clock management class
#
# This class is a singleton class that provides clock objects
# globally. It provides a IClock object by getClock(<clock
# type>). As clock types, "system", "logical" and "adjusted" are
# available.
#
# @endif


class ClockManager:
    """
    """

    def __init__(self):
        self._systemClock = SystemClock()
        self._logicalClock = LogicalClock()
        self._adjustedClock = AdjustedClock()
        return

    def getClock(self, clocktype):
        if clocktype == "logical":
            return self._logicalClock
        elif clocktype == "adjusted":
            return self._adjustedClock
        elif clocktype == "system":
            return self._systemClock

        return self._systemClock

    def instance():
        global clockmgr
        global clockmgr_mutex

        if not clockmgr:
            guard = OpenRTM_aist.ScopedLock(clockmgr_mutex)
            clockmgr = ClockManager()

        return clockmgr
    instance = staticmethod(instance)
