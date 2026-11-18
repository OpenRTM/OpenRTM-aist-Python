#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file MonitoringStore.py
# @brief Stores the monitoring information of SNMPManager (metrics and events) in SQLite
#
# @~japanese
# SNMPManager の監視情報 (メトリクスとイベント) を SQLite に保存する
#
# SNMPManager からは MetricsStore を使う。書き込みは専用スレッドで行うので、呼び出し側 (SNMP のポーリングやトラップ受信) を待たせない。
# コマンドとして中身を確認できる (使い方はモジュールの docstring)。
# @~english
# SNMPManager uses MetricsStore. Writes are done on a dedicated thread, so the callers (SNMP polling and trap reception) do not wait.
# The contents can be shown as a command (see the module docstring for the usage).
# @~
#
# @date $Date: 2026-11-13 16:24:34 $
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

"""SNMPManager の監視情報 (メトリクスとイベント) を SQLite に保存する。

SNMPManager からは MetricsStore を使う。書き込みは専用スレッドで行うので、
呼び出し側 (SNMP のポーリングやトラップ受信) を待たせない。

コマンドとして中身を確認できる:
  python3 MonitoringStore.py <db> latest              各ロボットの最新のメトリクス
  python3 MonitoringStore.py <db> events [件数]       最近のイベント (DOWN/UP、起動、マイグレーションなど)
  python3 MonitoringStore.py <db> history <ロボット> [件数]   そのロボットのメトリクスの推移
  python3 MonitoringStore.py <db> measurements [件数]  マネージャが計測した RTC の実測値 (新しいもの)
  python3 MonitoringStore.py <db> custom [ロボット] [件数]  追加の監視の値 (snmp.metrics) の推移
"""
import os
import queue
import sqlite3
import sys
import threading
import time

METRIC_COLUMNS = (
    "status", "cpu_usage", "memory_usage", "network_in", "network_out", "wifi_signal_dbm",
    "latency_ms", "jitter_ms", "packet_loss", "cg_cpu_usage", "cg_cpu_limit", "cg_mem_usage_mb", "cg_mem_limit_mb",
)

COLUMN_PLACEHOLDERS = ",".join("?" * (4 + len(METRIC_COLUMNS)))  # ts, observer, robot, ip + 指標

SCHEMA = """
CREATE TABLE IF NOT EXISTS metrics (
    ts REAL NOT NULL,           -- UNIX 時刻 (秒)
    observer TEXT NOT NULL,     -- 記録したマネージャ (自分のロボット名)
    robot TEXT NOT NULL,
    ip TEXT,
    status TEXT,                -- alive / dead / unknown
    cpu_usage REAL, memory_usage REAL, network_in REAL, network_out REAL, wifi_signal_dbm REAL,
    latency_ms REAL, jitter_ms REAL, packet_loss REAL,
    cg_cpu_usage REAL, cg_cpu_limit REAL, cg_mem_usage_mb REAL, cg_mem_limit_mb REAL
);
CREATE INDEX IF NOT EXISTS metrics_robot_ts ON metrics (robot, ts);
CREATE TABLE IF NOT EXISTS events (
    ts REAL NOT NULL,
    observer TEXT NOT NULL,
    robot TEXT,
    kind TEXT NOT NULL,         -- discovered / down / up / startup_completed / startup_failed / migration_* など
    detail TEXT
);
CREATE INDEX IF NOT EXISTS events_ts ON events (ts);
CREATE TABLE IF NOT EXISTS rtc_measurements (
    ts REAL NOT NULL,
    observer TEXT NOT NULL,
    robot TEXT,                 -- RTC が動いていたロボット
    manager TEXT,               -- slave マネージャ名
    instance TEXT, type TEXT, language TEXT,
    samples INTEGER,            -- CPU とメモリの標本数 (アクティブで、warmup の後)
    cpu_avg REAL, cpu_max REAL, cpu_p95 REAL,   -- 1 コア = 100
    mem_avg_mb REAL, mem_max_mb REAL,           -- USS の増分 (RTC の分)
    ports TEXT                  -- JSON: {ポート名: {direction, msgs, bytes, bytes_per_msg, bytes_max, hz}}
);
CREATE INDEX IF NOT EXISTS rtc_measurements_type ON rtc_measurements (type, ts);
CREATE TABLE IF NOT EXISTS custom_metrics (
    ts REAL NOT NULL,
    observer TEXT NOT NULL,
    robot TEXT NOT NULL,
    name TEXT NOT NULL,         -- 追加の監視の値の名前 (rtc.conf の snmp.metrics)
    value REAL                  -- 取れなければ NULL
);
CREATE INDEX IF NOT EXISTS custom_metrics_robot_ts ON custom_metrics (robot, name, ts);
"""


