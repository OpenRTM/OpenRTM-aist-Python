#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file SNMPManager.py
# @brief SNMPManager: master manager for monitoring, migration, automatic placement and recovery via SNMP
#
# @~japanese
# SNMPManager: SNMP による監視・マイグレーション・自動配置・自動復旧を行うマスターマネージャ
#
# OpenRTM-aist-Python のマスターマネージャに読み込む (または単独で起動する)。ロボットどうしを SNMP で発見し合い、監視の値 (死活、CPU、メモリ、電波強度、通信状態、cgroup、追加の監視の値) を集め、構成ファイル (migration.json) に従って、起動時の構成の適用、条件によるマイグレーション、RTC の自動配置、故障した RTC の自動復旧を行う。
# @~english
# Loaded into the master manager of OpenRTM-aist-Python (or started standalone). Robots discover each other via SNMP, collect monitoring values (liveness, CPU, memory, RSSI, link quality, cgroup and additional metrics), and, following the configuration file (migration.json), apply the startup configuration, migrate on conditions, place RTCs automatically and recover failed RTCs automatically.
# @~
#
# @date $Date: 2026-11-13 16:24:20 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2025
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import os
import sys
import platform

import RTC
import RTM
import OpenRTM_aist
from omniORB import CORBA

import socket
import time
import threading
import psutil
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import asyncio
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine, CommunityData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, NotificationType, get_cmd,
    walk_cmd, send_notification,
)
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.carrier.asyncio.dgram import udp
from pysnmp.entity import config
from pysnmp.entity.rfc3413 import ntfrcv
import traceback

import time
import datetime
import json
import ipaddress
import re
import operator
import collections
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import CustomMetrics      # 追加の監視の値 (カスタムメトリクス)


##
# @~japanese
# @brief 今日の 0 時からの秒数を返す
#
# @return 秒数
# @~english
# @brief Returns the seconds since midnight today
#
# @return seconds
# @~
def seconds_since_midnight():
    now = datetime.datetime.now()
    midnight = datetime.datetime.combine(now.date(), datetime.time())
    delta = now - midnight
    return delta.total_seconds()

##
# @~japanese
# @brief リトライしても解決しない起動時の失敗 (ロードできない RTC、制限内に配置できない等)
# @~english
# @brief Startup failure that retrying does not resolve (an RTC that cannot be loaded, cannot be placed within the limits, etc.)
# @~
class StartupFailure(Exception):

    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param message メッセージ
    # @param reasons 理由の一覧
    # @~english
    # @brief Constructor
    #
    # @param message message
    # @param reasons list of reasons
    # @~
    def __init__(self, message, reasons=None):
        super().__init__(message)
        self.reasons = reasons or []


##
# @~japanese
# @brief プラグイン (PluginManager.PluginContext) に SNMPManager の機能を渡す窓口
# @~english
# @brief Gateway that provides the functions of SNMPManager to plugins (PluginManager.PluginContext)
# @~
class _PluginHost:

    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param mgr SNMPManager
    # @~english
    # @brief Constructor
    #
    # @param mgr SNMPManager
    # @~
    def __init__(self, mgr):
        self._m = mgr

    ##
    # @~japanese
    # @brief 自分のロボットの名前を返す
    #
    # @return 名前
    # @~english
    # @brief Returns the name of this robot
    #
    # @return name
    # @~
    @property
    def name(self):
        return self._m._name

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
        self._m._log(message)

    ##
    # @~japanese
    # @brief 全ロボットの状態のスナップショットを返す
    #
    # @return 状態の辞書のリスト
    # @~english
    # @brief Returns a snapshot of the states of all robots
    #
    # @return list of state dictionaries
    # @~
    def robots(self):
        m = self._m
        with m._robot_lock:
            robots = ([m._robot] if m._robot is not None else []) + list(m._robotList)
        out = []
        for r in robots:
            snap = m._snapshot(r)
            snap.update(name=r.name, is_local=r.is_local, cgroup=dict(r.cgroup or {}),
                        inventory=[dict(c) for c in (r.inventory or [])], base_mem_mb=r.base_mem_mb)
            snap.pop("robot", None)
            out.append(snap)
        return out

    ##
    # @~japanese
    # @brief ロボット名のマスターマネージャの参照を返す
    #
    # @param name ロボット名
    # @return RTM.Manager の参照 (なければ None)
    # @~english
    # @brief Returns the reference of the master manager of a robot
    #
    # @param name robot name
    # @return reference of RTM.Manager (None if not found)
    # @~
    def manager(self, name):
        robot = self._m._findConditionRobot(name)
        if robot is None:
            raise RuntimeError(f"unknown robot {name}")
        return self._m._resolveManager(robot.ipaddress, robot.name)

    ##
    # @~japanese
    # @brief インスタンス名で RTC を探す
    #
    # @param instance_name インスタンス名
    # @param manager_name ロボット名
    # @return RTC の参照 (なければ None)
    # @~english
    # @brief Finds an RTC by instance name
    #
    # @param instance_name instance name
    # @param manager_name robot name
    # @return reference of the RTC (None if not found)
    # @~
    def find_component(self, instance_name, manager_name):
        return self._m._find_existing(instance_name, self.manager(manager_name))

    ##
    # @~japanese
    # @brief 計画を適用する
    #
    # @param plan 計画
    # @param label ログに出す名前
    # @return True
    # @~english
    # @brief Applies a plan
    #
    # @param plan plan
    # @param label name shown in logs
    # @return True
    # @~
    def apply_plan(self, plan, label):
        config_data = self._m.loadMigrationConfig()
        self._m._validate_plan(plan, config_data["managers"], label)
        self._m._apply_plan(config_data, plan, label)
        return True

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
        return self._m._conf.getProperty(key, default)

    ##
    # @~japanese
    # @brief 構成ファイルの内容を返す
    #
    # @return 構成ファイルの内容
    # @~english
    # @brief Returns the contents of the configuration file
    #
    # @return contents of the configuration file
    # @~
    def migration_config(self):
        return self._m.loadMigrationConfig()

    ##
    # @~japanese
    # @brief イベントを記録する
    #
    # @param robot ロボット名
    # @param kind イベントの種別
    # @param detail 詳細
    # @~english
    # @brief Records an event
    #
    # @param robot robot name
    # @param kind event kind
    # @param detail details
    # @~
    def event(self, robot, kind, detail=""):
        self._m._event(robot, kind, detail)


