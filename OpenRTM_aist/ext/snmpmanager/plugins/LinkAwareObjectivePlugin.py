#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file LinkAwareObjectivePlugin.py
# @brief Example objective plugin: an objective logic that weighs the link quality
#
# @~japanese
# 目的関数 (objective) プラグインの例: 通信状態を重く見る objective のロジック
#
# startup / migration (mode: auto) に次のように書くと、RTC ごとに、この関数の値が最大のロボットに置く。
# @code
#   "logic": "objective",
#   "objective_plugin": "link_aware",
#   "objective_args": {"latency_weight": 1.0, "loss_weight": 1.0}
# @endcode
# @verbatim
# 値 = 置いた後に残る CPU とメモリの割合
#      - ロボットをまたぐ通信量 (KB/s) x (1 + そのロボットのレイテンシ ms x latency_weight / 10)
#      - そのロボットのパケットロス (%) x loss_weight / 10
# @endverbatim
# item / robot は placement.Item / placement.Robot、state は {"assign", "usage", "edges", "primary", "robots"}。
# @~english
# When written in startup / migration (mode: auto) as below, each RTC is placed on the robot that maximizes this function.
# @code
#   "logic": "objective",
#   "objective_plugin": "link_aware",
#   "objective_args": {"latency_weight": 1.0, "loss_weight": 1.0}
# @endcode
# @verbatim
# value = ratio of CPU and memory left after placing
#         - traffic across robots (KB/s) x (1 + latency of the robot in ms x latency_weight / 10)
#         - packet loss of the robot (%) x loss_weight / 10
# @endverbatim
# item / robot are placement.Item / placement.Robot; state is {"assign", "usage", "edges", "primary", "robots"}.
# @~
#
# @date $Date: 2026-11-13 16:24:23 $
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

##
# @~japanese
# @brief プラグインを登録する (目的関数 link_aware を登録する)
#
# @param ctx プラグインのコンテキスト
# @param config プラグインの設定 (latency_weight、loss_weight の既定値)
# @~english
# @brief Registers the plugin (registers the objective function link_aware)
#
# @param ctx plugin context
# @param config plugin configuration (defaults of latency_weight and loss_weight)
# @~
def setup(ctx, config):
    def link_aware(ctx, item, robot, state, args):
        lw = float(args.get("latency_weight", config.get("latency_weight", 1.0)))
        pw = float(args.get("loss_weight", config.get("loss_weight", 1.0)))
        u = state["usage"][robot.name]
        cpu_left = (robot.cpu_free - u["cpu"] - item.cpu) / robot.cpu_free if robot.cpu_free > 0 else 0.0
        mem_left = (robot.mem_free_mb - u["mem"] - item.memory_mb) / robot.mem_free_mb if robot.mem_free_mb > 0 else 0.0
        traffic = 0.0
        for e in state["edges"]:
            other = e.b if e.a == item.name else (e.a if e.b == item.name else None)
            if other is not None and other in state["assign"] and state["assign"][other] != robot.name:
                traffic += e.weight
        link = robot.link or {}
        latency = float(link.get("latency_ms") or 0.0)
        loss = float(link.get("packet_loss") or 0.0)
        return cpu_left + mem_left - traffic / 1000.0 * (1.0 + latency * lw / 10.0) - loss * pw / 10.0

    ctx.register_objective("link_aware", link_aware)