##
# @~japanese
# @brief 値を数値にする (数値にできなければ None)
#
# @param value 値
# @return 数値 (または None)
# @~english
# @brief Converts a value into a number (None if it cannot be converted)
#
# @param value value
# @return number (or None)
# @~
def _num(value):
    try:
        return None if value is None else float(value)
    except (TypeError, ValueError):
        return None


##
# @~japanese
# @brief 監視情報を SQLite に保存する (書き込みは専用スレッド)
# @~english
# @brief Stores monitoring information in SQLite (writes are done on a dedicated thread)
# @~
class MetricsStore:
    ##
    # @~japanese
    # @brief コンストラクタ。データベースを開き、書き込みのスレッドを起動する
    #
    # @param path SQLite のファイル
    # @param observer 記録するロボット (自分) の名前
    # @param retention_hours 古い行を消すまでの時間 (時間)
    # @~english
    # @brief Constructor. Opens the database and starts the writer thread
    #
    # @param path SQLite file
    # @param observer name of the recording robot (this one)
    # @param retention_hours hours to keep rows before deleting them
    # @~
    def __init__(self, path, observer, retention_hours=24.0):
        self.path = path
        self.observer = observer
        self.retention = float(retention_hours) * 3600.0
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._ready = threading.Event()
        self._error = None
        d = os.path.dirname(os.path.abspath(path))
        os.makedirs(d, exist_ok=True)
        self._thread.start()
        self._ready.wait(10)
        if self._error:
            raise self._error

    # ---------------------------------------------------------------- API
    ##
    # @~japanese
    # @brief ロボットのメトリクスを記録する
    #
    # @param rows [{"robot", "ip", "status", \<METRIC_COLUMNS\>...}]
    # @~english
    # @brief Records metrics of robots
    #
    # @param rows [{"robot", "ip", "status", \<METRIC_COLUMNS\>...}]
    # @~
    def record_metrics(self, rows):
        now = time.time()
        self._queue.put(("metrics", [(now, self.observer, r.get("robot"), r.get("ip"), r.get(
            "status")) + tuple(_num(r.get(c)) for c in METRIC_COLUMNS[1:]) for r in rows]))

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
    def record_event(self, robot, kind, detail=""):
        self._queue.put(("event", (time.time(), self.observer, robot, kind, detail)))

    ##
    # @~japanese
    # @brief マネージャが計測した RTC の実測値を記録する
    #
    # @param runs SlaveMeasureModule.update_runs() で更新した計測 1 回分の一覧
    # @~english
    # @brief Records the RTC measurements made by the managers
    #
    # @param runs list of measurement runs updated by SlaveMeasureModule.update_runs()
    # @~
    def record_measurements(self, runs):
        import json
        now = time.time()
        rows = []
        for r in runs:
            cpu, mem = r.get("cpu") or {}, r.get("memory_mb") or {}
            rows.append((now, self.observer, r.get("robot"), r.get("manager"), r.get("instance"), r.get("type"),
                         r.get("language"), r.get("samples"), _num(cpu.get("avg")), _num(cpu.get("max")),
                         _num(cpu.get("p95")), _num(mem.get("avg")), _num(mem.get("max")),
                         json.dumps(r.get("ports") or {}, ensure_ascii=False)))
        if rows:
            self._queue.put(("measurements", rows))

    ##
    # @~japanese
    # @brief 追加の監視の値を記録する (1 ロボット・1 指標で 1 行)
    #
    # @param rows [{"robot", "metrics": {名前: 値}}]
    # @~english
    # @brief Records additional monitoring values (one row per robot and metric)
    #
    # @param rows [{"robot", "metrics": {name: value}}]
    # @~
    def record_custom_metrics(self, rows):
        now = time.time()
        out = [(now, self.observer, r.get("robot"), name, _num(v))
               for r in rows for name, v in sorted((r.get("metrics") or {}).items())]
        if out:
            self._queue.put(("custom", out))

    ##
    # @~japanese
    # @brief 書き込みのスレッドを止めて、データベースを閉じる
    # @~english
    # @brief Stops the writer thread and closes the database
    # @~
    def close(self):
        self._queue.put(("stop", None))
        self._thread.join(timeout=5)

    # ---------------------------------------------------------------- writer
    ##
    # @~japanese
    # @brief 書き込みのスレッドの本体
    # @~english
    # @brief Body of the writer thread
    # @~
    def _run(self):
        try:
            conn = sqlite3.connect(self.path)
            conn.executescript(SCHEMA)
            conn.commit()
        except Exception as exc:
            self._error = exc
            self._ready.set()
            return
        self._ready.set()
        last_cleanup = 0.0
        while True:
            kind, payload = self._queue.get()
            if kind == "stop":
                break
            try:
                self._write(conn, kind, payload)
                # まとめて書けるものはまとめる
                while not self._queue.empty():
                    k2, p2 = self._queue.get_nowait()
                    if k2 == "stop":
                        self._queue.put((k2, p2))
                        break
                    self._write(conn, k2, p2)
                conn.commit()
                if self.retention > 0 and time.time() - last_cleanup > 600:
                    limit = time.time() - self.retention
                    conn.execute("DELETE FROM metrics WHERE ts < ?", (limit,))
                    conn.execute("DELETE FROM events WHERE ts < ?", (limit,))
                    conn.execute("DELETE FROM rtc_measurements WHERE ts < ?", (limit,))
                    conn.execute("DELETE FROM custom_metrics WHERE ts < ?", (limit,))
                    conn.commit()
                    last_cleanup = time.time()
            except Exception as exc:  # 保存に失敗しても監視は止めない
                print("[MonitoringStore] write failed: %s" % exc, file=sys.stderr, flush=True)
        conn.close()

    ##
    # @~japanese
    # @brief 1 件を書き込む
    #
    # @param conn データベースの接続
    # @param kind 書き込むものの種別
    # @param payload 書き込む内容
    # @~english
    # @brief Writes one item
    #
    # @param conn database connection
    # @param kind kind of the item
    # @param payload contents to write
    # @~
    @staticmethod
    def _write(conn, kind, payload):
        if kind == "metrics":
            conn.executemany("INSERT INTO metrics VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", payload)
        elif kind == "event":
            conn.execute("INSERT INTO events VALUES (?,?,?,?,?)", payload)
        elif kind == "measurements":
            conn.executemany("INSERT INTO rtc_measurements VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", payload)
        elif kind == "custom":
            conn.executemany("INSERT INTO custom_metrics VALUES (?,?,?,?,?)", payload)


