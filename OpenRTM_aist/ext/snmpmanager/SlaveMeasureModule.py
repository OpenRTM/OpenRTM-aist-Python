#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file SlaveMeasureModule.py
# @brief Measurement of actual values by the managers
#
# @~japanese
# マネージャによる実測値の計測
#
# マネージャが、自身のプロセスの CPU 使用率、メモリ使用量や、RTC のデータポートで送信、受信したデータの情報を収集し、ファイルに保存する。
# RTC を動かすマネージャ (slave) に読み込むモジュール。rtc.conf の
# @code
#   manager.modules.preload: /opt/snmpmgr/SlaveMeasureModule.py
# @endcode
# で読み込む (マスターは rtc.conf を -f で slave に渡すので、slave も同じ設定で読み込む)。
# マスターマネージャ (manager.is_master: YES) では何もしない (snmp.measure.master: YES なら計測する)。
#
# 計測するもの (snmp.measure.interval 秒ごと)
# - CPU: プロセス全体の使用率 (1 コア = 100) と、RTC ごとの実行コンテキストのスレッドの使用率。RTC の値 = 自分の実行コンテキストのスレッド + 残り (ORB のスレッドなど) をスレッドの使用率の比で按分 (RTC が 1 つならプロセス全体と同じ)
# - メモリ: プロセスの USS。RTC の値 = (USS - 最初の RTC を置く直前の USS) を、生成したときの増分の比で按分 (生成したときの増分を下回らない。RTC が 1 つなら USS の増分)
# - データポート: InPort は受信 (ON_RECEIVED)、OutPort は送信 (ON_SEND) したデータのバイト数と回数 (コネクタごと)
#
# CPU とメモリは、その RTC がアクティブで、アクティブになってから snmp.measure.warmup 秒たった後の標本だけを使う。
# 結果は snmp.measure.runtime_dir/\<マネージャ名\>.json に書き出す。マスターの SNMPManager がそれを集めて、placement.xml (自動配置の見込み値) と SQLite に保存する。
# @~english
# The manager collects the CPU usage and memory usage of its own process and the information of the data sent and received by the data ports of RTCs, and saves them to a file.
# A module loaded into the managers that run RTCs (slaves). It is loaded with
# @code
#   manager.modules.preload: /opt/snmpmgr/SlaveMeasureModule.py
# @endcode
# in rtc.conf (the master passes rtc.conf to the slaves with -f, so the slaves load it with the same settings).
# It does nothing in the master manager (manager.is_master: YES) unless snmp.measure.master: YES.
#
# Measured items (every snmp.measure.interval seconds)
# - CPU: usage of the whole process (1 core = 100) and usage of the execution context threads of each RTC. Value of an RTC = its own execution context threads + the rest (ORB threads etc.) divided in proportion to the thread usages (same as the whole process if there is one RTC)
# - Memory: USS of the process. Value of an RTC = (USS - USS just before the first RTC was created) divided in proportion to the increments at creation (not less than the increment at creation; the USS increment if there is one RTC)
# - Data ports: number of bytes and count of the data received (ON_RECEIVED) by InPorts and sent (ON_SEND) by OutPorts (per connector)
#
# For CPU and memory, only samples taken while the RTC is active and at least snmp.measure.warmup seconds after it became active are used.
# The results are written to snmp.measure.runtime_dir/\<manager name\>.json. The master SNMPManager collects them and saves them to placement.xml (estimates for automatic placement) and SQLite.
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

import collections
import json
import os
import threading
import time

try:
    import psutil
except ImportError:      # psutil がなければ /proc から読む (Linux)
    psutil = None

MB = 1024.0 * 1024.0
MAX_SAMPLES = 3600


# ---------------------------------------------------------------------------
# 按分 (OpenRTM に依存しない。単体テストで確かめる)
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief プロセスの CPU 使用率を RTC ごとに分ける
#
# 残り (proc_cpu - 実行コンテキストのスレッドの合計) を、実行コンテキストのスレッドの使用率の比で按分する。
#
# @param proc_cpu プロセス全体の CPU 使用率
# @param ec_cpu {RTC: 実行コンテキストのスレッドの使用率}
# @return {RTC: CPU 使用率}
# @~english
# @brief Divides the CPU usage of the process among the RTCs
#
# The rest (proc_cpu - total of the execution context threads) is divided in proportion to the usages of the execution context threads.
#
# @param proc_cpu CPU usage of the whole process
# @param ec_cpu {RTC: usage of the execution context threads}
# @return {RTC: CPU usage}
# @~
def attribute_cpu(proc_cpu, ec_cpu):
    if not ec_cpu:
        return {}
    total = sum(max(0.0, v) for v in ec_cpu.values())
    rest = max(0.0, proc_cpu - total)
    out = {}
    for k, v in ec_cpu.items():
        v = max(0.0, v)
        share = (v / total) if total > 0 else 1.0 / len(ec_cpu)
        out[k] = v + rest * share
    return out


