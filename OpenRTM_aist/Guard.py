#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file  Guard.py
# @brief RT-Middleware mutx guard class
# @date  $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2008
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#


##
# @if jp
# @class ScopedLock
# @brief ScopedLock クラス
#
# 排他処理用ロッククラス。
#
# @since 0.4.0
#
# @else
#
# @endif
class ScopedLock:
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    # @param mutex ロック用ミューテックス
    #
    # @else
    #
    # @endif
    def __init__(self, mutex, defer_lock=False):
        self._mutex = mutex
        self._locked = False
        if not defer_lock:
            self.lock()

    ##
    # @if jp
    # @brief デストラクタ
    #
    # デストラクタ
    #
    # @param self
    #
    # @else
    #
    # @endif

    def __del__(self):
        self.unlock()

    ##
    # @if jp
    # @brief ミューテックスをする
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    #
    # @endif

    def lock(self):
        if not self._locked:
            self._locked = True
            self._mutex.acquire()

    ##
    # @if jp
    # @brief ミューテックスのロックを解除する
    #
    #
    # @param self
    #
    # @else
    #
    # @param self
    #
    # @endif

    def unlock(self):
        if self._locked:
            self._locked = False
            self._mutex.release()
