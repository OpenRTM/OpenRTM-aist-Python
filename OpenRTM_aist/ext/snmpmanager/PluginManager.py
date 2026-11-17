#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file PluginManager.py
# @brief Plugin mechanism of SNMPManager (independent of OpenRTM / SNMP)
#
# @~japanese
# SNMPManager のプラグイン機構 (OpenRTM / SNMP には依存しない)
#
# プラグインは setup(ctx, config) を持つ Python のファイル。setup の中で、次の拡張ポイントに関数を登録する。
# @verbatim
#   ctx.register_condition(name, fn)   fn(ctx, args, now) -> bool
#         migration_conditions の条件に {"plugin": name, "args": {...}} と書くと呼ばれる
#   ctx.register_action(name, fn)      fn(ctx, args) -> bool (成功したか)
#         migration / startup に {"plugin": name, "args": {...}} と書くと、計画の適用の代わりに呼ばれる
#   ctx.register_placement(name, fn)   fn(ctx, items, robots, edges, primary, args) -> {RTC 名: ロボット名}
#         startup (mode: auto) に "placement_plugin": name と書くと、組み込みのソルバの代わりに呼ばれる
#   ctx.register_objective(name, fn)   fn(ctx, item, robot, state, args) -> float (大きいほどよい)
#         startup / migration (mode: auto) に "logic": "objective", "objective_plugin": name と書くと、
#         配置の objective のロジック (RTC ごとに目的関数が最大のロボットを選ぶ) の目的関数として呼ばれる
#   ctx.subscribe(kind, fn)            fn(ctx, event) ; kind は "down" などのイベント種別、"*" で全部
#         イベント (discovered / down / up / startup_* / migration_* など) が起きると呼ばれる
# @endverbatim
# 設定 (migration.json などの最上位):
# @code
#   "plugins": [{"module": "least_loaded_migration", "config": {...}}, ...]
# @endcode
# module は snmp.plugin.path (カンマ区切り) のディレクトリから探す (拡張子 .py は省略可)。
# @~english
# A plugin is a Python file with setup(ctx, config). In setup, it registers functions to the following extension points.
# @verbatim
#   ctx.register_condition(name, fn)   fn(ctx, args, now) -> bool
#         called when {"plugin": name, "args": {...}} is written as a condition in migration_conditions
#   ctx.register_action(name, fn)      fn(ctx, args) -> bool (whether it succeeded)
#         called instead of applying the plan when {"plugin": name, "args": {...}} is written in migration / startup
#   ctx.register_placement(name, fn)   fn(ctx, items, robots, edges, primary, args) -> {RTC name: robot name}
#         called instead of the built-in solver when "placement_plugin": name is written in startup (mode: auto)
#   ctx.register_objective(name, fn)   fn(ctx, item, robot, state, args) -> float (larger is better)
#         called as the objective function of the objective logic (choose the robot maximizing the objective for each RTC)
#         when "logic": "objective", "objective_plugin": name is written in startup / migration (mode: auto)
#   ctx.subscribe(kind, fn)            fn(ctx, event) ; kind is an event kind such as "down", or "*" for all
#         called when an event (discovered / down / up / startup_* / migration_* etc.) occurs
# @endverbatim
# Settings (top level of migration.json etc.):
# @code
#   "plugins": [{"module": "least_loaded_migration", "config": {...}}, ...]
# @endcode
# module is searched in the directories of snmp.plugin.path (comma separated); the extension .py may be omitted.
# @~
#
# @date $Date: 2026-11-13 16:24:33 $
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

import importlib.util
import os
import queue
import threading
import time
import traceback

PLUGIN_API_VERSION = 1


##
# @~japanese
# @brief プラグインの読み込みや登録の誤りを表す例外
# @~english
# @brief Exception for errors in loading or registering plugins
# @~
class PluginError(Exception):
    pass