##
# @~japanese
# @brief USS の増分 (uss - baseline) を RTC ごとに分ける
#
# @param uss_mb プロセスの USS (MB)
# @param baseline_mb 最初の RTC を置く直前の USS (MB)
# @param increments {RTC: 生成したときの増分 MB}
# @return {RTC: メモリ (MB)}
# @~english
# @brief Divides the USS increment (uss - baseline) among the RTCs
#
# @param uss_mb USS of the process (MB)
# @param baseline_mb USS just before the first RTC was created (MB)
# @param increments {RTC: increment at creation in MB}
# @return {RTC: memory (MB)}
# @~
def attribute_memory(uss_mb, baseline_mb, increments):
    if not increments:
        return {}
    grown = max(0.0, uss_mb - baseline_mb)
    inc = {k: max(0.0, v) for k, v in increments.items()}
    total = sum(inc.values())
    return {k: grown * ((v / total) if total > 0 else 1.0 / len(inc)) for k, v in inc.items()}


##
# @~japanese
# @brief 標本の平均・最大・95 パーセンタイルを求める (標本がなければ値は None)
#
# @param values 標本
# @return {"avg", "max", "p95"}
# @~english
# @brief Computes the average, maximum and 95th percentile of samples (None if there are no samples)
#
# @param values samples
# @return {"avg", "max", "p95"}
# @~
def summarize(values):
    if not values:
        return {"avg": None, "max": None, "p95": None}
    s = sorted(values)
    p95 = s[min(len(s) - 1, int(round(0.95 * (len(s) - 1))))]
    return {"avg": round(sum(s) / len(s), 3), "max": round(s[-1], 3), "p95": round(p95, 3)}


# ---------------------------------------------------------------------------
# 保存 (マスターの SNMPManager が使う。OpenRTM に依存しない)
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief slave の計測ファイル (data) の RTC を runs ({キー: 計測 1 回分}) に入れる
#
# @param runs {キー: 計測 1 回分}
# @param robot ロボット名
# @param data 計測ファイルの内容
# @return 更新したキーの一覧
# @~english
# @brief Puts the RTCs in a slave's measurement file (data) into runs ({key: one measurement run})
#
# @param runs {key: one measurement run}
# @param robot robot name
# @param data contents of the measurement file
# @return list of updated keys
# @~
def update_runs(runs, robot, data):
    changed = []
    for inst, c in (data.get("components") or {}).items():
        inst = c.get("instance") or inst
        key = f"{data.get('manager')}/{inst}/{int(c.get('created') or 0)}"
        rec = dict(c, robot=robot, manager=data.get("manager"), instance=inst,
                   baseline_uss_mb=data.get("baseline_uss_mb"), updated=data.get("updated"))
        old = runs.get(key)
        if old is not None and old.get("samples") == rec.get("samples") and old.get("ports") == rec.get("ports"):
            continue
        runs[key] = rec
        changed.append(key)
    return changed