##
# @~japanese
# @brief SNMP による監視・マイグレーション・自動配置・自動復旧を行うマスターマネージャの拡張
# @~english
# @brief Master manager extension for monitoring, migration, automatic placement and recovery via SNMP
# @~
class SNMPManager:
    # UCD-SNMP-MIB ssCpuRaw* cumulative CPU tick counters.
    CpuRawOids = {
        'user': '1.3.6.1.4.1.2021.11.50.0',
        'nice': '1.3.6.1.4.1.2021.11.51.0',
        'system': '1.3.6.1.4.1.2021.11.52.0',
        'idle': '1.3.6.1.4.1.2021.11.53.0',
        'iowait': '1.3.6.1.4.1.2021.11.54.0',
        'kernel': '1.3.6.1.4.1.2021.11.55.0',
        'interrupt': '1.3.6.1.4.1.2021.11.56.0',
    }
    CpuOid = '1.3.6.1.4.1.2021.10.1.3.1'  # Legacy setting; no longer used for CPU usage.
    MemTotalOid = '1.3.6.1.4.1.2021.4.5.0'
    MemAvailOid = '1.3.6.1.4.1.2021.4.6.0'

    TrapNameOid = '1.3.6.1.2.1.1.1.0'
    TrapInfoOid = '1.3.6.1.2.1.1.5.0'
    InterdaceNameOid = '1.3.6.1.2.1.2.2.1.2'
    InterfaceRecieveOid = '1.3.6.1.2.1.2.2.1.10'
    InterfaceSendOid = '1.3.6.1.2.1.2.2.1.16'
    WirelessStrOid = '1.3.6.1.4.1.8072.1.3.2.3.1.2.12.119.105.102.105.83.116.114.101.110.103.116.104'
    ##
    # @~japanese
    # @brief コンストラクタ。rtc.conf の設定を読む
    #
    # @param manager OpenRTM のマネージャ
    # @param conf rtc.conf の設定 (Properties)
    # @param port SNMP のポート番号
    # @~english
    # @brief Constructor. Reads the settings of rtc.conf
    #
    # @param manager OpenRTM manager
    # @param conf settings of rtc.conf (Properties)
    # @param port SNMP port number
    # @~
    def __init__(self, manager, conf, port=161):
        self._conf = conf
        self._port = port
        self._robot = None
        self._robotList = []
        self._robot_lock = threading.RLock()
        self._own_ip = ""
        # 自分のロボットの IP を明示する (1 台の PC で複数のマスターマネージャを動かすとき。127.0.0.11 など)。
        # 書くと、自分の判定・スキャンからの除外・自分のマネージャへの接続・トラップの送り元と待ち受けに、このアドレスを使う
        self._configured_own_ip = conf.getProperty("snmp.own_ip", "").strip()
        self._running = False
        self._get_interval = float(conf.getProperty("snmp.get_interval", "3.0"))
        self._trap_interval = float(conf.getProperty("snmp.trap_interval", "3.0"))
        self._name = self._conf.getProperty("manager.instance_name", "").strip()
        if not self._name:
            raise ValueError("manager.instance_name is not configured")
        self._manager_corba_port = int(conf.getProperty("snmp.manager_corba_port", "2810"))
        self._migration_config_file = self._conf.getProperty("snmp.migration_config", "migration.json")
        self._loadSNMPConfig()
        self._migration_components = {}
        self._migration_managers = {}
        self._migration = False
        self._startup_completed = False
        self._startup_failure = None
        self._startup_thread = None
        self._migration_lock = threading.Lock()
        self._condition_lock = threading.Lock()
        self._condition_first_true = {}
        self._last_migration_attempt = None
        self._shutdown = False
        self._wifi_low = False
        self._wifi_low_time = time.time()
        self._wifi_high_time = time.time()
        self._migration_done = False
        self._scan_targets = []
        self._last_discovery = time.monotonic()
        # RTC の一覧 (待機モジュール・メモリの予約・実行ロボットの選出に使う)
        self._inventory_interval = float(conf.getProperty("snmp.inventory.interval", "3"))
        self._started_at = time.monotonic()
        self._last_elected = {}
        self._profile_db = None
        self._current_config = {}
        self._plan_assign = {}
        self._pending_reserve = {}
        self._down_managers = []
        self._migration_in_progress = False
        # 復帰したロボットが起動時の構成を繰り返さないための問い合わせ
        self._startup_querying = False
        self._startup_reply = threading.Event()
        self._startup_reported_by = None
        self._startup_pending_from = set()
        self._startup_query_targets = set()
        self._startup_known = False
        # 自動復旧 (切り替えの条件と段階的な復旧)
        self._recovery_where = {}      # 計画の RTC 名 -> {"robot", "instance"} (今どこで動いているか)
        self._recovery_first_seen = {}  # (RTC 名, 原因) -> 最初に見つけた時刻
        self._recovery_cooldown = {}   # キー -> この時刻までは同じ復旧をしない
        self._recovering = False
        self._plan_instances = {}      # 直前の計画で各 RTC が実際に使ったインスタンス名
        self._battery_enabled = conf.getProperty("snmp.battery.enabled", "NO").upper() == "YES"
        self._battery_extend = conf.getProperty("snmp.battery.extend", "batteryLevel")
        # 追加の監視の値 (snmp.metrics): {名前: OID}。条件・制約で "<名前>" / "<名前>_max" / "<名前>_min" として使う
        self._custom_metrics = CustomMetrics.parse_config(conf.getProperty)
        # 効率化: ポートの参照のキャッシュと、移動元の RTC の終了の並行実行
        self._port_cache_enabled = conf.getProperty("snmp.port_cache.enabled", "YES").upper() == "YES"
        self._port_cache_verify = conf.getProperty("snmp.port_cache.verify", "NO").upper() == "YES"
        self._port_cache = {}         # RTC の IOR -> {"instance": 名前, "ports": {ポート名: 参照}, "names": {参照の IOR: 名前}}
        self._port_index = {}         # モジュール名 -> [ポートの短い名前] (get_ports() の順)
        self._port_cache_lock = threading.Lock()
        self._parallel_remove_default = conf.getProperty("snmp.migration.parallel_remove", "NO").upper() == "YES"
        self._created_now = set()     # この計画で新しく生成した (= 接続がまだない) RTC
        self._removing_refs = []      # 並行して終了させている RTC (待機モジュールとして使わない)
        self._corba_calls = 0         # ポートの参照の取得で行った CORBA 呼び出しの数 (計測用)
        self._port_module = {}        # 計画の RTC 名 -> モジュール名 (この計画で生成した RTC)
        self._planned_instance = {}   # 計画の RTC 名 -> インスタンス名
        # マネージャによる実測値の計測と保存。slave の SlaveMeasureModule が書いた計測を集めて保存する
        yes = lambda key, default: conf.getProperty(key, default).strip().upper() == "YES"
        self._measure_enabled = yes("snmp.measure.enabled", "NO")
        self._measure_runtime_dir = conf.getProperty("snmp.measure.runtime_dir", "/run/rtm/measure")
        self._measure_dir = conf.getProperty("snmp.measure.dir", "measured")
        self._measure_save_interval = float(conf.getProperty("snmp.measure.save_interval", "10"))
        self._measure_min_samples = int(conf.getProperty("snmp.measure.min_samples", "10"))
        self._measure_max_runs = int(conf.getProperty("snmp.measure.max_runs", "20"))
        self._measure_cpu_stat = conf.getProperty("snmp.measure.cpu_stat", "max").strip().lower()
        self._measure_use = yes("snmp.measure.use_for_placement", "YES")
        self._measure_runs = None     # 計測 1 回分 (slave/インスタンス/生成時刻) -> 結果。runs.json に保存する
        self._measure_saved = {}      # (言語, 型名) -> 保存した (CPU, メモリ)
        self._profile_sig = None      # 計測を保存したディレクトリの状態 (変わったら見込み値を読み直す)
        # slave マネージャの終了の検知 (feature/processcallback の ProcessCallback)
        self._observer_enabled = yes("snmp.process_observer.enabled", "NO")
        self._observer_installed = False
        self._crashed = {}            # インスタンス名 -> (ロボット名, 検知した時刻)。復旧を待たずに始める
        self._recovery_wake = threading.Event()
        # コンポーネントオブザーバー (オブザーバ拡張マイグレーション)。自分のロボットの RTC に
        # サーバーオブジェクト (OpenRTM::ComponentObserver) を関連付け、ERROR の通知で自動復旧を待たずに始める
        self._observer_rtc_enabled = conf.getProperty("snmp.observer.enabled", "NO").strip().upper() == "YES"
        self._observer_status = conf.getProperty("snmp.observer.observed_status", "RTC_STATUS").strip()
        self._observers = {}          # RTC の IOR -> {"instance", "servant", "oid", "profile_id"}
        self._observer_lock = threading.Lock()
        self._error_notified = {}     # インスタンス名 -> (ロボット名, 通知を受けた時刻)
        self._notified_logged = set()  # 通知で待たずに始めることをログに出した RTC
        self._observer_noticed = set()  # 最初の通知をログに出した RTC

        self.mgr = manager
        self._rtcout = self.mgr.getLogbuf("SNMPManager")

        self._logfile = "snmpmgr.txt"
        with open(self._logfile, "w") as f:
          f.write("seconds_since_midnight\tinfo\trtc_name\trtc_status\n")

    ##
    # @~japanese
    # @brief 運用のメッセージを RTC のロガーと標準出力の両方に出す
    #
    # @param message メッセージ
    # @~english
    # @brief Writes an operational message to both the RTC logger and stdout
    #
    # @param message message
    # @~
    def _log(self, message):
        self._rtcout.RTC_INFO(message)
        print(f"[SNMPManager:{self._name}] {message}", flush=True)

    ##
    # @~japanese
    # @brief rtc.conf から OID の上書きと探索の範囲を読む
    # @~english
    # @brief Reads optional OID overrides and discovery ranges from rtc.conf
    # @~
    def _loadSNMPConfig(self):
        keys = (
            'CpuOid', 'MemTotalOid', 'MemAvailOid', 'TrapNameOid',
            'TrapInfoOid', 'InterdaceNameOid', 'InterfaceRecieveOid',
            'InterfaceSendOid', 'WirelessStrOid',
        )
        for key in keys:
            default = getattr(type(self), key)
            oid = self._conf.getProperty('snmp.oid.' + key, default).strip()
            if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)+', oid):
                raise ValueError(f'Invalid OID for snmp.oid.{key}: {oid!r}')
            setattr(self, key, oid)

        self._cpu_raw_oids = {name: self._conf.getProperty(
            'snmp.oid.CpuRaw' + name.capitalize() + 'Oid', oid).strip()
            for name, oid in self.CpuRawOids.items()}
        if any(not re.fullmatch(r'[0-9]+(?:\.[0-9]+)+', oid) for oid in self._cpu_raw_oids.values()):
            raise ValueError('Invalid snmp.oid.CpuRaw*Oid setting')
        self._discovery_mode = self._conf.getProperty('snmp.discovery_mode', 'trap').strip().lower()
        if self._discovery_mode not in ('trap', 'sysname'):
            raise ValueError('snmp.discovery_mode must be trap or sysname')
        self._sysname_oid = self._conf.getProperty('snmp.oid.SysNameOid', '1.3.6.1.2.1.1.5.0').strip()
        self._sysdescr_oid = self._conf.getProperty('snmp.oid.SysDescrOid', '1.3.6.1.2.1.1.1.0').strip()
        self._wifi_interface = self._conf.getProperty('snmp.wifi_interface', 'wlan0').strip()
        self._wifi_role = self._conf.getProperty('snmp.wifi_signal_source', 'client').strip().lower()
        if self._wifi_role not in ('client', 'ap'):
            raise ValueError('snmp.wifi_signal_source must be client or ap')
        # Net-SNMP extend OIDs are vendor-specific, not standard IF-MIB fields.
        # An explicit OID takes priority. Otherwise derive an extend token using the interface name.
        self._wifi_client_oid = self._conf.getProperty('snmp.wifi_client_oid', '').strip()
        self._wifi_ap_oid = self._conf.getProperty('snmp.wifi_ap_oid', '').strip()
        self._wifi_client_token_prefix = self._conf.getProperty('snmp.wifi_client_extend_prefix', 'wifiSignalClient_').strip()
        self._wifi_ap_token_prefix = self._conf.getProperty('snmp.wifi_ap_extend_prefix', 'wifiSignalAP_').strip()
        self._community = self._conf.getProperty('snmp.community', 'public')
        # Periodic re-discovery of robots that were not reachable at startup (0 = disabled).
        self._discovery_interval = float(self._conf.getProperty('snmp.discovery_interval', '0'))
        self._verbose = self._conf.getProperty('snmp.verbose', 'YES').strip().upper() == 'YES'

        # 死活監視と通信品質 (アクティブ: sysUpTime の GET、パッシブ: ハートビートのトラップ)
        yes = lambda key, default: self._conf.getProperty(key, default).strip().upper() == 'YES'
        self._liveness_enabled = yes('snmp.liveness.enabled', 'YES')
        self._probe_interval = float(self._conf.getProperty('snmp.liveness.probe_interval', '1.0'))
        self._probe_timeout = float(self._conf.getProperty('snmp.liveness.probe_timeout', '1.0'))
        self._probe_window = int(self._conf.getProperty('snmp.liveness.window', '20'))
        self._liveness_timeout = float(self._conf.getProperty('snmp.liveness.timeout', '6.0'))
        self._heartbeat_enabled = yes('snmp.heartbeat.enabled', 'YES')
        self._heartbeat_interval = float(self._conf.getProperty('snmp.heartbeat.interval', '2.0'))
        self._trap_port = int(self._conf.getProperty('snmp.trap_port', '162'))
        # 監視情報の保存 (SQLite)
        self._db_enabled = yes('snmp.db.enabled', 'NO')
        self._db_path = self._conf.getProperty('snmp.db.path', 'snmpmgr.db')
        self._db_interval = float(self._conf.getProperty('snmp.db.interval', '5'))
        self._db_retention = float(self._conf.getProperty('snmp.db.retention_hours', '24'))

        # Comma-separated CIDRs, single addresses, or start-end ranges.
        raw = self._conf.getProperty('snmp.ip_ranges', '').strip()
        self._scan_ranges = [item.strip() for item in raw.split(',') if item.strip()] if raw else None

    ##
    # @~japanese
    # @brief rtc.conf から、探索する IPv4 アドレスの一覧 (重複なし) を作る
    #
    # @return IP アドレスのリスト
    # @~english
    # @brief Builds unique IPv4 discovery targets from rtc.conf
    #
    # @return list of IP addresses
    # @~
    def _buildScanTargets(self):
        if self._scan_ranges is None:
            prefix = self._conf.getProperty('snmp.ip_mask', '192.168.215.')
            low = int(self._conf.getProperty('snmp.ip_range_min', '104'))
            high = int(self._conf.getProperty('snmp.ip_range_max', '123'))
            if low > high:
                raise ValueError('snmp.ip_range_min must be <= snmp.ip_range_max')
            return [str(ipaddress.IPv4Address(f'{prefix}{i}')) for i in range(low, high + 1)]

        result = set()
        for entry in self._scan_ranges:
            if '-' in entry:
                start, end = (part.strip() for part in entry.split('-', 1))
                first = ipaddress.IPv4Address(start)
                last = ipaddress.IPv4Address(end)
                if int(first) > int(last):
                    raise ValueError(f'Invalid IP range: {entry}')
                result.update(str(ipaddress.IPv4Address(i)) for i in range(int(first), int(last) + 1))
            elif '/' in entry:
                network = ipaddress.ip_network(entry, strict=False)
                if network.version != 4:
                    raise ValueError('Only IPv4 ranges are supported')
                result.update(str(ip) for ip in network.hosts())
            else:
                result.add(str(ipaddress.IPv4Address(entry)))
        return sorted(result, key=lambda ip: int(ipaddress.IPv4Address(ip)))

    ##
    # @~japanese
    # @brief 初期化する (トラップの受信、ロボットの探索、監視・起動時の構成・自動復旧などのスレッドを始める)
    # @~english
    # @brief Initializes (starts trap reception, robot discovery, and the threads for monitoring, startup configuration, recovery, etc.)
    # @~
    def init(self):
        if self._running:
            return
        self._running = True
        self._trap_loop = asyncio.new_event_loop()
        self._trap_ready = threading.Event()
        self._trap_error = None
        self._trap_thread = threading.Thread(target=self.trap_receiver, daemon=True)
        self._trap_thread.start()
        if not self._trap_ready.wait(timeout=10):
            raise RuntimeError('SNMP trap receiver initialization timed out')
        if self._trap_error is not None:
            raise RuntimeError('SNMP trap receiver initialization failed') from self._trap_error
        # 構成ファイルを先に読み、プラグインを読み込んでおく (起動直後のイベントも届くように)
        try:
            self.loadMigrationConfig()
        except Exception as exc:
            self._log(f"migration config not loaded at init: {exc}")
        self._open_store()

        local_ips = self.get_all_local_ips()
        ip_list = self._buildScanTargets()
        own_ips = [ip for ip in ip_list if ip in local_ips]
        if self._configured_own_ip:
            # 同じ PC のほかのマネージャ (127.0.0.12 など) は自分ではないので、自分の IP だけを自分とする
            local_ips = {self._configured_own_ip}
            self._own_ip = self._configured_own_ip
        elif own_ips:
            self._own_ip = own_ips[0]
        elif local_ips:
            self._own_ip = sorted(local_ips)[0]
        if self._own_ip:
            self._robot = SNMPManager.Robot(self._name, self._own_ip, is_local=True)
        ip_list = [ip for ip in ip_list if ip not in local_ips]
        self._scan_targets = ip_list

        with ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self.check_snmp_device, ip_list)
        self._last_discovery = time.monotonic()
        self._log("discovered robots: " + self._robotSummary())

        self._polling_thread = threading.Thread(target=self.trap_checking, daemon=True)
        self._trap_cheking_thread = threading.Thread(target=self.polling, daemon=True)

        self._polling_thread.start()
        self._trap_cheking_thread.start()
        self._start_monitoring()
        if self._conf.getProperty("snmp.startup_enabled", "YES").upper() == "YES":
            self._startup_thread = threading.Thread(
                target=self._startup_configuration, daemon=True)
            self._startup_thread.start()

    ##
    # @~japanese
    # @brief スレッドを止める
    # @~english
    # @brief Stops the threads
    # @~
    def stop(self):
        self._running = False
        loop = getattr(self, '_trap_loop', None)
        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(loop.stop)
        thread = getattr(self, '_trap_thread', None)
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=5)

    ##
    # @~japanese
    # @brief スレッドの終了を待つ
    # @~english
    # @brief Waits for the threads to finish
    # @~
    def join(self):
        self._trap_thread.join()
        self._polling_thread.join()
        self._trap_cheking_thread.join()
        
    ##
    # @~japanese
    # @brief その IP アドレスのロボットが登録済みか
    #
    # @param ip IP アドレス
    # @return 登録済みなら True
    # @~english
    # @brief Whether a robot with the IP address is registered
    #
    # @param ip IP address
    # @return True if registered
    # @~
    def existRobot(self, ip):
        with self._robot_lock:
            return any(robot.ipaddress == ip for robot in self._robotList)

    ##
    # @~japanese
    # @brief 登録済みのロボットの一覧の文字列を返す (ログ用)
    #
    # @return 文字列
    # @~english
    # @brief Returns a string listing the registered robots (for logs)
    #
    # @return string
    # @~
    def _robotSummary(self):
        with self._robot_lock:
            robots = list(self._robotList)
        own = f"{self._name}@{self._own_ip or '?'}(self)"
        return ", ".join([own] + [f"{r.name}@{r.ipaddress}" for r in robots])

    ##
    # @~japanese
    # @brief まだ登録していない探索対象に問い合わせる
    #
    # init() での探索は、既に動いているロボットしか見つけられない。後から起動したロボットを参加させる (snmp.discovery_interval で有効にする)。
    # @~english
    # @brief Probes scan targets that have not been registered yet
    #
    # Discovery at init() only sees robots that are already running; this lets robots that boot later join (enabled by snmp.discovery_interval).
    # @~
    def rediscover(self):
        if self._discovery_interval <= 0:
            return
        now = time.monotonic()
        if now - self._last_discovery < self._discovery_interval:
            return
        self._last_discovery = now
        pending = [ip for ip in self._scan_targets if not self.existRobot(ip)]
        if not pending:
            return
        with ThreadPoolExecutor(max_workers=20) as executor:
            found = list(executor.map(self.check_snmp_device, pending))
        if any(found) and self._discovery_mode == 'sysname':
            self._log("discovered robots: " + self._robotSummary())

    ##
    # @~japanese
    # @brief ロボットを登録する
    #
    # @param ip IP アドレス
    # @param name ロボット名
    # @return 新しく登録したら True
    # @~english
    # @brief Registers a robot
    #
    # @param ip IP address
    # @param name robot name
    # @return True if newly registered
    # @~
    def _registerRobot(self, ip, name):
        with self._robot_lock:
            for robot in self._robotList:
                if robot.ipaddress == ip:
                    robot.name = name
                    return False
            self._robotList.append(SNMPManager.Robot(name, ip))
        self._event(name, "discovered", ip)
        return True

    ##
    # @~japanese
    # @brief ロボットのマスターマネージャの corbaloc を返す
    #
    # @param ip IP アドレス
    # @param name ロボット名
    # @return corbaloc の文字列
    # @~english
    # @brief Returns the corbaloc of the master manager of a robot
    #
    # @param ip IP address
    # @param name robot name
    # @return corbaloc string
    # @~
    def _managerCorbaloc(self, ip, name):
        return f"corbaloc:iiop:{ip}:{self._manager_corba_port}/{name}"

    ##
    # @~japanese
    # @brief ロボットのマスターマネージャの参照を得る (キャッシュする)
    #
    # @param ip IP アドレス
    # @param name ロボット名
    # @return RTM.Manager の参照
    # @~english
    # @brief Obtains the reference of the master manager of a robot (cached)
    #
    # @param ip IP address
    # @param name robot name
    # @return reference of RTM.Manager
    # @~
    def _resolveManager(self, ip, name):
        corbaloc = self._managerCorbaloc(ip, name)
        obj = self.mgr.getORB().string_to_object(corbaloc)
        ref = obj._narrow(RTM.Manager)
        if ref is None or CORBA.is_nil(ref):
            raise RuntimeError("Manager reference unavailable: " + corbaloc)
        return ref

    ##
    # @~japanese
    # @brief 実行時に構成ファイルを読み、正しいかを確かめる
    #
    # @return 構成ファイルの内容
    # @~english
    # @brief Reads and validates the configuration file at execution time
    #
    # @return contents of the configuration file
    # @~
    def loadMigrationConfig(self):
        path = Path(self._migration_config_file).expanduser()
        with path.open("r", encoding="utf-8") as f:
            config_data = json.load(f)
        if not isinstance(config_data, dict):
            raise ValueError("Migration configuration must be a JSON object")
        managers = config_data.get("managers", {})
        # Backward compatible: legacy top-level components/connections become
        # the migration plan; startup and migration plans can also be separate.
        components = config_data.get("components", [])
        connections = config_data.get("connections", [])
        if not isinstance(managers, dict) or not isinstance(components, list) or not isinstance(connections, list):
            raise ValueError("managers, components, or connections has an invalid type")
        # プラグイン (内容が変わったときだけ読み込み直す)
        plugins = self.plugins()
        if plugins is not None:
            if plugins.load_all(config_data.get("plugins", [])):
                self._log(plugins.describe())
        elif config_data.get("plugins"):
            raise ValueError("plugins are configured but PluginManager is unavailable")
        for section in ("startup", "migration"):
            if section in config_data:
                plan = config_data[section]
                if not isinstance(plan, dict):
                    raise ValueError(f"{section} must be an object")
                if plan.get("plugin") is not None:
                    # 計画の代わりにプラグインの処理 (action) を呼ぶ
                    if plugins is None or not plugins.has_action(plan["plugin"]):
                        raise ValueError(f"{section}: unknown action plugin {plan['plugin']}")
                    continue
                if plan.get("placement_plugin") is not None and \
                        (plugins is None or not plugins.has_placement(plan["placement_plugin"])):
                    raise ValueError(f"{section}: unknown placement plugin {plan['placement_plugin']}")
                self._validate_plan(plan, managers, section)
        self._validate_plan({"components": components, "connections": connections}, managers, "legacy")
        if "migration_conditions" in config_data:
            self._validate_condition_group(config_data["migration_conditions"])
        self._validate_extensions(config_data, managers, plugins, tuple(self._custom_metrics))
        return config_data

    ##
    # @~japanese
    # @brief 拡張の設定 (待機モジュール、メモリの予約、配置のロジック、実行ロボットの選出) を確かめる
    #
    # @param config_data 構成ファイルの内容
    # @param managers ロボット名のリスト
    # @param plugins プラグインマネージャ
    # @param metrics カスタムメトリクスの名前
    # @~english
    # @brief Validates the extension settings (standby modules, memory reservation, placement logic, executor election)
    #
    # @param config_data contents of the configuration file
    # @param managers list of robot names
    # @param plugins plugin manager
    # @param metrics names of the custom metrics
    # @~
    @staticmethod
    def _validate_extensions(config_data, managers, plugins, metrics=()):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import RTCPlacement as pl
        # 追加の監視の値の制約: 置くロボット (metric_constraints) と実行ロボット (executor_constraints)
        for section in ("startup", "migration", "migration_conditions", "recovery"):
            sec = config_data.get(section)
            if not isinstance(sec, dict):
                continue
            if section in ("startup", "migration", "recovery"):
                CustomMetrics.validate_constraints(sec.get("metric_constraints"), metrics, f"{section}.metric_constraints")
            CustomMetrics.validate_constraints(sec.get("executor_constraints"), metrics, f"{section}.executor_constraints")
        sb = config_data.get("standby")
        if sb is not None:
            if not isinstance(sb, dict):
                raise ValueError("standby must be an object")
            if sb.get("scope", "any") not in ("any", "same"):
                raise ValueError("standby.scope must be any or same")
            names = set()
            for m in sb.get("modules", []):
                if not isinstance(m, dict) or not isinstance(m.get("name"), str) or \
                        m.get("manager") not in managers or not m.get("create"):
                    raise ValueError("standby.modules entries need name, manager (configured) and create")
                if m["name"] in names:
                    raise ValueError("duplicate standby module " + m["name"])
                names.add(m["name"])
        rs = config_data.get("reservation")
        if rs is not None:
            if not isinstance(rs, dict) or not isinstance(rs.get("memory_mb", {}), dict):
                raise ValueError("reservation must be an object with memory_mb {type: MB}")
            for v in list(rs.get("memory_mb", {}).values()) + [rs.get("default_mb", 0)]:
                if float(v) < 0:
                    raise ValueError("reservation sizes must be nonnegative")
        for section in ("startup", "migration"):
            plan = config_data.get(section)
            if not isinstance(plan, dict):
                continue
            logic = plan.get("logic")
            if logic is not None and logic not in pl.LOGICS:
                raise ValueError(f"{section}: logic must be one of {', '.join(pl.LOGICS)}")
            if plan.get("objective_plugin") is not None and \
                    (plugins is None or not plugins.has_objective(plan["objective_plugin"])):
                raise ValueError(f"{section}: unknown objective plugin {plan['objective_plugin']}")
            weights = plan.get("objective", {}).get("weights", {}) if isinstance(plan.get("objective"), dict) else {}
            for k in weights:
                if k not in pl.DEFAULT_WEIGHTS:
                    raise ValueError(f"{section}: unknown objective weight {k}")
            for key in ("from", "exclude"):
                vals = plan.get(key)
                vals = [vals] if isinstance(vals, str) else (vals or [])
                for v in vals:
                    if v not in managers:
                        raise ValueError(f"{section}: {key} names unknown manager {v}")
        rc = config_data.get("recovery")
        if rc is not None:
            if not isinstance(rc, dict):
                raise ValueError("recovery must be an object")
            if not isinstance(config_data.get("startup"), dict):
                raise ValueError("recovery needs the startup plan (the system configuration to keep running)")
            names = {c["name"] for c in config_data["startup"].get("components", [])}
            for n in rc.get("components", []):
                if n not in names:
                    raise ValueError(f"recovery.components names {n}, which is not in the startup plan")
            conds = rc.get("conditions", {})
            known = set(SNMPManager.RecoveryThresholds) | {"down", "error", "missing", "duration_seconds"} \
                | set(CustomMetrics.constraint_keys(metrics))
            for k in conds:
                if k not in known:
                    raise ValueError(f"recovery.conditions: unknown key {k}")
            stages = rc.get("stages", {})
            for kind in ("local", "remote"):
                for st in stages.get(kind, []):
                    if st not in SNMPManager.RecoveryStages:
                        raise ValueError(f"recovery.stages.{kind}: unknown stage {st}")
            if rc.get("logic") is not None and rc["logic"] not in pl.LOGICS:
                raise ValueError(f"recovery.logic must be one of {', '.join(pl.LOGICS)}")
            if rc.get("target", "largest") not in ("largest", "all"):
                raise ValueError("recovery.target must be largest or all")
        for sec in (config_data.get("startup"), config_data.get("migration"), config_data.get("migration_conditions"),
                    config_data.get("recovery")):
            if isinstance(sec, dict):
                for c in sec.get("executor_candidates", []):
                    if c not in managers:
                        raise ValueError(f"executor_candidates names unknown manager {c}")

    ##
    # @~japanese
    # @brief 計画 (components、connections、remove) を確かめる
    #
    # @param plan 計画
    # @param managers ロボット名のリスト
    # @param label エラーのメッセージに出す名前
    # @~english
    # @brief Validates a plan (components, connections, remove)
    #
    # @param plan plan
    # @param managers list of robot names
    # @param label name shown in error messages
    # @~
    @staticmethod
    def _validate_plan(plan, managers, label):
        components = plan.get("components", [])
        connections = plan.get("connections", [])
        if not isinstance(components, list) or not isinstance(connections, list):
            raise ValueError(f"{label}: components and connections must be lists")
        mode = plan.get("mode", "manual")
        if mode not in ("manual", "auto"):
            raise ValueError(f"{label}: mode must be manual or auto")
        names = set()
        for entry in components:
            # auto では manager は省略可 (書いた場合はそのロボットに固定する)
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str) or \
                    (mode == "manual" and not isinstance(entry.get("manager"), str)):
                raise ValueError(f"{label}: component needs name and manager")
            if entry["name"] in names:
                raise ValueError(f"{label}: duplicate component {entry['name']}")
            names.add(entry["name"])
            if entry.get("manager") is not None and entry["manager"] not in managers:
                raise ValueError(f"{label}: unknown manager {entry['manager']}")
            if bool(entry.get("create")) == bool(entry.get("existing")):
                raise ValueError(f"{label}: specify exactly one of create or existing")
            if mode == "auto" and not entry.get("create") and not entry.get("manager"):
                # auto でも、動かさない既存の RTC は manager を書いて計画に含められる (通信量の計算に使う)
                raise ValueError(f"{label}: auto mode needs create, or existing with manager, for {entry['name']}")
        if mode == "auto" and plan.get("primary") is not None and plan["primary"] not in managers:
            raise ValueError(f"{label}: unknown primary manager {plan['primary']}")
        for entry in connections:
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str):
                raise ValueError(f"{label}: invalid connection")
            for endpoint in (entry.get("source"), entry.get("target")):
                if not isinstance(endpoint, dict) or endpoint.get("component") not in names or not endpoint.get("port"):
                    raise ValueError(f"{label}: invalid connection endpoint {endpoint}")
            if not isinstance(entry.get("properties", {}), dict):
                raise ValueError(f"{label}: connection properties must be an object")
        # Optional: RTCs to stop and delete after the new configuration is up
        # (make-before-break migration).
        removes = plan.get("remove", [])
        if not isinstance(removes, list):
            raise ValueError(f"{label}: remove must be a list")
        for entry in removes:
            if not isinstance(entry, dict) or not isinstance(entry.get("name"), str) or not isinstance(entry.get("manager"), str):
                raise ValueError(f"{label}: remove entry needs name and manager")
            if entry["manager"] not in managers:
                raise ValueError(f"{label}: unknown manager {entry['manager']}")
        executor = plan.get("executor")
        if executor is not None and (not isinstance(executor, str) or not executor):
            raise ValueError(f"{label}: executor must be a manager name or auto")

    ##
    # @~japanese
    # @brief このマネージャが計画を適用するかを返す
    #
    # 全マネージャが同じ JSON を読むので、"executor" がなければ全マネージャが同じ計画を同時に適用してしまう。executor を書いた最初のセクションで決める。executor がなければ従来どおり。"executor": "auto" なら生きているロボットから 1 つを選ぶ (単一障害点の対策)。
    #
    # @param config_data 構成ファイルの内容
    # @param counts ロボットごとの RTC の数 (選出に使う)
    # @param purpose ログに出す目的
    # @param *sections executor を探すセクション
    # @return 適用するなら True
    # @~english
    # @brief Returns whether this manager should apply the plan
    #
    # All managers read the same JSON, so without an "executor" every manager would apply the same plan concurrently. The first section that names an executor decides; no executor keeps the old behavior. "executor": "auto" elects one of the live robots (to avoid a single point of failure).
    #
    # @param config_data contents of the configuration file
    # @param counts number of RTCs on each robot (used for the election)
    # @param purpose purpose shown in logs
    # @param *sections sections to look for executor
    # @return True if this manager applies the plan
    # @~
    def _isExecutor(self, config_data, *sections, counts=None, purpose="plan"):
        for section in sections:
            if isinstance(section, dict) and section.get("executor"):
                if section["executor"] != "auto":
                    return section["executor"] == self._name
                return self._elect_executor(config_data, section, counts, purpose) == self._name
        return True

    ##
    # @~japanese
    # @brief 計画を実行するロボットを選ぶ
    #
    # 候補 (executor_candidates、既定は managers の順) のうち、生きていて通信状態がよいロボットから、割り当てられた RTC の数 (counts、既定は今動いている RTC の数) が最も多いものを選ぶ。同数ならリストの順。どのロボットも同じ規則で選ぶので、選ばれたロボットが止まると、残ったロボットの中から次が選ばれる。まだ状態の分からない候補 (起動直後) があるときは None (保留)。
    #
    # @param config_data 構成ファイルの内容
    # @param section executor を書いたセクション
    # @param counts ロボットごとの RTC の数
    # @param purpose ログに出す目的
    # @return 選ばれたロボット名 (保留なら None)
    # @~english
    # @brief Elects the robot that executes the plan
    #
    # Among the candidates (executor_candidates; default: the order of managers), picks the alive robot with a good link that has the most assigned RTCs (counts; default: the number of RTCs running now). Ties are broken by the list order. Every robot uses the same rule, so if the elected robot stops, the next one is elected from the remaining robots. Returns None (pending) while some candidates have unknown states (just after startup).
    #
    # @param config_data contents of the configuration file
    # @param section section with executor
    # @param counts number of RTCs on each robot
    # @param purpose purpose shown in logs
    # @return name of the elected robot (None if pending)
    # @~
    def _elect_executor(self, config_data, section, counts=None, purpose="plan"):
        cands = list(section.get("executor_candidates") or config_data["managers"])
        max_loss = float(self._conf.getProperty("snmp.executor.max_packet_loss", "50"))
        max_latency = float(self._conf.getProperty("snmp.executor.max_latency_ms", "0"))
        # Wi-Fi の電波強度 (RSSI, dBm) がこの値より弱いロボットは選ばない (空なら見ない)。自分のロボットにも使う
        min_rssi = self._conf.getProperty("snmp.executor.min_rssi_dbm", "").strip()
        min_rssi = float(min_rssi) if min_rssi else None
        grace = self._liveness_timeout + max(self._discovery_interval, 0.0) + 1.0
        # 追加の監視の値の制約 (executor_constraints) を満たさないロボットは選ばない
        ex_cons = section.get("executor_constraints") if isinstance(section, dict) else None
        eligible, weak, hot = [], [], []
        for name in cands:
            robot = self._findConditionRobot(name)
            if robot is None:
                if time.monotonic() - self._started_at <= grace:
                    return None     # まだ見つかっていない (起動が遅れているだけかもしれない)
                continue
            if not robot.is_local and self._liveness_enabled:
                if robot.status == "unknown":
                    return None
                if robot.status != "alive":
                    continue
                if robot.packet_loss is not None and robot.packet_loss > max_loss:
                    continue
                if max_latency > 0 and robot.latency_ms is not None and robot.latency_ms > max_latency:
                    continue
            if min_rssi is not None:
                try:
                    rssi = float(robot.data.get("wifi_signal_dbm"))
                except (TypeError, ValueError):
                    rssi = None     # 分からなければ外さない
                if rssi is not None and rssi < min_rssi:
                    weak.append(name)
                    continue
            if ex_cons:
                bad = CustomMetrics.violations(robot.metrics, ex_cons, tuple(self._custom_metrics))
                if bad:
                    hot.append(f"{name} ({', '.join(CustomMetrics.describe(v) for v in bad)})")
                    continue
            eligible.append(name)
        excluded = f"; weak RSSI: {', '.join(weak)}" if weak else ""
        if hot:
            excluded += f"; metric constraints: {', '.join(hot)}"
        if not eligible and (weak or hot):
            # 全員が条件を満たさない: 電波強度・追加の値の条件は外して選ぶ (実行するロボットがいなくならないように)
            eligible = weak + [h.split(" ")[0] for h in hot]
            eligible = [n for n in cands if n in eligible]
            excluded = "; all robots have weak RSSI" if not hot else "; all robots fail the RSSI / metric constraints"
        if not eligible:
            return None
        if counts is None:
            counts = {n: len(self._findConditionRobot(n).inventory or []) for n in eligible}
        best = max(eligible, key=lambda n: (counts.get(n, 0), -cands.index(n)))
        if self._last_elected.get(purpose) != best:
            self._last_elected[purpose] = best
            detail = ", ".join(f"{n}:{counts.get(n, 0)}" for n in eligible)
            self._event(best, "executor_elected", f"{purpose} (candidates {detail}{excluded})")
        return best


    ##
    # @~japanese
    # @brief マイグレーションの条件のグループを確かめる
    #
    # @param group 条件のグループ
    # @~english
    # @brief Validates a group of migration conditions
    #
    # @param group condition group
    # @~
    def _validate_condition_group(self, group):
        if not isinstance(group, dict) or group.get("operator") not in ("AND", "OR"):
            raise ValueError("Condition group must use AND or OR")
        conditions = group.get("conditions")
        if not isinstance(conditions, list) or not conditions:
            raise ValueError("Condition group requires a nonempty conditions list")
        for condition in conditions:
            if not isinstance(condition, dict):
                raise ValueError("Invalid migration condition")
            if "conditions" in condition:
                self._validate_condition_group(condition)
                continue
            if condition.get("plugin") is not None:
                plugins = self.plugins()
                if plugins is None or not plugins.has_condition(condition["plugin"]):
                    raise ValueError("Unknown condition plugin: " + str(condition["plugin"]))
                continue
            if condition.get("metric") not in ("wifi_strength", "wifi_signal_dbm", "wifi_signal_client_dbm", "wifi_signal_ap_dbm", "cpu_usage", "memory_usage", "network_in", "network_out", "battery_pct") + self.LivenessMetrics + tuple(self._custom_metrics):
                raise ValueError("Unknown metric: " + str(condition.get("metric")))
            if condition.get("operator") not in ("<", "<=", ">", ">=", "==", "!="):
                raise ValueError("Unknown comparison operator")
            if condition.get("robot", "self") not in ("self", self._name):
                # Remote robots may be named explicitly; checked when evaluating.
                if not isinstance(condition.get("robot"), str) or not condition["robot"]:
                    raise ValueError("Invalid robot name")
            float(condition["value"])
        if float(group.get("duration_seconds", 0)) < 0 or float(group.get("cooldown_seconds", 0)) < 0:
            raise ValueError("Duration and cooldown must be nonnegative")

    # 死活監視のプローブで更新する指標 (migration_conditions で使える)
    LivenessMetrics = ("alive", "latency_ms", "jitter_ms", "packet_loss")

    ##
    # @~japanese
    # @brief プラグインマネージャを返す
    #
    # @return PluginManager.PluginManager (モジュールがなければ None)
    # @~english
    # @brief Returns the plugin manager
    #
    # @return PluginManager.PluginManager (None if the module is not available)
    # @~
    def plugins(self):
        pm = getattr(self, "_plugin_manager", None)
        if pm is None:
            here = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, here)
            try:
                import PluginManager
            except ImportError:
                return None
            paths = [p.strip() for p in self._conf.getProperty(
                "snmp.plugin.path", os.path.join(here, "plugins")).split(",")]
            pm = PluginManager.PluginManager(_PluginHost(self), paths)
            self._plugin_manager = pm
        return pm

    ##
    # @~japanese
    # @brief 条件の対象のロボットを名前で探す
    #
    # @param name ロボット名
    # @return Robot (なければ None)
    # @~english
    # @brief Finds the robot of a condition by name
    #
    # @param name robot name
    # @return Robot (None if not found)
    # @~
    def _findConditionRobot(self, name):
        if name in ("self", self._name):
            return self._robot
        with self._robot_lock:
            return next((robot for robot in self._robotList if robot.name == name), None)

    ##
    # @~japanese
    # @brief マイグレーションの条件を 1 つ評価する
    #
    # @param condition 条件
    # @param now 現在の時刻
    # @return 満たせば True
    # @~english
    # @brief Evaluates one migration condition
    #
    # @param condition condition
    # @param now current time
    # @return True if satisfied
    # @~
    def evaluate_condition(self, condition, now):
        comparisons = {
            "<": operator.lt, "<=": operator.le,
            ">": operator.gt, ">=": operator.ge,
            "==": operator.eq, "!=": operator.ne,
        }
        if condition.get("plugin") is not None:
            try:
                return self.plugins().condition(condition["plugin"], condition.get("args", {}), now)
            except Exception:
                self._rtcout.RTC_ERROR("condition plugin failed: " + traceback.format_exc())
                return False
        robot = self._findConditionRobot(condition.get("robot", "self"))
        if robot is None:
            return False
        if condition["metric"] in self.LivenessMetrics:
            # 死活・通信品質はプローブで更新され続ける (停止したロボットにも使う) ので鮮度は見ない
            try:
                value = robot.data.get(condition["metric"])
                return value is not None and comparisons[condition["operator"]](float(value), float(condition["value"]))
            except (ValueError, TypeError):
                return False
        # A robot must have a successful SNMP sample before any metric can trigger migration.
        if robot.last_data_update is None:
            return False
        max_age = float(self._conf.getProperty("snmp.condition_max_data_age", "10"))
        if max_age >= 0 and now - robot.last_data_update > max_age:
            return False
        try:
            metric = condition["metric"]
            # 追加の監視の値 (snmp.metrics) は robot.metrics にある (取れていなければ None で False)
            value = float(robot.metrics.get(metric) if metric in self._custom_metrics else robot.data[metric])
            return comparisons[condition["operator"]](value, float(condition["value"]))
        except (KeyError, ValueError, TypeError):
            return False

    ##
    # @~japanese
    # @brief 条件のグループを評価する (AND / OR)
    #
    # @param group 条件のグループ
    # @param now 現在の時刻
    # @return 満たせば True
    # @~english
    # @brief Evaluates a condition group (AND / OR)
    #
    # @param group condition group
    # @param now current time
    # @return True if satisfied
    # @~
    def evaluate_conditions(self, group, now):
        results = [
            self.evaluate_conditions(item, now) if "conditions" in item
            else self.evaluate_condition(item, now)
            for item in group["conditions"]
        ]
        return all(results) if group["operator"] == "AND" else any(results)

    ##
    # @~japanese
    # @brief 監視の値でマイグレーションの条件を評価する (継続時間とクールダウンは単調な時計で数える)
    # @~english
    # @brief Evaluates the migration rules using the sampled metrics; duration and cooldown use monotonic time
    # @~
    def check_migration_conditions(self):
        try:
            config_data = self.loadMigrationConfig()
            group = config_data.get("migration_conditions")
            if not self._startup_completed:
                return
            if group is None or not group.get("enabled", True):
                return
            if not self._isExecutor(config_data, group, config_data.get("migration"), purpose="migration"):
                return
            if self._migration_done and not group.get("repeat", True):
                return
            now = time.monotonic()
            with self._condition_lock:
                if not self.evaluate_conditions(group, now):
                    if self._condition_first_true:
                        self._log("migration conditions no longer satisfied")
                    self._condition_first_true.clear()
                    return
                key = "migration"
                if key not in self._condition_first_true:
                    self._log("migration conditions satisfied; waiting "
                              f"{float(group.get('duration_seconds', 0))}s before migrating")
                first = self._condition_first_true.setdefault(key, now)
                if now - first < float(group.get("duration_seconds", 0)):
                    return
                cooldown = float(group.get("cooldown_seconds", 60))
                if self._last_migration_attempt is not None and now - self._last_migration_attempt < cooldown:
                    return
                if self._migration or self._migration_in_progress:
                    return
                self._migration_in_progress = True   # 配置の計算からまとめて 1 回だけ
                self._last_migration_attempt = now
            # Never block SNMP polling or trap dispatcher during RTC migration.
            threading.Thread(target=self._migration_from_conditions, daemon=True).start()
        except Exception:
            self._rtcout.RTC_ERROR("Migration condition check failed: " + traceback.format_exc())

    ##
    # @~japanese
    # @brief 条件が成り立ったときのマイグレーションを、別スレッドで始める
    # @~english
    # @brief Starts the migration on conditions in another thread
    # @~
    def _migration_from_conditions(self):
        try:
            self._run_migration_from_conditions()
        finally:
            self._migration_in_progress = False

    ##
    # @~japanese
    # @brief 条件が成り立ったときのマイグレーションを行う
    # @~english
    # @brief Performs the migration on conditions
    # @~
    def _run_migration_from_conditions(self):
        try:
            self._log("migration started")
            self._event(self._name, "migration_started")
            if self.migration():
                self._migration_done = True
                self._log("migration completed")
                self._event(self._name, "migration_completed")
        except Exception:
            self._rtcout.RTC_ERROR("Migration failed: " + traceback.format_exc())
            print(f"[SNMPManager:{self._name}] migration failed:\n" + traceback.format_exc(), flush=True)
            self._event(self._name, "migration_failed", traceback.format_exc().strip().splitlines()[-1])

    ##
    # @~japanese
    # @brief 構成ファイルのロボットのマネージャの参照を、発見したロボットから得る
    #
    # allow_down=True (マイグレーション) なら、止まっているロボットは飛ばす (_down_managers に入れる)。
    #
    # @param config_data 構成ファイルの内容
    # @param allow_down 止まっているロボットを許すか
    # @~english
    # @brief Resolves the managers in the configuration file directly from the discovered robots
    #
    # With allow_down=True (migration), stopped robots are skipped (put into _down_managers).
    #
    # @param config_data contents of the configuration file
    # @param allow_down whether stopped robots are allowed
    # @~
    def getManagerRef(self, config_data, allow_down=False):
        with self._robot_lock:
            robots = list(self._robotList)
            if self._robot is not None:
                robots.append(self._robot)

        by_name = {}
        for robot in robots:
            if robot.name in by_name and by_name[robot.name] != robot.ipaddress:
                raise RuntimeError(
                    f"Duplicate robot name {robot.name}: "
                    f"{by_name[robot.name]}, {robot.ipaddress}"
                )
            by_name[robot.name] = robot.ipaddress

        self._migration_managers = {}
        self._down_managers = []
        for name in config_data["managers"]:
            try:
                if name not in by_name:
                    raise RuntimeError(f"Robot {name} not discovered via SNMP")
                if self._liveness_enabled and not self.isAlive(name):
                    raise RuntimeError(f"Robot {name} is down (no response)")
                self._migration_managers[name] = self._resolveManager(by_name[name], name)
            except Exception:
                if not allow_down:
                    raise
                self._down_managers.append(name)

    ##
    # @~japanese
    # @brief ロボット名のマネージャの参照を返す
    #
    # @param name ロボット名
    # @return マネージャの参照
    # @~english
    # @brief Returns the manager reference of a robot
    #
    # @param name robot name
    # @return manager reference
    # @~
    def _mgr_ref(self, name):
        mgr = self._migration_managers.get(name)
        if mgr is None:
            raise RuntimeError(f"robot {name} is not available (down or unknown)")
        return mgr

    ##
    # @~japanese
    # @brief インスタンス名で RTC を探す (スレーブマネージャも含む)
    #
    # @param name インスタンス名
    # @param mgr マネージャの参照
    # @return RTC の参照
    # @~english
    # @brief Finds an RTC by instance name, including slave managers
    #
    # @param name instance name
    # @param mgr manager reference
    # @return reference of the RTC
    # @~
    def getComponent(self, name, mgr):
        candidates = [mgr] + list(mgr.get_slave_managers())
        for candidate in candidates:
            found = candidate.get_components_by_name(name)
            if found:
                return found[0]
        raise RuntimeError("RTC not found: " + name)

    ##
    # @~japanese
    # @brief SNMP の探索を待ち、起動時の構成を 1 回だけ適用する
    # @~english
    # @brief Waits for SNMP discovery, then applies the startup plan once
    # @~
    def _startup_configuration(self):
        retry = max(0.2, float(self._conf.getProperty("snmp.startup_retry_interval", "3")))
        timeout = float(self._conf.getProperty("snmp.startup_timeout", "60"))
        deadline = time.monotonic() + timeout if timeout >= 0 else None
        while self._running and not self._startup_completed:
            try:
                config_data = self.loadMigrationConfig()
                plan = config_data.get("startup")
                if plan is None:
                    # Legacy JSON describes migration only; do not unexpectedly
                    # launch components at startup.
                    self._startup_completed = True
                    return
                if plan.get("executor") == "auto":
                    # 実行するロボットを選ぶ。選ばれなかったロボットは、完了の通知 (トラップ) か、
                    # 計画の RTC がそろったのを見て完了とする。選ばれたロボットが止まれば次が選ばれる
                    counts = self._planned_counts(plan)
                    elected = self._elect_executor(config_data, plan, counts, "startup")
                    if elected is None:
                        raise RuntimeError("electing the executor (waiting for robot status)")
                    if elected != self._name:
                        if self._startup_observed(plan):
                            self._startup_completed = True
                            self._startup_known = True   # 構成が適用済みだと分かっている (問い合わせに答えてよい)
                            self._log(f"startup configuration observed (applied by {elected})")
                            return
                        if self._already_started_elsewhere():
                            # 復帰したロボット: 待機モジュールに切り替わった RTC は計画の名前で見つからないので、
                            # 構成が終わっていると知っているロボットの返事で加わる
                            self._startup_completed = True
                            self._startup_known = True
                            self._log(f"startup configuration already applied (reported by {self._startup_reported_by}); "
                                      "joining the running system")
                            self._event(self._name, "startup_joined", f"reported by {self._startup_reported_by}")
                            self._write_startup_status("joined", reported_by=self._startup_reported_by)
                            return
                        raise RuntimeError(f"startup plan is applied by {elected}; waiting for completion")
                elif not self._isExecutor(config_data, plan):
                    self._log(f"startup plan is applied by {plan['executor']}; skipped here")
                    self._startup_completed = True
                    return
                if self._already_started_elsewhere():
                    # 止まっていたロボットが復帰した: ほかのロボットで構成が動いているので、起動時の構成はしない
                    self._startup_completed = True
                    self._startup_known = True   # 構成が適用済みだと分かっている (問い合わせに答えてよい)
                    self._log(f"startup configuration already applied (reported by {self._startup_reported_by}); "
                              "joining the running system")
                    self._event(self._name, "startup_joined", f"reported by {self._startup_reported_by}")
                    self._write_startup_status("joined", reported_by=self._startup_reported_by)
                    return
                placement_lines = []
                if plan.get("plugin") is not None:
                    # 起動時の構成をプラグインの処理で行う
                    self.getManagerRef(config_data)  # 全ロボットがそろうまで待つ
                    if not self.plugins().action(plan["plugin"], plan.get("args", {})):
                        raise StartupFailure(f"startup plugin {plan['plugin']} reported failure")
                    self._startup_completed = True
                    self._startup_known = True   # 構成が適用済みだと分かっている (問い合わせに答えてよい)
                    self._event(self._name, "startup_completed", f"plugin {plan['plugin']}")
                    self._write_startup_status("ok", plugin=plan["plugin"])
                    return
                if plan.get("mode") == "auto":
                    plan, placement_lines = self._auto_plan(config_data, plan)
                self._apply_plan(config_data, plan, "startup")
                assign = dict(self._plan_assign)
                self._launch_standby(config_data)
                # 作った RTC を一覧に反映しておく (直後の実行ロボットの選出が古い RTC の数を使わないように)
                try:
                    self._refresh_inventory()
                except Exception:
                    pass
                self._startup_completed = True
                self._startup_known = True   # 構成が適用済みだと分かっている (問い合わせに答えてよい)
                self._log("startup configuration completed")
                self._event(self._name, "startup_completed", ", ".join(f"{c['name']}@{assign.get(c['name'], c.get('manager'))}" for c in plan.get("components", [])))
                self._write_startup_status("ok", executor=self._name, placement=[
                    {"name": c["name"], "manager": assign.get(c["name"], c.get("manager"))} for c in plan.get("components", [])],
                    details=placement_lines)
                self._notify_startup_completed()
                return
            except StartupFailure as exc:
                # ロードできない RTC がある / 制限内に配置できない: リトライしても変わらないので失敗とする
                self._startup_failed(str(exc), exc.reasons)
                return
            except Exception as exc:
                if deadline is not None and time.monotonic() >= deadline:
                    self._rtcout.RTC_ERROR("Startup configuration failed: " + str(exc))
                    self._startup_failed("startup configuration timed out: " + str(exc), [])
                    return
                self._log(f"startup configuration pending ({exc}); retrying in {retry}s")
                time.sleep(retry)

    ##
    # @~japanese
    # @brief manual の計画で各ロボットに割り当てた RTC の数を返す
    #
    # @param plan 計画
    # @return {ロボット名: 数} (auto は配置前なので None = 今の RTC の数)
    # @~english
    # @brief Returns the number of RTCs assigned to each robot in a manual plan
    #
    # @param plan plan
    # @return {robot name: count} (None for auto, which is before placement, meaning the current number of RTCs)
    # @~
    @staticmethod
    def _planned_counts(plan):
        if plan.get("mode") == "auto":
            return None
        counts = {}
        for c in plan.get("components", []):
            counts[c["manager"]] = counts.get(c["manager"], 0) + 1
        return counts

    ##
    # @~japanese
    # @brief 計画の項目のインスタンス名を返す
    #
    # @param entry 計画の項目
    # @return インスタンス名
    # @~english
    # @brief Returns the instance name of an entry in a plan
    #
    # @param entry entry of a plan
    # @return instance name
    # @~
    @staticmethod
    def _instance_name(entry):
        if entry.get("existing"):
            return entry["existing"]
        match = re.search(r"(?:\?|&)instance_name=([^&]+)", entry.get("create", ""))
        return match.group(1) if match else entry["name"]

    ##
    # @~japanese
    # @brief 計画の RTC が (どこかのロボットで) すべて動いているかを、RTC の一覧で確かめる
    #
    # @param plan 計画
    # @return すべて動いていれば True
    # @~english
    # @brief Checks with the RTC lists whether all RTCs of the plan are running (on some robot)
    #
    # @param plan plan
    # @return True if all are running
    # @~
    def _startup_observed(self, plan):
        self._refresh_inventory()
        with self._robot_lock:
            robots = ([self._robot] if self._robot is not None else []) + list(self._robotList)
        names = {c["name"] for r in robots for c in (r.inventory or [])}
        return all(self._instance_name(c) in names for c in plan.get("components", []))

    ##
    # @~japanese
    # @brief ほかのロボットに起動時の構成の完了を知らせる (executor: auto のとき、待っているロボットが進める)
    # @~english
    # @brief Notifies the other robots that the startup configuration is completed (with executor: auto, waiting robots proceed)
    # @~
    def _notify_startup_completed(self):
        with self._robot_lock:
            ips = [r.ipaddress for r in self._robotList]

        def send():
            for ip in ips:
                try:
                    self._send_trap_message(ip, "Startup Completed")
                except Exception:
                    pass
        threading.Thread(target=send, daemon=True).start()

    ##
    # @~japanese
    # @brief 起動時の構成の完了の通知を受けたときの処理
    #
    # @param src_ip 送り元の IP アドレス
    # @param sender 送り元のロボット名
    # @~english
    # @brief Handles a notice that the startup configuration is completed
    #
    # @param src_ip source IP address
    # @param sender name of the sending robot
    # @~
    def _on_startup_notice(self, src_ip, sender):
        self._startup_reported_by = sender or src_ip
        if self._startup_querying:
            # 問い合わせへの返事: _already_started_elsewhere() が受け取る
            self._startup_reply.set()
            return
        self._startup_known = True
        if not self._startup_completed:
            self._startup_completed = True
            self._log(f"startup configuration completed by {sender or src_ip}")

    ##
    # @~japanese
    # @brief 起動時の構成の問い合わせに答える (終わっていれば 'Startup Completed'、まだなら 'Startup Pending')
    #
    # executor でないので飛ばしただけ (適用されたかは知らない) の場合は 'Startup Pending' と答える。
    #
    # @param src_ip 問い合わせ元の IP アドレス
    # @~english
    # @brief Answers a query about the startup configuration ('Startup Completed' if done, 'Startup Pending' otherwise)
    #
    # If this robot only skipped it because it is not the executor (and does not know whether it was applied), it answers 'Startup Pending'.
    #
    # @param src_ip IP address of the inquirer
    # @~
    def _on_startup_query(self, src_ip):
        done = self._startup_known and self._startup_failure is None
        threading.Thread(target=self._send_trap_message,
                         args=(src_ip, "Startup Completed" if done else "Startup Pending"), daemon=True).start()

    ##
    # @~japanese
    # @brief 'Startup Pending' の返事を受けたときの処理
    #
    # @param src_ip 送り元の IP アドレス
    # @~english
    # @brief Handles a 'Startup Pending' reply
    #
    # @param src_ip source IP address
    # @~
    def _on_startup_pending(self, src_ip):
        if self._startup_querying:
            self._startup_pending_from.add(src_ip)
            if self._startup_pending_from >= self._startup_query_targets:
                self._startup_reply.set()   # 全員がまだ: 待たずに進める

    ##
    # @~japanese
    # @brief ほかのロボットで起動時の構成が終わっているか (止まっていたロボットの復帰かどうか) を調べる
    #
    # 生きているほかのロボットに 'Startup Query' のトラップを送り、snmp.startup.query_wait 秒 (既定 2) の間に 'Startup Completed' の返事が来れば True。全ロボットが同時に起動したときは、まだ誰も終わっていないので、全員から 'Startup Pending' が返った時点で False にする。
    #
    # @return 終わっていれば True
    # @~english
    # @brief Checks whether the startup configuration has been completed on another robot (whether this is a recovering robot)
    #
    # Sends a 'Startup Query' trap to the other alive robots and returns True if a 'Startup Completed' reply arrives within snmp.startup.query_wait seconds (default 2). When all robots start at the same time, nobody has finished yet, so it returns False as soon as all of them reply 'Startup Pending'.
    #
    # @return True if completed elsewhere
    # @~
    def _already_started_elsewhere(self):
        wait = float(self._conf.getProperty("snmp.startup.query_wait", "2"))
        if wait <= 0:
            return False
        with self._robot_lock:
            ips = [r.ipaddress for r in self._robotList if r.status != "dead"]
        if not ips:
            return False
        self._startup_reply.clear()
        self._startup_reported_by = None
        self._startup_pending_from = set()
        self._startup_query_targets = set(ips)
        self._startup_querying = True
        try:
            for ip in ips:
                threading.Thread(target=self._send_trap_message, args=(ip, "Startup Query"), daemon=True).start()
            self._startup_reply.wait(wait)
            return self._startup_reported_by is not None
        finally:
            self._startup_querying = False

    ##
    # @~japanese
    # @brief standby.modules の待機モジュールを、アクティブにせずに起動しておく
    #
    # @param config_data 構成ファイルの内容
    # @~english
    # @brief Starts the standby modules in standby.modules without activating them
    #
    # @param config_data contents of the configuration file
    # @~
    def _launch_standby(self, config_data):
        sb = self._standby_cfg(config_data)
        mods = (sb or {}).get("modules", [])
        if not mods:
            return
        plan = {"components": [dict(m, activate=False) for m in mods], "connections": [], "_no_standby": True}
        self._apply_plan(config_data, plan, "standby")
        self._event(self._name, "standby_launched",
                    ", ".join(f"{m['name']}@{self._plan_assign.get(m['name'], m['manager'])}" for m in mods))

    ##
    # @~japanese
    # @brief 起動時の構成の状態をファイルに書く
    #
    # @param status 状態
    # @param **extra 追加の項目
    # @~english
    # @brief Writes the status of the startup configuration to a file
    #
    # @param status status
    # @param **extra additional items
    # @~
    def _write_startup_status(self, status, **extra):
        path = self._conf.getProperty("snmp.startup_status_file", "startup_status.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(dict(status=status, time=time.strftime("%Y-%m-%dT%H:%M:%S%z"), **extra),
                          f, ensure_ascii=False, indent=1)
        except OSError:
            self._rtcout.RTC_WARN("cannot write " + path)

    ##
    # @~japanese
    # @brief 起動時の構成の失敗 (システム起動失敗) を記録する
    #
    # @param message メッセージ
    # @param reasons 理由の一覧
    # @~english
    # @brief Records a failure of the startup configuration (system startup failure)
    #
    # @param message message
    # @param reasons list of reasons
    # @~
    def _startup_failed(self, message, reasons):
        self._startup_failure = message
        self._rtcout.RTC_ERROR("SYSTEM STARTUP FAILED: " + message)
        self._log("SYSTEM STARTUP FAILED: " + message)
        for r in reasons:
            self._rtcout.RTC_ERROR("  " + r)
            self._log("  " + r)
        self._write_startup_status("failed", error=message, reasons=reasons)
        self._event(self._name, "startup_failed", message)

    # ------------------------------------------------------------------
    # 自動配置 (startup.mode: auto)
    # ------------------------------------------------------------------
    ##
    # @~japanese
    # @brief 追加の監視の値の制約を満たさないロボットの名前を返す (ログに理由を出す)。値が分からないロボットは外さない
    #
    # @param config_data 構成ファイルの内容
    # @param constraints 制約
    # @param already 既に除いたロボット
    # @return ロボット名の集合
    # @~english
    # @brief Returns the names of robots that violate the custom metric constraints (reasons are logged). Robots with unknown values are not excluded
    #
    # @param config_data contents of the configuration file
    # @param constraints constraints
    # @param already robots already excluded
    # @return set of robot names
    # @~
    def _metric_excluded(self, config_data, constraints, already=()):
        out = []
        if not constraints:
            return out
        for name in config_data["managers"]:
            robot = self._findConditionRobot(name)
            if name in already or robot is None:
                continue
            bad = CustomMetrics.violations(robot.metrics, constraints, tuple(self._custom_metrics))
            if bad:
                self._log(f"placement: {name} is excluded ({', '.join(CustomMetrics.describe(v) for v in bad)})")
                out.append(name)
        return out

    ##
    # @~japanese
    # @brief cgroup の空き・get_loadable_modules()・placement.xml から配置先を決め、manual の計画にして返す
    #
    # 起動時 (strict=True) は全ロボットがそろうまで待つ。マイグレーション (strict=False) は、止まっているロボットと exclude (移動元) を除いたロボットに置く。待機モジュールがあればそれを優先し、メモリの予約を差し引いた空きで、logic (optimal / first_fit / objective / 配置プラグイン) で置き場所を決める。
    #
    # @param config_data 構成ファイルの内容
    # @param plan auto の計画
    # @param exclude 置かないロボット
    # @param strict 全ロボットがそろうまで待つか
    # @param force_standby 待機モジュールを必ず使うか
    # @return (manual の計画, 説明の行)
    # @~english
    # @brief Decides the placement from the free cgroup resources, get_loadable_modules() and placement.xml, and returns it as a manual plan
    #
    # At startup (strict=True), it waits until all robots are present. For migration (strict=False), RTCs are placed on robots other than the stopped robots and exclude (the source). Standby modules are preferred if available, and the placement is decided by logic (optimal / first_fit / objective / placement plugin) with the free resources minus the memory reservations.
    #
    # @param config_data contents of the configuration file
    # @param plan auto plan
    # @param exclude robots not to place on
    # @param strict whether to wait until all robots are present
    # @param force_standby whether standby modules must be used
    # @return (manual plan, lines of explanation)
    # @~
    def _auto_plan(self, config_data, plan, exclude=(), strict=True, force_standby=False):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import RTCPlacement as pl

        self.getManagerRef(config_data, allow_down=not strict)  # 起動時は全ロボットが見つかるまで例外 (リトライ)
        # 追加の監視の値の制約 (metric_constraints) を満たさないロボットには、新しく置かない (移動元と同じ扱い)
        exclude = list(exclude) + self._metric_excluded(config_data, plan.get("metric_constraints"), exclude)
        names = [n for n in config_data["managers"] if n in self._migration_managers and n not in exclude]
        if not names:
            raise RuntimeError("no robot is available for placement")
        executor = plan.get("executor") if plan.get("executor") not in (None, "auto") else None
        primary = plan.get("primary") or executor or self._name
        if primary not in names:
            primary = names[0]
        creates = [c for c in plan["components"] if c.get("create")]
        existing = [c for c in plan["components"] if not c.get("create")]

        # 1. 各マスターマネージャで生成できるモジュール
        loadable, languages = {}, {}
        for name in names:
            mgr = self._migration_managers[name]
            mods = [self._nvlist_to_dict(m.properties) for m in mgr.get_loadable_modules()]
            loadable[name] = pl.loadable_index(mods)
            self.__dict__.setdefault("_module_cache", {})[name] = loadable[name]
            langs = set()
            for slave in mgr.get_slave_managers():
                langs.add(self._nvlist_to_dict(slave.get_configuration()).get("manager.language", ""))
            languages[name] = langs
        missing = []
        for c in creates:
            module = pl.module_name_of(c["create"])
            if not any(module in loadable[n] for n in names):
                missing.append(f"{c['name']} ({module}): どのマスターマネージャの get_loadable_modules() にもない")
        if missing:
            avail = [f"{n}: {', '.join(sorted(loadable[n])) or '(なし)'}" for n in names]
            raise StartupFailure("起動予定の RTC をロードできるマスターマネージャがありません",
                                 missing + ["ロード可能なモジュール:"] + avail)

        # 2. 各ロボットの空き (cgroup の制限 - max(現在の使用量, 予約) - margin) と通信状態
        rcfg = self._reservation_cfg(config_data)
        self._refresh_inventory()
        link_rules = plan.get("link_constraints") or {}
        robots = [self._robot_capacity(name, config_data, languages[name], rcfg, link_rules) for name in names]
        # 除外したロボット (移動元など) でも、生きていれば、そこで動き続ける既存の RTC は置ける (空き 0 で加える)
        for name in sorted({c["manager"] for c in existing if c["manager"] not in names
                            and c["manager"] in self._migration_managers}):
            robots.append(pl.Robot(name, 0.0, 0.0, set(), set()))
            self._log(f"capacity {name}: excluded from placement (keeps its existing RTCs only)")

        # 3. RTC の見込み値と置けるロボット (待機モジュールがあればそこに固定する)
        db = self._profiles()
        sb = self._standby_cfg(config_data) or ({"scope": "any"} if force_standby else None)
        used_standby = []
        # 計画の RTC と、計画で消す RTC (移動元。並行して終了させる) は待機モジュールにしない
        plan_names = {self._instance_name(c) for c in plan["components"]} | {r["name"] for r in plan.get("remove", [])}
        items, problems = [], []
        for c in creates:
            module = pl.module_name_of(c["create"])
            mod = next(loadable[n][module] for n in names if module in loadable[n])
            prof = db.get(mod.get("type_name") or module, mod.get("language", "Python"))
            if prof is None:
                problems.append(f"{c['name']} ({mod.get('type_name')}): placement.xml に計測値がない")
                continue
            cands = [r.name for r in robots if r.name in loadable and module in loadable[r.name]
                     and (c.get("manager") is None or c["manager"] == r.name)
                     and prof.requires <= r.tags]
            mem = prof.memory_mb
            if rcfg is not None:
                # 置く RTC も予約量を確保する (見込みより予約が大きければ予約で数える)
                mem = max(mem, self._reserve_mb(rcfg, module, prof.rtc, prof.language, c))
            item = pl.Item(c["name"], module, prof.language, prof.cpu, mem,
                           self._slave_overhead(prof.language, prof), cands, prof)
            # 同じ名前の RTC が移動先の候補で既に動いている (別のロボットが一度実行した) なら、そのまま使う
            inst = self._instance_name(c)
            where = next((r.name for r in robots if r.name in names
                          and any(x["name"] == inst for x in (self._robot_inventory(r.name) or []))), None)
            if not strict and where is not None:
                item.candidates, item.cpu, item.memory_mb, item.slave_overhead_mb, item.fixed = [where], 0.0, 0.0, 0.0, True
            elif sb is not None and c.get("standby", True):
                scope = [c["manager"]] if (sb.get("scope") == "same" and c.get("manager")) else \
                    ([c["manager"]] if c.get("manager") else []) + [n for n in names if n != c.get("manager")]
                found = self._find_standby(module, [n for n in scope if n in cands], used_standby, plan_names)
                if found is not None:
                    rname, comp = found
                    used_standby.append(comp["ref"])
                    # 待機モジュールのメモリは既に使用量 (と予約) に入っている。アクティブにすると CPU を使う
                    item.candidates, item.memory_mb, item.slave_overhead_mb, item.standby = [rname], 0.0, 0.0, comp["name"]
            items.append(item)
        for c in existing:
            if c["manager"] not in {r.name for r in robots}:
                problems.append(f"{c['name']}: 既存の RTC のロボット {c['manager']} が使えない")
                continue
            info = next((x for x in (self._robot_inventory(c["manager"]) or []) if x["name"] == c["existing"]), None)
            prof = db.get(info["type"], info.get("language") or "Python") if info else None
            items.append(pl.Item(c["name"], info["type"] if info else c["existing"],
                                 (info or {}).get("language") or "Python", 0.0, 0.0, 0.0, [c["manager"]], prof,
                                 fixed=True))
        if problems:
            raise StartupFailure("RTC の見込み値がないため配置できません", problems)
        edges = pl.build_edges(plan.get("connections", []), items)
        logic = plan.get("logic") or self._conf.getProperty("snmp.placement.logic", "optimal")
        try:
            if plan.get("placement_plugin"):
                logic = "plugin " + plan["placement_plugin"]
                result = self._plugin_placement(pl, plan, items, robots, edges, primary)
            else:
                result = pl.solve(items, robots, edges, primary, logic, self._objective_fn(pl, plan))
        except pl.PlacementError as exc:
            raise StartupFailure(str(exc), exc.reasons) from exc
        lines = [f"logic: {logic}" + (f", objective plugin {plan['objective_plugin']}" if plan.get("objective_plugin") else "")]
        measured = [f"{it.name} ({it.profile.rtc} cpu {it.profile.cpu:g}% mem {it.profile.memory_mb:g}MB, "
                    f"{it.profile.samples} samples)" for it in items
                    if it.profile is not None and it.profile.measured and not it.fixed]
        if measured:
            lines.append("measured estimates: " + ", ".join(measured))
        lines += pl.describe(result, items, robots, edges, primary)
        self._log("auto placement:")
        for line in lines:
            self._log("  " + line)
        by_name = {it.name: it for it in items}
        comps = []
        for c in plan["components"]:
            entry = dict(c, manager=result.assign[c["name"]])
            if by_name[c["name"]].standby:
                entry["standby_instance"] = by_name[c["name"]].standby
            comps.append(entry)
        manual = dict(plan, mode="manual", components=comps)
        return manual, lines

    ##
    # @~japanese
    # @brief objective のロジックの目的関数を返す (objective_plugin があればプラグイン、なければ重み付き和)
    #
    # @param pl placement モジュール
    # @param plan 計画
    # @return fn(item, robot, state) -> float
    # @~english
    # @brief Returns the objective function of the objective logic (the plugin if objective_plugin is given, otherwise the weighted sum)
    #
    # @param pl placement module
    # @param plan plan
    # @return fn(item, robot, state) -> float
    # @~
    def _objective_fn(self, pl, plan):
        if plan.get("objective_plugin"):
            name, args = plan["objective_plugin"], plan.get("objective_args", {})
            return lambda item, robot, state: self.plugins().objective(name, item, robot, state, args)
        weights = (plan.get("objective") or {}).get("weights")
        return lambda item, robot, state: pl.objective_value(item, robot, state, weights)

    ##
    # @~japanese
    # @brief ロボットの空き (CPU・メモリ、予約、通信状態) を placement.Robot にする
    #
    # @param name ロボット名
    # @param config_data 構成ファイルの内容
    # @param languages 既に slave が動いている言語
    # @param rcfg メモリの予約の設定
    # @param link_rules ロボット間の制約
    # @return placement.Robot
    # @~english
    # @brief Makes a placement.Robot with the free resources of a robot (CPU, memory, reservations, link quality)
    #
    # @param name robot name
    # @param config_data contents of the configuration file
    # @param languages languages whose slaves are already running
    # @param rcfg memory reservation settings
    # @param link_rules inter-robot constraints
    # @return placement.Robot
    # @~
    def _robot_capacity(self, name, config_data, languages, rcfg, link_rules):
        import RTCPlacement as pl
        cpu_margin = float(self._conf.getProperty("snmp.placement.cpu_margin", "10"))
        mem_margin = float(self._conf.getProperty("snmp.placement.memory_margin_mb", "32"))
        unlimited_cpu = float(self._conf.getProperty("snmp.placement.unlimited_cpu", "100"))
        default_tags = {t.strip() for t in self._conf.getProperty("snmp.placement.robot_tags", "").split(",") if t.strip()}
        robot = self._findConditionRobot(name)
        cg = getattr(robot, "cgroup", None) if robot is not None else None
        min_samples = int(self._conf.getProperty("snmp.placement.min_cpu_samples", "3"))
        if not cg or cg.get("cpu_usage_pct") is None or len(cg.get("cpu_samples", [])) < min_samples:
            # 起動直後の負荷を拾わないよう、使用率のサンプルがそろうまで待つ
            raise RuntimeError(f"waiting for cgroup metrics of {name}")
        cpu_cap = cg["cpu_limit_pct"] or unlimited_cpu
        mem_cap = cg["mem_limit_mb"] or float(robot.data.get("mem_total_mb") or 0)
        mc = config_data["managers"][name]
        tags = set(mc.get("tags", default_tags)) if isinstance(mc, dict) else default_tags
        mem_used = cg["mem_usage_mb"]
        reserved = 0.0
        note = ""
        if rcfg is not None:
            # メモリの予約: 動いている RTC (待機モジュールを含む) ごとに予約量を確保済みとみなす。
            # 実際の使用量が予約より少なくても (起動直後・負荷の小さいとき)、予約分は使えない
            reserved = self._reserved_on(rcfg, robot)
            committed = (robot.base_mem_mb or 0.0) + reserved + self._pending_reserve.get(name, 0.0)
            if committed > mem_used:
                note = f" (reserved {reserved:.1f}MB + base {robot.base_mem_mb or 0:.1f}MB = {committed:.1f}MB > used)"
            mem_used = max(mem_used, committed)
        link = {"latency_ms": robot.latency_ms, "jitter_ms": robot.jitter_ms,
                "packet_loss": robot.packet_loss, "rssi_dbm": robot.data.get("wifi_signal_dbm")}
        link_ok = robot.is_local or self._link_ok(link, link_rules)
        r = pl.Robot(name, max(0.0, cpu_cap - cg["cpu_usage_pct"] - cpu_margin),
                     max(0.0, mem_cap - mem_used - mem_margin), tags, languages, cpu_cap, mem_cap,
                     link_ok, link, reserved)
        self._log(f"capacity {name}: CPU limit {cpu_cap:.0f}% used {cg['cpu_usage_pct']:.1f}% -> free "
                  f"{r.cpu_free:.1f}%, memory limit {mem_cap:.0f}MB used {cg['mem_usage_mb']:.1f}MB{note} "
                  f"-> free {r.mem_free_mb:.1f}MB" + ("" if link_ok else ", link constraints NOT satisfied"))
        return r

    ##
    # @~japanese
    # @brief ロボット間の制約: 通信する RTC をこのロボットとまたいで置いてよいかを調べる
    #
    # @param link 通信状態
    # @param rules 制約
    # @return 置いてよければ True
    # @~english
    # @brief Inter-robot constraint: checks whether communicating RTCs may be placed across this robot
    #
    # @param link link quality
    # @param rules constraints
    # @return True if allowed
    # @~
    @staticmethod
    def _link_ok(link, rules):
        def val(k):
            v = link.get(k)
            return None if v is None else float(v)
        checks = [("max_latency_ms", "latency_ms", lambda v, t: v <= t),
                  ("max_jitter_ms", "jitter_ms", lambda v, t: v <= t),
                  ("max_packet_loss", "packet_loss", lambda v, t: v <= t),
                  ("min_rssi_dbm", "rssi_dbm", lambda v, t: v >= t)]
        for rule, key, ok in checks:
            if rules.get(rule) is not None and val(key) is not None and not ok(val(key), float(rules[rule])):
                return False
        return True

    # ------------------------------------------------------------------
    # 自動復旧: 切り替えの条件と段階的な復旧
    # ------------------------------------------------------------------
    # 切り替えの条件のしきい値 (recovery.conditions) -> (原因, 説明)
    RecoveryThresholds = {
        "memory_free_min_mb": ("memory", "空きメモリ (cgroup の制限 - 使用量) がしきい値より少ない"),
        "memory_max_pct": ("memory", "メモリ使用率 (cgroup。なければホスト) がしきい値を超えた"),
        "cpu_max_pct": ("cpu", "CPU 使用率 (cgroup の制限に対する割合) がしきい値を超えた"),
        "battery_min_pct": ("battery", "バッテリー残量がしきい値より少ない"),
        "rssi_min_dbm": ("communication", "Wi-Fi の信号強度 (RSSI) がしきい値より弱い"),
        "latency_max_ms": ("communication", "レイテンシがしきい値を超えた"),
        "jitter_max_ms": ("communication", "ジッタがしきい値を超えた"),
        "throughput_min_mbps": ("communication", "スループット (受信 + 送信) がしきい値より少ない"),
        "packet_loss_max": ("communication", "パケットロス (%) がしきい値を超えた"),
    }
    # 同じロボットの中で直すことを試す原因 (RTC の ERROR・消失と、メモリ・CPU の不足)。ほかは別のロボットへ移す
    RecoveryLocalCauses = ("error", "missing", "memory", "cpu")
    RecoveryStages = ("reset", "standby_same", "restart", "other")
    RecoveryDefaultStages = {"local": ["reset", "standby_same", "restart", "other"], "remote": ["other"]}

    ##
    # @~japanese
    # @brief 自動復旧の設定を返す
    #
    # @param config_data 構成ファイルの内容
    # @return 設定 (無効なら None)
    # @~english
    # @brief Returns the recovery settings
    #
    # @param config_data contents of the configuration file
    # @return settings (None if disabled)
    # @~
    @staticmethod
    def _recovery_cfg(config_data):
        rc = (config_data or {}).get("recovery")
        return rc if isinstance(rc, dict) and rc.get("enabled", True) else None

    ##
    # @~japanese
    # @brief 自動復旧のスレッドの本体
    # @~english
    # @brief Body of the recovery thread
    # @~
    def _recovery_loop(self):
        while self._running:
            interval = 2.0
            try:
                cfg = self.loadMigrationConfig()
                rc = self._recovery_cfg(cfg)
                if rc is not None:
                    interval = float(rc.get("interval", 2))
                    self._recovery_tick(cfg, rc)
            except Exception:
                self._rtcout.RTC_WARN("recovery check failed: " + traceback.format_exc())
            # slave の異常終了を知ったら、待たずに次の確認をする
            self._recovery_wake.wait(max(0.5, interval))
            self._recovery_wake.clear()

    ##
    # @~japanese
    # @brief ロボットの切り替えの条件のうち、今満たしているものを返す
    #
    # @param robot ロボット
    # @param conds 切り替えの条件
    # @return [(原因, 説明)]
    # @~english
    # @brief Returns the robot switching conditions that currently hold
    #
    # @param robot robot
    # @param conds switching conditions
    # @return [(cause, description)]
    # @~
    def _robot_problems(self, robot, conds):
        if robot is None:
            return []
        if not robot.is_local and robot.status == "dead":
            return [("down", "no response")] if conds.get("down", True) else []
        out = []
        cg = robot.cgroup or {}
        data = robot.data

        def num(v):
            try:
                return None if v is None else float(v)
            except (TypeError, ValueError):
                return None
        checks = []
        if cg.get("mem_limit_mb") and cg.get("mem_usage_mb") is not None:
            checks.append(("memory_free_min_mb", cg["mem_limit_mb"] - cg["mem_usage_mb"], "<"))
            checks.append(("memory_max_pct", cg["mem_usage_mb"] / cg["mem_limit_mb"] * 100.0, ">"))
        else:
            checks.append(("memory_max_pct", num(data.get("memory_usage")), ">"))
        if cg.get("cpu_usage_pct") is not None and cg.get("cpu_limit_pct"):
            checks.append(("cpu_max_pct", cg["cpu_usage_pct"] / cg["cpu_limit_pct"] * 100.0, ">"))
        else:
            checks.append(("cpu_max_pct", num(data.get("cpu_usage")), ">"))
        checks.append(("battery_min_pct", num(data.get("battery_pct")), "<"))
        if not robot.is_local:
            checks.append(("rssi_min_dbm", num(data.get("wifi_signal_dbm")), "<"))
            checks.append(("latency_max_ms", robot.latency_ms, ">"))
            checks.append(("jitter_max_ms", robot.jitter_ms, ">"))
            checks.append(("packet_loss_max", robot.packet_loss, ">"))
        tin, tout = num(data.get("network_in")), num(data.get("network_out"))
        checks.append(("throughput_min_mbps", None if tin is None or tout is None else tin + tout, "<"))
        for key, value, op in checks:
            limit = conds.get(key)
            if limit is None or value is None:
                continue
            if (op == "<" and value < float(limit)) or (op == ">" and value > float(limit)):
                cause, _ = self.RecoveryThresholds[key]
                out.append((cause, f"{key}: {value:.1f} {op} {float(limit):g}"))
        # 追加の監視の値 ("<名前>_max" / "<名前>_min")。ロボットの状態なので、別のロボットへ移す原因
        for v in CustomMetrics.violations(robot.metrics, conds, tuple(self._custom_metrics)):
            out.append(("metric", f"{v[0]}: {CustomMetrics.describe(v)}"))
        return out

    ##
    # @~japanese
    # @brief 計画の RTC が今どこで動いているかを返す
    #
    # 状態は ACTIVE / INACTIVE / ERROR、ロボットが止まっていれば "down"、ロボットは生きているのに RTC がなければ "missing"、分からなければ None。
    #
    # @param name 計画の RTC の名前
    # @param entry 計画の項目
    # @return (ロボット名, インスタンス名, 状態)
    # @~english
    # @brief Returns where an RTC of the plan is running now
    #
    # The state is ACTIVE / INACTIVE / ERROR, "down" if the robot is stopped, "missing" if the robot is alive but the RTC is not found, or None if unknown.
    #
    # @param name name of the RTC in the plan
    # @param entry entry of the plan
    # @return (robot name, instance name, state)
    # @~
    def _recovery_locate(self, name, entry):
        with self._robot_lock:
            robots = ([self._robot] if self._robot is not None else []) + list(self._robotList)
        by_name = {r.name: r for r in robots}
        where = self._recovery_where.get(name)
        candidates = [where["instance"]] if where else []
        if self._instance_name(entry) not in candidates:
            candidates.append(self._instance_name(entry))
        # 覚えている場所を先に、なければ全ロボットから同じインスタンス名を探す
        order = ([where["robot"]] if where and where["robot"] in by_name else []) + \
            [r.name for r in robots if not where or r.name != where["robot"]]
        for rname in order:
            inv = by_name[rname].inventory
            for c in inv or []:
                if c["name"] in candidates:
                    self._recovery_where[name] = {"robot": rname, "instance": c["name"]}
                    return rname, c["name"], c["state"]
        if where and where["robot"] in by_name:
            robot = by_name[where["robot"]]
            if not robot.is_local and robot.status == "dead":
                return where["robot"], where["instance"], "down"
            # 計画を適用する前に取った一覧では、生成したばかりの RTC がまだ載っていない (消えたとは言えない)
            if robot.inventory is not None and                     (robot.inventory_time or 0) >= getattr(self, "_last_plan_applied", 0):
                return where["robot"], where["instance"], "missing"
        return (where["robot"], where["instance"], None) if where else (None, None, None)

    ##
    # @~japanese
    # @brief 切り替えの条件を満たす RTC を返す
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @return [(RTC 名, 原因, ロボット, 説明)]
    # @~english
    # @brief Returns the RTCs that satisfy the switching conditions
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @return [(RTC name, cause, robot, description)]
    # @~
    def _recovery_problems(self, cfg, rc):
        plan = cfg["startup"]
        entries = {c["name"]: c for c in plan.get("components", [])}
        monitored = rc.get("components") or list(entries)
        conds = rc.get("conditions", {})
        located = {n: self._recovery_locate(n, entries[n]) for n in monitored}
        out = []
        robot_causes = {}
        for n, (robot, inst, state) in located.items():
            if state == "ERROR" and conds.get("error", True):
                out.append((n, "error", robot, f"{inst} is in ERROR state"))
            elif state == "missing" and conds.get("missing", True):
                out.append((n, "missing", robot, f"{inst} disappeared from {robot}"))
            elif state == "down" and conds.get("down", True):
                out.append((n, "down", robot, f"{robot} is down"))
            if robot and state not in ("down", None):
                if robot not in robot_causes:
                    robot_causes[robot] = self._robot_problems(self._findConditionRobot(robot), conds)
        db = self._profiles()
        for robot, causes in robot_causes.items():
            on_robot = [n for n, (r, _, st) in located.items() if r == robot and st not in ("down", "missing")]
            for cause, detail in causes:
                if cause in ("memory", "cpu") and rc.get("target", "largest") == "largest" and on_robot:
                    # 資源の不足: 見込みが最も大きい RTC から 1 つずつ移す
                    def size(n):
                        inv = next((c for c in (self._robot_inventory(robot) or []) if c["name"] == located[n][1]), None)
                        prof = db.get(inv["type"], inv.get("language") or "Python") if inv else None
                        return (prof.memory_mb if cause == "memory" else prof.cpu) if prof else 0.0
                    targets = [max(on_robot, key=size)]
                else:
                    targets = on_robot
                for n in targets:
                    if not any(o[0] == n for o in out):
                        out.append((n, cause, robot, detail))
        return out

    ##
    # @~japanese
    # @brief 自動復旧の 1 回分の確認と処理
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @~english
    # @brief One round of checking and handling for recovery
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @~
    def _recovery_tick(self, cfg, rc):
        if not self._startup_completed or self._recovering:
            return
        if not self._isExecutor(cfg, rc, purpose="recovery"):
            self._recovery_first_seen.clear()
            return
        if self._migration or self._migration_in_progress:
            return
        problems = self._recovery_problems(cfg, rc)
        now = time.monotonic()
        duration = float(rc.get("conditions", {}).get("duration_seconds", 3))
        current = {(n, c) for n, c, _, _ in problems}
        for key in list(self._recovery_first_seen):
            if key not in current:
                del self._recovery_first_seen[key]
        due = []
        for n, cause, robot, detail in problems:
            first = self._recovery_first_seen.setdefault((n, cause), now)
            crashed = cause == "missing" and self._crash_hint(n, now)
            if cause == "error" and self._crash_hint(n, now, table=self._error_notified):
                crashed = True
                if first != now and n not in self._notified_logged:
                    self._notified_logged.add(n)
                    self._log(f"recovery: {n} on {robot}: ERROR notified by the component observer, recovering now")
            if first == now:
                reason = "its slave manager exited abnormally" if cause == "missing" else \
                    "ERROR notified by the component observer"
                self._log(f"recovery: {n} on {robot}: {cause} ({detail}); "
                          + (f"{reason}, recovering now" if crashed else f"waiting {duration:g}s"))
            if now - first < duration and not crashed:
                continue
            if self._recovery_cooldown.get(n, 0) > now or self._recovery_cooldown.get((robot, cause), 0) > now:
                continue
            due.append((n, cause, robot, detail))
        if not due:
            return
        self._recovering = True
        self._migration_in_progress = True   # 条件によるマイグレーションと重ねない
        try:
            self._recover(cfg, rc, due)
        finally:
            self._recovering = False
            self._migration_in_progress = False
            for n, cause, _, _ in due:
                self._recovery_first_seen.pop((n, cause), None)
                inst = (self._recovery_where.get(n) or {}).get("instance")
                self._crashed.pop(n, None)
                self._error_notified.pop(n, None)
                self._notified_logged.discard(n)
                if inst:
                    self._crashed.pop(inst, None)
                    self._error_notified.pop(inst, None)

    ##
    # @~japanese
    # @brief 段階的に復旧する: 同じロボットで直せる原因は段階的に試し、だめなら別のロボットへ切り替える
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @param due 復旧する RTC
    # @~english
    # @brief Recovers step by step: causes that can be fixed on the same robot are tried in stages, otherwise switches to another robot
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @param due RTCs to recover
    # @~
    def _recover(self, cfg, rc, due):
        started = time.perf_counter()
        cooldown = float(rc.get("cooldown_seconds", 20))
        stages = dict(self.RecoveryDefaultStages, **rc.get("stages", {}))
        self._event(self._name, "recovery_started",
                    ", ".join(f"{n}@{robot}: {cause}" for n, cause, robot, _ in due))
        switching, results = [], []
        for n, cause, robot, detail in due:
            kind = "local" if cause in self.RecoveryLocalCauses else "remote"
            done = False
            for stage in stages[kind]:
                if stage == "other":
                    switching.append((n, cause, robot))
                    break
                try:
                    done = self._recovery_stage_local(cfg, rc, stage, n, cause, robot)
                except Exception as exc:
                    self._log(f"recovery: {n}: stage {stage} failed: {exc}")
                    self._rtcout.RTC_WARN(traceback.format_exc())
                    done = False
                if done:
                    results.append(f"{n}: {stage}")
                    break
            else:
                if not done:
                    results.append(f"{n}: not recovered")
        if switching:
            try:
                where = self._recovery_switch_other(cfg, rc, switching)
                results += [f"{n}: other -> {where.get(n)}" for n, _, _ in switching]
            except Exception as exc:
                self._log(f"recovery: switching to other robots failed: {exc}")
                print(traceback.format_exc(), flush=True)
                results += [f"{n}: failed ({exc})" for n, _, _ in switching]
        now = time.monotonic()
        for n, cause, robot, _ in due:
            self._recovery_cooldown[n] = now + cooldown
            self._recovery_cooldown[(robot, cause)] = now + cooldown
        elapsed = time.perf_counter() - started
        ok = not any("failed" in r or "not recovered" in r for r in results)
        self._event(self._name, "recovery_completed" if ok else "recovery_failed",
                    f"{'; '.join(results)} ({elapsed:.2f}s)")
        with open(self._logfile, "a") as f:
            f.write(f"{seconds_since_midnight():.6f}\tRecoveryTime:{elapsed}\t{';'.join(results)}\t\n")

    ##
    # @~japanese
    # @brief 段階の後、settle_seconds 待ってから、その RTC の切り替えの条件がまだ成り立つかを調べる
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @param name RTC の名前
    # @param cause 原因
    # @param robot ロボット名
    # @return 直っていれば True
    # @~english
    # @brief After a stage, waits settle_seconds and checks whether the switching condition of the RTC still holds
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @param name name of the RTC
    # @param cause cause
    # @param robot robot name
    # @return True if resolved
    # @~
    def _recovery_resolved(self, cfg, rc, name, cause, robot):
        time.sleep(float(rc.get("settle_seconds", 4)))
        self._refresh_inventory()
        entry = next(c for c in cfg["startup"]["components"] if c["name"] == name)
        where, inst, state = self._recovery_locate(name, entry)
        if state in (None, "down", "missing", "ERROR"):
            return False
        if cause in ("memory", "cpu"):
            conds = rc.get("conditions", {})
            return not any(c == cause for c, _ in self._robot_problems(self._findConditionRobot(where), conds))
        return True

    ##
    # @~japanese
    # @brief names の RTC につながる接続と、相手の RTC (動かさない既存の RTC) を含む計画を作る
    #
    # @param cfg 構成ファイルの内容
    # @param names RTC の名前
    # @param extra_components 追加の項目
    # @return {"components", "connections"}
    # @~english
    # @brief Makes a plan with the connections of the RTCs in names and their peer RTCs (existing RTCs that are not moved)
    #
    # @param cfg contents of the configuration file
    # @param names names of the RTCs
    # @param extra_components additional components
    # @return {"components", "connections"}
    # @~
    def _recovery_peer_plan(self, cfg, names, extra_components):
        plan = cfg["startup"]
        entries = {c["name"]: c for c in plan.get("components", [])}
        comps = list(extra_components)
        conns, peers = [], {}
        for conn in plan.get("connections", []):
            ends = (conn["source"]["component"], conn["target"]["component"])
            if not any(e in names for e in ends):
                continue
            ok = True
            for e in ends:
                if e in names or e in peers:
                    continue
                robot, inst, state = self._recovery_locate(e, entries[e])
                if state in (None, "down", "missing"):
                    ok = False
                    self._log(f"recovery: skip connection {conn['name']}: {e} is not running")
                    break
                peers[e] = {"name": e, "existing": inst, "manager": robot}
            if ok:
                conns.append(conn)
        return {"components": comps + list(peers.values()), "connections": conns}

    ##
    # @~japanese
    # @brief 同じロボットでの段階 (reset / standby_same / restart) を行う
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @param stage 段階
    # @param name RTC の名前
    # @param cause 原因
    # @param robot ロボット名
    # @return 直れば True
    # @~english
    # @brief Performs a stage on the same robot (reset / standby_same / restart)
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @param stage stage
    # @param name name of the RTC
    # @param cause cause
    # @param robot robot name
    # @return True if resolved
    # @~
    def _recovery_stage_local(self, cfg, rc, stage, name, cause, robot):
        import RTCPlacement as pl
        entry = next(c for c in cfg["startup"]["components"] if c["name"] == name)
        where, inst, state = self._recovery_locate(name, entry)
        if where is None or state == "down":
            return False
        self.getManagerRef(cfg, allow_down=True)
        mgr = self._mgr_ref(where)
        comp = self._find_existing(inst, mgr) if state != "missing" else None
        module = pl.module_name_of(entry["create"]) if entry.get("create") else None
        if stage == "reset":
            # ERROR のときだけリセットできる (リセットすると INACTIVE に戻るので、アクティブにし直す)
            if comp is None or state != "ERROR":
                return False
            self._log(f"recovery: {name}: reset {inst} on {where}")
            ecs = comp.get_owned_contexts()
            if not ecs or ecs[0].reset_component(comp) != RTC.RTC_OK:
                return False
            if entry.get("activate", True):
                ecs[0].activate_component(comp)
            ok = self._recovery_resolved(cfg, rc, name, cause, where)
            self._event(where, "recovery_stage", f"{name}: reset -> {'ok' if ok else 'not resolved'}")
            return ok
        if module is None:
            return False
        if stage == "standby_same":
            found = self._find_standby(module, [where], [comp] if comp is not None else [], {inst})
            if found is None:
                return False
            _, info = found
            self._log(f"recovery: {name}: switch to standby {info['name']} on {where}")
            self._recovery_terminate(name, inst, where, comp)
            plan = self._recovery_peer_plan(cfg, {name}, [dict(entry, manager=where, standby_instance=info["name"],
                                                               activate=entry.get("activate", True))])
            self._apply_plan(cfg, plan, "Recovery")
            ok = self._recovery_resolved(cfg, rc, name, cause, where)
            self._event(where, "recovery_stage", f"{name}: standby_same {info['name']} -> {'ok' if ok else 'not resolved'}")
            return ok
        if stage == "restart":
            self._log(f"recovery: {name}: restart {inst} on {where}")
            self._recovery_terminate(name, inst, where, comp)
            plan = self._recovery_peer_plan(cfg, {name}, [dict(entry, manager=where, standby=False,
                                                               activate=entry.get("activate", True))])
            plan["_no_standby"] = True
            self._apply_plan(cfg, plan, "Recovery")
            ok = self._recovery_resolved(cfg, rc, name, cause, where)
            self._event(where, "recovery_stage", f"{name}: restart -> {'ok' if ok else 'not resolved'}")
            return ok
        return False

    ##
    # @~japanese
    # @brief 故障した RTC を終了させ、消えるまで待つ (同じ名前で作り直すため)
    #
    # @param name RTC の名前
    # @param inst インスタンス名
    # @param robot ロボット名
    # @param comp RTC の参照
    # @~english
    # @brief Terminates a failed RTC and waits until it disappears (to recreate it with the same name)
    #
    # @param name name of the RTC
    # @param inst instance name
    # @param robot robot name
    # @param comp reference of the RTC
    # @~
    def _recovery_terminate(self, name, inst, robot, comp):
        if comp is None:
            return
        mgr = self._migration_managers.get(robot)
        try:
            self._remove_one({"name": inst, "manager": robot}, comp)
        except Exception as exc:
            self._log(f"recovery: terminating {inst} on {robot} failed: {exc}")
        deadline = time.monotonic() + 5
        while mgr is not None and time.monotonic() < deadline:
            try:
                if self._find_existing(inst, mgr) is None:
                    break
            except Exception:
                break
            time.sleep(0.2)
        self._recovery_where.pop(name, None)

    ##
    # @~japanese
    # @brief 別のロボットへ切り替える: 故障した RTC を終了させ、別のロボットの待機モジュールに切り替えるか、別のロボットで起動する
    #
    # 移す先からは、元のロボットと、切り替えの条件を今満たしているロボットを除く。置き場所は、待機モジュールを優先し、空き容量 (メモリの予約を含む) を確かめて、logic で決める。
    #
    # @param cfg 構成ファイルの内容
    # @param rc 自動復旧の設定
    # @param switching 切り替える RTC
    # @return {RTC 名: 移した先のロボット}
    # @~english
    # @brief Switches to another robot: terminates the failed RTCs and switches to standby modules on another robot or starts them there
    #
    # The original robot and the robots that currently satisfy the switching conditions are excluded from the destinations. Standby modules are preferred, the free capacity (including memory reservations) is checked, and the location is decided by logic.
    #
    # @param cfg contents of the configuration file
    # @param rc recovery settings
    # @param switching RTCs to switch
    # @return {RTC name: destination robot}
    # @~
    def _recovery_switch_other(self, cfg, rc, switching):
        names = {n for n, _, _ in switching}
        entries = {c["name"]: c for c in cfg["startup"]["components"]}
        conds = rc.get("conditions", {})
        self.getManagerRef(cfg, allow_down=True)
        exclude = set()
        for n, cause, robot in switching:
            exclude.add(robot)
            _, inst, state = self._recovery_locate(n, entries[n])
            if state not in ("down", "missing", None) and robot in self._migration_managers:
                comp = self._find_existing(inst, self._migration_managers[robot])
                self._recovery_terminate(n, inst, robot, comp)
        for rname in cfg["managers"]:
            if rname in exclude:
                continue
            if self._robot_problems(self._findConditionRobot(rname), conds):
                self._log(f"recovery: {rname} is excluded (it meets a switching condition)")
                exclude.add(rname)
        creates = []
        for n in names:
            e = dict(entries[n])
            e.pop("manager", None)
            e["activate"] = entries[n].get("activate", True)
            creates.append(e)
        plan = self._recovery_peer_plan(cfg, names, creates)
        plan.update(mode="auto", logic=rc.get("logic") or cfg.get("startup", {}).get("logic") or "first_fit")
        if rc.get("link_constraints"):
            plan["link_constraints"] = rc["link_constraints"]
        self._refresh_inventory()
        manual, lines = self._auto_plan(cfg, plan, exclude=sorted(exclude), strict=False, force_standby=True)
        manual["_force_standby"] = True
        self._apply_plan(cfg, manual, "Recovery")
        where = {n: self._plan_assign.get(n) for n in names}
        for n in names:
            self._event(where[n] or "-", "recovery_stage",
                        f"{n}: other -> {where[n]} ({self._plan_instances.get(n, n)})")
        return where

    # ------------------------------------------------------------------
    # RTC の一覧・待機モジュール・メモリの予約
    # ------------------------------------------------------------------
    _STATES = None

    ##
    # @~japanese
    # @brief マネージャ (と slave) の RTC の一覧を返す
    #
    # @param mgr マネージャの参照
    # @return [{name, type, language, state, slave, ref}]
    # @~english
    # @brief Returns the list of RTCs of a manager (and its slaves)
    #
    # @param mgr manager reference
    # @return [{name, type, language, state, slave, ref}]
    # @~
    def _list_components(self, mgr):
        if SNMPManager._STATES is None:
            SNMPManager._STATES = {RTC.ACTIVE_STATE: "ACTIVE", RTC.INACTIVE_STATE: "INACTIVE",
                                   RTC.ERROR_STATE: "ERROR", RTC.CREATED_STATE: "CREATED"}
        try:
            slaves = list(mgr.get_slave_managers())
        except Exception:
            slaves = []
        out, seen = [], set()
        # マスターの get_components() は slave の RTC も返すので、slave を先に調べる (どの slave の RTC か分かるように)
        for idx, m in [(i + 1, s) for i, s in enumerate(slaves)] + [(0, mgr)]:
            try:
                comps = m.get_components()
            except Exception:
                continue
            slave_name = ""
            if idx > 0 and comps:
                try:
                    slave_name = self._nvlist_to_dict(m.get_configuration()).get("manager.instance_name", "")
                except Exception:
                    pass
            for comp in comps:
                try:
                    prof = comp.get_component_profile()
                    if prof.instance_name in seen:
                        continue
                    seen.add(prof.instance_name)
                    state = "UNKNOWN"
                    ecs = comp.get_owned_contexts()
                    if ecs:
                        state = SNMPManager._STATES.get(ecs[0].get_component_state(comp), "UNKNOWN")
                    # ComponentProfile に言語の項目はないので、properties (implementation_id, language) から取る
                    props = self._nvlist_to_dict(prof.properties)
                    out.append({"name": prof.instance_name, "type": prof.type_name,
                                "impl": props.get("implementation_id") or prof.type_name,
                                "language": props.get("language") or "", "state": state, "slave": idx,
                                "slave_name": slave_name, "ref": comp})
                except Exception:
                    continue
        return out

    ##
    # @~japanese
    # @brief 全ロボットの RTC の一覧を更新する
    # @~english
    # @brief Refreshes the RTC lists of all robots
    # @~
    def _refresh_inventory(self):
        with self._robot_lock:
            robots = ([self._robot] if self._robot is not None else []) + list(self._robotList)
        for r in robots:
            if not r.is_local and r.status == "dead":
                r.inventory = None
                continue
            try:
                inv = self._list_components(self._resolveManager(r.ipaddress, r.name))
            except Exception:
                r.inventory = None
                continue
            r.inventory = [{k: v for k, v in c.items() if k != "ref"} for c in inv]
            r.inventory_time = time.monotonic()
            if r.is_local and self._observer_rtc_enabled:
                try:
                    self._attach_observers(inv)
                except Exception:
                    self._rtcout.RTC_WARN("observer attach failed: " + traceback.format_exc())
            cg = r.cgroup or {}
            if not inv and cg.get("mem_usage_mb") is not None:
                # RTC がないときの使用量 (予約の土台)
                r.base_mem_mb = cg["mem_usage_mb"]

    ##
    # @~japanese
    # @brief RTC の一覧を定期的に更新するスレッドの本体
    # @~english
    # @brief Body of the thread that refreshes the RTC lists periodically
    # @~
    def _inventory_loop(self):
        while self._running:
            try:
                self._refresh_inventory()
            except Exception:
                self._rtcout.RTC_WARN("inventory refresh failed: " + traceback.format_exc())
            time.sleep(self._inventory_interval)

    ##
    # @~japanese
    # @brief ロボットの RTC の一覧を返す
    #
    # @param name ロボット名
    # @return RTC の一覧 (分からなければ None)
    # @~english
    # @brief Returns the RTC list of a robot
    #
    # @param name robot name
    # @return RTC list (None if unknown)
    # @~
    def _robot_inventory(self, name):
        robot = self._findConditionRobot(name)
        return robot.inventory if robot is not None else None

    ##
    # @~japanese
    # @brief 配置のプロファイル (placement.ProfileDB) を返す (計測が更新されていれば読み直す)
    #
    # @return placement.ProfileDB
    # @~english
    # @brief Returns the placement profiles (placement.ProfileDB), reloading them if measurements were updated
    #
    # @return placement.ProfileDB
    # @~
    def _profiles(self):
        sig = self._measured_signature() if (self._measure_enabled and self._measure_use) else None
        if self._profile_db is None or sig != self._profile_sig:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import RTCPlacement as pl
            root = self._conf.getProperty("snmp.placement.profile_dir", "placement")
            if self._measure_enabled and self._measure_use:
                root += "," + self._measure_dir
            self._profile_db = pl.ProfileDB(root, self._conf.getProperty("snmp.placement.environment", ""),
                                            prefer_measured=self._measure_use,
                                            min_samples=self._measure_min_samples)
            self._profile_sig = sig
        return self._profile_db

    ##
    # @~japanese
    # @brief 計測の保存先の placement.xml (ほかのロボットが保存したものも) の一覧と更新時刻を返す
    #
    # @return ((パス, 更新時刻), ...) (保存先がなければ None)
    # @~english
    # @brief Returns the list and modification times of the measured placement.xml files (including those saved by other robots)
    #
    # @return ((path, mtime), ...) (None if there is no output directory)
    # @~
    def _measured_signature(self):
        import glob
        try:
            return tuple(sorted((p, os.path.getmtime(p)) for p in
                                glob.glob(os.path.join(self._measure_dir, "**", "placement.xml"), recursive=True)))
        except OSError:
            return None

    # ------------------------------------------------------------------
    # マネージャによる実測値の計測と保存
    # ------------------------------------------------------------------
    ##
    # @~japanese
    # @brief マネージャによる実測値を定期的に集めて保存するスレッドの本体
    # @~english
    # @brief Body of the thread that periodically collects and saves the measurements made by the managers
    # @~
    def _measure_loop(self):
        while self._running:
            time.sleep(self._measure_save_interval)
            try:
                self._collect_measurements()
            except Exception:
                self._rtcout.RTC_WARN("measurement save failed: " + traceback.format_exc())

    ##
    # @~japanese
    # @brief 自分のロボットの計測の保存先のディレクトリを返す
    #
    # @return ディレクトリのパス
    # @~english
    # @brief Returns the output directory of measurements for this robot
    #
    # @return directory path
    # @~
    def _robot_measure_dir(self):
        import SlaveMeasureModule as ms
        return os.path.join(self._measure_dir, ms.safe_name(self._name))

    ##
    # @~japanese
    # @brief 自分のロボットの slave が書いた計測を集め、runs.json・placement.xml・SQLite に保存する
    #
    # @return 保存した placement.xml のリスト
    # @~english
    # @brief Collects the measurements written by the slaves of this robot and saves them to runs.json, placement.xml and SQLite
    #
    # @return list of saved placement.xml files
    # @~
    def _collect_measurements(self):
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import glob
        import SlaveMeasureModule as ms
        own = self._robot_measure_dir()
        runs_path = os.path.join(own, "runs.json")
        if self._measure_runs is None:
            try:
                with open(runs_path) as f:
                    self._measure_runs = json.load(f)
            except (OSError, ValueError):
                self._measure_runs = {}
        changed = []
        for path in sorted(glob.glob(os.path.join(self._measure_runtime_dir, "*.json"))):
            try:
                with open(path) as f:
                    data = json.load(f)
            except (OSError, ValueError):
                continue
            changed += ms.update_runs(self._measure_runs, self._name, data)
        if not changed:
            return []
        os.makedirs(own, exist_ok=True)
        tmp = runs_path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self._measure_runs, f, ensure_ascii=False, indent=1)
        os.replace(tmp, runs_path)
        store = getattr(self, "_store", None)
        if store is not None:
            store.record_measurements([self._measure_runs[k] for k in changed])
        env = self._conf.getProperty("snmp.placement.environment", "")
        groups = ms.aggregate(self._measure_runs, self._measure_min_samples, self._measure_max_runs,
                              self._measure_cpu_stat)
        touched = {(self._measure_runs[k].get("language") or "Python", self._measure_runs[k].get("type"))
                   for k in changed}
        saved = []
        for key in sorted(touched):
            agg = groups.get(key)
            if agg is None:
                continue        # 標本がまだ少ない
            d = os.path.join(own, ms.safe_name(agg["language"]), ms.safe_name(agg["type"]))
            os.makedirs(d, exist_ok=True)
            path = os.path.join(d, "placement.xml")
            with open(path + ".tmp", "w", encoding="utf-8") as f:
                f.write(ms.render_placement(agg, env, self._name))
            os.replace(path + ".tmp", path)
            value = (round(agg["cpu_value"], 1), round(agg["memory_mb"]["max"], 1))
            if self._measure_saved.get(key) != value:
                first = key not in self._measure_saved
                self._measure_saved[key] = value
                ports = ", ".join(f"{n} {p['bytes_per_msg']}B x {p['hz']}Hz"
                                  for n, p in sorted(agg["ports"].items()) if p["msgs"])
                self._log(f"measured {agg['type']} ({agg['language']}): cpu {value[0]}% ({agg['cpu_stat']}), "
                          f"memory {value[1]}MB, {agg['samples']} samples" + (f", ports {ports}" if ports else ""))
                if first:
                    self._event(self._name, "measurement_saved",
                                f"{agg['type']} cpu={value[0]} mem={value[1]}MB -> {path}")
            saved.append(path)
        return saved

    # ------------------------------------------------------------------
    # slave マネージャの終了の検知 (feature/processcallback の ProcessCallback)
    # ------------------------------------------------------------------
    ##
    # @~japanese
    # @brief マスターマネージャが slave を Process (launch_type: observer) で起動し、終了したら知らせるようにする
    #
    # OpenRTM-aist-Python の feature/processcallback (ProcessCallbackFactory) が必要。なければポーリングだけで検知する。
    #
    # @return 使えれば True
    # @~english
    # @brief Makes the master manager start slaves with Process (launch_type: observer) and notify when they exit
    #
    # Requires feature/processcallback (ProcessCallbackFactory) of OpenRTM-aist-Python. Without it, detection is done only by polling.
    #
    # @return True if available
    # @~
    def _install_process_observer(self):
        if not self._observer_enabled or self._observer_installed:
            return False
        factory_cls = getattr(OpenRTM_aist, "ProcessCallbackFactory", None)
        base = getattr(OpenRTM_aist, "ProcessCallbackBase", None)
        if factory_cls is None or base is None:
            self._log("process observer: OpenRTM has no ProcessCallbackFactory (feature/processcallback); "
                      "slave exits are detected by polling only")
            return False
        owner = self

        class SNMPProcessCallback(base):
            def callback(self, code, options):
                owner._on_slave_exit(code, options or {})

        factory = factory_cls.instance()
        if not factory.hasFactory("SNMPProcessCallback"):
            factory.addFactory("SNMPProcessCallback", SNMPProcessCallback)
        conf = self.mgr.getConfig()
        if not conf.getProperty("manager.launch_type"):
            conf.setProperty("manager.launch_type", "observer")
        if not conf.getProperty("manager.process_callback"):
            conf.setProperty("manager.process_callback", "SNMPProcessCallback")
        self._observer_installed = True
        self._log("process observer: slaves are launched with launch_type=observer, callback="
                  + conf.getProperty("manager.process_callback"))
        return True

    ##
    # @~japanese
    # @brief slave マネージャの RTC の名前を返す
    #
    # @param slave_name slave マネージャの名前
    # @return RTC の名前のリスト
    # @~english
    # @brief Returns the names of the RTCs in a slave manager
    #
    # @param slave_name name of the slave manager
    # @return list of RTC names
    # @~
    def _rtcs_in_slave(self, slave_name):
        inv = (self._robot.inventory if self._robot is not None else None) or []
        return [c["name"] for c in inv if c.get("slave_name") == slave_name]

    ##
    # @~japanese
    # @brief slave が終わったときに ProcessCallback から呼ばれる (slave を待つスレッド)。0 以外 (シグナルなら負) で終わったら異常終了として復旧を急ぐ
    #
    # 0 は正常な終了 (RTC がなくなった manager.shutdown_on_nortcs など)。RTC の一覧は数秒前のものなので、マイグレーションの直後に正常に終わった slave を異常と取り違えないよう、終了コードだけで判断する。
    #
    # @param code 終了コード
    # @param options slave の情報 (manager_name、pid、command、module)
    # @~english
    # @brief Called by ProcessCallback when a slave exits (on the thread waiting for the slave). A non-zero code (negative for signals) is treated as a crash and recovery is hastened
    #
    # 0 is a normal exit (manager.shutdown_on_nortcs when no RTCs are left, etc.). The RTC list is a few seconds old, so the decision is made only by the exit code so that a slave that exited normally right after a migration is not mistaken for a crash.
    #
    # @param code exit code
    # @param options information of the slave (manager_name, pid, command, module)
    # @~
    def _on_slave_exit(self, code, options):
        name = options.get("manager_name") or ""
        pid = options.get("pid")
        rtcs = self._rtcs_in_slave(name)
        detail = f"{name} pid={pid} code={code}" + (f" rtcs={','.join(rtcs)}" if rtcs else "")
        if code == 0:
            self._event(self._name, "slave_exited", detail)
            return
        self._event(self._name, "slave_crashed", detail)
        with open(self._logfile, "a") as f:
            f.write(f"{seconds_since_midnight():.6f}\tSLAVE_CRASHED\t{name}\t{code}\n")
        self._mark_crashed(self._name, rtcs)
        with self._robot_lock:
            ips = [r.ipaddress for r in self._robotList if r.status != "dead"]
        info = f"{self._name}|{','.join(rtcs)}"

        def send():
            for ip in ips:
                try:
                    self._send_trap_message(ip, "Slave Exited", info=info)
                except Exception:
                    pass
        threading.Thread(target=send, daemon=True).start()

    ##
    # @~japanese
    # @brief ほかのロボットから slave の異常終了の通知を受けたときの処理
    #
    # @param src_ip 送り元の IP アドレス
    # @param info 通知の内容
    # @~english
    # @brief Handles a notice of a slave crash from another robot
    #
    # @param src_ip source IP address
    # @param info contents of the notice
    # @~
    def _on_slave_exit_notice(self, src_ip, info):
        robot, _, names = (info or "").partition("|")
        rtcs = [n for n in names.split(",") if n]
        self._log(f"slave of {robot or src_ip} exited abnormally: {', '.join(rtcs) or '-'}")
        self._mark_crashed(robot or src_ip, rtcs)

    ##
    # @~japanese
    # @brief slave の異常終了を記録する (自動復旧が使う)
    #
    # @param robot ロボット名
    # @param rtcs その slave の RTC
    # @~english
    # @brief Records a slave crash (used by recovery)
    #
    # @param robot robot name
    # @param rtcs RTCs of the slave
    # @~
    def _mark_crashed(self, robot, rtcs):
        now = time.monotonic()
        for n in rtcs:
            self._crashed[n] = (robot, now)

        def refresh():
            try:
                self._refresh_inventory()     # RTC がなくなったことを、次のポーリングを待たずに反映する
            except Exception:
                pass
            self._recovery_wake.set()
        threading.Thread(target=refresh, daemon=True).start()

    ##
    # @~japanese
    # @brief 計画の RTC name (かそのインスタンス) の slave が最近異常終了したかを調べる
    #
    # @param name RTC の名前
    # @param now 現在の時刻
    # @param window 最近とみなす秒数
    # @param table 異常終了の記録 (省略時は slave の記録)
    # @return 最近異常終了していれば True
    # @~english
    # @brief Checks whether the slave of the RTC name (or its instance) in the plan crashed recently
    #
    # @param name name of the RTC
    # @param now current time
    # @param window seconds regarded as recent
    # @param table crash records (slave records if omitted)
    # @return True if it crashed recently
    # @~
    def _crash_hint(self, name, now, window=60.0, table=None):
        table = self._crashed if table is None else table
        inst = (self._recovery_where.get(name) or {}).get("instance")
        for key in (name, inst):
            hit = table.get(key) if key else None
            if hit is not None and now - hit[1] < window:
                return True
        return False

    # ------------------------------------------------------------------
    # コンポーネントオブザーバー (オブザーバ拡張マイグレーション)
    #   RTC 側: rtc.conf の manager.modules.preload に ComponentObserverConsumer を入れ、
    #           sdo.service.consumer.enabled_services: ALL (C++ の RTC は sdo_service.consumer_types: ALL)
    #   SNMPManager 側: RTC ごとにサーバーオブジェクト (OpenRTM::ComponentObserver) を起動し、
    #           RTC の SDO 設定に ServiceProfile (IDL:OpenRTM/ComponentObserver:1.0) として関連付ける
    # ------------------------------------------------------------------
    ##
    # @~japanese
    # @brief RTC の一覧の RTC に、コンポーネントオブザーバーを関連付ける (オブザーバ拡張マイグレーション)
    #
    # RTC 側は、rtc.conf の manager.modules.preload に ComponentObserverConsumer を入れ、sdo.service.consumer.enabled_services: ALL (C++ の RTC は sdo_service.consumer_types: ALL) にする。
    #
    # @param inv RTC の一覧
    # @~english
    # @brief Attaches component observers to the RTCs in the inventory (observer-extended migration)
    #
    # On the RTC side, ComponentObserverConsumer is added to manager.modules.preload in rtc.conf, with sdo.service.consumer.enabled_services: ALL (sdo_service.consumer_types: ALL for C++ RTCs).
    #
    # @param inv RTC list
    # @~
    def _attach_observers(self, inv):
        orb = self.mgr.getORB()
        current = {}
        for c in inv:
            try:
                current[orb.object_to_string(c["ref"])] = c
            except Exception:
                continue
        with self._observer_lock:
            known = dict(self._observers)
        for ior, entry in known.items():
            if ior not in current:
                self._detach_observer(ior, entry)
        for ior, c in current.items():
            if ior in known:
                continue
            entry = self._attach_observer(c["ref"], c["name"])
            if entry is not None:
                with self._observer_lock:
                    self._observers[ior] = entry

    ##
    # @~japanese
    # @brief RTC にサーバーオブジェクトを関連付ける。インターフェースは RTC 側の言語で違うので、順に試す
    #
    # - IDL:OpenRTM/ComponentObserver:1.0: OpenRTM-aist-Python の ComponentObserverConsumer
    # - IDL:omg.org/RTC/ComponentObserver:1.0: OpenRTM-aist C++ 2.1 の ComponentObserverConsumer.so
    #
    # @param rtc RTC の参照
    # @param instance インスタンス名
    # @return {"instance", "servant", "oid", "profile_id", ...}
    # @~english
    # @brief Attaches a server object to an RTC. The interface differs by the language of the RTC, so they are tried in order
    #
    # - IDL:OpenRTM/ComponentObserver:1.0: ComponentObserverConsumer of OpenRTM-aist-Python
    # - IDL:omg.org/RTC/ComponentObserver:1.0: ComponentObserverConsumer.so of OpenRTM-aist C++ 2.1
    #
    # @param rtc reference of the RTC
    # @param instance instance name
    # @return {"instance", "servant", "oid", "profile_id", ...}
    # @~
    def _attach_observer(self, rtc, instance):
        import uuid
        import SDOPackage
        poa = self.mgr.getPOA()
        errors = []
        for module, servant_cls in _observer_interfaces():
            status = self._observer_status
            if module == "RTC" and "HEARTBEAT" in status and "RTC_HEARTBEAT" not in status:
                status = status.replace("HEARTBEAT", "RTC_HEARTBEAT")    # FSM4RTC 版の名前
            servant = servant_cls(self, instance)
            oid = poa.activate_object(servant)
            ref = poa.id_to_reference(oid)
            props = [OpenRTM_aist.NVUtil.newNV("observed_status", status)]
            profile = SDOPackage.ServiceProfile(str(uuid.uuid4()), servant_cls.REPO_ID, props, ref)
            try:
                ok = rtc.get_configuration().add_service_profile(profile)
                if not ok:
                    errors.append(f"{servant_cls.REPO_ID}: add_service_profile returned false")
            except Exception as exc:
                ok = False
                errors.append(f"{servant_cls.REPO_ID}: {exc}")
            if ok:
                self._log(f"observer: attached to {instance} ({status}, {servant_cls.REPO_ID})")
                return {"instance": instance, "servant": servant, "oid": oid, "profile_id": profile.id,
                        "interface_type": servant_cls.REPO_ID}
            poa.deactivate_object(oid)
        # RTC 側に ComponentObserverConsumer がない (preload していない) と失敗する。一覧ごとに試し直さない
        self._log(f"observer: cannot attach to {instance} ({'; '.join(errors)})")
        return {"instance": instance, "servant": None, "oid": None, "profile_id": None}

    ##
    # @~japanese
    # @brief RTC からサーバーオブジェクトを外す
    #
    # @param ior RTC の IOR
    # @param entry 関連付けの記録
    # @~english
    # @brief Detaches a server object from an RTC
    #
    # @param ior IOR of the RTC
    # @param entry record of the attachment
    # @~
    def _detach_observer(self, ior, entry):
        with self._observer_lock:
            self._observers.pop(ior, None)
        if entry.get("oid") is not None:
            try:
                self.mgr.getPOA().deactivate_object(entry["oid"])
            except Exception:
                pass

    ##
    # @~japanese
    # @brief オブザーバーの通知を受ける (RTC のスレッドから CORBA で呼ばれる)。ERROR なら自動復旧を待たずに始める
    #
    # @param instance インスタンス名
    # @param kind 状態の種別
    # @param hint 詳細
    # @~english
    # @brief Receives a notification of the observer (called via CORBA from the thread of the RTC). On ERROR, recovery starts without waiting
    #
    # @param instance instance name
    # @param kind status kind
    # @param hint hint
    # @~
    def _on_observer_status(self, instance, kind, hint):
        if instance not in self._observer_noticed:
            self._observer_noticed.add(instance)
            self._log(f"observer: first notice from {instance}: {kind} {hint}")
        if kind != "RTC_STATUS" or not str(hint).startswith("ERROR"):
            return
        self._event(self._name, "rtc_error_notified", f"{instance} ({hint})")
        self._mark_error(self._name, instance)
        with self._robot_lock:
            ips = [r.ipaddress for r in self._robotList if r.status != "dead"]
        info = f"{self._name}|{instance}"

        def send():
            for ip in ips:
                try:
                    self._send_trap_message(ip, "RTC Error", info=info)
                except Exception:
                    pass
        threading.Thread(target=send, daemon=True).start()

    ##
    # @~japanese
    # @brief ほかのロボットから RTC のエラーの通知を受けたときの処理
    #
    # @param src_ip 送り元の IP アドレス
    # @param info 通知の内容
    # @~english
    # @brief Handles a notice of an RTC error from another robot
    #
    # @param src_ip source IP address
    # @param info contents of the notice
    # @~
    def _on_rtc_error_notice(self, src_ip, info):
        robot, _, instance = (info or "").partition("|")
        if instance:
            self._log(f"RTC {instance} on {robot or src_ip} reported ERROR (component observer)")
            self._mark_error(robot or src_ip, instance)

    ##
    # @~japanese
    # @brief RTC のエラーを記録する (自動復旧が使う)
    #
    # @param robot ロボット名
    # @param instance インスタンス名
    # @~english
    # @brief Records an RTC error (used by recovery)
    #
    # @param robot robot name
    # @param instance instance name
    # @~
    def _mark_error(self, robot, instance):
        self._error_notified[instance] = (robot, time.monotonic())

        def refresh():
            try:
                self._refresh_inventory()     # ERROR になったことを、次のポーリングを待たずに反映する
            except Exception:
                pass
            self._recovery_wake.set()
        threading.Thread(target=refresh, daemon=True).start()

    ##
    # @~japanese
    # @brief slave マネージャ 1 つ分のメモリを返す (snmp.placement.slave_overhead_mb の 言語:MB、なければ計測値)
    #
    # @param language 言語
    # @param prof プロファイル
    # @return メモリ (MB)
    # @~english
    # @brief Returns the memory of one slave manager (language:MB in snmp.placement.slave_overhead_mb, otherwise the measured value)
    #
    # @param language language
    # @param prof profile
    # @return memory (MB)
    # @~
    def _slave_overhead(self, language, prof=None):
        for part in self._conf.getProperty("snmp.placement.slave_overhead_mb", "").split(","):
            if ":" in part:
                lang, mb = part.rsplit(":", 1)
                if lang.strip() == language:
                    return float(mb)
        return prof.slave_overhead_mb if prof is not None else 0.0

    ##
    # @~japanese
    # @brief 待機モジュールの設定を返す
    #
    # @param config_data 構成ファイルの内容
    # @return 設定 (無効なら None)
    # @~english
    # @brief Returns the standby settings
    #
    # @param config_data contents of the configuration file
    # @return settings (None if disabled)
    # @~
    @staticmethod
    def _standby_cfg(config_data):
        sb = (config_data or {}).get("standby")
        return sb if isinstance(sb, dict) and sb.get("enabled", True) else None

    ##
    # @~japanese
    # @brief メモリの予約の設定を返す
    #
    # @param config_data 構成ファイルの内容
    # @return 設定 (無効なら None)
    # @~english
    # @brief Returns the memory reservation settings
    #
    # @param config_data contents of the configuration file
    # @return settings (None if disabled)
    # @~
    @staticmethod
    def _reservation_cfg(config_data):
        rs = (config_data or {}).get("reservation")
        return rs if isinstance(rs, dict) and rs.get("enabled", True) else None

    ##
    # @~japanese
    # @brief RTC 1 つの予約量を返す: reserve_mb > reservation.memory_mb (実装 ID か型名) > placement.xml の見込み (型名で引く) > default_mb
    #
    # @param rcfg メモリの予約の設定
    # @param impl 実装 ID
    # @param type_name 型名
    # @param language 言語
    # @param entry 計画の項目
    # @return 予約量 (MB)
    # @~english
    # @brief Returns the reservation of one RTC: reserve_mb > reservation.memory_mb (implementation ID or type name) > estimate in placement.xml (by type name) > default_mb
    #
    # @param rcfg memory reservation settings
    # @param impl implementation ID
    # @param type_name type name
    # @param language language
    # @param entry entry of the plan
    # @return reservation (MB)
    # @~
    def _reserve_mb(self, rcfg, impl, type_name, language, entry=None):
        if entry is not None and entry.get("reserve_mb") is not None:
            return float(entry["reserve_mb"])
        table = rcfg.get("memory_mb", {})
        for key in (impl, type_name):
            if key in table:
                return float(table[key])
        for lang in ([language] if language else []) + ["Python", "C++"]:
            prof = self._profiles().get(type_name, lang)
            if prof is not None:
                return float(prof.memory_mb)
        return float(rcfg.get("default_mb", 0))

    ##
    # @~japanese
    # @brief ロボットで動いている RTC の予約の合計を返す (slave マネージャの分を含む。RTC が終われば外れる)
    #
    # @param rcfg メモリの予約の設定
    # @param robot ロボット名
    # @return 予約の合計 (MB)
    # @~english
    # @brief Returns the total reservation of the RTCs running on a robot (including slave managers; released when an RTC ends)
    #
    # @param rcfg memory reservation settings
    # @param robot robot name
    # @return total reservation (MB)
    # @~
    def _reserved_on(self, rcfg, robot):
        total, slaves = 0.0, {}
        for c in robot.inventory or []:
            total += self._reserve_mb(rcfg, c.get("impl"), c["type"], c.get("language"))
            if c.get("slave"):
                slaves[c["slave"]] = c.get("language") or "Python"
        total += sum(self._slave_overhead(lang) for lang in slaves.values())
        return total

    ##
    # @~japanese
    # @brief get_loadable_modules() のモジュールの情報を返す (マネージャごとにキャッシュする)
    #
    # @param manager_name ロボット名
    # @param module モジュール名
    # @return {type_name, language}
    # @~english
    # @brief Returns the module information from get_loadable_modules() (cached per manager)
    #
    # @param manager_name robot name
    # @param module module name
    # @return {type_name, language}
    # @~
    def _module_info(self, manager_name, module):
        import RTCPlacement as pl
        cache = self.__dict__.setdefault("_module_cache", {})
        if manager_name not in cache or module not in cache[manager_name]:
            try:
                mods = [self._nvlist_to_dict(m.properties) for m in self._mgr_ref(manager_name).get_loadable_modules()]
                cache[manager_name] = pl.loadable_index(mods)
            except Exception:
                cache.setdefault(manager_name, {})
        return cache[manager_name].get(module, {})

    ##
    # @~japanese
    # @brief robot_names の順に、型が module の非アクティブな RTC (待機モジュール) を探す
    #
    # @param module モジュール名
    # @param robot_names ロボット名のリスト
    # @param used_refs 使用済みの RTC
    # @param exclude_names 除くインスタンス名
    # @return (ロボット名, RTC) (なければ None)
    # @~english
    # @brief Searches robot_names in order for an inactive RTC of type module (standby module)
    #
    # @param module module name
    # @param robot_names list of robot names
    # @param used_refs RTCs already used
    # @param exclude_names instance names to exclude
    # @return (robot name, RTC) (None if not found)
    # @~
    def _find_standby(self, module, robot_names, used_refs, exclude_names):
        for name in robot_names:
            mgr = self._migration_managers.get(name)
            if mgr is None:
                continue
            for c in self._list_components(mgr):
                if c["state"] != "INACTIVE" or module not in (c["impl"], c["type"]) or c["name"] in exclude_names:
                    continue
                if any(c["ref"]._is_equivalent(u) for u in used_refs):
                    continue
                return name, c
        return None

    ##
    # @~japanese
    # @brief 生成する前に、予約を含めてメモリが足りるかを確かめる (enforce: true なら足りないと失敗)
    #
    # @param rcfg メモリの予約の設定
    # @param manager_name ロボット名
    # @param entry 計画の項目
    # @return 必要な量 (MB)
    # @~english
    # @brief Checks before creation whether the memory including reservations is sufficient (fails if insufficient with enforce: true)
    #
    # @param rcfg memory reservation settings
    # @param manager_name robot name
    # @param entry entry of the plan
    # @return required amount (MB)
    # @~
    def _check_reservation(self, rcfg, manager_name, entry):
        import RTCPlacement as pl
        robot = self._findConditionRobot(manager_name)
        cg = getattr(robot, "cgroup", None) if robot is not None else None
        module = pl.module_name_of(entry["create"])
        info = self._module_info(manager_name, module)
        need = self._reserve_mb(rcfg, module, info.get("type_name") or module, info.get("language"), entry)
        if cg and cg.get("mem_limit_mb"):
            margin = float(self._conf.getProperty("snmp.placement.memory_margin_mb", "32"))
            committed = (robot.base_mem_mb or 0.0) + self._reserved_on(rcfg, robot) + \
                self._pending_reserve.get(manager_name, 0.0)
            free = cg["mem_limit_mb"] - margin - max(cg["mem_usage_mb"], committed)
            if need > free:
                msg = (f"memory reservation for {entry['name']} ({need:.1f}MB) exceeds free memory of "
                       f"{manager_name} ({free:.1f}MB)")
                if rcfg.get("enforce", False):
                    raise RuntimeError(msg)
                self._log("warning: " + msg)
        self._pending_reserve[manager_name] = self._pending_reserve.get(manager_name, 0.0) + need
        return need

    ##
    # @~japanese
    # @brief 配置プラグインの結果を受け取り、制約 (置けるロボット・空き容量) を満たすか確かめる
    #
    # @param pl placement モジュール
    # @param plan 計画
    # @param items 配置する RTC
    # @param robots ロボット
    # @param edges 接続
    # @param primary 主ロボットの名前
    # @return {RTC 名: ロボット名}
    # @~english
    # @brief Receives the result of a placement plugin and checks that it satisfies the constraints (allowed robots and free capacity)
    #
    # @param pl placement module
    # @param plan plan
    # @param items RTCs to place
    # @param robots robots
    # @param edges connections
    # @param primary name of the primary robot
    # @return {RTC name: robot name}
    # @~
    def _plugin_placement(self, pl, plan, items, robots, edges, primary):
        name = plan["placement_plugin"]
        assign = self.plugins().placement(name, items, robots, edges, primary, plan.get("placement_args", {}))
        if not isinstance(assign, dict):
            raise pl.PlacementError(f"placement plugin {name} returned {type(assign).__name__}, not dict")
        reasons = []
        for it in items:
            r = assign.get(it.name)
            if r is None:
                reasons.append(f"{it.name} が割り当てられていない")
            elif r not in it.candidates:
                reasons.append(f"{it.name} を置けないロボット {r} に割り当てた (置けるのは {', '.join(it.candidates)})")
        if reasons:
            raise pl.PlacementError(f"placement plugin {name} の結果が不正です", reasons)
        result = pl._evaluate(assign, items, robots, edges, primary)
        if result is None:
            raise pl.PlacementError(f"placement plugin {name} の結果はリソースの制限を超えます",
                                    pl.capacity_report(items, robots))
        self._log(f"placement by plugin {name}")
        return result

    ##
    # @~japanese
    # @brief NVList を辞書にする
    #
    # @param nvlist NVList
    # @return 辞書
    # @~english
    # @brief Converts an NVList into a dictionary
    #
    # @param nvlist NVList
    # @return dictionary
    # @~
    @staticmethod
    def _nvlist_to_dict(nvlist):
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, nvlist)
        return {k: prop.getProperty(k) for k in prop.propertyNames()}

    ##
    # @~japanese
    # @brief 既存の RTC を探す
    #
    # @param name インスタンス名
    # @param mgr マネージャの参照
    # @return RTC の参照 (なければ None)
    # @~english
    # @brief Finds an existing RTC
    #
    # @param name instance name
    # @param mgr manager reference
    # @return reference of the RTC (None if not found)
    # @~
    def _find_existing(self, name, mgr):
        try:
            return self.getComponent(name, mgr)
        except RuntimeError as exc:
            if str(exc).startswith("RTC not found:"):
                return None
            raise

    ##
    # @~japanese
    # @brief 既存の RTC を探し、ない RTC を生成する (繰り返しても安全)
    #
    # 待機モジュール (standby) が有効なら、生成する前に同じ型の非アクティブな RTC を探して使う。メモリの予約 (reservation) が有効なら、生成する前に予約を含めた空きを確かめる。
    #
    # @param config_data 計画
    # @~english
    # @brief Resolves existing RTCs and creates missing RTCs; safe to repeat
    #
    # If standby is enabled, an inactive RTC of the same type is searched for and used before creation. If reservation is enabled, the free memory including reservations is checked before creation.
    #
    # @param config_data plan
    # @~
    def createComponent(self, config_data):
        import RTCPlacement as pl
        self._port_module = {}
        self._migration_components = {}
        self._plan_assign = {}
        self._pending_reserve = {}
        self._created_now = set()
        self._plan_instances = {}
        sb = None if config_data.get("_no_standby") else self._standby_cfg(self._current_config)
        if sb is None and config_data.get("_force_standby"):
            sb = {"scope": "any"}
        rcfg = self._reservation_cfg(self._current_config)
        order = [n for n in self._current_config.get("managers", {}) if n in self._migration_managers]
        plan_names = {self._instance_name(e) for e in config_data["components"]}
        for entry in config_data["components"]:
            name = entry["name"]
            manager_name = entry["manager"]
            mgr = self._mgr_ref(manager_name)
            actual_name = self._instance_name(entry)
            self._last_instance = actual_name
            comp = None
            if entry.get("standby_instance"):
                # 自動配置で選んだ待機モジュール
                comp = self._find_existing(entry["standby_instance"], mgr)
                if comp is not None:
                    self._last_instance = entry["standby_instance"]
                    self._log(f"using standby {entry['standby_instance']} on {manager_name} for {name}")
                    self._event(manager_name, "standby_used", f"{name} -> {entry['standby_instance']}")
            if comp is None:
                comp = self._find_existing(actual_name, mgr)
            if comp is None and entry.get("create") and sb is not None and entry.get("standby", True):
                scope = [manager_name] + ([n for n in order if n != manager_name] if sb.get("scope", "any") == "any" else [])
                found = self._find_standby(pl.module_name_of(entry["create"]), scope,
                                           list(self._migration_components.values()) + list(self._removing_refs),
                                           plan_names)
                if found is not None:
                    manager_name, info = found
                    comp = info["ref"]
                    self._last_instance = info["name"]
                    self._log(f"using standby {info['name']} on {manager_name} for {name}")
                    self._event(manager_name, "standby_used", f"{name} -> {info['name']}")
            if comp is None:
                if not entry.get("create"):
                    raise RuntimeError("Existing RTC not found: " + actual_name)
                if rcfg is not None:
                    self._check_reservation(rcfg, manager_name, entry)
                comp = mgr.create_component(entry["create"])
                if comp is None or CORBA.is_nil(comp):
                    raise RuntimeError("RTC creation failed: " + name)
                with open(self._logfile, "a") as f:
                    f.write(f"{seconds_since_midnight():.6f}\tRTC_STATUS\t{name}\t1\n")
                self._log(f"created {actual_name} on {manager_name}")
                self._created_now.add(name)
                if entry.get("create"):
                    self._port_module[name] = pl.module_name_of(entry["create"])
            self._migration_components[name] = comp
            self._plan_assign[name] = manager_name
            self._plan_instances[name] = self._last_instance

    ##
    # @~japanese
    # @brief 計画の RTC をアクティブにする
    #
    # @param config_data 計画
    # @~english
    # @brief Activates the RTCs of the plan
    #
    # @param config_data plan
    # @~
    def activateComp(self, config_data):
        for entry in config_data["components"]:
            if not entry.get("activate", False):
                continue
            comp = self._migration_components[entry["name"]]
            # Avoid reactivating already active RTCs on repeated plans.
            # (この計画で生成した RTC は非アクティブなので、状態の問い合わせを省く)
            if entry["name"] not in self._created_now:
                ecs = comp.get_owned_contexts()
                if ecs and ecs[0].get_component_state(comp) == RTC.ACTIVE_STATE:
                    continue
            result = OpenRTM_aist.CORBA_RTCUtil.activate(comp)
            if result != RTC.RTC_OK:
                raise RuntimeError(f"RTC activation failed: {entry['name']} ({result})")

    ##
    # @~japanese
    # @brief 接続するポートの参照と名前を返す
    #
    # snmp.port_cache.enabled (既定 YES) なら、RTC ごとにポートの参照を一度だけ取ってキャッシュする。
    # - 同じモジュールの RTC を一度見ていれば、get_ports() 1 回で、ポートの並び順 (インデックス) から取る
    # - 初めてのモジュールは get_component_profile() 1 回で、全ポートの名前と参照を取り、並び順を覚える
    #
    # キャッシュを使わない場合は、従来どおりエンドポイントごとに get_component_profile() と get_port_by_name() (ポートの数だけ get_port_profile()) を呼ぶ。
    #
    # @param endpoint 接続の端 ({"component", "port", ...})
    # @return (ポートの参照, ポートの名前)
    # @~english
    # @brief Returns the reference and name of a port to connect
    #
    # With snmp.port_cache.enabled (default YES), port references are obtained once per RTC and cached.
    # - If an RTC of the same module has been seen, they are taken with one get_ports() call by the port order (index)
    # - For a new module, the names and references of all ports are obtained with one get_component_profile() call and the order is remembered
    #
    # Without the cache, get_component_profile() and get_port_by_name() (get_port_profile() for each port) are called for each endpoint as before.
    #
    # @param endpoint endpoint of a connection ({"component", "port", ...})
    # @return (port reference, port name)
    # @~
    def _getMigrationPort(self, endpoint):
        comp = self._migration_components[endpoint["component"]]
        port_name = endpoint["port"]
        if not self._port_cache_enabled:
            # 従来の方法 (CORBA_RTCUtil.get_port_by_name と同じ手順。呼び出しの数を数える)
            instance_name = comp.get_component_profile().instance_name
            full_name = port_name if port_name.startswith(instance_name + ".") else instance_name + "." + port_name
            self._corba_calls += 2
            port = None
            for p in comp.get_ports():
                self._corba_calls += 1
                if p.get_port_profile().name == full_name:
                    port = p
                    break
            if port is None or CORBA.is_nil(port):
                raise RuntimeError("Port not found: " + full_name)
            return port, full_name
        entry = self._ports_of(comp, self._port_module.get(endpoint["component"]))
        short = port_name.split(".", 1)[1] if port_name.startswith(entry["instance"] + ".") else port_name
        port = entry["ports"].get(short)
        if port is None:
            # 並び順が変わった (別のバージョンの RTC など): 取り直す
            self._forget_ports(comp)
            entry = self._ports_of(comp, None)
            port = entry["ports"].get(short)
            if port is None:
                raise RuntimeError(f"Port not found: {entry['instance']}.{short}")
        return port, f"{entry['instance']}.{short}"

    ##
    # @~japanese
    # @brief キャッシュのキー (RTC の IOR) を返す
    #
    # @param comp RTC の参照
    # @return IOR
    # @~english
    # @brief Returns the cache key (IOR of the RTC)
    #
    # @param comp reference of the RTC
    # @return IOR
    # @~
    def _comp_key(self, comp):
        return self.mgr.getORB().object_to_string(comp)

    ##
    # @~japanese
    # @brief RTC のポートのキャッシュを消す
    #
    # @param comp RTC の参照
    # @~english
    # @brief Clears the port cache of an RTC
    #
    # @param comp reference of the RTC
    # @~
    def _forget_ports(self, comp):
        with self._port_cache_lock:
            self._port_cache.pop(self._comp_key(comp), None)

    ##
    # @~japanese
    # @brief RTC のポートの参照と名前を返す (キャッシュする)
    #
    # @param comp RTC の参照
    # @param module モジュール名
    # @return ポートの記録
    # @~english
    # @brief Returns the port references and names of an RTC (cached)
    #
    # @param comp reference of the RTC
    # @param module module name
    # @return record of the ports
    # @~
    def _ports_of(self, comp, module):
        key = self._comp_key(comp)
        with self._port_cache_lock:
            cached = self._port_cache.get(key)
        if cached is not None:
            return cached
        entry = None
        names = self._port_index.get(module) if module else None
        if names is not None:
            # 同じモジュールの RTC を前に見ている: get_ports() の並び順で取る (プロファイルを取らない)
            ports = comp.get_ports()
            self._corba_calls += 1
            if len(ports) == len(names):
                instance = None
                if self._port_cache_verify:
                    pp = ports[0].get_port_profile()
                    self._corba_calls += 1
                    instance = pp.name.split(".", 1)[0] if pp.name.split(".", 1)[-1] == names[0] else None
                else:
                    instance = self._instance_of(comp)
                if instance is not None:
                    entry = {"instance": instance, "ports": dict(zip(names, ports))}
        if entry is None:
            prof = comp.get_component_profile()
            self._corba_calls += 1
            shorts = [pp.name.split(".", 1)[1] if "." in pp.name else pp.name for pp in prof.port_profiles]
            entry = {"instance": prof.instance_name,
                     "ports": {n: pp.port_ref for n, pp in zip(shorts, prof.port_profiles)}}
            if module:
                self._port_index[module] = shorts
        with self._port_cache_lock:
            self._port_cache[key] = entry
        return entry

    ##
    # @~japanese
    # @brief 生成したばかりの RTC のインスタンス名を返す (計画から分かるので CORBA で問い合わせない)
    #
    # @param comp RTC の参照
    # @return インスタンス名
    # @~english
    # @brief Returns the instance name of a newly created RTC (known from the plan, so CORBA is not queried)
    #
    # @param comp reference of the RTC
    # @return instance name
    # @~
    def _instance_of(self, comp):
        for name, c in self._migration_components.items():
            if c is comp:
                return self._planned_instance.get(name, name)
        prof = comp.get_component_profile()
        self._corba_calls += 1
        return prof.instance_name

    ##
    # @~japanese
    # @brief 同じ名前の接続が既にあるかを調べる
    #
    # @param source 接続元のポート
    # @param target 接続先のポート
    # @param name 接続の名前
    # @return あれば True
    # @~english
    # @brief Checks whether a connector with the same name already exists
    #
    # @param source source port
    # @param target target port
    # @param name connector name
    # @return True if it exists
    # @~
    @staticmethod
    def _connector_exists(source, target, name):
        # Compare object references, not port names: after a migration the
        # moved RTC keeps its instance name, so the old and new ports share
        # the same name while being different objects.
        for profile in source.get_connector_profiles():
            if profile.name != name:
                continue
            for p in profile.ports:
                try:
                    if p._is_equivalent(target):
                        return True
                except Exception:
                    continue
        return False

    ##
    # @~japanese
    # @brief 計画のポートを接続する
    #
    # @param config_data 計画
    # @~english
    # @brief Connects the ports of the plan
    #
    # @param config_data plan
    # @~
    def connectPort(self, config_data):
        self._planned_instance = {e["name"]: self._instance_name(e) for e in config_data["components"]}
        for entry in config_data["connections"]:
            for attempt in (0, 1):
                source, source_name = self._getMigrationPort(entry["source"])
                target, target_name = self._getMigrationPort(entry["target"])
                try:
                    # この計画で生成した RTC には接続がまだないので、既存の接続の確認を省く
                    new = entry["source"]["component"] in self._created_now or \
                        entry["target"]["component"] in self._created_now
                    if not new and self._connector_exists(source, target, entry["name"]):
                        break
                    prop = OpenRTM_aist.Properties()
                    for key, value in entry.get("properties", {}).items():
                        prop.setProperty(str(key), str(value))
                    result = OpenRTM_aist.CORBA_RTCUtil.connect(entry["name"], prop, source, target)
                except (CORBA.OBJECT_NOT_EXIST, CORBA.TRANSIENT, CORBA.COMM_FAILURE):
                    if attempt or not self._port_cache_enabled:
                        raise
                    # キャッシュした参照が古い (RTC が作り直された): 取り直してもう一度
                    for ep in (entry["source"], entry["target"]):
                        self._forget_ports(self._migration_components[ep["component"]])
                    continue
                if result != RTC.RTC_OK:
                    raise RuntimeError(f"Port connection failed: {entry['name']} ({result})")
                if not self._port_cache_enabled:
                    # 従来はログのためにポートのプロファイルを取り直していた
                    source_name, target_name = source.get_port_profile().name, target.get_port_profile().name
                    self._corba_calls += 2
                self._log(f"connected {source_name} -> {target_name} ({entry['name']})")
                break

    ##
    # @~japanese
    # @brief plan["remove"] の RTC を非アクティブにし、接続を切り、削除する
    #
    # 新しい RTC を生成・接続・アクティブにした後に行うので、古い RTC が消える前にデータの流れが切り替わる。ない RTC は飛ばすので、同じマイグレーションを繰り返しても害がない。
    #
    # @param plan 計画
    # @~english
    # @brief Deactivates, disconnects and deletes the RTCs listed in plan["remove"]
    #
    # Runs after the new RTCs are created, connected and activated, so the data flow is switched over before the old RTCs disappear. Missing RTCs are skipped, which keeps a repeated migration harmless.
    #
    # @param plan plan
    # @~
    def removeComponents(self, plan):
        for entry, comp in self._resolve_removals(plan):
            # Never delete an RTC that this plan itself uses.
            if any(comp._is_equivalent(used) for used in self._migration_components.values()):
                raise RuntimeError(f"Refusing to remove {entry['name']}: it is part of the new configuration")
            self._remove_one(entry, comp)

    ##
    # @~japanese
    # @brief 計画の remove の RTC を探す
    #
    # @param plan 計画
    # @return [(項目, RTC の参照)]
    # @~english
    # @brief Resolves the RTCs in "remove" of the plan
    #
    # @param plan plan
    # @return [(entry, reference of the RTC)]
    # @~
    def _resolve_removals(self, plan):
        out = []
        for entry in plan.get("remove", []):
            mgr = self._migration_managers.get(entry["manager"])
            if mgr is None:
                # 止まっているロボットの RTC は消せない (ロボットごと止まっている)
                self._log(f"skip removing {entry['name']}: {entry['manager']} is down")
                continue
            comp = self._find_existing(entry["name"], mgr)
            if comp is not None:
                out.append((entry, comp))
        return out

    ##
    # @~japanese
    # @brief 移動元の RTC の終了を、新しい RTC の生成・接続と並行して別スレッドで行う
    #
    # 先に消す RTC を決め、計画が使う RTC (同じロボットの同じ名前) を消さないことを確かめてから始める。返り値の関数を呼ぶと、終わるのを待って、失敗していれば例外を投げる。
    #
    # @param plan 計画
    # @return 終わるのを待つ関数 (かかった秒数を返す)
    # @~english
    # @brief Terminates the source RTCs in another thread in parallel with creating and connecting the new RTCs
    #
    # The RTCs to remove are decided first, and it starts after confirming that no RTC used by the plan (same name on the same robot) is removed. Calling the returned function waits for completion and raises an exception on failure.
    #
    # @param plan plan
    # @return function that waits for completion (returns the elapsed seconds)
    # @~
    def _start_parallel_removal(self, plan):
        removals = self._resolve_removals(plan)
        used = {(e.get("manager"), self._instance_name(e)) for e in plan.get("components", [])}
        for entry, _ in removals:
            if (entry["manager"], entry["name"]) in used:
                raise RuntimeError(f"Refusing to remove {entry['name']}: it is part of the new configuration")
        self._removing_refs = [comp for _, comp in removals]
        if not removals:
            return lambda: 0.0
        started = time.perf_counter()
        pool = ThreadPoolExecutor(max_workers=max(1, len(removals)), thread_name_prefix="remove")
        futures = [pool.submit(self._remove_one, entry, comp) for entry, comp in removals]
        self._log(f"removing {', '.join(e['name'] for e, _ in removals)} in parallel")

        def join():
            try:
                for f in futures:
                    f.result()
            finally:
                pool.shutdown(wait=True)
                self._removing_refs = []
            return time.perf_counter() - started
        return join

    ##
    # @~japanese
    # @brief RTC を 1 つ非アクティブにし、接続を切り、削除する
    #
    # @param entry 計画の項目
    # @param comp RTC の参照
    # @~english
    # @brief Deactivates, disconnects and deletes one RTC
    #
    # @param entry entry of the plan
    # @param comp reference of the RTC
    # @~
    def _remove_one(self, entry, comp):
        for ec in comp.get_owned_contexts():
            try:
                if ec.get_component_state(comp) == RTC.ACTIVE_STATE:
                    ec.deactivate_component(comp)
            except Exception:
                self._rtcout.RTC_WARN("Deactivation failed: " + traceback.format_exc())
        for port in comp.get_ports():
            try:
                port.disconnect_all()
            except Exception:
                self._rtcout.RTC_WARN("Disconnect failed: " + traceback.format_exc())
        result = comp.exit()
        if result != RTC.RTC_OK:
            raise RuntimeError(f"RTC exit failed: {entry['name']} ({result})")
        with open(self._logfile, "a") as f:
            f.write(f"{seconds_since_midnight():.6f}\tRTC_STATUS\t{entry['name']}\t0\n")
        self._forget_ports(comp)
        self._log(f"removed {entry['name']} from {entry['manager']}")

    ##
    # @~japanese
    # @brief 計画を適用する (生成・接続・アクティブ化・削除)
    #
    # @param config_data 構成ファイルの内容
    # @param plan 計画
    # @param label ログに出す名前
    # @~english
    # @brief Applies a plan (create, connect, activate, remove)
    #
    # @param config_data contents of the configuration file
    # @param plan plan
    # @param label name shown in logs
    # @~
    def _apply_plan(self, config_data, plan, label):
        with self._migration_lock:
            if self._migration:
                raise RuntimeError("Another RTC configuration operation is running")
            self._migration = True
        start = time.perf_counter()
        try:
            # 起動時は全ロボットがそろっていること。マイグレーションでは止まったロボットを飛ばす
            self.getManagerRef(config_data, allow_down=label not in ("startup", "standby"))
            if self._down_managers:
                self._log(f"{label}: robots down: {', '.join(self._down_managers)}")
            self._current_config = config_data
            parallel = plan.get("parallel_remove", self._parallel_remove_default) and bool(plan.get("remove"))
            join_removal = self._start_parallel_removal(plan) if parallel else None
            calls_before = self._corba_calls
            try:
                self.createComponent(plan)
                create_finish = time.perf_counter()
                self.connectPort(plan)
                connect_finish = time.perf_counter()
                self.activateComp(plan)
                activate_finish = time.perf_counter()
            finally:
                if join_removal is not None:
                    remove_time = join_removal()   # 失敗していればここで例外になる
            if join_removal is None:
                self.removeComponents(plan)
                remove_time = time.perf_counter() - activate_finish
            for name, robot in self._plan_assign.items():
                self._recovery_where[name] = {"robot": robot, "instance": self._plan_instances.get(name, name)}
            self._last_plan_applied = time.monotonic()
            end = time.perf_counter()
            with open(self._logfile, "a") as f:
                f.write(f"{seconds_since_midnight():.6f}\t{label}Time:{end-start}:{create_finish-start}:{connect_finish-create_finish}:{end-activate_finish}\t\t\n")
            if plan.get("connections") or plan.get("remove"):
                self._log(f"{label} timing: total {end-start:.3f}s (create {create_finish-start:.3f}s, "
                          f"connect {connect_finish-create_finish:.3f}s, activate {activate_finish-connect_finish:.3f}s, "
                          f"remove {remove_time:.3f}s{' in parallel' if parallel else ''}); "
                          f"port lookups {self._corba_calls - calls_before} CORBA calls"
                          f"{'' if self._port_cache_enabled else ' (port cache off)'}")
        finally:
            self._removing_refs = []
            with self._migration_lock:
                self._migration = False

    ##
    # @~japanese
    # @brief ネットワークの状態のイベントでマイグレーションの計画を適用する
    #
    # @return 適用したら True
    # @~english
    # @brief Applies the migration plan on a network condition event
    #
    # @return True if applied
    # @~
    def migration(self):
        config_data = self.loadMigrationConfig()
        plan = config_data.get("migration")
        if plan is None:
            plan = {"components": config_data.get("components", []),
                    "connections": config_data.get("connections", [])}
        if plan.get("plugin") is not None:
            # 計画の代わりにプラグインの処理を実行する。
            # 構成変更の排他はプラグインが呼ぶ ctx.apply_plan() (= _apply_plan) ごとに行う
            # (ここでフラグを立てると、プラグインの apply_plan が自分自身と重なって失敗する)
            ok = bool(self.plugins().action(plan["plugin"], plan.get("args", {})))
            if not ok:
                raise RuntimeError(f"migration plugin {plan['plugin']} reported failure")
            return True
        if not plan.get("components") and not plan.get("connections") and not plan.get("remove"):
            return False
        if plan.get("mode") == "auto":
            # 移動先を今の状態から決め直す (移動元と止まっているロボットを除く)
            exclude = plan.get("exclude") or plan.get("from") or []
            exclude = [exclude] if isinstance(exclude, str) else list(exclude)
            plan, _ = self._auto_plan(config_data, plan, exclude=exclude, strict=False)
        self._apply_plan(config_data, plan, "Migration")
        self._event(self._name, "migration_placement",
                    ", ".join(f"{k}@{v}" for k, v in self._plan_assign.items()))
        return True

    ##
    # @~japanese
    # @brief SNMP のトラップを受けたときの処理 (pysnmp のコールバック)
    #
    # @param snmpEngine SNMP エンジン
    # @param stateRef 状態の参照
    # @param contextEngineId コンテキストのエンジン ID
    # @param contextName コンテキストの名前
    # @param varBinds 変数のバインディング
    # @param cbCtx コールバックのコンテキスト
    # @~english
    # @brief Handles a received SNMP trap (callback of pysnmp)
    #
    # @param snmpEngine SNMP engine
    # @param stateRef state reference
    # @param contextEngineId context engine ID
    # @param contextName context name
    # @param varBinds variable bindings
    # @param cbCtx callback context
    # @~
    def trap_callback(self, snmpEngine, stateRef, contextEngineId, contextName, varBinds, cbCtx):
        try:
            # PySNMP 7.x dispatcher exposes get_transport_info().
            src_ip = snmpEngine.message_dispatcher.get_transport_info(stateRef)[1][0]
            oid_dict = {str(oid): val for oid, val in varBinds}
            if self.TrapNameOid not in oid_dict:
                return
            message = str(oid_dict[self.TrapNameOid])
            if message in ('Register Device', 'Register Device Reply'):
                if self._discovery_mode != 'trap':
                    return
                name = str(oid_dict.get(self.TrapInfoOid, '')).strip()
                if name:
                    self._registerRobot(src_ip, name)
                    if message == 'Register Device':
                        threading.Thread(target=self.send_snmp_trap_reply,
                                         args=(src_ip,), daemon=True).start()
            elif message == 'Heartbeat':
                self._on_heartbeat(src_ip)
            elif message == 'Startup Query':
                self._on_startup_query(src_ip)
            elif message == 'Startup Pending':
                self._on_startup_pending(src_ip)
            elif message == 'RTC Error':
                self._on_rtc_error_notice(src_ip, str(oid_dict.get(self.TrapInfoOid, '')).strip())
            elif message == 'Slave Exited':
                self._on_slave_exit_notice(src_ip, str(oid_dict.get(self.TrapInfoOid, '')).strip())
            elif message == 'Startup Completed':
                self._on_startup_notice(src_ip, str(oid_dict.get(self.TrapInfoOid, '')).strip())
            elif message == 'WiFi Low':
                # Avoid blocking the asyncio trap receiver with migration checks.
                threading.Thread(target=self.check_migration_conditions,
                                 daemon=True).start()
        except Exception:
            self._rtcout.RTC_ERROR(traceback.format_exc())

    ##
    # @~japanese
    # @brief SNMP のトラップ (通知) を送る (非同期)
    #
    # @param target_ip 送り先の IP アドレス
    # @param message メッセージ
    # @param community コミュニティ名
    # @param port ポート番号
    # @param shared 共有の SNMP エンジンを使うか
    # @param info 追加の情報
    # @~english
    # @brief Sends an SNMP trap (notification) asynchronously
    #
    # @param target_ip destination IP address
    # @param message message
    # @param community community name
    # @param port port number
    # @param shared whether to use the shared SNMP engine
    # @param info additional information
    # @~
    async def _send_notification_async(self, target_ip, message, community, port, shared=False, info=None):
        engine = self._shared_engine() if shared else SnmpEngine()
        try:
            target = await UdpTransportTarget.create((target_ip, port))
            if self._configured_own_ip:
                # 受け手は送り元の IP でロボットを見分けるので、自分の IP から送る
                target.set_local_address((self._configured_own_ip, 0))
            return await send_notification(
                engine,
                CommunityData(community),
                target,
                ContextData(), 'trap',
                NotificationType(ObjectIdentity('1.3.6.1.6.3.1.1.5.1')).add_varbinds(
                    (self.TrapNameOid, OctetString(message)),
                    (self.TrapInfoOid, OctetString(self._name if info is None else info))
                )
            )
        finally:
            if not shared:
                engine.close_dispatcher()

    ##
    # @~japanese
    # @brief SNMP のトラップでメッセージを送る
    #
    # @param target_ip 送り先の IP アドレス
    # @param message メッセージ
    # @param community コミュニティ名
    # @param port ポート番号
    # @param info 追加の情報
    # @return 送れたら True
    # @~english
    # @brief Sends a message by an SNMP trap
    #
    # @param target_ip destination IP address
    # @param message message
    # @param community community name
    # @param port port number
    # @param info additional information
    # @return True if sent
    # @~
    def _send_trap_message(self, target_ip, message, community=None, port=162, info=None):
        result = asyncio.run(self._send_notification_async(
            target_ip, message, community or self._community, port, info=info))
        error_indication, error_status, error_index, var_binds = result
        if error_indication or error_status:
            print('SNMP trap error:', error_indication or error_status)
            return False
        return True

    ##
    # @~japanese
    # @brief 'Register Device' のトラップを送る (探索)
    #
    # @param target_ip 送り先の IP アドレス
    # @param community コミュニティ名
    # @param port ポート番号
    # @return 送れたら True
    # @~english
    # @brief Sends a 'Register Device' trap (discovery)
    #
    # @param target_ip destination IP address
    # @param community community name
    # @param port port number
    # @return True if sent
    # @~
    def send_snmp_trap(self, target_ip, community=None, port=162):
        return self._send_trap_message(target_ip, 'Register Device', community, port)

    ##
    # @~japanese
    # @brief 'Register Device Reply' のトラップを送る (探索の返事)
    #
    # @param target_ip 送り先の IP アドレス
    # @param community コミュニティ名
    # @param port ポート番号
    # @return 送れたら True
    # @~english
    # @brief Sends a 'Register Device Reply' trap (reply to discovery)
    #
    # @param target_ip destination IP address
    # @param community community name
    # @param port port number
    # @return True if sent
    # @~
    def send_snmp_trap_reply(self, target_ip, community=None, port=162):
        return self._send_trap_message(target_ip, 'Register Device Reply', community, port)

    ##
    # @~japanese
    # @brief sysName.0 (または以前の登録・返事のトラップ) でロボットを探す
    #
    # @param ip IP アドレス
    # @param community コミュニティ名
    # @return 見つかれば True
    # @~english
    # @brief Discovers a robot by sysName.0 or legacy register/reply traps
    #
    # @param ip IP address
    # @param community community name
    # @return True if found
    # @~
    def check_snmp_device(self, ip, community=None):
        if self._discovery_mode == 'sysname':
            result = self.get_snmp_data(ip, [self._sysname_oid])
            if not result:
                return False
            name = str(result.get(self._sysname_oid, '')).strip()
            if not name or name.lower() in ('nosuchinstance', 'nosuchobject'):
                return False
            self._registerRobot(ip, name)
            return True
        result = self.get_snmp_data(ip, [self._sysdescr_oid])
        if not result:
            return False
        self.send_snmp_trap(ip, community=community or self._community)
        return True

    ##
    # @~japanese
    # @brief 自分の IP アドレスの一覧を返す
    #
    # @return IP アドレスのリスト
    # @~english
    # @brief Returns the list of local IP addresses
    #
    # @return list of IP addresses
    # @~
    def get_all_local_ips(self):
        local_ips = set()
        addrs = psutil.net_if_addrs()
        for iface, iface_addrs in addrs.items():
            for addr in iface_addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                    local_ips.add(addr.address)
        return local_ips
        
    ##
    # @~japanese
    # @brief トラップ受信用のループ上で使い回す SnmpEngine を返す
    #
    # SNMP の問い合わせごとに SnmpEngine と asyncio のループを作り直すと重い (マネージャ 1 つで CPU 30% 前後を使っていた) ので、1 つを使い回す。
    #
    # @return SnmpEngine
    # @~english
    # @brief Returns the SnmpEngine reused on the trap receiver loop
    #
    # Recreating an SnmpEngine and an asyncio loop for every SNMP request was heavy (around 30% CPU for one manager), so one engine is reused.
    #
    # @return SnmpEngine
    # @~
    def _shared_engine(self):
        engine = getattr(self, "_snmp_client_engine", None)
        if engine is None:
            engine = SnmpEngine()
            self._snmp_client_engine = engine
        return engine

    ##
    # @~japanese
    # @brief SNMP のコルーチンを実行する (共有のループがあればその上で)
    #
    # @param make_coro make_coro(shared) -> コルーチン
    # @param timeout 待つ秒数
    # @return コルーチンの結果
    # @~english
    # @brief Runs an SNMP coroutine (on the shared loop if available)
    #
    # @param make_coro make_coro(shared) -> coroutine
    # @param timeout seconds to wait
    # @return result of the coroutine
    # @~
    def _run_snmp(self, make_coro, timeout=15):
        loop = getattr(self, "_trap_loop", None)
        if loop is not None and loop.is_running() and threading.current_thread() is not getattr(self, "_trap_thread", None):
            return asyncio.run_coroutine_threadsafe(make_coro(True), loop).result(timeout)
        return asyncio.run(make_coro(False))

    ##
    # @~japanese
    # @brief SNMP で値を取る (非同期)
    #
    # @param ip IP アドレス
    # @param oids OID のリスト
    # @param shared 共有の SNMP エンジンを使うか
    # @return 値のリスト
    # @~english
    # @brief Gets values via SNMP asynchronously
    #
    # @param ip IP address
    # @param oids list of OIDs
    # @param shared whether to use the shared SNMP engine
    # @return list of values
    # @~
    async def _get_snmp_data_async(self, ip, oids, shared=False):
        engine = self._shared_engine() if shared else SnmpEngine()
        try:
            result = await get_cmd(
                engine, CommunityData(self._community),
                await UdpTransportTarget.create((ip, self._port), timeout=2, retries=1),
                ContextData(),
                *[ObjectType(ObjectIdentity(oid)) for oid in oids]
            )
            error_indication, error_status, error_index, var_binds = result
            if error_indication or error_status:
                print('SNMP GET error:', error_indication or error_status)
                return None
            return {str(oid): value for oid, value in var_binds}
        finally:
            if not shared:
                engine.close_dispatcher()

    ##
    # @~japanese
    # @brief SNMP で値を取る
    #
    # @param ipaddress IP アドレス
    # @param oids OID のリスト
    # @return 値のリスト
    # @~english
    # @brief Gets values via SNMP
    #
    # @param ipaddress IP address
    # @param oids list of OIDs
    # @return list of values
    # @~
    def get_snmp_data(self, ipaddress, oids):
        return self._run_snmp(lambda shared: self._get_snmp_data_async(ipaddress, oids, shared))

    ##
    # @~japanese
    # @brief インターフェース名から ifIndex を探す (非同期)
    #
    # @param ipaddress IP アドレス
    # @param ifname インターフェース名
    # @param shared 共有の SNMP エンジンを使うか
    # @return ifIndex (なければ None)
    # @~english
    # @brief Finds the ifIndex of an interface name asynchronously
    #
    # @param ipaddress IP address
    # @param ifname interface name
    # @param shared whether to use the shared SNMP engine
    # @return ifIndex (None if not found)
    # @~
    async def _get_ifindex_by_name_async(self, ipaddress, ifname, shared=False):
        engine = self._shared_engine() if shared else SnmpEngine()
        try:
            target = await UdpTransportTarget.create(
                (ipaddress, self._port), timeout=2, retries=1)
            async for error_indication, error_status, error_index, var_binds in walk_cmd(
                engine, CommunityData(self._community), target, ContextData(),
                ObjectType(ObjectIdentity(self.InterdaceNameOid)),
                lexicographicMode=False
            ):
                if error_indication or error_status:
                    print('SNMP WALK error:', error_indication or error_status)
                    return None
                for oid, value in var_binds:
                    # Windows の Net-SNMP は ifDescr の末尾に NUL を付けて返すので、比べる前に取り除く
                    if str(value).rstrip('\x00') == ifname:
                        return int(str(oid).split('.')[-1])
        finally:
            if not shared:
                engine.close_dispatcher()
        return None

    ##
    # @~japanese
    # @brief インターフェース名から ifIndex を探す
    #
    # @param ipaddress IP アドレス
    # @param ifname インターフェース名
    # @return ifIndex (なければ None)
    # @~english
    # @brief Finds the ifIndex of an interface name
    #
    # @param ipaddress IP address
    # @param ifname interface name
    # @return ifIndex (None if not found)
    # @~
    def get_ifindex_by_name(self, ipaddress, ifname):
        return self._run_snmp(lambda shared: self._get_ifindex_by_name_async(ipaddress, ifname, shared))

    ##
    # @~japanese
    # @brief 'WiFi Low' のトラップを送る
    #
    # @param target_ip 送り先の IP アドレス
    # @param community コミュニティ名
    # @param port ポート番号
    # @return 送れたら True
    # @~english
    # @brief Sends a 'WiFi Low' trap
    #
    # @param target_ip destination IP address
    # @param community community name
    # @param port port number
    # @return True if sent
    # @~
    def send_wifi_trap(self, target_ip, community=None, port=162):
        return self._send_trap_message(target_ip, 'WiFi Low', community, port)

    ##
    # @~japanese
    # @brief localhost とこのロボットの名前で、自分のマスターマネージャの参照を得る
    #
    # @return マネージャの参照
    # @~english
    # @brief Resolves the local master manager using localhost and this robot name
    #
    # @return manager reference
    # @~
    def get_own_comps(self):
        self._own_manager_ref = self._resolveManager(self._configured_own_ip or "localhost", self._name)
        return self._own_manager_ref

    ##
    # @~japanese
    # @brief 自分のマスターマネージャと、登録されたすべての slave マネージャを終了させる
    #
    # slave を先に終了させる。マスターを止めるとこのプロセス (SNMP の拡張そのもの) が終わることがあるので、マスターは最後に終了させる。
    # @~english
    # @brief Shuts down the local master and all its registered slave managers
    #
    # Slaves are shut down first. The local master is shut down last, since stopping it can terminate this process and the SNMP extension itself.
    # @~
    def shutdown_comp(self):
        if self._shutdown and getattr(self, "_shutdown_started", False):
            return
        self._shutdown = True
        self._shutdown_started = True
        try:
            master = self.get_own_comps()
            slaves = list(master.get_slave_managers())
            for slave in slaves:
                try:
                    slave.shutdown()
                except Exception:
                    self._rtcout.RTC_ERROR("Slave manager shutdown failed: " + traceback.format_exc())
            # This call may terminate the process; do not rely on code after it.
            master.shutdown()
        except Exception:
            self._shutdown = False
            self._shutdown_started = False
            self._rtcout.RTC_ERROR("Manager shutdown failed: " + traceback.format_exc())
            raise

    #def disconnect_own_comp(self):
    #    self._dnm1 = self.getComponent("DnmRtComponentRTC1", self.mgrref_r1)[0]
        
    #def deactivate_own_comp(self):
    #    pass

    ##
    # @~japanese
    # @brief 受けたトラップを処理するスレッドの本体
    # @~english
    # @brief Body of the thread that handles received traps
    # @~
    def trap_checking(self):
        count = 0
        while self._running:
            if self._robot is None:
                time.sleep(self._trap_interval)
                continue
            self.setRobotData(self._robot, self._trap_interval)
            dbm = self._robot.data.get("wifi_signal_dbm") if self._robot.last_data_update is not None else None
            if dbm != getattr(self, "_last_logged_dbm", None):
                self._log(f"wifi_signal_dbm={dbm} cpu={self._robot.data.get('cpu_usage')} "
                          f"mem={self._robot.data.get('memory_usage')}")
                self._last_logged_dbm = dbm
            self.check_migration_conditions()
            if self._verbose:
                print("wifi_strength:" + str(self._robot.data.get("wifi_strength")))
                print("count: "+str(count))
            count += 1
            trap_count = int(self._conf.getProperty("snmp.trap_count", "-1"))
            wifi_value = self._robot.data.get('wifi_strength') if self._robot.last_data_update is not None else None
            wifi_low = wifi_value is not None and float(wifi_value) < float(self._conf.getProperty("snmp.wifi_strength_min", "45"))
            if wifi_low or (trap_count > 0 and trap_count <= count):
                if self._verbose:
                    print("count: " + str(count) + " trap_count:" + str(trap_count))
                if not self._wifi_low:
                    self._wifi_low_time = time.time()
                    self._wifi_low = True
                else:
                    now = time.time()
                    diff = now - self._wifi_low_time
                    if diff > float(self._conf.getProperty("snmp.wifi_low_limit", "6")):
                        if not self._shutdown and self._conf.getProperty("snmp.shutdown_on_wifi_low", "NO").upper() == "YES":
                            with open(self._logfile, "a") as f:
                                sec = seconds_since_midnight()
                                f.write(f"{sec:.6f}\tMigrationStart\t\t\n")
                            start_shutdown = time.perf_counter()
                            self._shutdown = True
                            thread = threading.Thread(target=self.shutdown_comp, daemon=True)
                            thread.start()
                            #self.shutdown_comp()
                            end_shutdown = time.perf_counter()
                            difftime = end_shutdown - start_shutdown
                            with open(self._logfile, "a") as f:
                                sec = seconds_since_midnight()
                                f.write(f"{sec:.6f}\tShutdownTime:{difftime}\t\t\n")
                            
                            #self.get_own_comps()
                            #self.disconnect_own_comp()
                            #self.deactivate_own_comp()

                            self._shutdown = True
                        self.send_wifi_trap(self._conf.getProperty("snmp.main_robot", "192.168.215.137"))

            time.sleep(self._trap_interval)
            
        
    ##
    # @~japanese
    # @brief snmpd の extend の出力 (nsExtendOutput1Line) の OID を返す
    #
    # @param token extend の名前
    # @return OID
    # @~english
    # @brief Returns the OID of the output of an snmpd extend (nsExtendOutput1Line)
    #
    # @param token name of the extend
    # @return OID
    # @~
    @staticmethod
    def _extend_output_oid(token):
        # NET-SNMP-EXTEND-MIB::nsExtendOutput1Line."token"
        encoded = '.'.join(str(b) for b in token.encode('utf-8'))
        return '1.3.6.1.4.1.8072.1.3.2.3.1.2.' + str(len(token.encode('utf-8'))) + '.' + encoded

    ##
    # @~japanese
    # @brief 電波強度を取る OID を返す
    #
    # @return OID
    # @~english
    # @brief Returns the OID for the RSSI
    #
    # @return OID
    # @~
    def _wifi_oid(self):
        if self._wifi_role == 'client':
            if self._wifi_client_oid:
                return self._wifi_client_oid
            # Backward compatibility only for the legacy wlan0 deployment.
            if self._wifi_interface == 'wlan0' and self._conf.getProperty('snmp.wifi_client_extend_prefix', '') == '':
                return self.WirelessStrOid
            return self._extend_output_oid(self._wifi_client_token_prefix + self._wifi_interface)
        if self._wifi_ap_oid:
            return self._wifi_ap_oid
        return self._extend_output_oid(self._wifi_ap_token_prefix + self._wifi_interface)

    ##
    # @~japanese
    # @brief 累積の CPU のカウンタの 2 回の値から使用率を求める (最初の標本は無効)
    #
    # Linux の UCD の生のカウンタは累積の tick で、iowait はアイドルとして扱う。カウンタが戻ったり差分がなかったりすれば、その標本は無効。
    #
    # @param robot ロボット
    # @param counters カウンタの値
    # @return 使用率 (%) (無効なら None)
    # @~english
    # @brief Calculates the utilization from two cumulative CPU snapshots; the first sample is invalid
    #
    # Linux UCD raw counters are cumulative ticks; iowait is treated as idle. A counter reset or missing delta invalidates the sample.
    #
    # @param robot robot
    # @param counters counter values
    # @return utilization (%) (None if invalid)
    # @~
    @staticmethod
    def _cpu_usage_from_counters(robot, counters):
        previous = robot.last_cpu_counters
        robot.last_cpu_counters = counters
        if previous is None:
            return None
        deltas = {key: counters[key] - previous[key] for key in counters}
        if any(delta < 0 for delta in deltas.values()):
            return None
        total = sum(deltas.values())
        if total <= 0:
            return None
        idle = deltas['idle'] + deltas['iowait']
        return max(0.0, min(100.0, (total - idle) * 100.0 / total))

    # NET-SNMP-EXTEND-MIB の extend 名 (docker-test/rtm/cgroup-metrics を snmpd が呼ぶ)
    CgroupExtendTokens = {"mem_limit": "cgroupMemLimit", "mem_usage": "cgroupMemUsage",
                          "cpu_limit": "cgroupCpuLimit", "cpu_usage": "cgroupCpuUsage"}

    ##
    # @~japanese
    # @brief コンテナ (cgroup) の制限と使用量を取得して robot.cgroup に入れる
    #
    # cpu_usage_pct は累計 CPU 時間の差分から求めた使用率 (1 コア = 100) の直近の平均。制限なしの項目は 0。
    #
    # @param robot ロボット
    # @~english
    # @brief Gets the limits and usage of the container (cgroup) and stores them in robot.cgroup
    #
    # cpu_usage_pct is the recent average of the utilization (1 core = 100) computed from the difference of the cumulative CPU time. Unlimited items are 0.
    #
    # @param robot robot
    # @~
    def _updateCgroup(self, robot):
        if self._conf.getProperty("snmp.cgroup.enabled", "NO").upper() != "YES":
            return
        oids = {k: self._extend_output_oid(v) for k, v in self.CgroupExtendTokens.items()}
        data = self.get_snmp_data(robot.ipaddress, list(oids.values()))
        if not data:
            return
        try:
            raw = {k: str(data[o]).split() for k, o in oids.items()}
            vals = {k: int(v[0]) for k, v in raw.items()}
            # cpu_usage は "累計ns 読み取り時刻ns"。時刻がなければ受信時刻で代用する
            cpu_ts = int(raw["cpu_usage"][1]) if len(raw["cpu_usage"]) > 1 else int(time.monotonic() * 1e9)
        except (KeyError, ValueError, TypeError, IndexError):
            return
        now = time.monotonic()
        cg = robot.cgroup or {"cpu_samples": [], "cpu_usage_pct": None}
        prev = robot.last_cg_cpu
        # snmpd のキャッシュで同じ値が返った場合 (時刻が進んでいない) は捨てる
        if prev is None or cpu_ts > prev[1]:
            robot.last_cg_cpu = (vals["cpu_usage"], cpu_ts)
        if prev and cpu_ts > prev[1] and vals["cpu_usage"] >= prev[0]:
            pct = (vals["cpu_usage"] - prev[0]) / (cpu_ts - prev[1]) * 100.0
            window = int(self._conf.getProperty("snmp.cgroup.cpu_window", "5"))
            cg["cpu_samples"] = (cg["cpu_samples"] + [pct])[-window:]
            cg["cpu_usage_pct"] = round(sum(cg["cpu_samples"]) / len(cg["cpu_samples"]), 2)
        cg.update(mem_limit_mb=round(vals["mem_limit"] / 1048576, 1),
                  mem_usage_mb=round(vals["mem_usage"] / 1048576, 1),
                  cpu_limit_pct=round(vals["cpu_limit"] / 10.0, 1), updated=now)
        robot.cgroup = cg
        robot.data['cgroup'] = {k: v for k, v in cg.items() if k != "cpu_samples"}

    ##
    # @~japanese
    # @brief バッテリー残量 (%) を snmpd の extend (snmp.battery.extend) から取る。取れなければ None
    #
    # @param robot ロボット
    # @~english
    # @brief Gets the battery level (%) from the snmpd extend (snmp.battery.extend); None if not available
    #
    # @param robot robot
    # @~
    def _updateBattery(self, robot):
        oid = self._extend_output_oid(self._battery_extend)
        try:
            data = self.get_snmp_data(robot.ipaddress, [oid])
            robot.data['battery_pct'] = float(str(data[oid]).strip()) if data and oid in data else None
        except (ValueError, TypeError, KeyError):
            robot.data['battery_pct'] = None

    ##
    # @~japanese
    # @brief ロボットの監視の値を SNMP で取って更新する
    #
    # @param robot ロボット
    # @param interval ポーリングの間隔 (秒)
    # @~english
    # @brief Updates the monitoring values of a robot via SNMP
    #
    # @param robot robot
    # @param interval polling interval (seconds)
    # @~
    def setRobotData(self, robot, interval):
        try:
            self._updateCgroup(robot)
        except Exception:
            self._rtcout.RTC_WARN("cgroup metrics failed: " + traceback.format_exc())
        if robot.data['os'] == 'unknown':
            os_data = self.get_snmp_data(robot.ipaddress, [self._sysdescr_oid])
            if os_data and self._sysdescr_oid in os_data:
                robot.data['os'] = str(os_data[self._sysdescr_oid])
        # 値は 1 つずつ使う: エージェントによっては返さない値がある (Windows の Net-SNMP は UCD-SNMP-MIB の
        # CPU・メモリを返さない)。返ってきた値だけを更新し、1 つも取れなければ「データなし」にする
        # インタフェース番号は変わらないので、取れたら覚えておく (毎回の WALK を避ける)
        ifid = getattr(robot, "ifindex", None) or self.get_ifindex_by_name(robot.ipaddress, self._wifi_interface)
        recv_oid = self.InterfaceRecieveOid + '.' + str(ifid) if ifid is not None else None
        send_oid = self.InterfaceSendOid + '.' + str(ifid) if ifid is not None else None
        wifi_oid = self._wifi_oid()
        oids = [self.MemTotalOid, self.MemAvailOid, wifi_oid] + list(self._cpu_raw_oids.values())
        oids += [o for o in self._custom_metrics.values() if o not in oids]
        if ifid is not None:
            oids = [recv_oid, send_oid] + oids
        data = self.get_snmp_data(robot.ipaddress, oids)
        if not data:
            robot.last_data_update = None
            robot.ifindex = None
            return
        got = False
        now = time.monotonic()
        # CPU (UCD-SNMP-MIB ssCpuRaw*)。Never publish a fabricated 0% CPU usage on the first sample.
        try:
            counters = {name: int(data[oid]) for name, oid in self._cpu_raw_oids.items()}
            cpu_percent = self._cpu_usage_from_counters(robot, counters)
            robot.data['cpu_usage'] = str(cpu_percent) if cpu_percent is not None else None
            got = True
        except (ValueError, TypeError, KeyError):
            robot.data['cpu_usage'] = None
        # メモリ (memTotalReal / memAvailReal。kB)
        try:
            mem_total = float(data[self.MemTotalOid])
            mem_avail = float(data[self.MemAvailOid])
            if mem_total <= 0:
                raise ValueError('Invalid memory total')
            robot.data['memory_usage'] = str((mem_total - mem_avail) / mem_total * 100.0)
            robot.data['mem_total_mb'] = round(mem_total / 1024.0, 1)
            got = True
        except (ValueError, TypeError, KeyError):
            robot.data['memory_usage'] = None
        # Wi-Fi の電波強度 (dBm)
        robot.data['wifi_interface'] = self._wifi_interface
        robot.data['wifi_signal_source'] = self._wifi_role
        try:
            wifi_dbm = float(str(data[wifi_oid]).strip())
            robot.data['wifi_signal_client_dbm'] = str(wifi_dbm) if self._wifi_role == 'client' else None
            robot.data['wifi_signal_ap_dbm'] = str(wifi_dbm) if self._wifi_role == 'ap' else None
            robot.data['wifi_signal_dbm'] = str(wifi_dbm)
            # Retain old percentage-based migration rules for compatibility.
            robot.data['wifi_strength'] = str(max(0.0, min(100.0, (70.0 + wifi_dbm) / 70.0 * 100.0)))
            got = True
        except (ValueError, TypeError, KeyError):
            for k in ('wifi_signal_client_dbm', 'wifi_signal_ap_dbm', 'wifi_signal_dbm', 'wifi_strength'):
                robot.data[k] = None
        # 通信量 (IF-MIB の ifInOctets / ifOutOctets)
        try:
            if ifid is None:
                raise KeyError('interface')
            recv = int(data[recv_oid])
            sent = int(data[send_oid])
            robot.ifindex = ifid
            if robot.last_if_sample_time is not None:
                elapsed = now - robot.last_if_sample_time
                recv_diff = recv - robot.last_if_recv
                send_diff = sent - robot.last_if_send
                if elapsed > 0 and recv_diff >= 0 and send_diff >= 0:
                    robot.data['network_in'] = str(recv_diff * 8.0 / elapsed / 1_000_000)
                    robot.data['network_out'] = str(send_diff * 8.0 / elapsed / 1_000_000)
            robot.last_if_recv = recv
            robot.last_if_send = sent
            robot.last_if_sample_time = now
            got = True
        except (ValueError, TypeError, KeyError):
            robot.ifindex = None      # 次の回にインタフェースを探し直す
            robot.data['network_in'] = robot.data['network_out'] = None
            robot.last_if_sample_time = None
        # 追加の監視の値 (snmp.metrics)
        if self._custom_metrics:
            values = {name: CustomMetrics.parse_value(data.get(oid)) for name, oid in self._custom_metrics.items()}
            robot.metrics = values
            got = got or any(v is not None for v in values.values())
        if not got:
            robot.last_data_update = None
            return
        if self._battery_enabled:
            self._updateBattery(robot)
        # Do not consider the first CPU snapshot a valid CPU utilization sample.
        robot.last_data_update = now
        robot.last_seen = now  # ポーリングの成功も応答があった証拠にする
        robot.data['timestamp'] = str(time.time())

    # ------------------------------------------------------------------
    # 死活監視と通信品質 (レイテンシ・ジッタ・パケットロス)
    # ------------------------------------------------------------------
    SysUpTimeOid = '1.3.6.1.2.1.1.3.0'

    ##
    # @~japanese
    # @brief sysUpTime を 1 回だけ GET する (再送なし)
    #
    # @param ip IP アドレス
    # @return (成功したか, 往復時間 ms)
    # @~english
    # @brief GETs sysUpTime once (no retries)
    #
    # @param ip IP address
    # @return (whether it succeeded, round-trip time in ms)
    # @~
    async def _probe_async(self, ip):
        t0 = time.perf_counter()
        try:
            target = await UdpTransportTarget.create((ip, self._port), timeout=self._probe_timeout, retries=0)
            ei, es, _, _ = await get_cmd(self._shared_engine(), CommunityData(self._community), target,
                                         ContextData(), ObjectType(ObjectIdentity(self.SysUpTimeOid)))
            ok = not ei and not es
        except Exception:
            ok = False
        return ok, (time.perf_counter() - t0) * 1000.0

    ##
    # @~japanese
    # @brief 全ロボットへ並行してプローブを送る
    #
    # @param ips IP アドレスのリスト
    # @return プローブの結果のリスト
    # @~english
    # @brief Sends probes to all robots in parallel
    #
    # @param ips list of IP addresses
    # @return list of probe results
    # @~
    async def _probe_all_async(self, ips):
        return await asyncio.gather(*[self._probe_async(ip) for ip in ips])

    ##
    # @~japanese
    # @brief プローブの結果 (往復時間・ジッタ・損失) を記録する
    #
    # @param robot ロボット
    # @param ok 成功したか
    # @param rtt_ms 往復時間 (ms)
    # @param now 現在の時刻
    # @~english
    # @brief Records a probe result (round-trip time, jitter, loss)
    #
    # @param robot robot
    # @param ok whether it succeeded
    # @param rtt_ms round-trip time (ms)
    # @param now current time
    # @~
    def _record_probe(self, robot, ok, rtt_ms, now):
        if robot.probes.maxlen != self._probe_window:
            robot.probes = collections.deque(robot.probes, maxlen=self._probe_window)
        robot.probes.append((ok, rtt_ms if ok else None))
        rtts = [r for o, r in robot.probes if o]
        robot.packet_loss = round(100.0 * (1 - len(rtts) / len(robot.probes)), 1)
        robot.latency_ms = round(sum(rtts) / len(rtts), 3) if rtts else None
        # ジッタ: 連続して成功した往復時間どうしの差の絶対値の平均 (RFC 3550 の考え方を単純化)
        diffs = [abs(a - b) for a, b in zip(rtts, rtts[1:])]
        robot.jitter_ms = round(sum(diffs) / len(diffs), 3) if diffs else (0.0 if rtts else None)
        if ok:
            robot.last_seen = now
        robot.data['latency_ms'] = robot.latency_ms
        robot.data['jitter_ms'] = robot.jitter_ms
        robot.data['packet_loss'] = robot.packet_loss
        self._update_status(robot, now)

    ##
    # @~japanese
    # @brief ロボットの状態を更新する。最後の応答 (プローブ・ポーリング・ハートビート) から liveness.timeout 以内なら alive
    #
    # @param robot ロボット
    # @param now 現在の時刻
    # @~english
    # @brief Updates the status of a robot. Alive if within liveness.timeout from the last response (probe, polling, heartbeat)
    #
    # @param robot robot
    # @param now current time
    # @~
    def _update_status(self, robot, now):
        if robot.is_local:
            return
        evidence = max([t for t in (robot.last_seen, robot.last_heartbeat) if t is not None], default=None)
        since = now - (evidence if evidence is not None else robot.registered_at)
        new = "alive" if evidence is not None and since <= self._liveness_timeout else \
            ("dead" if since > self._liveness_timeout else robot.status)
        robot.data['alive'] = 1 if new == "alive" else (0 if new == "dead" else None)
        if new != robot.status:
            old, robot.status = robot.status, new
            if new == "dead":
                self._event(robot.name, "down", f"no response for {since:.1f}s (was {old})")
            elif new == "alive" and old == "dead":
                self._event(robot.name, "up", "responding again")
            elif new == "alive":
                self._event(robot.name, "alive", "first response")

    ##
    # @~japanese
    # @brief アクティブ監視: probe_interval ごとに全ロボットへ並行してプローブを送る
    # @~english
    # @brief Active monitoring: sends probes to all robots in parallel every probe_interval
    # @~
    def _liveness_loop(self):
        while self._running:
            started = time.monotonic()
            with self._robot_lock:
                robots = list(self._robotList)
            if robots:
                try:
                    results = self._run_snmp(lambda shared: self._probe_all_async([r.ipaddress for r in robots]),
                                             timeout=self._probe_timeout + 10)
                    now = time.monotonic()
                    for robot, (ok, rtt) in zip(robots, results):
                        self._record_probe(robot, ok, rtt, now)
                except Exception:
                    self._rtcout.RTC_WARN("liveness probe failed: " + traceback.format_exc())
            time.sleep(max(0.05, self._probe_interval - (time.monotonic() - started)))

    ##
    # @~japanese
    # @brief 全ロボットへ Heartbeat のトラップを送る (非同期)
    #
    # @param ips IP アドレスのリスト
    # @~english
    # @brief Sends Heartbeat traps to all robots asynchronously
    #
    # @param ips list of IP addresses
    # @~
    async def _heartbeat_all_async(self, ips):
        async def one(ip):
            try:
                await self._send_notification_async(ip, 'Heartbeat', self._community, self._trap_port, shared=True)
            except Exception:
                pass
        await asyncio.gather(*[one(ip) for ip in ips])

    ##
    # @~japanese
    # @brief パッシブ監視の送信側: 他のロボットへ Heartbeat のトラップを送り続ける
    # @~english
    # @brief Sender side of passive monitoring: keeps sending Heartbeat traps to the other robots
    # @~
    def _heartbeat_loop(self):
        while self._running:
            with self._robot_lock:
                ips = [r.ipaddress for r in self._robotList]
            if ips:
                try:
                    self._run_snmp(lambda shared: self._heartbeat_all_async(ips), timeout=10)
                except Exception:
                    self._rtcout.RTC_WARN("heartbeat send failed: " + traceback.format_exc())
            time.sleep(self._heartbeat_interval)

    ##
    # @~japanese
    # @brief Heartbeat のトラップを受けたときの処理
    #
    # @param src_ip 送り元の IP アドレス
    # @~english
    # @brief Handles a received Heartbeat trap
    #
    # @param src_ip source IP address
    # @~
    def _on_heartbeat(self, src_ip):
        now = time.monotonic()
        with self._robot_lock:
            robot = next((r for r in self._robotList if r.ipaddress == src_ip), None)
        if robot is not None:
            robot.last_heartbeat = now
            self._update_status(robot, now)

    ##
    # @~japanese
    # @brief ロボットが生きているか
    #
    # @param name ロボット名
    # @return 生きていれば True
    # @~english
    # @brief Whether a robot is alive
    #
    # @param name robot name
    # @return True if alive
    # @~
    def isAlive(self, name):
        robot = self._findConditionRobot(name)
        return robot is not None and (robot.is_local or robot.status != "dead")

    # ------------------------------------------------------------------
    # 監視情報の保存 (SQLite)
    # ------------------------------------------------------------------
    ##
    # @~japanese
    # @brief イベントを記録する (ログ、SQLite、プラグインへの通知)
    #
    # @param robot_name ロボット名
    # @param kind イベントの種別
    # @param detail 詳細
    # @~english
    # @brief Records an event (log, SQLite and notification to plugins)
    #
    # @param robot_name robot name
    # @param kind event kind
    # @param detail details
    # @~
    def _event(self, robot_name, kind, detail=""):
        self._log(f"event {kind}: {robot_name or '-'} {detail}".rstrip())
        store = getattr(self, "_store", None)
        if store is not None:
            store.record_event(robot_name, kind, detail)
        pm = getattr(self, "_plugin_manager", None)
        if pm is not None:
            import PluginManager
            pm.publish(PluginManager.make_event(self._name, robot_name, kind, detail))

    ##
    # @~japanese
    # @brief ロボットの監視の値を辞書にする
    #
    # @param robot ロボット
    # @return 監視の値の辞書
    # @~english
    # @brief Converts the monitoring values of a robot into a dictionary
    #
    # @param robot robot
    # @return dictionary of monitoring values
    # @~
    def _snapshot(self, robot):
        cg = robot.cgroup or {}
        return {"robot": robot.name, "ip": robot.ipaddress, "status": robot.status,
                "cpu_usage": robot.data.get("cpu_usage"), "memory_usage": robot.data.get("memory_usage"),
                "network_in": robot.data.get("network_in"), "network_out": robot.data.get("network_out"),
                "wifi_signal_dbm": robot.data.get("wifi_signal_dbm"),
                "latency_ms": robot.latency_ms, "jitter_ms": robot.jitter_ms, "packet_loss": robot.packet_loss,
                "cg_cpu_usage": cg.get("cpu_usage_pct"), "cg_cpu_limit": cg.get("cpu_limit_pct"),
                "cg_mem_usage_mb": cg.get("mem_usage_mb"), "cg_mem_limit_mb": cg.get("mem_limit_mb"),
                "metrics": dict(robot.metrics or {})}

    ##
    # @~japanese
    # @brief 監視の値を定期的に SQLite に保存するスレッドの本体
    # @~english
    # @brief Body of the thread that periodically saves the monitoring values to SQLite
    # @~
    def _store_loop(self):
        while self._running:
            time.sleep(self._db_interval)
            with self._robot_lock:
                robots = ([self._robot] if self._robot is not None else []) + list(self._robotList)
            try:
                snaps = [self._snapshot(r) for r in robots]
                self._store.record_metrics(snaps)
                if self._custom_metrics:
                    self._store.record_custom_metrics(snaps)
            except Exception:
                self._rtcout.RTC_WARN("metrics store failed: " + traceback.format_exc())

    ##
    # @~japanese
    # @brief SQLite の保存先を開く (探索の discovered イベントより前に開く)
    # @~english
    # @brief Opens the SQLite store (before the discovered events of discovery)
    # @~
    def _open_store(self):
        if self._db_enabled:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import MonitoringStore
            self._store = MonitoringStore.MetricsStore(self._db_path, self._name, self._db_retention)
            self._event(self._name, "started", f"db={self._db_path}")

    ##
    # @~japanese
    # @brief 監視のスレッドを始める
    # @~english
    # @brief Starts the monitoring threads
    # @~
    def _start_monitoring(self):
        if getattr(self, "_store", None) is not None:
            threading.Thread(target=self._store_loop, daemon=True).start()
        if self._liveness_enabled:
            threading.Thread(target=self._liveness_loop, daemon=True).start()
        if self._heartbeat_enabled:
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()
        if self._inventory_interval > 0:
            threading.Thread(target=self._inventory_loop, daemon=True).start()
        threading.Thread(target=self._recovery_loop, daemon=True).start()
        if self._measure_enabled:
            threading.Thread(target=self._measure_loop, daemon=True).start()

    ##
    # @~japanese
    # @brief 全ロボットの監視の値を定期的に取るスレッドの本体
    # @~english
    # @brief Body of the thread that periodically polls the monitoring values of all robots
    # @~
    def polling(self):
        while self._running:
            try:
                self.rediscover()
            except Exception:
                self._rtcout.RTC_ERROR("Rediscovery failed: " + traceback.format_exc())
            with self._robot_lock:
                robots = list(self._robotList)
            for robot in robots:
                # 停止中のロボットはタイムアウト待ちで他のポーリングを遅らせるので飛ばす
                # (復帰はプローブで検知する)
                if self._liveness_enabled and robot.status == "dead":
                    continue
                self.setRobotData(robot, self._get_interval)
            time.sleep(self._get_interval)

    ##
    # @~japanese
    # @brief SNMP のトラップを受けるスレッドの本体
    # @~english
    # @brief Body of the thread that receives SNMP traps
    # @~
    def trap_receiver(self):
        loop = self._trap_loop
        asyncio.set_event_loop(loop)
        engine = None
        try:
            engine = SnmpEngine()
            self._snmp_engine = engine
            config.add_transport(
                engine, udp.DOMAIN_NAME,
                udp.UdpAsyncioTransport().open_server_mode(
                    (self._conf.getProperty('snmp.trap_address', '').strip() or self._configured_own_ip or '0.0.0.0',
                     int(self._conf.getProperty('snmp.trap_port', '162')))
                )
            )
            config.add_v1_system(engine, 'my-area', self._community)
            ntfrcv.NotificationReceiver(engine, self.trap_callback)
            self._trap_ready.set()
            loop.run_forever()
        except Exception as exc:
            self._trap_error = exc
            self._rtcout.RTC_ERROR(traceback.format_exc())
            self._trap_ready.set()
        finally:
            if engine is not None:
                engine.close_dispatcher()
            loop.close()

    ##
    # @~japanese
    # @brief 監視するロボットの状態
    # @~english
    # @brief State of a monitored robot
    # @~
    class Robot:
        ##
        # @~japanese
        # @brief コンストラクタ
        #
        # @param name ロボット名
        # @param ipaddress IP アドレス
        # @param is_local 自分のロボットなら True
        # @~english
        # @brief Constructor
        #
        # @param name robot name
        # @param ipaddress IP address
        # @param is_local True for this robot
        # @~
        def __init__(self, name, ipaddress, is_local=False):
            self.name = name
            self.ipaddress = ipaddress
            self.is_local = is_local
            self.data = self.initData()
            self.last_if_recv = 0
            self.last_if_send = 0
            self.last_if_sample_time = None
            self.last_cpu_counters = None
            self.last_data_update = None
            self.cgroup = None          # コンテナ (cgroup) の制限と使用量
            self.metrics = {}           # 追加の監視の値 (snmp.metrics): {名前: 数値か None}
            self.last_cg_cpu = None
            # 死活監視と通信品質
            self.status = "alive" if is_local else "unknown"   # unknown / alive / dead
            self.last_seen = None       # 最後に応答があった時刻 (monotonic。プローブ・ポーリング・ハートビート)
            self.last_heartbeat = None
            self.registered_at = time.monotonic()
            self.probes = collections.deque(maxlen=20)       # (成功したか, 往復時間 ms)
            self.latency_ms = None
            self.jitter_ms = None
            self.packet_loss = None
            # 動いている RTC の一覧 (_inventory_loop が更新する) と、RTC がないときのメモリ使用量
            self.inventory = None
            self.inventory_time = None
            self.base_mem_mb = None
        ##
        # @~japanese
        # @brief ロボットを文字列にする
        #
        # @return 文字列
        # @~english
        # @brief Converts the robot into a string
        #
        # @return string
        # @~
        def __str__(self):
            return "[name="+self.name+", ipaddress="+self.ipaddress+"]"
        ##
        # @~japanese
        # @brief 監視の値の初期値を返す
        #
        # @return 監視の値の辞書
        # @~english
        # @brief Returns the initial monitoring values
        #
        # @return dictionary of monitoring values
        # @~
        def initData(self):
            return {       
                    "name": self.name,
                    "ip_address": self.ipaddress,
                    "os": platform.platform() if self.is_local else "unknown",
                    "timestamp": str(time.time()),
                    "cpu_usage": None,
                    "memory_usage": "0",
                    "network_in": "0",
                    "network_out": "0",
                    "wifi_strength": None,
                    "wifi_signal_dbm": None,
                    "wifi_signal_client_dbm": None,
                    "wifi_signal_ap_dbm": None,
                    "wifi_signal_source": None,
                    "wifi_interface": None,
                    "alive": 1 if self.is_local else None,
                    "latency_ms": None,
                    "jitter_ms": None,
                    "packet_loss": None,
                    "pose2d":
                    {
                        "position": [0.0, 0.0],
                        "heading": 0.0
                    },
                    "pose3d":
                    {
                        "position": [0.0, 0.0, 0.0],
                        "quaternion": [0.0, 0.0, 0.0, 0.0]
                    },
                    "network":
                    {
                    },
                    "components":
                    [
                    ]
                   }
        

