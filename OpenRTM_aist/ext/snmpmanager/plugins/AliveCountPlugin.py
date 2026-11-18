#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file AliveCountPlugin.py
# @brief Example condition plugin: decides by the number of alive robots
#
# @~japanese
# 条件 (condition) プラグインの例: 生きているロボットの数で判定する
#
# migration.json での使い方:
# @code
#   "plugins": [{"module": "alive_count"}],
#   "migration_conditions": {"operator": "AND", "conditions": [
#       {"plugin": "alive_count", "args": {"op": ">=", "value": 2}}
#   ]}
# @endcode
# args:
# - op: 比較演算子 (<, \<=, \>, >=, ==, !=。既定 ">=")
# - value: 比べる数
# - robots: 数える対象のロボット名のリスト (省略時は全ロボット。自分を含む)
# @~english
# Usage in migration.json:
# @code
#   "plugins": [{"module": "alive_count"}],
#   "migration_conditions": {"operator": "AND", "conditions": [
#       {"plugin": "alive_count", "args": {"op": ">=", "value": 2}}
#   ]}
# @endcode
# args:
# - op: comparison operator (<, \<=, \>, >=, ==, !=; default ">=")
# - value: the number to compare with
# - robots: names of the robots to count (default: all robots, including this one)
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

import operator

PLUGIN_API = 1
OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge,
       "==": operator.eq, "!=": operator.ne}


##
# @~japanese
# @brief プラグインを登録する (条件 alive_count を登録する)
#
# @param ctx プラグインのコンテキスト
# @param config migration.json の plugins の項目
# @~english
# @brief Registers the plugin (registers the condition alive_count)
#
# @param ctx plugin context
# @param config entry of "plugins" in migration.json
# @~
def setup(ctx, config) -> None:
    def alive_count(ctx, args, now):
        targets = set(args.get("robots", []))
        n = sum(1 for r in ctx.alive_robots() if not targets or r["name"] in targets)
        return OPS[args.get("op", ">=")](n, int(args["value"]))

    ctx.register_condition("alive_count", alive_count)
