#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file LeastLoadedMigrationPlugin.py
# @brief Example action plugin: migrates RTCs to the alive robot with the lowest load at that time
#
# @~japanese
# 処理 (action) プラグインの例: 移動先を、その時点で負荷が最も低い生きているロボットに決めて移す
#
# migration.json の migration を固定の計画の代わりにこのプラグインにすると、移動先をあらかじめ書かなくてよくなる。
# @code
#   "plugins": [{"module": "least_loaded_migration"}],
#   "migration": {
#     "executor": "robot1",
#     "plugin": "least_loaded_migration",
#     "args": {
#       "from": "robot1",                       # 移動元 (このロボットの RTC を消す)
#       "exclude": ["robot1"],                  # 移動先にしないロボット (省略時は from)
#       "components": [                         # 移す RTC (移動先で create し、移動元から remove する)
#         {"name": "SeqOut0", "create": "SeqOut?instance_name=SeqOut0", "activate": true}
#       ],
#       "connections": [ ... migration と同じ形式 ... ]
#     }
#   }
# @endcode
# connections に出てくる、移さない RTC (SeqIn0 など) は、生きているロボットから自動で探して existing にする。
# 負荷は cgroup の CPU 使用率 / 制限 (なければ cpu_usage) で比べ、1 つ置くたびに load_step だけ足して分散させる。
# @~english
# When "migration" in migration.json uses this plugin instead of a fixed plan, the destinations need not be written in advance.
# @code
#   "plugins": [{"module": "least_loaded_migration"}],
#   "migration": {
#     "executor": "robot1",
#     "plugin": "least_loaded_migration",
#     "args": {
#       "from": "robot1",                       # source robot (its RTCs are removed)
#       "exclude": ["robot1"],                  # robots not used as destinations (default: from)
#       "components": [                         # RTCs to migrate (created on the destination, removed from the source)
#         {"name": "SeqOut0", "create": "SeqOut?instance_name=SeqOut0", "activate": true}
#       ],
#       "connections": [ ... same format as migration ... ]
#     }
#   }
# @endcode
# RTCs in "connections" that are not migrated (such as SeqIn0) are found automatically on the alive robots and used as "existing".
# The load is compared by the cgroup CPU usage / limit (cpu_usage if not available); load_step is added each time an RTC is placed so that RTCs are distributed.
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

PLUGIN_API = 1


##
# @~japanese
# @brief プラグインを登録する (処理 least_loaded_migration を登録する)
#
# @param ctx プラグインのコンテキスト
# @param config プラグインの設定 (load_step: 1 つ置くたびに足す負荷。既定 10)
# @~english
# @brief Registers the plugin (registers the action least_loaded_migration)
#
# @param ctx plugin context
# @param config plugin configuration (load_step: load added for each placed RTC; default 10)
# @~
def setup(ctx, config) -> None:
    default_step = float(config.get("load_step", 10.0))

    def load_of(robot):
        cg = robot.get("cgroup") or {}
        if cg.get("cpu_limit_pct"):
            return 100.0 * float(cg.get("cpu_usage_pct") or 0.0) / float(cg["cpu_limit_pct"])
        try:
            return float(robot.get("cpu_usage") or 0.0)
        except (TypeError, ValueError):
            return 0.0

    def migrate(ctx, args) -> bool:
        source = args["from"]
        exclude = set(args.get("exclude", [source]))
        step = float(args.get("load_step", default_step))
        targets = {r["name"]: load_of(r) for r in ctx.alive_robots() if r["name"] not in exclude}
        if not targets:
            ctx.log("移動先にできる生きているロボットがありません")
            return False
        moved = {c["name"] for c in args["components"]}
        components, remove = [], []
        for c in args["components"]:
            dest = min(targets, key=lambda n: (targets[n], n))
            targets[dest] += step
            components.append(dict(c, manager=dest))
            remove.append({"name": c["name"], "manager": source})
            ctx.log(f"{c['name']}: {source} -> {dest}")
        # 接続先のうち移さない RTC は、生きているロボットから探して existing にする
        others = set()
        for conn in args.get("connections", []):
            for end in ("source", "target"):
                if conn[end]["component"] not in moved:
                    others.add(conn[end]["component"])
        for name in sorted(others):
            where = None
            for r in ctx.alive_robots():
                try:
                    if ctx.find_component(name, r["name"]) is not None:
                        where = r["name"]
                        break
                except Exception:
                    continue
            if where is None:
                ctx.log(f"接続先の {name} が見つかりません")
                return False
            components.append({"name": name, "manager": where, "existing": name,
                               "activate": args.get("activate_existing", True)})
        plan = {"components": components, "connections": args.get("connections", []), "remove": remove}
        ctx.apply_plan(plan, "least_loaded_migration")
        ctx.event(ctx.name, "plugin_migration", ", ".join(f"{c['name']}@{c['manager']}" for c in components
                                                          if c["name"] in moved))
        return True

    ctx.register_action("least_loaded_migration", migrate)
