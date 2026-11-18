#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file EventLogPlugin.py
# @brief Example event plugin: appends events to a JSON Lines file
#
# @~japanese
# イベント (event) プラグインの例: イベントを JSON Lines のファイルに追記する
#
# 外部への通知 (HTTP の webhook など) も、同じ形で subscribe すれば作れる。
# @code
#   "plugins": [{"module": "event_log", "config": {"path": "/var/lib/rtm/plugin_events.jsonl",
#                                                   "kinds": ["down", "up", "migration_completed"]}}]
# @endcode
# config:
# - path: 出力先 (既定 plugin_events.jsonl)
# - kinds: 記録するイベントの種別 (省略時は全部)
# @~english
# Notifications to external systems (such as an HTTP webhook) can be made by subscribing in the same way.
# @code
#   "plugins": [{"module": "event_log", "config": {"path": "/var/lib/rtm/plugin_events.jsonl",
#                                                   "kinds": ["down", "up", "migration_completed"]}}]
# @endcode
# config:
# - path: output file (default plugin_events.jsonl)
# - kinds: kinds of events to record (default: all)
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

import json
import threading

PLUGIN_API = 1


##
# @~japanese
# @brief プラグインを登録する (config の kinds のイベントを購読し、ファイルに書く)
#
# @param ctx プラグインのコンテキスト
# @param config プラグインの設定 (path、kinds)
# @~english
# @brief Registers the plugin (subscribes to the event kinds in config and writes them to the file)
#
# @param ctx plugin context
# @param config plugin configuration (path, kinds)
# @~
def setup(ctx, config) -> None:
    path = config.get("path", "plugin_events.jsonl")
    lock = threading.Lock()

    def write(ctx, event) -> None:
        with lock, open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    for kind in config.get("kinds", ["*"]):
        ctx.subscribe(kind, write)
