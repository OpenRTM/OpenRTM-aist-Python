#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FirstFitPlacementPlugin.py
# @brief Example placement plugin: the first_fit logic (places each RTC on the first robot in order that satisfies the constraints)
#
# @~japanese
# 配置 (placement) プラグインの例: first_fit のロジック (ロボットの一覧の順に、最初に条件を満たしたロボットに置く)
#
# 組み込みのソルバ (接続をまとめる全探索) の代わりに使う。
# @code
#   "plugins": [{"module": "first_fit_placement"}],
#   "startup": {"mode": "auto", "placement_plugin": "first_fit", "placement_args": {"order": ["robot1", "robot2", "robot3"]}, ...}
# @endcode
# RTC は構成ファイルの components の順に、order (省略時は primary、その後は残りのロボット) の順で
# 最初に入るロボットへ置く。接続のまとまりは考えない。
# 置けない RTC があれば placement.PlacementError を投げる (システム起動失敗になる)。
# @~english
# Used instead of the built-in solver (exhaustive search that groups connected RTCs).
# @code
#   "plugins": [{"module": "first_fit_placement"}],
#   "startup": {"mode": "auto", "placement_plugin": "first_fit", "placement_args": {"order": ["robot1", "robot2", "robot3"]}, ...}
# @endcode
# RTCs are placed in the order of "components" in the configuration file, each on the first robot that fits,
# trying robots in the order of "order" (default: primary, then the other robots). Connections are not considered.
# If an RTC cannot be placed, placement.PlacementError is raised (the system startup fails).
# @~
#
# @date $Date: 2026-11-13 16:24:22 $
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

PLUGIN_API = 1


##
# @~japanese
# @brief プラグインを登録する (配置のロジック first_fit を登録する)
#
# @param ctx プラグインのコンテキスト
# @param config プラグインの設定 (使わない)
# @~english
# @brief Registers the plugin (registers the placement logic first_fit)
#
# @param ctx plugin context
# @param config plugin configuration (not used)
# @~
def setup(ctx, config):
    def first_fit(ctx, items, robots, edges, primary, args):
        import RTCPlacement as pl
        order = args.get("order") or [primary] + [r.name for r in robots if r.name != primary]
        rmap = {r.name: r for r in robots}
        used = {r.name: {"cpu": 0.0, "mem": 0.0, "langs": set(r.languages)} for r in robots}
        assign = {}
        for it in items:
            for name in order:
                if name not in it.candidates:
                    continue
                u, r = used[name], rmap[name]
                extra = 0.0 if it.language in u["langs"] else it.slave_overhead_mb
                if u["cpu"] + it.cpu <= r.cpu_free and u["mem"] + it.memory_mb + extra <= r.mem_free_mb:
                    u["cpu"] += it.cpu
                    u["mem"] += it.memory_mb + extra
                    u["langs"].add(it.language)
                    assign[it.name] = name
                    break
            else:
                raise pl.PlacementError(f"first_fit: {it.name} を置けるロボットがありません",
                                        pl.capacity_report(items, robots))
        return assign

    ctx.register_placement("first_fit", first_fit)