##
# @~japanese
# @brief 登録された関数を持つ。PluginContext から使う
# @~english
# @brief Holds the registered functions. Used from PluginContext
# @~
class PluginRegistry:

    ##
    # @~japanese
    # @brief コンストラクタ
    # @~english
    # @brief Constructor
    # @~
    def __init__(self):
        self.conditions = {}
        self.actions = {}
        self.placements = {}
        self.objectives = {}
        self.subscribers = []      # (kind, fn, plugin 名)
        self.loaded = []           # [(module 名, path)]

    ##
    # @~japanese
    # @brief 関数を表に登録する (呼び出せない、または同じ名前が登録済みなら PluginError)
    #
    # @param table 登録先の表
    # @param kind 種別 (condition など)
    # @param name 名前
    # @param fn 関数
    # @param plugin 登録するプラグインの名前
    # @~english
    # @brief Registers a function to a table (PluginError if not callable or the name is already registered)
    #
    # @param table table to register to
    # @param kind kind (condition etc.)
    # @param name name
    # @param fn function
    # @param plugin name of the registering plugin
    # @~
    def _put(self, table, kind, name, fn, plugin):
        if not callable(fn):
            raise PluginError(f"{plugin}: {kind} {name} is not callable")
        if name in table:
            raise PluginError(f"{plugin}: {kind} '{name}' is already registered by {table[name][1]}")
        table[name] = (fn, plugin)