##
# @~japanese
# @brief runs を (言語, 型名) ごとにまとめる。新しい max_runs 回分、標本数が min_samples 以上の回だけ使う
#
# @param runs {キー: 計測 1 回分}
# @param min_samples 使う回の最小の標本数
# @param max_runs 使う回の数
# @param cpu_stat CPU の値に使う統計 (avg / max / p95)
# @return {(言語, 型名): まとめた結果}
# @~english
# @brief Aggregates runs by (language, type name). Uses only the latest max_runs runs with at least min_samples samples
#
# @param runs {key: one measurement run}
# @param min_samples minimum number of samples of a run to use
# @param max_runs number of runs to use
# @param cpu_stat statistic used for the CPU value (avg / max / p95)
# @return {(language, type name): aggregated result}
# @~
def aggregate(runs, min_samples=10, max_runs=20, cpu_stat="max"):
    groups = collections.defaultdict(list)
    for r in runs.values():
        if (r.get("samples") or 0) >= min_samples and r.get("cpu", {}).get("max") is not None:
            groups[(r.get("language") or "Python", r.get("type"))].append(r)
    out = {}
    for key, rs in groups.items():
        rs = sorted(rs, key=lambda r: r.get("updated") or 0)[-max_runs:]
        n = sum(r["samples"] for r in rs)

        def wavg(field):
            return round(sum(r[field]["avg"] * r["samples"] for r in rs) / n, 3)

        cpu = {"avg": wavg("cpu"), "max": max(r["cpu"]["max"] for r in rs), "p95": max(r["cpu"]["p95"] for r in rs)}
        mem = {"avg": wavg("memory_mb"), "max": max(r["memory_mb"]["max"] for r in rs)}
        ports = {}
        for r in rs:
            for name, p in (r.get("ports") or {}).items():
                q = ports.setdefault(name, {"direction": p.get("direction"), "msgs": 0, "bytes": 0,
                                            "bytes_max": 0, "hz": 0.0})
                q["msgs"] += p.get("msgs") or 0
                q["bytes"] += p.get("bytes") or 0
                q["bytes_max"] = max(q["bytes_max"], p.get("bytes_max") or 0)
                q["hz"] = max(q["hz"], p.get("hz") or 0.0)
        for q in ports.values():
            q["bytes_per_msg"] = round(q["bytes"] / q["msgs"], 2) if q["msgs"] else None
        out[key] = {"language": key[0], "type": key[1], "impl": rs[-1].get("impl"), "runs": len(rs), "samples": n,
                    "interval": rs[-1].get("interval"), "cpu": cpu, "memory_mb": mem,
                    "cpu_value": cpu.get(cpu_stat, cpu["max"]),
                    "baseline_uss_mb": max((r.get("baseline_uss_mb") or 0.0) for r in rs),
                    "robots": sorted({r.get("robot") for r in rs if r.get("robot")}),
                    "instances": sorted({r.get("instance") for r in rs}),
                    "updated": max(r.get("updated") or 0 for r in rs), "ports": ports, "cpu_stat": cpu_stat}
    return out


##
# @~japanese
# @brief aggregate() の 1 件を placement.xml (RTCPlacement.py の ProfileDB が読む形式) にする
#
# @param agg aggregate() の 1 件
# @param environment 環境の名前
# @param robot ロボット名
# @return XML の文字列
# @~english
# @brief Renders one item of aggregate() as placement.xml (the format read by ProfileDB in RTCPlacement.py)
#
# @param agg one item of aggregate()
# @param environment name of the environment
# @param robot robot name
# @return XML string
# @~
def render_placement(agg, environment, robot):
    from xml.sax.saxutils import quoteattr as q

    def a(name, value):
        return f' plc:{name}={q(str(value))}'

    date = time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(agg["updated"] or time.time()))
    L = ['<?xml version="1.0" encoding="UTF-8"?>',
         f'<!-- SNMPManager が実行中に計測した値 (SlaveMeasureModule)。{robot} の RTC: {", ".join(agg["instances"])} -->',
         '<plc:RtcPlacement xmlns:plc="urn:snmpmanager:placement:1"' + a("rtc", agg["type"])
         + a("rtcId", agg.get("impl") or agg["type"]) + a("language", agg["language"])
         + a("origin", "runtime") + a("robot", robot) + '>',
         '  <plc:Measurements>',
         '    <plc:Measurement' + a("environment", environment) + a("status", "ok") + a("date", date)
         + a("samples", agg["samples"]) + a("runs", agg["runs"]) + a("intervalSec", agg.get("interval") or "")
         + a("durationSec", round(agg["samples"] * (agg.get("interval") or 0), 1)) + '>',
         '      <plc:Resources' + a("cpu", round(agg["cpu_value"], 2)) + a("memoryMb", round(agg["memory_mb"]["max"], 2))
         + a("basis", f'measured by the manager: cpu={agg["cpu_stat"]} of the RTC share, '
                      'memory=max USS - empty manager USS (RTC share)') + '/>',
         '      <plc:Cpu' + a("avg", agg["cpu"]["avg"]) + a("max", agg["cpu"]["max"]) + a("p95", agg["cpu"]["p95"])
         + a("unit", "percent-of-one-core") + '/>',
         '      <plc:Memory plc:unit="MB">',
         '        <plc:Uss' + a("avg", agg["memory_mb"]["avg"]) + a("max", agg["memory_mb"]["max"])
         + a("baseline", round(agg["baseline_uss_mb"], 2)) + '/>',
         '      </plc:Memory>']
    for name, p in sorted(agg["ports"].items()):
        if not p["msgs"]:
            continue
        L.append('      <plc:PortObservation' + a("name", name) + a("bytesPerMsg", p["bytes_per_msg"])
                 + a("bytesPerMsgMax", p["bytes_max"]) + a("hz", p["hz"]) + a("msgs", p["msgs"]) + '/>')
    L += ['    </plc:Measurement>', '  </plc:Measurements>', '  <plc:Ports>']
    for name, p in sorted(agg["ports"].items()):
        size = a("bytesPerMsg", p["bytes_per_msg"]) if p["bytes_per_msg"] is not None else ""
        L.append('    <plc:Port' + a("name", name) + a("direction", p["direction"]) + a("basis", "measured") + size + '/>')
    L += ['  </plc:Ports>', '</plc:RtcPlacement>', '']
    return "\n".join(L)