##
# @~japanese
# @brief コンポーネントオブザーバーのサーバーオブジェクト。RTC ごとに 1 つ (通知にはどの RTC かが入らないため)
# @~english
# @brief Server object of the component observer. One per RTC (the notification does not identify the RTC)
# @~
class _ObserverMixin:

    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param owner SNMPManager
    # @param instance RTC のインスタンス名
    # @~english
    # @brief Constructor
    #
    # @param owner SNMPManager
    # @param instance instance name of the RTC
    # @~
    def __init__(self, owner, instance):
        self._owner = owner
        self._instance = instance

    ##
    # @~japanese
    # @brief RTC の状態の通知を受ける (ComponentObserver::update_status)
    #
    # @param status_kind 状態の種別
    # @param hint 詳細
    # @~english
    # @brief Receives a status notification of the RTC (ComponentObserver::update_status)
    #
    # @param status_kind status kind
    # @param hint hint
    # @~
    def update_status(self, status_kind, hint):
        try:
            kind = str(status_kind).split(".")[-1]   # OpenRTM.RTC_STATUS -> "RTC_STATUS"
            self._owner._on_observer_status(self._instance, kind, hint)
        except Exception:
            traceback.print_exc()


_OBSERVER_CLASSES = None


##
# @~japanese
# @brief オブザーバーのインターフェースの一覧を返す。IDL のスタブは OpenRTM_aist の RTM_IDL にある
#
# @return [(モジュール名, サーバントのクラス)]
# @~english
# @brief Returns the list of observer interfaces. The IDL stubs are in RTM_IDL of OpenRTM_aist
#
# @return [(module name, servant class)]
# @~
def _observer_interfaces():
    global _OBSERVER_CLASSES
    if _OBSERVER_CLASSES is None:
        out = []
        import OpenRTM
        import OpenRTM__POA
        out.append(("OpenRTM", type("_ObserverOpenRTM", (_ObserverMixin, OpenRTM__POA.ComponentObserver),
                                    {"REPO_ID": OpenRTM.ComponentObserver._NP_RepositoryId})))
        try:
            import ComponentObserver_idl    # noqa: F401  (RTC モジュールの ComponentObserver を登録する)
            import RTC__POA
            out.append(("RTC", type("_ObserverRTC", (_ObserverMixin, RTC__POA.ComponentObserver),
                                    {"REPO_ID": RTC.ComponentObserver._NP_RepositoryId})))
        except (ImportError, AttributeError):
            pass
        _OBSERVER_CLASSES = out
    return _OBSERVER_CLASSES