##
# @~japanese
# @brief プラグインに渡す API。SNMPManager がサブクラスで実装を与える (host)
#
# host に必要なメソッド: log(msg), robots(), manager(name), apply_plan(plan, label), find_component(instance, manager), conf(key, default), event(robot, kind, detail), migration_config()
# @~english
# @brief API given to plugins. SNMPManager provides the implementation (host)
#
# Methods required of the host: log(msg), robots(), manager(name), apply_plan(plan, label), find_component(instance, manager), conf(key, default), event(robot, kind, detail), migration_config()
# @~
class PluginContext:

    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param host SNMPManager (機能を与えるもの)
    # @param registry 登録先
    # @param plugin_name プラグインの名前
    # @~english
    # @brief Constructor
    #
    # @param host SNMPManager (provider of the functions)
    # @param registry registry
    # @param plugin_name name of the plugin
    # @~
    def __init__(self, host, registry, plugin_name="(core)"):
        self._host = host
        self._registry = registry
        self.plugin = plugin_name

    # ---- 登録 ----------------------------------------------------------
    ##
    # @~japanese
    # @brief 条件 (condition) を登録する
    #
    # @param name 名前
    # @param fn fn(ctx, args, now) -> bool
    # @~english
    # @brief Registers a condition
    #
    # @param name name
    # @param fn fn(ctx, args, now) -> bool
    # @~
    def register_condition(self, name, fn):
        self._registry._put(self._registry.conditions, "condition", name, fn, self.plugin)

    ##
    # @~japanese
    # @brief 処理 (action) を登録する
    #
    # @param name 名前
    # @param fn fn(ctx, args) -> bool
    # @~english
    # @brief Registers an action
    #
    # @param name name
    # @param fn fn(ctx, args) -> bool
    # @~
    def register_action(self, name, fn):
        self._registry._put(self._registry.actions, "action", name, fn, self.plugin)

    ##
    # @~japanese
    # @brief 配置 (placement) のロジックを登録する
    #
    # @param name 名前
    # @param fn fn(ctx, items, robots, edges, primary, args) -> {RTC 名: ロボット名}
    # @~english
    # @brief Registers a placement logic
    #
    # @param name name
    # @param fn fn(ctx, items, robots, edges, primary, args) -> {RTC name: robot name}
    # @~
    def register_placement(self, name, fn):
        self._registry._put(self._registry.placements, "placement", name, fn, self.plugin)

    ##
    # @~japanese
    # @brief 目的関数 (objective) を登録する
    #
    # @param name 名前
    # @param fn fn(ctx, item, robot, state, args) -> float
    # @~english
    # @brief Registers an objective function
    #
    # @param name name
    # @param fn fn(ctx, item, robot, state, args) -> float
    # @~
    def register_objective(self, name, fn):
        self._registry._put(self._registry.objectives, "objective", name, fn, self.plugin)

    ##
    # @~japanese
    # @brief イベントを購読する
    #
    # @param kind イベントの種別 ("*" で全部)
    # @param fn fn(ctx, event)
    # @~english
    # @brief Subscribes to events
    #
    # @param kind event kind ("*" for all)
    # @param fn fn(ctx, event)
    # @~
    def subscribe(self, kind, fn):
        if not callable(fn):
            raise PluginError(f"{self.plugin}: subscriber is not callable")
        self._registry.subscribers.append((kind, fn, self.plugin))

    # ---- SNMPManager の機能 --------------------------------------------
    ##
    # @~japanese
    # @brief 自分のロボット (マネージャ) の名前を返す
    #
    # @return 名前
    # @~english
    # @brief Returns the name of this robot (manager)
    #
    # @return name
    # @~
    @property
    def name(self):
        return self._host.name

    ##
    # @~japanese
    # @brief ログを出す
    #
    # @param message メッセージ
    # @~english
    # @brief Outputs a log message
    #
    # @param message message
    # @~
    def log(self, message):
        self._host.log(f"[plugin {self.plugin}] {message}")

    ##
    # @~japanese
    # @brief 全ロボット (自分を含む) の状態のスナップショットを返す
    #
    # @return [{"name", "ip", "status", "is_local", "cpu_usage", "memory_usage", "latency_ms", "jitter_ms", "packet_loss", "wifi_signal_dbm", "cgroup": {...}}]
    # @~english
    # @brief Returns a snapshot of the states of all robots (including this one)
    #
    # @return [{"name", "ip", "status", "is_local", "cpu_usage", "memory_usage", "latency_ms", "jitter_ms", "packet_loss", "wifi_signal_dbm", "cgroup": {...}}]
    # @~
    def robots(self):
        return self._host.robots()

    ##
    # @~japanese
    # @brief 名前でロボットの状態を返す
    #
    # @param name ロボット名
    # @return 状態 (なければ None)
    # @~english
    # @brief Returns the state of a robot by name
    #
    # @param name robot name
    # @return state (None if not found)
    # @~
    def robot(self, name):
        return next((r for r in self.robots() if r["name"] == name), None)

    ##
    # @~japanese
    # @brief 生きているロボットの状態を返す
    #
    # @return 状態のリスト
    # @~english
    # @brief Returns the states of the alive robots
    #
    # @return list of states
    # @~
    def alive_robots(self):
        return [r for r in self.robots() if r["status"] == "alive"]

    ##
    # @~japanese
    # @brief ロボット名のマスターマネージャを返す
    #
    # @param name ロボット名
    # @return RTM.Manager の CORBA 参照
    # @~english
    # @brief Returns the master manager of a robot
    #
    # @param name robot name
    # @return CORBA reference of RTM.Manager
    # @~
    def manager(self, name):
        return self._host.manager(name)

    ##
    # @~japanese
    # @brief インスタンス名で RTC を探す (スレーブマネージャも含む)
    #
    # @param instance_name インスタンス名
    # @param manager_name ロボット名
    # @return RTC の参照 (なければ None)
    # @~english
    # @brief Finds an RTC by instance name (including slave managers)
    #
    # @param instance_name instance name
    # @param manager_name robot name
    # @return reference of the RTC (None if not found)
    # @~
    def find_component(self, instance_name, manager_name):
        return self._host.find_component(instance_name, manager_name)

    ##
    # @~japanese
    # @brief migration と同じ形式の計画 ({"components", "connections", "remove"}) を適用する
    #
    # @param plan 計画
    # @param label ログに出す名前
    # @~english
    # @brief Applies a plan in the same format as migration ({"components", "connections", "remove"})
    #
    # @param plan plan
    # @param label name shown in logs
    # @~
    def apply_plan(self, plan, label="plugin"):
        return self._host.apply_plan(plan, label)

    ##
    # @~japanese
    # @brief rtc.conf の値を返す
    #
    # @param key キー
    # @param default 既定値
    # @return 値
    # @~english
    # @brief Returns a value of rtc.conf
    #
    # @param key key
    # @param default default value
    # @return value
    # @~
    def conf(self, key, default=""):
        return self._host.conf(key, default)

    ##
    # @~japanese
    # @brief 現在の構成ファイル (migration.json など) の内容を返す
    #
    # @return 構成ファイルの内容
    # @~english
    # @brief Returns the contents of the current configuration file (migration.json etc.)
    #
    # @return contents of the configuration file
    # @~
    def migration_config(self):
        return self._host.migration_config()

    ##
    # @~japanese
    # @brief イベントを記録する (ログと SQLite。ほかのプラグインの subscribe にも届く)
    #
    # @param robot ロボット名
    # @param kind イベントの種別
    # @param detail 詳細
    # @~english
    # @brief Records an event (logs and SQLite; also delivered to the subscribers of other plugins)
    #
    # @param robot robot name
    # @param kind event kind
    # @param detail details
    # @~
    def event(self, robot, kind, detail=""):
        self._host.event(robot, kind, detail)