##
# @~japanese
# @brief ファイル名に使えない文字を置き換える
#
# @param text 文字列
# @return ファイル名に使える文字列
# @~english
# @brief Replaces characters that cannot be used in file names
#
# @param text string
# @return string usable as a file name
# @~
def safe_name(text):
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in str(text)) or "_"


# ---------------------------------------------------------------------------
# プロセスの情報
# ---------------------------------------------------------------------------
_CLK = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100


##
# @~japanese
# @brief 自分のプロセスの CPU 時間・スレッドごとの CPU 時間・USS を読む
# @~english
# @brief Reads the CPU time, per-thread CPU time and USS of this process
# @~
class ProcInfo:

    ##
    # @~japanese
    # @brief コンストラクタ
    # @~english
    # @brief Constructor
    # @~
    def __init__(self):
        self._p = psutil.Process() if psutil is not None else None

    ##
    # @~japanese
    # @brief プロセスの CPU 時間を返す
    #
    # @return CPU 秒
    # @~english
    # @brief Returns the CPU time of the process
    #
    # @return CPU seconds
    # @~
    def cpu_seconds(self):
        if self._p is not None:
            t = self._p.cpu_times()
            return t.user + t.system
        t = os.times()
        return t.user + t.system

    ##
    # @~japanese
    # @brief スレッドごとの CPU 時間を返す
    #
    # @return {ネイティブのスレッド ID: CPU 秒}
    # @~english
    # @brief Returns the CPU time of each thread
    #
    # @return {native thread ID: CPU seconds}
    # @~
    def thread_seconds(self):
        if self._p is not None:
            try:
                return {t.id: t.user_time + t.system_time for t in self._p.threads()}
            except Exception:
                return {}
        out = {}
        try:
            for tid in os.listdir("/proc/self/task"):
                with open(f"/proc/self/task/{tid}/stat") as f:
                    fields = f.read().rsplit(")", 1)[1].split()
                out[int(tid)] = (int(fields[11]) + int(fields[12])) / _CLK
        except OSError:
            pass
        return out

    ##
    # @~japanese
    # @brief プロセスの USS を返す
    #
    # @return USS (MB)
    # @~english
    # @brief Returns the USS of the process
    #
    # @return USS (MB)
    # @~
    def uss_mb(self):
        if self._p is not None:
            try:
                return self._p.memory_full_info().uss / MB
            except Exception:
                return self._p.memory_info().rss / MB
        try:
            total = 0
            with open("/proc/self/smaps_rollup") as f:
                for line in f:
                    if line.startswith(("Private_Clean:", "Private_Dirty:")):
                        total += int(line.split()[1])
            return total / 1024.0
        except OSError:
            return 0.0