# Module extension entry point. OpenRTM Manager.load("SNMPManager.py", "SNMPManagerInit")
# invokes this function with the existing Manager instance.
_snmp_manager = None
_snmp_listener = None


##
# @~japanese
# @brief マネージャの終了を受けて SNMPManager を止めるリスナー
# @~english
# @brief Listener that stops SNMPManager when the manager shuts down
# @~
class SNMPManagerListener(OpenRTM_aist.ManagerActionListener):
    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param snmp_manager SNMPManager
    # @~english
    # @brief Constructor
    #
    # @param snmp_manager SNMPManager
    # @~
    def __init__(self, snmp_manager):
        self._snmp_manager = snmp_manager

    ##
    # @~japanese
    # @brief マネージャの終了の直前に呼ばれる
    # @~english
    # @brief Called just before the manager shuts down
    # @~
    def preShutdown(self):
        self._snmp_manager.stop()


##
# @~japanese
# @brief マネージャに読み込まれたときの入口 (SNMPManager を作って始める)
#
# @param manager マネージャ
# @~english
# @brief Entry point when loaded into a manager (creates and starts SNMPManager)
#
# @param manager manager
# @~
def SNMPManagerInit(manager):
    global _snmp_manager, _snmp_listener
    if _snmp_manager is not None:
        return
    conf = manager.getConfig()
    snmp_manager = SNMPManager(
        manager, conf, port=int(conf.getProperty("snmp.port", "161"))
    )
    listener = SNMPManagerListener(snmp_manager)
    manager.addManagerActionListener(listener)
    snmp_manager._install_process_observer()
    _snmp_listener = listener
    _snmp_manager = snmp_manager
    try:
        snmp_manager.init()
    except Exception:
        snmp_manager.stop()
        _snmp_manager = None
        raise


##
# @~japanese
# @brief 単独で起動したときの入口 (マネージャを初期化し、SNMPManager を始める)
# @~english
# @brief Entry point when started standalone (initializes the manager and starts SNMPManager)
# @~
def main():
    # Standalone mode: initialize the OpenRTM Manager only once.
    manager = OpenRTM_aist.Manager.init(sys.argv)
    manager.activateManager()
    SNMPManagerInit(manager)
    try:
        manager.runManager()
    finally:
        if _snmp_manager is not None:
            _snmp_manager.stop()


if __name__ == "__main__":
    main()
