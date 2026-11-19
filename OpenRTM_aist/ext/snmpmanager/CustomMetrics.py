#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CustomMetrics.py
# @brief Additional monitoring values (custom metrics)
#
# @~japanese
# 追加の監視の値 (カスタムメトリクス)
#
# ロボットの snmpd の extend (または任意の OID) の値を、ほかの監視の値と一緒に SNMP で取り、マイグレーションの条件・自動復旧の条件・配置の制約・実行ロボットの選出に使えるようにする。
# @verbatim
# rtc.conf
#   snmp.metrics: temperature, motor_current                    使う名前 (カンマ区切り)
#   snmp.metric.temperature.extend: cpuTemp                     snmpd の extend の名前 (nsExtendOutput1Line)
#   snmp.metric.motor_current.oid: 1.3.6.1.4.1.99999.1.2.0      または OID を直接
# 構成ファイル
#   migration_conditions:  {"robot": "robot1", "metric": "temperature", "operator": ">", "value": 70}
#   recovery.conditions:   {"temperature_max": 70, "motor_current_min": 0.1}
#   startup / migration:   "metric_constraints":   {"temperature_max": 70}   置くロボットの条件
#   startup / migration / recovery / migration_conditions:
#                          "executor_constraints": {"temperature_max": 70}   実行ロボットに選ぶ条件
# @endverbatim
# 制約は "\<名前\>_max" (この値より大きければ外す) と "\<名前\>_min" (この値より小さければ外す)。値が分からない (取れていない) ロボットは外さない。
# @~english
# Values of extend in snmpd on the robots (or any OID) are read via SNMP together with the other monitoring values, and can be used in migration conditions, recovery conditions, placement constraints and the election of the executor robot.
# @verbatim
# rtc.conf
#   snmp.metrics: temperature, motor_current                    names to use (comma separated)
#   snmp.metric.temperature.extend: cpuTemp                     name of extend in snmpd (nsExtendOutput1Line)
#   snmp.metric.motor_current.oid: 1.3.6.1.4.1.99999.1.2.0      or the OID directly
# Configuration file
#   migration_conditions:  {"robot": "robot1", "metric": "temperature", "operator": ">", "value": 70}
#   recovery.conditions:   {"temperature_max": 70, "motor_current_min": 0.1}
#   startup / migration:   "metric_constraints":   {"temperature_max": 70}   conditions of robots to place on
#   startup / migration / recovery / migration_conditions:
#                          "executor_constraints": {"temperature_max": 70}   conditions of robots chosen as executor
# @endverbatim
# Constraints are "\<name\>_max" (excluded if greater than this value) and "\<name\>_min" (excluded if less than this value). Robots whose value is unknown (not obtained) are not excluded.
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

import re
import typing as _typing

NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
# ほかの監視の値と重なる名前は使えない (条件の metric で区別できなくなる)
RESERVED = {
    "wifi_strength", "wifi_signal_dbm", "wifi_signal_client_dbm", "wifi_signal_ap_dbm", "cpu_usage", "memory_usage",
    "network_in", "network_out", "battery_pct", "alive", "latency_ms", "jitter_ms", "packet_loss",
}


##
# @~japanese
# @brief NET-SNMP-EXTEND-MIB\::nsExtendOutput1Line."token" の OID を返す
#
# @param token extend の名前
# @return OID
# @~english
# @brief Returns the OID of NET-SNMP-EXTEND-MIB\::nsExtendOutput1Line."token"
#
# @param token name of the extend
# @return OID
# @~
def extend_output_oid(token):
    data = token.encode("utf-8")
    return "1.3.6.1.4.1.8072.1.3.2.3.1.2." + str(len(data)) + "." + ".".join(str(b) for b in data)