# ---------------------------------------------------------------------------
# データポートのリスナー
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief 1 つのポートの送受信 (コネクタごとの回数と、バイト数) を数える
# @~english
# @brief Counts the data sent/received by one port (count and bytes per connector)
# @~
class PortCounter:

    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param name ポートの名前
    # @param direction in / out
    # @~english
    # @brief Constructor
    #
    # @param name port name
    # @param direction in / out
    # @~
    def __init__(self, name, direction):
        self.name = name
        self.direction = direction
        self.lock = threading.Lock()
        self.msgs = 0
        self.bytes = 0
        self.bytes_max = 0
        self.per_connector = collections.Counter()
        self.first = None
        self.last = None

    ##
    # @~japanese
    # @brief 1 回の送受信を足す
    #
    # @param connector_id コネクタの ID
    # @param size バイト数
    # @~english
    # @brief Adds one transmission
    #
    # @param connector_id connector ID
    # @param size number of bytes
    # @~
    def add(self, connector_id, size):
        now = time.monotonic()
        with self.lock:
            self.msgs += 1
            self.bytes += size
            self.bytes_max = max(self.bytes_max, size)
            self.per_connector[connector_id] += 1
            if self.first is None:
                self.first = now
            self.last = now

    ##
    # @~japanese
    # @brief 現在の値を返す
    #
    # @return {"direction", "msgs", "bytes", "bytes_per_msg", "bytes_max", "connectors" (コネクタの数), "hz"}
    # @~english
    # @brief Returns the current values
    #
    # @return {"direction", "msgs", "bytes", "bytes_per_msg", "bytes_max", "connectors" (number of connectors), "hz"}
    # @~
    def snapshot(self):
        with self.lock:
            span = (self.last - self.first) if (self.first is not None and self.last is not None) else 0.0
            busiest = max(self.per_connector.values()) if self.per_connector else 0
            # 周期は、いちばん多く送受信したコネクタの回数から求める (1 つのポートに複数のコネクタがあっても重ねない)
            hz = (busiest - 1) / span if span > 0 and busiest > 1 else 0.0
            return {"direction": self.direction, "msgs": self.msgs, "bytes": self.bytes,
                    "bytes_per_msg": round(self.bytes / self.msgs, 2) if self.msgs else None,
                    "bytes_max": self.bytes_max, "connectors": len(self.per_connector), "hz": round(hz, 3)}


##
# @~japanese
# @brief ポートの送受信を数えるコネクタのデータリスナーを作る
#
# @param counter PortCounter
# @return リスナー
# @~english
# @brief Makes a connector data listener that counts the data of a port
#
# @param counter PortCounter
# @return listener
# @~
def _make_listener(counter):
    import OpenRTM_aist

    class _Listener(OpenRTM_aist.ConnectorDataListener):
        def __call__(self, info, cdrdata):
            try:
                size = len(cdrdata) if isinstance(cdrdata, (bytes, bytearray, memoryview)) else 0
                counter.add(getattr(info, "id", "") or getattr(info, "name", ""), size)
            except Exception:
                pass
            return OpenRTM_aist.ConnectorListenerStatus.NO_CHANGE, cdrdata
    return _Listener()