##
# @~japanese
# @brief プラグインを読み込み、登録された関数を呼び出す
# @~english
# @brief Loads plugins and calls the registered functions
# @~
class PluginManager:
    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param host SNMPManager (機能を与えるもの)
    # @param paths プラグインを探すディレクトリのリスト
    # @~english
    # @brief Constructor
    #
    # @param host SNMPManager (provider of the functions)
    # @param paths list of directories to search for plugins
    # @~
    def __init__(self, host, paths):
        self.host = host
        self.paths = [p for p in paths if p]
        self.registry = PluginRegistry()
        self._events = queue.Queue()
        self._thread = None
        self._signature = None

    # ---- 読み込み ------------------------------------------------------
    ##
    # @~japanese
    # @brief プラグインのファイルを探す (なければ PluginError)
    #
    # \<module\>.py がなければ、大文字小文字と "_" を無視して \<module\>Plugin.py と一致するファイルを探す
    # (例: least_loaded_migration -> LeastLoadedMigrationPlugin.py)
    #
    # @param module モジュール名 (拡張子 .py は省略可)
    # @return ファイルのパス
    # @~english
    # @brief Finds the file of a plugin (PluginError if not found)
    #
    # If \<module\>.py is not found, a file that matches \<module\>Plugin.py ignoring the case and "_" is searched
    # (e.g. least_loaded_migration -> LeastLoadedMigrationPlugin.py).
    #
    # @param module module name (the extension .py may be omitted)
    # @return path of the file
    # @~
    def find(self, module):
        name = module if module.endswith(".py") else module + ".py"
        if os.path.isabs(name) and os.path.isfile(name):
            return name
        for d in self.paths:
            p = os.path.join(d, name)
            if os.path.isfile(p):
                return p
        key = name[:-3].replace("_", "").lower() + "plugin.py"
        for d in self.paths:
            try:
                files = sorted(os.listdir(d))
            except OSError:
                continue
            for f in files:
                if f.replace("_", "").lower() == key and os.path.isfile(os.path.join(d, f)):
                    return os.path.join(d, f)
        raise PluginError(f"plugin module {module} not found in {self.paths}")

    ##
    # @~japanese
    # @brief プラグインをすべて読み込む。同じ内容なら読み込み直さない
    #
    # @param specs [{"module": ..., "config": {...}}]
    # @~english
    # @brief Loads all plugins. Does not reload if the specs are the same
    #
    # @param specs [{"module": ..., "config": {...}}]
    # @~
    def load_all(self, specs):
        signature = repr(specs)
        if signature == self._signature:
            return False
        self.registry = PluginRegistry()
        for spec in specs or []:
            if isinstance(spec, str):
                spec = {"module": spec}
            module = spec.get("module")
            if not module:
                raise PluginError("plugin entry needs module")
            path = self.find(module)
            modname = "snmpmgr_plugin_" + os.path.splitext(os.path.basename(path))[0]
            mspec = importlib.util.spec_from_file_location(modname, path)
            mod = importlib.util.module_from_spec(mspec)
            mspec.loader.exec_module(mod)
            api = getattr(mod, "PLUGIN_API", PLUGIN_API_VERSION)
            if api != PLUGIN_API_VERSION:
                raise PluginError(f"{module}: PLUGIN_API {api} is not supported (expected {PLUGIN_API_VERSION})")
            setup = getattr(mod, "setup", None)
            if not callable(setup):
                raise PluginError(f"{module}: setup(ctx, config) is not defined")
            ctx = PluginContext(self.host, self.registry, spec.get("name") or os.path.splitext(os.path.basename(path))[0])
            setup(ctx, spec.get("config", {}))
            self.registry.loaded.append((ctx.plugin, path))
        self._signature = signature
        return True

    ##
    # @~japanese
    # @brief 読み込んだプラグインと登録された関数の説明を返す
    #
    # @return 説明文
    # @~english
    # @brief Returns a description of the loaded plugins and registered functions
    #
    # @return description
    # @~
    def describe(self):
        r = self.registry
        return (f"plugins: {', '.join(n for n, _ in r.loaded) or '-'}; "
                f"conditions: {', '.join(r.conditions) or '-'}; actions: {', '.join(r.actions) or '-'}; "
                f"placements: {', '.join(r.placements) or '-'}; objectives: {', '.join(r.objectives) or '-'}; "
                f"subscribers: {len(r.subscribers)}")

    # ---- 呼び出し ------------------------------------------------------
    ##
    # @~japanese
    # @brief プラグインに渡すコンテキストを作る
    #
    # @param plugin プラグインの名前
    # @return PluginContext
    # @~english
    # @brief Makes the context given to a plugin
    #
    # @param plugin name of the plugin
    # @return PluginContext
    # @~
    def _ctx(self, plugin):
        return PluginContext(self.host, self.registry, plugin)

    ##
    # @~japanese
    # @brief 条件が登録されているか
    #
    # @param name 名前
    # @return 登録されていれば True
    # @~english
    # @brief Whether the condition is registered
    #
    # @param name name
    # @return True if registered
    # @~
    def has_condition(self, name):
        return name in self.registry.conditions

    ##
    # @~japanese
    # @brief 処理が登録されているか
    #
    # @param name 名前
    # @return 登録されていれば True
    # @~english
    # @brief Whether the action is registered
    #
    # @param name name
    # @return True if registered
    # @~
    def has_action(self, name):
        return name in self.registry.actions

    ##
    # @~japanese
    # @brief 配置のロジックが登録されているか
    #
    # @param name 名前
    # @return 登録されていれば True
    # @~english
    # @brief Whether the placement logic is registered
    #
    # @param name name
    # @return True if registered
    # @~
    def has_placement(self, name):
        return name in self.registry.placements

    ##
    # @~japanese
    # @brief 目的関数が登録されているか
    #
    # @param name 名前
    # @return 登録されていれば True
    # @~english
    # @brief Whether the objective function is registered
    #
    # @param name name
    # @return True if registered
    # @~
    def has_objective(self, name):
        return name in self.registry.objectives

    ##
    # @~japanese
    # @brief 条件を呼び出す
    #
    # @param name 名前
    # @param args 引数
    # @param now 現在の時刻
    # @return 条件を満たせば True
    # @~english
    # @brief Calls a condition
    #
    # @param name name
    # @param args arguments
    # @param now current time
    # @return True if the condition holds
    # @~
    def condition(self, name, args, now):
        fn, plugin = self.registry.conditions[name]
        return bool(fn(self._ctx(plugin), args or {}, now))

    ##
    # @~japanese
    # @brief 処理を呼び出す
    #
    # @param name 名前
    # @param args 引数
    # @return 成功すれば True
    # @~english
    # @brief Calls an action
    #
    # @param name name
    # @param args arguments
    # @return True if succeeded
    # @~
    def action(self, name, args):
        fn, plugin = self.registry.actions[name]
        return fn(self._ctx(plugin), args or {})

    ##
    # @~japanese
    # @brief 配置のロジックを呼び出す
    #
    # @param name 名前
    # @param items 配置する RTC
    # @param robots ロボット
    # @param edges 接続
    # @param primary 主ロボットの名前
    # @param args placement_args
    # @return {RTC 名: ロボット名}
    # @~english
    # @brief Calls a placement logic
    #
    # @param name name
    # @param items RTCs to place
    # @param robots robots
    # @param edges connections
    # @param primary name of the primary robot
    # @param args placement_args
    # @return {RTC name: robot name}
    # @~
    def placement(self, name, items, robots, edges, primary, args):
        fn, plugin = self.registry.placements[name]
        return fn(self._ctx(plugin), items, robots, edges, primary, args or {})

    ##
    # @~japanese
    # @brief 目的関数を呼び出す
    #
    # @param name 名前
    # @param item 置く RTC
    # @param robot 置くロボット
    # @param state 配置の途中の状態
    # @param args objective_args
    # @return 目的関数の値
    # @~english
    # @brief Calls an objective function
    #
    # @param name name
    # @param item RTC to place
    # @param robot robot to place on
    # @param state state of the placement
    # @param args objective_args
    # @return value of the objective function
    # @~
    def objective(self, name, item, robot, state, args):
        fn, plugin = self.registry.objectives[name]
        return float(fn(self._ctx(plugin), item, robot, state, args or {}))

    # ---- イベント (専用スレッドで配る。通知元を待たせない) ---------------
    ##
    # @~japanese
    # @brief イベントを購読者に配る (専用スレッドで配る。通知元を待たせない)
    #
    # @param event イベント
    # @~english
    # @brief Delivers an event to the subscribers (delivered on a dedicated thread; the notifier does not wait)
    #
    # @param event event
    # @~
    def publish(self, event):
        if not self.registry.subscribers:
            return
        if self._thread is None:
            self._thread = threading.Thread(target=self._dispatch, daemon=True)
            self._thread.start()
        self._events.put(event)

    ##
    # @~japanese
    # @brief イベントを配るスレッドの本体
    # @~english
    # @brief Body of the thread that delivers events
    # @~
    def _dispatch(self):
        while True:
            event = self._events.get()
            for kind, fn, plugin in list(self.registry.subscribers):
                if kind not in ("*", event.get("kind")):
                    continue
                try:
                    fn(self._ctx(plugin), event)
                except Exception:
                    self.host.log(f"[plugin {plugin}] event handler failed: {traceback.format_exc()}")


##
# @~japanese
# @brief イベントの辞書を作る
#
# @param observer 観測したロボットの名前
# @param robot 対象のロボットの名前
# @param kind イベントの種別
# @param detail 詳細
# @return {"time", "observer", "robot", "kind", "detail"}
# @~english
# @brief Makes an event dictionary
#
# @param observer name of the observing robot
# @param robot name of the target robot
# @param kind event kind
# @param detail details
# @return {"time", "observer", "robot", "kind", "detail"}
# @~
def make_event(observer, robot, kind, detail):
    return {"time": time.time(), "observer": observer, "robot": robot, "kind": kind, "detail": detail}