##
# @~japanese
# @brief rtc.conf からカスタムメトリクスの設定を読む。設定が正しくなければ ValueError を投げる
#
# @param get_property get_property(key, default) -> str (OpenRTM の Properties.getProperty)
# @return {名前: OID}
# @~english
# @brief Reads the custom metrics settings from rtc.conf. Raises ValueError if the settings are invalid
#
# @param get_property get_property(key, default) -> str (Properties.getProperty of OpenRTM)
# @return {name: OID}
# @~
def parse_config(get_property: '_typing.Callable[..., object]'):
    names = [n.strip() for n in get_property("snmp.metrics", "").split(",") if n.strip()]
    out = {}
    for name in names:
        if not NAME_RE.match(name):
            raise ValueError(f"snmp.metrics: invalid metric name {name!r} (letters, digits and _)")
        if name in RESERVED:
            raise ValueError(f"snmp.metrics: {name} is a built-in metric")
        if name in out:
            raise ValueError(f"snmp.metrics: duplicate metric {name}")
        oid = get_property(f"snmp.metric.{name}.oid", "").strip().lstrip(".")
        extend = get_property(f"snmp.metric.{name}.extend", "").strip()
        if bool(oid) == bool(extend):
            raise ValueError(f"snmp.metric.{name}: set exactly one of .oid and .extend")
        if oid and not re.fullmatch(r"[0-9]+(?:\.[0-9]+)+", oid):
            raise ValueError(f"snmp.metric.{name}.oid: invalid OID {oid}")
        out[name] = oid or extend_output_oid(extend)
    return out


##
# @~japanese
# @brief SNMP の値 (文字列・数値) を数値にする (前後の空白と末尾の NUL は無視する)
#
# @param raw SNMP の値
# @return 数値 (数値でなければ None)
# @~english
# @brief Converts an SNMP value (string or number) into a number (leading/trailing spaces and a trailing NUL are ignored)
#
# @param raw SNMP value
# @return number (None if not a number)
# @~
def parse_value(raw: str):
    if raw is None:
        return None
    try:
        return float(str(raw).strip().rstrip("\x00").strip())
    except (TypeError, ValueError):
        return None


##
# @~japanese
# @brief 使える制約のキーを返す
#
# @param names カスタムメトリクスの名前
# @return {"\<名前\>_max": (名前, ">"), "\<名前\>_min": (名前, "<")}
# @~english
# @brief Returns the available constraint keys
#
# @param names names of the custom metrics
# @return {"\<name\>_max": (name, ">"), "\<name\>_min": (name, "<")}
# @~
def constraint_keys(names: list):
    out = {}
    for n in names:
        out[n + "_max"] = (n, ">")
        out[n + "_min"] = (n, "<")
    return out


##
# @~japanese
# @brief 制約 ({"temperature_max": 70, ...}) を確かめる。正しくなければ ValueError を投げる
#
# @param constraints 制約
# @param names カスタムメトリクスの名前
# @param where エラーのメッセージに出す場所
# @~english
# @brief Validates constraints ({"temperature_max": 70, ...}). Raises ValueError if invalid
#
# @param constraints constraints
# @param names names of the custom metrics
# @param where location shown in the error message
# @~
def validate_constraints(constraints: dict, names: list, where: str) -> None:
    if constraints is None:
        return
    if not isinstance(constraints, dict):
        raise ValueError(f"{where} must be an object like {{\"<metric>_max\": value}}")
    keys = constraint_keys(names)
    for k, v in constraints.items():
        if k not in keys:
            raise ValueError(f"{where}: unknown key {k} (custom metrics: {', '.join(names) or 'none'})")
        try:
            float(v)
        except (TypeError, ValueError):
            raise ValueError(f"{where}.{k} must be a number")


##
# @~japanese
# @brief 制約を満たさないものを返す。値が None (分からない) の指標は見ない
#
# @param values {名前: 値}
# @param constraints 制約
# @param names カスタムメトリクスの名前
# @return [(キー, 名前, 値, 演算子, しきい値)]
# @~english
# @brief Returns the constraints that are violated. Metrics whose value is None (unknown) are ignored
#
# @param values {name: value}
# @param constraints constraints
# @param names names of the custom metrics
# @return [(key, name, value, operator, threshold)]
# @~
def violations(values: dict, constraints: dict, names: list):
    out = []
    if not constraints:
        return out
    keys = constraint_keys(names)
    for k, limit in constraints.items():
        if k not in keys:
            continue
        name, op = keys[k]
        value = values.get(name) if values else None
        if value is None:
            continue
        limit = float(limit)
        if (op == ">" and value > limit) or (op == "<" and value < limit):
            out.append((k, name, value, op, limit))
    return out


##
# @~japanese
# @brief violations() の 1 件を文字列にする (例: "temperature 75 > 70")
#
# @param v violations() の 1 件
# @return 文字列
# @~english
# @brief Converts one item of violations() into a string (e.g. "temperature 75 > 70")
#
# @param v one item of violations()
# @return string
# @~
def describe(v) -> str:
    _, name, value, op, limit = v
    return f"{name} {value:g} {op} {limit:g}"