# ---------------------------------------------------------------------------
# 計測
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief マネージャの RTC の CPU・メモリ・データポートを計測し、ファイルに書き出す
# @~english
# @brief Measures the CPU, memory and data ports of the RTCs in the manager and writes them to a file
# @~
class Measure:
    ##
    # @~japanese
    # @brief コンストラクタ。計測のスレッドを起動する
    #
    # @param manager マネージャ
    # @param conf rtc.conf の設定
    # @~english
    # @brief Constructor. Starts the measurement thread
    #
    # @param manager manager
    # @param conf settings of rtc.conf
    # @~
    def __init__(self, manager, conf):
        self._mgr = manager
        self._conf = conf
        self._name = conf.getProperty("manager.instance_name", "") or f"manager_{os.getpid()}"
        self._dir = conf.getProperty("snmp.measure.runtime_dir", "/run/rtm/measure")
        self._interval = float(conf.getProperty("snmp.measure.interval", "1.0"))
        self._warmup = float(conf.getProperty("snmp.measure.warmup", "3"))
        self._write_interval = float(conf.getProperty("snmp.measure.write_interval", "5"))
        self._language = conf.getProperty("manager.language", "Python") or "Python"
        self._proc = ProcInfo()
        self._lock = threading.RLock()
        self._comps = {}             # id(RTC) -> 記録 (インスタンス名は生成の後で付くので、毎回 RTC から読む)
        self._pending_uss = None     # preCreate のときの USS
        self._baseline = self._proc.uss_mb()   # RTC を置く前のマネージャ (空マネージャ)
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    # ------------------------------------------------------------ RTC の生成
    ##
    # @~japanese
    # @brief RTC を生成する直前に呼ばれ、USS を記録する
    # @~english
    # @brief Called just before an RTC is created; records the USS
    # @~
    def pre_create(self):
        self._pending_uss = self._proc.uss_mb()
        with self._lock:
            if not self._comps:
                # 最初の RTC を置く直前の USS を空マネージャの値にする (preload の時点より、起動の一時的な分が減っている)
                self._baseline = self._pending_uss

    ##
    # @~japanese
    # @brief 生成した RTC を記録する
    #
    # @param rtobj RTC
    # @param increment 生成したときの USS の増分 (None なら pre_create との差)
    # @~english
    # @brief Records a created RTC
    #
    # @param rtobj RTC
    # @param increment USS increment at creation (difference from pre_create if None)
    # @~
    def post_create(self, rtobj, increment=None):
        if rtobj is None:
            return
        try:
            props = rtobj.getProperties()
            rec = {"rtobj": rtobj, "type": rtobj.getTypeName(),
                   "impl": props.getProperty("implementation_id") or rtobj.getTypeName(),
                   "language": props.getProperty("language") or self._language,
                   "created": time.time(),
                   "increment": max(0.0, self._proc.uss_mb() - (self._pending_uss or self._baseline))
                   if increment is None else increment,
                   "ports": {}, "cpu": collections.deque(maxlen=MAX_SAMPLES),
                   "mem": collections.deque(maxlen=MAX_SAMPLES), "ec_prev": {}, "active_since": None,
                   "active_seconds": 0.0, "removed": False, "name": rtobj.getInstanceName()}
            with self._lock:
                self._comps.setdefault(id(rtobj), rec)
        except Exception as exc:
            print(f"[SlaveMeasureModule] post_create failed: {exc}", flush=True)

    ##
    # @~japanese
    # @brief まだリスナーを付けていないポートに付ける (ポートは onInitialize で作られるので、標本ごとに確かめる)
    #
    # @param rtobj RTC
    # @param rec RTC の記録
    # @~english
    # @brief Attaches listeners to ports that do not have them yet (ports are created in onInitialize, so this is checked for each sample)
    #
    # @param rtobj RTC
    # @param rec record of the RTC
    # @~
    def _attach_ports(self, rtobj, rec):
        import OpenRTM_aist
        T = OpenRTM_aist.ConnectorDataListenerType
        try:
            ports = rtobj._portAdmin._portServants.getObjects()
        except Exception:
            ports = []
        for port in ports:
            try:
                short = port.getName().split(".")[-1]
                if short in rec["ports"]:
                    continue
                if isinstance(port, OpenRTM_aist.InPortBase):
                    counter = PortCounter(short, "in")
                    port.addConnectorDataListener(T.ON_RECEIVED, _make_listener(counter))
                elif isinstance(port, OpenRTM_aist.OutPortBase):
                    counter = PortCounter(short, "out")
                    port.addConnectorDataListener(T.ON_SEND, _make_listener(counter))
                else:
                    continue
                rec["ports"][short] = counter
            except Exception as exc:
                print(f"[SlaveMeasureModule] port listener failed: {exc}", flush=True)

    # ------------------------------------------------------------ 標本
    ##
    # @~japanese
    # @brief RTC の実行コンテキストのスレッドを返す
    #
    # @param rtobj RTC
    # @return ネイティブのスレッド ID のリスト
    # @~english
    # @brief Returns the execution context threads of an RTC
    #
    # @param rtobj RTC
    # @return list of native thread IDs
    # @~
    @staticmethod
    def _ec_threads(rtobj):
        out = []
        for ec in list(getattr(rtobj, "_eclist", []) or []):
            th = getattr(ec, "_thread", None)
            tid = getattr(th, "native_id", None)
            if tid is not None:
                out.append(tid)
        return out

    ##
    # @~japanese
    # @brief RTC がアクティブか
    #
    # @param rtobj RTC
    # @return アクティブなら True
    # @~english
    # @brief Whether the RTC is active
    #
    # @param rtobj RTC
    # @return True if active
    # @~
    @staticmethod
    def _is_active(rtobj):
        import RTC
        try:
            ec = rtobj.getExecutionContext(0)
            return ec.get_component_state(rtobj.getObjRef()) == RTC.ACTIVE_STATE
        except Exception:
            return False

    ##
    # @~japanese
    # @brief マネージャの RTC を返す。記録していない RTC (このモジュールを読み込む前に生成されたもの) も記録する
    #
    # slave は登録した直後にマスターから create_component を受けるので、preload より先に RTC ができることがある。その場合、生成したときの増分は分からないので 0 とする (メモリは増えた分を等分する)。
    #
    # @return RTC の ID の集合
    # @~english
    # @brief Returns the RTCs of the manager. Also records RTCs not yet recorded (created before this module was loaded)
    #
    # A slave receives create_component from the master right after it registers, so an RTC may be created before preload. In that case the increment at creation is unknown and is set to 0 (the increased memory is divided equally).
    #
    # @return set of RTC IDs
    # @~
    def _alive_ids(self):
        try:
            comps = list(self._mgr.getComponents())
        except Exception:
            return None
        for c in comps:
            if id(c) not in self._comps:
                self.post_create(c, increment=0.0)
        return {id(c) for c in comps}

    ##
    # @~japanese
    # @brief 計測のスレッドの本体 (snmp.measure.interval 秒ごとに標本を取り、書き出す)
    # @~english
    # @brief Body of the measurement thread (takes a sample and writes it every snmp.measure.interval seconds)
    # @~
    def _loop(self):
        prev_t, prev_cpu = time.monotonic(), self._proc.cpu_seconds()
        last_write = 0.0
        while self._running:
            time.sleep(self._interval)
            try:
                now, cpu = time.monotonic(), self._proc.cpu_seconds()
                dt = max(1e-6, now - prev_t)
                proc_cpu = 100.0 * (cpu - prev_cpu) / dt
                prev_t, prev_cpu = now, cpu
                self._sample(now, dt, proc_cpu)
                if now - last_write >= self._write_interval:
                    self.write()
                    last_write = now
            except Exception as exc:
                print(f"[SlaveMeasureModule] sample failed: {exc}", flush=True)

    ##
    # @~japanese
    # @brief 標本を 1 つ取る
    #
    # @param now 現在の時刻
    # @param dt 前の標本からの秒数
    # @param proc_cpu プロセス全体の CPU 使用率
    # @~english
    # @brief Takes one sample
    #
    # @param now current time
    # @param dt seconds since the previous sample
    # @param proc_cpu CPU usage of the whole process
    # @~
    def _sample(self, now, dt, proc_cpu):
        threads = self._proc.thread_seconds()
        uss = self._proc.uss_mb()
        alive = self._alive_ids()
        with self._lock:
            live = {}
            for key, rec in self._comps.items():
                if rec["removed"]:
                    continue
                if alive is not None and key not in alive:
                    rec["removed"] = True
                    rec["removed_at"] = time.time()
                    continue
                try:
                    rec["name"] = rec["rtobj"].getInstanceName()
                except Exception:
                    pass
                self._attach_ports(rec["rtobj"], rec)
                live[key] = rec
            ec_cpu = {}
            for name, rec in live.items():
                used = 0.0
                for tid in self._ec_threads(rec["rtobj"]):
                    t = threads.get(tid)
                    if t is None:
                        continue
                    p = rec["ec_prev"].get(tid)
                    if p is not None:
                        used += 100.0 * max(0.0, t - p) / dt
                    rec["ec_prev"][tid] = t
                ec_cpu[name] = used
            cpu_of = attribute_cpu(proc_cpu, ec_cpu)
            mem_of = attribute_memory(uss, self._baseline, {n: r["increment"] for n, r in live.items()})
            for name, rec in live.items():
                if not self._is_active(rec["rtobj"]):
                    rec["active_since"] = None
                    continue
                if rec["active_since"] is None:
                    rec["active_since"] = now
                    continue
                rec["active_seconds"] += dt
                if now - rec["active_since"] < self._warmup:
                    continue
                rec["cpu"].append(cpu_of.get(name, 0.0))
                # 生成したときの増分を下回らない (Python は後で解放して USS が減ることがある)
                rec["mem"].append(max(rec["increment"], mem_of.get(name, 0.0)))
            self._last = {"proc_cpu": round(proc_cpu, 3), "uss_mb": round(uss, 3)}

    # ------------------------------------------------------------ 書き出し
    ##
    # @~japanese
    # @brief 計測の結果を返す
    #
    # @return 計測ファイルの内容
    # @~english
    # @brief Returns the measurement results
    #
    # @return contents of the measurement file
    # @~
    def snapshot(self):
        with self._lock:
            comps = {}
            for rec in sorted(self._comps.values(), key=lambda r: r["created"]):
                key = rec["name"]
                if key in comps:          # 同じ名前で作り直した RTC: 前の分は別のキーで残す
                    prev = comps.pop(key)
                    comps[f"{key}#{int(prev['created'])}"] = prev
                comps[key] = {
                    "instance": rec["name"], "type": rec["type"], "impl": rec["impl"], "language": rec["language"],
                    "created": rec["created"], "removed": rec["removed"],
                    "samples": len(rec["cpu"]), "interval": self._interval,
                    "active_seconds": round(rec["active_seconds"], 2),
                    "increment_mb": round(rec["increment"], 3),
                    "cpu": summarize(list(rec["cpu"])), "memory_mb": summarize(list(rec["mem"])),
                    "ports": {p: c.snapshot() for p, c in rec["ports"].items()}}
            return {"manager": self._name, "pid": os.getpid(), "language": self._language,
                    "updated": time.time(), "baseline_uss_mb": round(self._baseline, 3),
                    "process": getattr(self, "_last", {}), "components": comps}

    ##
    # @~japanese
    # @brief 計測の結果をファイルに書き出す
    # @~english
    # @brief Writes the measurement results to the file
    # @~
    def write(self):
        data = self.snapshot()
        if not data["components"]:
            return
        os.makedirs(self._dir, exist_ok=True)
        path = os.path.join(self._dir, f"{self._name}.json")
        tmp = path + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        os.replace(tmp, path)

    ##
    # @~japanese
    # @brief 計測を止めて、最後の結果を書き出す
    # @~english
    # @brief Stops the measurement and writes the final results
    # @~
    def stop(self):
        self._running = False
        try:
            self.write()
        except Exception:
            pass


