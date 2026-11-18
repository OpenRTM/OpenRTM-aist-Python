#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file TestPCBGeneric.py
# @brief OpenRTM process callback adapter for RTCFailover
#
# @~japanese
# RTCFailover のための OpenRTM のプロセスのコールバックのアダプタ
#
# プロセス終了のコールバック (ProcessCallbackBase / ProcessCallbackFactory) は、拡張マネージャ (feature/processcallback) の機能で、OpenRTM-aist の master にはない。master の OpenRTM-aist では、RTCFailover の生存確認 (liveness_interval) がプロセス終了の検知を代わりに行うので、このモジュールは不要。
# 拡張マネージャを使う場合だけ callback=TestPCBGeneric を指定する。フェイルオーバーのコントローラーは親プロセスで初期化しておくこと。
# @~english
# The process exit callback (ProcessCallbackBase / ProcessCallbackFactory) is a feature of the extended manager (feature/processcallback) and is not in the master branch of OpenRTM-aist. With the master OpenRTM-aist, the liveness check of RTCFailover (liveness_interval) detects process exits instead, so this module is not needed.
# Specify callback=TestPCBGeneric only when using the extended manager. The failover controller must be initialized in the parent process.
# @~
#
# @date $Date: 2026-11-13 16:24:19 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2026
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import logging
import OpenRTM_aist
import RTCFailover

LOG = logging.getLogger(__name__)
_SUPPORTED = hasattr(OpenRTM_aist, 'ProcessCallbackBase') and hasattr(OpenRTM_aist, 'ProcessCallbackFactory')

if _SUPPORTED:
    ##
    # @~japanese
    # @brief slave のプロセスが終わったら、RTCFailover の切り替えを行うコールバック
    # @~english
    # @brief Callback that performs the switching of RTCFailover when a slave process exits
    # @~
    class TestPCBGeneric(OpenRTM_aist.ProcessCallbackBase):
        ##
        # @~japanese
        # @brief コールバックの終了処理
        # @~english
        # @brief Finalization of the callback
        # @~
        def exit(self) -> None:
            pass

        ##
        # @~japanese
        # @brief プロセスが終わったときに呼ばれ、グループを切り替える
        #
        # @param id 終了コード
        # @param options プロセスの情報
        # @~english
        # @brief Called when a process exits; switches the groups
        #
        # @param id exit code
        # @param options process information
        # @~
        def callback(self, id: int, options: dict) -> None:
            if id == 0:
                return
            LOG.warning('RTC process event: id=%r options=%r', id, options)
            try:
                RTCFailover.reconnect()
            except Exception:
                LOG.exception('failover on process callback failed')


##
# @~japanese
# @brief コールバックのファクトリに登録する (feature/processcallback がなければ警告だけを出す)
#
# @param manager マネージャ
# @~english
# @brief Registers the callback to the factory (only warns if feature/processcallback is not available)
#
# @param manager manager
# @~
def TestPCBGenericInit(manager) -> None:
    if not _SUPPORTED:
        LOG.warning('この OpenRTM-aist には ProcessCallback がないため TestPCBGeneric は登録しません '
                    '(プロセス終了は RTCFailover の liveness で検知します)')
        return
    OpenRTM_aist.ProcessCallbackFactory.instance().addFactory('TestPCBGeneric', TestPCBGeneric)