# -------------------------------------------------------------------- CLI
##
# @~japanese
# @brief 時刻を表示用の文字列にする
#
# @param ts UNIX 時刻
# @return 文字列
# @~english
# @brief Formats a timestamp for display
#
# @param ts UNIX time
# @return string
# @~
def _fmt_ts(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


##
# @~japanese
# @brief 数値を表示用の文字列にする (None は "-")
#
# @param v 値
# @param nd 小数点以下の桁数
# @return 文字列
# @~english
# @brief Formats a number for display ("-" for None)
#
# @param v value
# @param nd number of decimal places
# @return string
# @~
def _fmt(v, nd=1):
    return "-" if v is None else (("%." + str(nd) + "f") % v if isinstance(v, float) else str(v))


##
# @~japanese
# @brief コマンドの入口 (latest / events / history / measurements / custom)
#
# @param argv コマンドの引数
# @return 終了コード
# @~english
# @brief Entry point of the command (latest / events / history / measurements / custom)
#
# @param argv command arguments
# @return exit code
# @~
def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 1
    conn = sqlite3.connect(argv[1])
    cmd = argv[2]
    if cmd == "latest":
        rows = conn.execute(
            "SELECT m.* FROM metrics m JOIN (SELECT robot, MAX(ts) t FROM metrics GROUP BY robot) x "
            "ON m.robot = x.robot AND m.ts = x.t ORDER BY m.robot").fetchall()
        print("%-19s %-8s %-15s %-7s %6s %6s %8s %8s %6s %7s %8s" % (
            "time", "robot", "ip", "status", "cpu%", "mem%", "lat(ms)", "jit(ms)", "loss%", "cgcpu%", "cgmemMB"))
        for r in rows:
            print("%-19s %-8s %-15s %-7s %6s %6s %8s %8s %6s %7s %8s" % (
                _fmt_ts(r[0]), r[2], r[3], r[4], _fmt(r[5]), _fmt(r[6]), _fmt(r[10], 2), _fmt(r[11], 2),
                _fmt(r[12]), _fmt(r[13]), _fmt(r[15])))
    elif cmd == "events":
        n = int(argv[3]) if len(argv) > 3 else 30
        for r in reversed(conn.execute("SELECT * FROM events ORDER BY ts DESC LIMIT ?", (n,)).fetchall()):
            print("%s  %-8s %-20s %s" % (_fmt_ts(r[0]), r[2] or "-", r[3], r[4] or ""))
    elif cmd == "history":
        n = int(argv[4]) if len(argv) > 4 else 20
        rows = conn.execute("SELECT * FROM metrics WHERE robot = ? ORDER BY ts DESC LIMIT ?", (argv[3], n)).fetchall()
        print("%-19s %-7s %6s %6s %8s %8s %6s" % ("time", "status", "cpu%", "mem%", "lat(ms)", "jit(ms)", "loss%"))
        for r in reversed(rows):
            print("%-19s %-7s %6s %6s %8s %8s %6s" % (_fmt_ts(r[0]), r[4], _fmt(r[5]), _fmt(r[6]),
                                                      _fmt(r[10], 2), _fmt(r[11], 2), _fmt(r[12])))
    elif cmd == "measurements":
        import json
        n = int(argv[3]) if len(argv) > 3 else 20
        rows = conn.execute("SELECT * FROM rtc_measurements ORDER BY ts DESC LIMIT ?", (n,)).fetchall()
        print("%-19s %-8s %-18s %-22s %6s %7s %7s %7s %8s  %s" % (
            "time", "robot", "instance", "type", "n", "cpuAvg", "cpuMax", "cpuP95", "memMaxMB", "ports (bytes/msg x hz)"))
        for r in reversed(rows):
            ports = ", ".join("%s:%s x %s" % (k, _fmt(v.get("bytes_per_msg")), _fmt(v.get("hz")))
                              for k, v in sorted(json.loads(r[13] or "{}").items()) if v.get("msgs"))
            print("%-19s %-8s %-18s %-22s %6s %7s %7s %7s %8s  %s" % (
                _fmt_ts(r[0]), r[2] or "-", r[4], r[5], r[7], _fmt(r[8]), _fmt(r[9]), _fmt(r[10]), _fmt(r[12], 2), ports))
    elif cmd == "custom":
        robot = argv[3] if len(argv) > 3 and not argv[3].isdigit() else None
        n = int(argv[-1]) if len(argv) > 3 and argv[-1].isdigit() else 20
        if robot:
            rows = conn.execute(
                "SELECT ts, robot, name, value FROM custom_metrics WHERE robot = ? ORDER BY ts DESC LIMIT ?",
                (robot, n)).fetchall()
        else:
            rows = conn.execute(
                "SELECT ts, robot, name, value FROM custom_metrics ORDER BY ts DESC LIMIT ?",
                (n,)).fetchall()
        print("%-19s %-8s %-20s %10s" % ("time", "robot", "metric", "value"))
        for r in reversed(rows):
            print("%-19s %-8s %-20s %10s" % (_fmt_ts(r[0]), r[1], r[2], _fmt(r[3], 2)))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