_measure = None


##
# @~japanese
# @brief manager.modules.preload で読み込まれたときの入口 (ファイル名 SlaveMeasureModule.py でも読めるように別名も置く)
#
# @param manager マネージャ
# @~english
# @brief Entry point when loaded by manager.modules.preload (an alias is also defined so that it can be loaded by the file name SlaveMeasureModule.py)
#
# @param manager manager
# @~
def SNMPMeasureInit(manager):
    global _measure
    conf = manager.getConfig()
    if conf.getProperty("snmp.measure.enabled", "NO").strip().upper() != "YES":
        return
    if (conf.getProperty("manager.is_master", "NO").strip().upper() == "YES"
            and conf.getProperty("snmp.measure.master", "NO").strip().upper() != "YES"):
        return
    if _measure is not None:
        return
    _measure = Measure(manager, conf)
    print(f"[SlaveMeasureModule] measuring RTCs of {_measure._name} (pid {os.getpid()}) -> {_measure._dir}", flush=True)
    try:   # kill -USR1 <pid> でスレッドのスタックを出す (調査用)
        import faulthandler
        import signal
        import sys
        faulthandler.register(signal.SIGUSR1, file=sys.stderr, all_threads=True)
    except Exception:
        pass

    lifecycle, shutdown = make_listeners(_measure)
    manager.addRtcLifecycleActionListener(lifecycle)
    manager.addManagerActionListener(shutdown)


##
# @~japanese
# @brief RTC の生成とマネージャの終了のリスナーを作る
#
# @param measure Measure
# @return リスナー
# @~english
# @brief Makes the listeners for RTC creation and manager shutdown
#
# @param measure Measure
# @return listeners
# @~
def make_listeners(measure):
    import OpenRTM_aist

    class _Lifecycle(OpenRTM_aist.RtcLifecycleActionListener):
        def preCreate(self, args):
            measure.pre_create()
            return args          # 戻り値が生成の引数になる (None を返すと生成できない)

        def postCreate(self, rtobj):
            measure.post_create(rtobj)

    class _Shutdown(OpenRTM_aist.ManagerActionListener):
        def preShutdown(self):
            measure.stop()

    return _Lifecycle(), _Shutdown()


SlaveMeasureModuleInit = SNMPMeasureInit
