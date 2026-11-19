#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file RTCPlacement.py
# @brief Automatic placement of RTCs (used by SNMPManager; independent of SNMP / CORBA)
#
# @~japanese
# RTC の自動配置 (SNMPManager から使う。SNMP / CORBA には依存しない)
#
# 入力
# - RTC ごとの見込み値: placement.xml (rtcxml-gen/bench で計測)。環境ごとの Measurement から、指定した環境のもの (なければ別の環境の値を perfScore の比で換算) を使う
# - 各ロボット (コンテナ) の空き: cgroup の制限 - 現在の使用量 - margin
# - 各マスターマネージャの get_loadable_modules(): その RTC を生成できるロボット
# - 接続: データポート (bytesPerMsg x hz) とサービスポート (一定の重み)
#
# 出力: RTC -> ロボットの割り当て
#
# 配置のロジック (solve の logic):
# - optimal (既定): 全探索 (大きい問題は貪欲法) で、次の優先順位 (辞書式) の最良解を求める
#   1. 制約を守る (各ロボットの CPU / メモリの空きを超えない、生成できるロボットにだけ置く、通信状態の悪いロボットをまたいで接続しない)
#   2. ロボット間をまたぐ接続の通信量を最小にする (つながった RTC はできるだけ同じコンテナ)
#   3. primary (robot1) に置く RTC の数を最大にする
#   4. primary の CPU をできるだけ使う
#   5. primary 以外のロボットの CPU 使用率の最大値を最小にする (分散させる)
# - first_fit: RTC を並び順に、ロボットのリストの先頭から、制約 (ロボットごとの空きと、通信する RTC とのロボット間の制約) を満たす最初のロボットに置く
# - objective: RTC を並び順に、制約を満たすロボットのうち目的関数が最大のものに置く。目的関数は重み付き和 (objective_value) か、呼び出し側が渡す関数 (プラグイン)
#
# 待機モジュール (既に動いている非アクティブの RTC) と、動かさない既存の RTC は、candidates をそのロボットだけにし、メモリ (既存の RTC は CPU も) を 0 にした Item として渡す。
# @~english
# Inputs
# - Estimated values for each RTC: placement.xml (measured with rtcxml-gen/bench). Among the Measurement elements for each environment, the one of the specified environment is used (otherwise a value of another environment converted by the ratio of perfScore)
# - Free resources of each robot (container): cgroup limit - current usage - margin
# - get_loadable_modules() of each master manager: the robots that can create the RTC
# - Connections: data ports (bytesPerMsg x hz) and service ports (a fixed weight)
#
# Output: assignment of RTCs to robots
#
# Placement logics (logic of solve):
# - optimal (default): finds the best solution by exhaustive search (greedy for large problems) with the following lexicographic priorities
#   1. keep the constraints (do not exceed the free CPU / memory of each robot, place only on robots that can create the RTC, do not connect across robots with a bad link)
#   2. minimize the traffic of connections across robots (connected RTCs are put in the same container as much as possible)
#   3. maximize the number of RTCs on the primary (robot1)
#   4. use the CPU of the primary as much as possible
#   5. minimize the maximum CPU usage of the robots other than the primary (distribute)
# - first_fit: places RTCs in order on the first robot in the robot list that satisfies the constraints (free resources of each robot and the inter-robot constraints with communicating RTCs)
# - objective: places RTCs in order on the robot that maximizes the objective function among those satisfying the constraints. The objective is a weighted sum (objective_value) or a function given by the caller (plugin)
#
# Standby modules (inactive RTCs already running) and existing RTCs that are not moved are given as Items whose candidates are only that robot and whose memory (and CPU for existing RTCs) is 0.
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

import glob
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from xml.parsers import expat


def _read_profile_xml(path):
    builder = ET.TreeBuilder()

    def qualified(name):
        return "{" + name if "}" in name else name

    def start(name, attributes):
        builder.start(qualified(name), {
            qualified(key): value for key, value in attributes.items()
        })

    def reject_doctype(*args):
        raise ET.ParseError("placement XML must not contain a DTD")

    parser = expat.ParserCreate(namespace_separator="}")
    parser.StartElementHandler = start
    parser.EndElementHandler = lambda name: builder.end(qualified(name))
    parser.CharacterDataHandler = builder.data
    parser.StartDoctypeDeclHandler = reject_doctype
    try:
        with open(path, "rb") as stream:
            parser.ParseFile(stream)
    except expat.ExpatError as exc:
        raise ET.ParseError(str(exc)) from exc
    return builder.close()


NS = "{urn:snmpmanager:placement:1}"
SERVICE_WEIGHT = 1000.0      # サービスポート接続の重み (bytes/s 相当)
EXHAUSTIVE_LIMIT = 12        # この数までは全探索で最適解を求める


##
# @~japanese
# @brief 配置できないことを表す例外 (システム起動失敗として扱う)。reasons に理由の一覧を持つ
# @~english
# @brief Exception that the placement is impossible (treated as a system startup failure). reasons holds the list of reasons
# @~
class PlacementError(Exception):

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


# ---------------------------------------------------------------------------
# RTC のプロファイル (placement.xml)
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief RTC のプロファイル (placement.xml から読んだ CPU・メモリ・ポートの通信量の見込み値)
# @~english
# @brief Profile of an RTC (estimated CPU, memory and port traffic read from placement.xml)
# @~
@dataclass
class RtcProfile:
    rtc: str
    language: str
    cpu: float                  # CPU 使用率の見込み (1 コア = 100)
    memory_mb: float            # USS の増分
    slave_overhead_mb: float    # その言語の空マネージャの USS (最初の RTC を置くときに上乗せ)
    environment: str
    scaled_from: str = None     # 別の環境の値を換算した場合、その環境
    requires: set = field(default_factory=set)
    ports: dict = field(default_factory=dict)   # name -> {"direction", "bytes", "hz"}
    source: str = ""
    measured: bool = False      # マネージャが実行中に計測した値 (plc:origin="runtime") を使った
    samples: int = 0            # その計測の標本数


RUNTIME_ORIGIN = "runtime"


##
# @~japanese
# @brief placement.xml の集まり。RTC の型名と言語からプロファイルを引く
# @~english
# @brief Collection of placement.xml files. Looks up profiles by the type name and language of an RTC
# @~
class ProfileDB:
    ##
    # @~japanese
    # @brief コンストラクタ。root の下の placement.xml を読む
    #
    # マネージャが実行中に計測して保存した placement.xml (plc:origin="runtime") があれば、prefer_measured のとき、その値 (複数のロボットの計測があれば大きい方) で CPU・メモリ・ポートの通信量を置き換える。標本数が min_samples に満たない計測は使わない。
    #
    # @param root placement.xml を探すディレクトリ (カンマ区切りで複数指定できる)
    # @param environment 使う計測の環境の名前
    # @param prefer_measured 実行中の計測値を優先するか
    # @param min_samples 使う計測の最小の標本数
    # @~english
    # @brief Constructor. Reads placement.xml files under root
    #
    # If there are placement.xml files measured and saved by the managers at runtime (plc:origin="runtime") and prefer_measured is set, their values (the larger one if measured on several robots) replace the CPU, memory and port traffic. Measurements with fewer samples than min_samples are not used.
    #
    # @param root directories to search for placement.xml (comma separated)
    # @param environment name of the measurement environment to use
    # @param prefer_measured whether to prefer runtime measurements
    # @param min_samples minimum number of samples of a measurement to use
    # @~
    def __init__(self, root, environment, prefer_measured=True, min_samples=1):
        self.environment = environment
        self.prefer_measured = prefer_measured
        self.min_samples = int(min_samples)
        self.perf = {}
        roots = [r.strip() for r in str(root).split(",") if r.strip()]
        for r in roots:
            env_xml = os.path.join(r, "environments.xml")
            if os.path.exists(env_xml):
                for e in _read_profile_xml(env_xml):
                    try:
                        self.perf.setdefault(e.get(NS + "id"), float(e.get(NS + "perfScore")))
                    except (TypeError, ValueError):
                        pass
        self.entries = {}
        paths = sorted(p for r in roots for p in glob.glob(os.path.join(r, "**", "placement.xml"), recursive=True))
        for path in paths:
            try:
                root_el = _read_profile_xml(path)
            except ET.ParseError:
                continue
            key = (root_el.get(NS + "language"), root_el.get(NS + "rtc"))
            self.entries.setdefault(key, []).append((path, root_el))

    ##
    # @~japanese
    # @brief RTC のプロファイルを返す
    #
    # @param type_name RTC の型名
    # @param language RTC の言語
    # @return プロファイル (RtcProfile)。計測値がなければ None
    # @~english
    # @brief Returns the profile of an RTC
    #
    # @param type_name type name of the RTC
    # @param language language of the RTC
    # @return profile (RtcProfile); None if there is no measurement
    # @~
    def get(self, type_name, language):
        cands = self.entries.get((language, type_name), [])
        static = self._best([(p, el) for p, el in cands if el.get(NS + "origin") != RUNTIME_ORIGIN])
        if not self.prefer_measured:
            return static
        runtime = [prof for prof in (self._from_element(p, el) for p, el in cands
                                     if el.get(NS + "origin") == RUNTIME_ORIGIN)
                   if prof is not None and prof.samples >= self.min_samples]
        if not runtime:
            return static
        exact = [r for r in runtime if r.scaled_from is None]
        return merge_measured(static, exact or runtime)

    ##
    # @~japanese
    # @brief 候補の中から、指定した環境で計測したプロファイルを優先して選ぶ
    #
    # @param cands 候補 [(パス, 要素)]
    # @return プロファイル (なければ None)
    # @~english
    # @brief Selects a profile from the candidates, preferring one measured in the specified environment
    #
    # @param cands candidates [(path, element)]
    # @return profile (None if none)
    # @~
    def _best(self, cands):
        best = None
        for path, el in cands:
            prof = self._from_element(path, el)
            if prof is None:
                continue
            if prof.scaled_from is None:
                return prof
            best = best or prof
        return best

    ##
    # @~japanese
    # @brief placement.xml の要素からプロファイルを作る (環境が違えば perfScore の比で換算する)
    #
    # @param path placement.xml のパス
    # @param el RTC の要素
    # @return プロファイル (使える計測がなければ None)
    # @~english
    # @brief Makes a profile from an element of placement.xml (converted by the ratio of perfScore if the environment differs)
    #
    # @param path path of placement.xml
    # @param el element of the RTC
    # @return profile (None if there is no usable measurement)
    # @~
    def _from_element(self, path, el):
        ms = [m for m in el.iter(NS + "Measurement") if m.get(NS + "status") == "ok" and m.find(NS + "Resources") is not None]
        if not ms:
            return None
        m = next((x for x in ms if x.get(NS + "environment") == self.environment), None)
        scaled_from = None
        factor = 1.0
        if m is None:
            m = ms[0]
            scaled_from = m.get(NS + "environment")
            src, dst = self.perf.get(scaled_from), self.perf.get(self.environment)
            if src and dst:
                factor = src / dst
        res = m.find(NS + "Resources")
        uss = m.find(f"{NS}Memory/{NS}Uss")
        overhead = float(uss.get(NS + "baseline", 0)) if uss is not None else 0.0
        observed = {o.get(NS + "name"): float(o.get(NS + "hz")) for o in m.iter(NS + "PortObservation")}
        rate = float(m.get(NS + "executionRate", 1000) or 1000)
        ports = {}
        for p in el.iter(NS + "Port"):
            b = p.get(NS + "bytesPerMsg") or p.get(NS + "referenceBytesPerMsg") or p.get(NS + "bytesPerMsgMin")
            name = p.get(NS + "name")
            ports[name] = {"direction": p.get(NS + "direction"), "bytes": float(b) if b else 0.0,
                           "hz": observed.get(name, rate)}
        return RtcProfile(
            rtc=el.get(NS + "rtc"), language=el.get(NS + "language"),
            cpu=round(float(res.get(NS + "cpu")) * factor, 2), memory_mb=float(res.get(NS + "memoryMb")),
            slave_overhead_mb=overhead, environment=m.get(NS + "environment"), scaled_from=scaled_from,
            requires={t.get(NS + "name") for t in el.iter(NS + "Tag")}, ports=ports, source=path,
            measured=el.get(NS + "origin") == RUNTIME_ORIGIN, samples=int(float(m.get(NS + "samples", 0) or 0)))


##
# @~japanese
# @brief 静的な見込み値を、実行中の計測値で置き換える
#
# CPU・メモリ・slave の分は計測値の最大 (複数のロボットで計測していれば大きい方)。ポートは、計測で送受信があったものだけ置き換え、ほかは静的な値を残す。requires は静的な値を使う。
#
# @param static 静的な見込み値 (なければ None)
# @param runtime 実行中の計測値 (1 つ以上)
# @return 置き換えたプロファイル
# @~english
# @brief Replaces the static estimates with runtime measurements
#
# CPU, memory and slave overhead are the maximum of the measurements (the larger one if measured on several robots). Only the ports with traffic in the measurements are replaced; the others keep the static values. requires is taken from the static values.
#
# @param static static estimates (None if not available)
# @param runtime runtime measurements (one or more)
# @return merged profile
# @~
def merge_measured(static, runtime):
    first = runtime[0]
    ports = {k: dict(v) for k, v in (static.ports if static is not None else {}).items()}
    for r in runtime:
        for name, p in r.ports.items():
            if not p.get("bytes"):
                continue
            cur = ports.get(name)
            if cur is None or not cur.get("measured") or p["bytes"] * p["hz"] > cur["bytes"] * cur["hz"]:
                ports[name] = dict(p, measured=True)
    overhead = max(r.slave_overhead_mb for r in runtime)
    if not overhead and static is not None:
        overhead = static.slave_overhead_mb
    return RtcProfile(
        rtc=first.rtc, language=first.language,
        cpu=max(r.cpu for r in runtime), memory_mb=max(r.memory_mb for r in runtime),
        slave_overhead_mb=overhead, environment=first.environment,
        scaled_from=first.scaled_from,
        requires=set(static.requires) if static is not None else set().union(*(r.requires for r in runtime)),
        ports=ports, source="measured: " + ", ".join(r.source for r in runtime),
        measured=True, samples=sum(r.samples for r in runtime))


# ---------------------------------------------------------------------------
# get_loadable_modules
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief create 文字列 ("SeqOut?instance_name=..." / "RTC:AIST:example:SeqOut:C++:1.0") のモジュール名を返す
#
# @param create create 文字列
# @return モジュール名
# @~english
# @brief Returns the module name of a create string ("SeqOut?instance_name=..." / "RTC:AIST:example:SeqOut:C++:1.0")
#
# @param create create string
# @return module name
# @~
def module_name_of(create):
    base = create.split("?", 1)[0]
    if ":" in base:
        parts = base.split(":")
        return parts[3] if len(parts) > 3 else parts[-1]
    return base


##
# @~japanese
# @brief get_loadable_modules() の結果を、implementation_id で引ける辞書にする
#
# @param modules [{implementation_id, type_name, language, ...}]
# @return {implementation_id: プロファイル}
# @~english
# @brief Converts the result of get_loadable_modules() into a dictionary keyed by implementation_id
#
# @param modules [{implementation_id, type_name, language, ...}]
# @return {implementation_id: profile}
# @~
def loadable_index(modules):
    out = {}
    for m in modules:
        impl = m.get("implementation_id") or m.get("type_name")
        if impl:
            out.setdefault(impl, m)
    return out


# ---------------------------------------------------------------------------
# ソルバ
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief 配置の対象のロボット (空きの CPU・メモリ、動いている言語、通信状態)
# @~english
# @brief Robot for the placement (free CPU and memory, running languages, link quality)
# @~
@dataclass
class Robot:
    name: str
    cpu_free: float             # 使える CPU (1 コア = 100)
    mem_free_mb: float
    tags: set = field(default_factory=set)
    languages: set = field(default_factory=set)   # 既に slave マネージャが動いている言語
    cpu_limit: float = 0.0
    mem_limit_mb: float = 0.0
    link_ok: bool = True        # 通信状態がロボット間の制約を満たすか (False ならまたぐ接続を置かない)
    link: dict = field(default_factory=dict)      # latency_ms / jitter_ms / packet_loss / rssi_dbm
    reserved_mb: float = 0.0    # 予約済みのメモリ (説明用。mem_free_mb には反映済み)


##
# @~japanese
# @brief 配置する RTC (見込みの CPU・メモリと、置いてよいロボット)
# @~english
# @brief RTC to place (estimated CPU and memory, and the robots it may be placed on)
# @~
@dataclass
class Item:
    name: str                   # インスタンス名 (startup の components[].name)
    module: str
    language: str
    cpu: float
    memory_mb: float
    slave_overhead_mb: float
    candidates: list            # 置いてよいロボット (生成でき、requires を満たす)
    profile: RtcProfile = None
    standby: str = None         # 待機モジュールを使う場合、そのインスタンス名
    fixed: bool = False         # 既存の RTC (動かさない。通信量の計算にだけ使う)


##
# @~japanese
# @brief RTC の間の接続 (通信量の重み)
# @~english
# @brief Connection between RTCs (weight of the traffic)
# @~
@dataclass
class Edge:
    a: str
    b: str
    weight: float
    kind: str                   # data / service
    label: str = ""


##
# @~japanese
# @brief 配置の結果 (割り当て、ロボットをまたぐ接続、ロボットごとの使用量、評価値)
# @~english
# @brief Result of the placement (assignment, connections across robots, usage of each robot, score)
# @~
@dataclass
class Placement:
    assign: dict
    cross: list
    usage: dict                 # robot -> {"cpu", "mem"}
    score: tuple


##
# @~japanese
# @brief 構成ファイルの接続から、配置に使う接続 (Edge) を作る
#
# @param connections 構成ファイルの connections
# @param items 配置する RTC
# @return Edge のリスト
# @~english
# @brief Builds the connections (Edge) for the placement from the connections in the configuration file
#
# @param connections connections in the configuration file
# @param items RTCs to place
# @return list of Edge
# @~
def build_edges(connections, items):
    by_name = {i.name: i for i in items}
    edges = []
    for c in connections:
        s, t = c["source"]["component"], c["target"]["component"]
        if s not in by_name or t not in by_name:
            continue
        sp, tp = c["source"]["port"], c["target"]["port"]
        prof = by_name[s].profile
        port = (prof.ports.get(sp) if prof else None) or {}
        if port.get("direction") in ("out", "in"):
            src_port = port if port["direction"] == "out" else \
                ((by_name[t].profile.ports.get(tp) if by_name[t].profile else None) or {})
            w = src_port.get("bytes", 0.0) * src_port.get("hz", 1.0)
            edges.append(Edge(s, t, max(w, 1.0), "data", c.get("name", "")))
        else:
            edges.append(Edge(s, t, SERVICE_WEIGHT, "service", c.get("name", "")))
    # 同じ 2 つの RTC の間の接続はまとめる
    merged = {}
    for e in edges:
        k = tuple(sorted((e.a, e.b)))
        if k in merged:
            merged[k].weight += e.weight
            merged[k].label += "," + e.label
        else:
            merged[k] = Edge(k[0], k[1], e.weight, e.kind, e.label)
    return list(merged.values())


##
# @~japanese
# @brief ロボットをまたぐ接続の両端のロボットが、ロボット間の制約 (通信状態) を満たすかを調べる
#
# @param assign {RTC 名: ロボット名}
# @param edges 接続
# @param rmap {ロボット名: Robot}
# @return 満たせば True
# @~english
# @brief Checks whether the robots at both ends of each connection across robots satisfy the inter-robot constraints (link quality)
#
# @param assign {RTC name: robot name}
# @param edges connections
# @param rmap {robot name: Robot}
# @return True if satisfied
# @~
def _links_ok(assign, edges, rmap):
    for e in edges:
        if e.a in assign and e.b in assign and assign[e.a] != assign[e.b]:
            if not (rmap[assign[e.a]].link_ok and rmap[assign[e.b]].link_ok):
                return False
    return True


##
# @~japanese
# @brief 割り当てを評価する (制約を満たさなければ None)
#
# @param assign {RTC 名: ロボット名}
# @param items 配置する RTC
# @param robots ロボット
# @param edges 接続
# @param primary 主ロボットの名前
# @return Placement (制約を満たさなければ None)
# @~english
# @brief Evaluates an assignment (None if the constraints are not satisfied)
#
# @param assign {RTC name: robot name}
# @param items RTCs to place
# @param robots robots
# @param edges connections
# @param primary name of the primary robot
# @return Placement (None if the constraints are not satisfied)
# @~
def _evaluate(assign, items, robots, edges, primary):
    usage = {r.name: {"cpu": 0.0, "mem": 0.0, "langs": set(r.languages)} for r in robots}
    for it in items:
        u = usage[assign[it.name]]
        u["cpu"] += it.cpu
        u["mem"] += it.memory_mb
        if it.language not in u["langs"]:
            u["mem"] += it.slave_overhead_mb
            u["langs"].add(it.language)
    rmap = {r.name: r for r in robots}
    for name, u in usage.items():
        if u["cpu"] > rmap[name].cpu_free + 1e-9 or u["mem"] > rmap[name].mem_free_mb + 1e-9:
            return None
    if not _links_ok(assign, edges, rmap):
        return None
    cross = [e for e in edges if assign[e.a] != assign[e.b]]
    n_primary = sum(1 for it in items if assign[it.name] == primary)
    sec = [usage[r.name]["cpu"] / r.cpu_free for r in robots if r.name != primary and r.cpu_free > 0]
    primary_cpu = usage[primary]["cpu"] if primary in usage else 0.0
    score = (round(sum(e.weight for e in cross), 3), -n_primary, -round(primary_cpu, 3),
             round(max(sec) if sec else 0.0, 4))
    return Placement(dict(assign), cross, {k: {"cpu": round(v["cpu"], 2), "mem": round(v["mem"], 2)}
                                           for k, v in usage.items()}, score)


LOGICS = ("optimal", "first_fit", "objective")


##
# @~japanese
# @brief items を robots に割り当てる。配置できなければ PlacementError を投げる
#
# robots の並びが「ロボットのリスト」、items の並びが「起動する RTC のリスト」の順になる。
#
# @param items 配置する RTC (Item)
# @param robots ロボット (Robot)
# @param edges 接続 (Edge)
# @param primary 主ロボットの名前
# @param logic optimal / first_fit / objective
# @param objective logic=objective のときの目的関数 fn(item, robot, state) -> float (None なら objective_value)
# @return Placement
# @~english
# @brief Assigns items to robots. Raises PlacementError if they cannot be placed
#
# The order of robots is the "robot list", and the order of items is the "list of RTCs to start".
#
# @param items RTCs to place (Item)
# @param robots robots (Robot)
# @param edges connections (Edge)
# @param primary name of the primary robot
# @param logic optimal / first_fit / objective
# @param objective objective function fn(item, robot, state) -> float for logic=objective (objective_value if None)
# @return Placement
# @~
def solve(items, robots, edges, primary, logic="optimal", objective=None):
    reasons = [f"{it.name} ({it.module}) を置けるロボットがない" for it in items if not it.candidates]
    if reasons:
        raise PlacementError("配置できない RTC があります", reasons)
    if logic not in LOGICS:
        raise PlacementError(f"未知の配置ロジック {logic} (使えるのは {', '.join(LOGICS)})")
    if logic != "optimal":
        return _sequential(items, robots, edges, primary, logic, objective)
    if len(items) <= EXHAUSTIVE_LIMIT:
        best = _exhaustive(items, robots, edges, primary)
    else:
        best = _greedy(items, robots, edges, primary)
    if best is None:
        raise PlacementError("リソースの制限内に全 RTC を配置できません", capacity_report(items, robots))
    return best


##
# @~japanese
# @brief 全探索で最良の配置を求める (小さい問題向け)
#
# @param items 配置する RTC
# @param robots ロボット
# @param edges 接続
# @param primary 主ロボットの名前
# @return 最良の Placement (なければ None)
# @~english
# @brief Finds the best placement by exhaustive search (for small problems)
#
# @param items RTCs to place
# @param robots robots
# @param edges connections
# @param primary name of the primary robot
# @return best Placement (None if none)
# @~
def _exhaustive(items, robots, edges, primary):
    order = sorted(items, key=lambda i: -i.cpu)
    rmap = {r.name: r for r in robots}
    best = [None]
    assign = {}
    used = {r.name: [0.0, 0.0, set(r.languages)] for r in robots}

    def partial_cross():
        return sum(e.weight for e in edges if e.a in assign and e.b in assign and assign[e.a] != assign[e.b])

    def rec(k):
        if best[0] is not None and round(partial_cross(), 3) > best[0].score[0]:
            return  # ロボットをまたぐ通信量が既に最良解より多い
        if k == len(order):
            p = _evaluate(assign, items, robots, edges, primary)
            if p is not None and (best[0] is None or p.score < best[0].score):
                best[0] = p
            return
        it = order[k]
        for rn in it.candidates:
            u = used[rn]
            extra = 0.0 if it.language in u[2] else it.slave_overhead_mb
            if u[0] + it.cpu > rmap[rn].cpu_free + 1e-9 or u[1] + it.memory_mb + extra > rmap[rn].mem_free_mb + 1e-9:
                continue
            new_lang = it.language not in u[2]
            u[0] += it.cpu
            u[1] += it.memory_mb + extra
            if new_lang:
                u[2].add(it.language)
            assign[it.name] = rn
            rec(k + 1)
            del assign[it.name]
            u[0] -= it.cpu
            u[1] -= it.memory_mb + extra
            if new_lang:
                u[2].discard(it.language)

    rec(0)
    return best[0]


##
# @~japanese
# @brief 貪欲法で配置する (大きい問題向け)。接続でつながったグループ単位で、primary から順に詰める
#
# @param items 配置する RTC
# @param robots ロボット
# @param edges 接続
# @param primary 主ロボットの名前
# @return Placement (なければ None)
# @~english
# @brief Places by a greedy method (for large problems). Packs groups of connected RTCs, starting from the primary
#
# @param items RTCs to place
# @param robots robots
# @param edges connections
# @param primary name of the primary robot
# @return Placement (None if none)
# @~
def _greedy(items, robots, edges, primary):
    groups = connected_groups(items, edges)
    groups.sort(key=lambda g: -sum(i.cpu for i in g))
    assign = {}
    order = [primary] + [r.name for r in robots if r.name != primary]
    for g in groups:
        placed = False
        for rn in order:
            trial = dict(assign, **{i.name: rn for i in g})
            if all(rn in i.candidates for i in g) and \
                    _evaluate(trial, [i for i in items if i.name in trial], robots, edges, primary) is not None:
                assign = trial
                placed = True
                break
        if not placed:
            for i in sorted(g, key=lambda x: -x.cpu):
                for rn in order:
                    trial = dict(assign, **{i.name: rn})
                    if rn in i.candidates and \
                            _evaluate(trial, [x for x in items if x.name in trial], robots, edges, primary):
                        assign = trial
                        break
                else:
                    return None
    return _evaluate(assign, items, robots, edges, primary)


DEFAULT_WEIGHTS = {"cpu": 1.0, "memory": 1.0, "traffic": 1.0, "primary": 0.0, "link": 0.0}


##
# @~japanese
# @brief objective のロジックの既定の目的関数 (大きいほどよい)
#
# - cpu, memory: 置いた後に残る空きの割合 (0〜1)
# - traffic: 置いたことで増える、ロボットをまたぐ通信量 (KB/s) を引く
# - primary: primary に置くと 1
# - link: 通信状態の悪さ (latency_ms/10 + jitter_ms/10 + packet_loss/10) を引く
#
# @param item 置く RTC
# @param robot 置くロボット
# @param state 配置の途中の状態 {"assign", "usage", "edges", "primary", "robots"}
# @param weights 項ごとの重み (省略時は既定値)
# @return 目的関数の値
# @~english
# @brief Default objective function of the objective logic (larger is better)
#
# - cpu, memory: ratio of free resources left after placing (0 to 1)
# - traffic: subtracts the traffic across robots added by placing (KB/s)
# - primary: 1 if placed on the primary
# - link: subtracts the badness of the link (latency_ms/10 + jitter_ms/10 + packet_loss/10)
#
# @param item RTC to place
# @param robot robot to place on
# @param state state of the placement {"assign", "usage", "edges", "primary", "robots"}
# @param weights weight of each term (defaults if omitted)
# @return value of the objective function
# @~
def objective_value(item, robot, state, weights=None):
    w = dict(DEFAULT_WEIGHTS, **(weights or {}))
    u = state["usage"][robot.name]
    extra = 0.0 if item.language in u["langs"] else item.slave_overhead_mb
    cpu_left = (robot.cpu_free - u["cpu"] - item.cpu) / robot.cpu_free if robot.cpu_free > 0 else 0.0
    mem_left = (robot.mem_free_mb - u["mem"] - item.memory_mb - extra) / robot.mem_free_mb \
        if robot.mem_free_mb > 0 else 0.0
    assign = state["assign"]
    traffic = 0.0
    for e in state["edges"]:
        other = e.b if e.a == item.name else (e.a if e.b == item.name else None)
        if other is not None and other in assign and assign[other] != robot.name:
            traffic += e.weight
    link = robot.link or {}
    badness = sum(float(link.get(k) or 0.0) / 10.0 for k in ("latency_ms", "jitter_ms", "packet_loss"))
    return (w["cpu"] * cpu_left + w["memory"] * mem_left - w["traffic"] * traffic / 1000.0 + w["primary"] * (1.0 if robot.name == state["primary"] else 0.0) - w["link"] * badness)


##
# @~japanese
# @brief first_fit と objective のロジック。RTC を 1 つずつ置く
#
# @param items 配置する RTC
# @param robots ロボット
# @param edges 接続
# @param primary 主ロボットの名前
# @param logic first_fit / objective
# @param objective 目的関数
# @return Placement
# @~english
# @brief The first_fit and objective logics. Places RTCs one by one
#
# @param items RTCs to place
# @param robots robots
# @param edges connections
# @param primary name of the primary robot
# @param logic first_fit / objective
# @param objective objective function
# @return Placement
# @~
def _sequential(items, robots, edges, primary, logic, objective):
    rmap = {r.name: r for r in robots}
    assign = {}
    usage = {r.name: {"cpu": 0.0, "mem": 0.0, "langs": set(r.languages)} for r in robots}
    fn = objective or (lambda it, rb, st: objective_value(it, rb, st))
    # 待機モジュールと既存の RTC (置き場所が決まっているもの) を先に置く
    order = [it for it in items if it.standby or it.fixed] + [it for it in items if not (it.standby or it.fixed)]
    for it in order:
        feasible = []
        for r in robots:
            if r.name not in it.candidates:
                continue
            u = usage[r.name]
            extra = 0.0 if it.language in u["langs"] else it.slave_overhead_mb
            if u["cpu"] + it.cpu > r.cpu_free + 1e-9 or u["mem"] + it.memory_mb + extra > r.mem_free_mb + 1e-9:
                continue
            # CHECK: 通信する RTC が別のロボットにあるなら、ロボット間の制約を満たすこと
            if not _links_ok(dict(assign, **{it.name: r.name}), edges, rmap):
                continue
            feasible.append(r)
            if logic == "first_fit":
                break
        if not feasible:
            raise PlacementError(f"{it.name} ({it.module}) を置けるロボットがありません (ロジック {logic})",
                                 capacity_report(items, robots))
        if logic == "first_fit" or len(feasible) == 1:
            chosen = feasible[0]
        else:
            state = {"assign": assign, "usage": usage, "edges": edges, "primary": primary, "robots": robots}
            scores = [(float(fn(it, r, state)), -i, r) for i, r in enumerate(feasible)]
            chosen = max(scores, key=lambda x: (x[0], x[1]))[2]
        u = usage[chosen.name]
        u["cpu"] += it.cpu
        u["mem"] += it.memory_mb + (0.0 if it.language in u["langs"] else it.slave_overhead_mb)
        u["langs"].add(it.language)
        assign[it.name] = chosen.name
    result = _evaluate(assign, items, robots, edges, primary)
    if result is None:   # 起こらないはず (逐次の確認と同じ制約)
        raise PlacementError(f"ロジック {logic} の結果が制約を満たしません", capacity_report(items, robots))
    return result


##
# @~japanese
# @brief 接続でつながった RTC のグループに分ける
#
# @param items RTC
# @param edges 接続
# @return グループ (Item のリスト) のリスト
# @~english
# @brief Splits RTCs into groups connected by connections
#
# @param items RTCs
# @param edges connections
# @return list of groups (lists of Item)
# @~
def connected_groups(items, edges):
    parent = {i.name: i.name for i in items}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for e in edges:
        parent[find(e.a)] = find(e.b)
    groups = {}
    for i in items:
        groups.setdefault(find(i.name), []).append(i)
    return list(groups.values())


##
# @~japanese
# @brief 配置できないときの説明 (必要量の合計、ロボットごとの空き、どこにも入らない RTC) を作る
#
# @param items 配置する RTC
# @param robots ロボット
# @return 説明の行のリスト
# @~english
# @brief Makes the explanation for a failed placement (total demand, free resources of each robot, RTCs that fit nowhere)
#
# @param items RTCs to place
# @param robots robots
# @return list of lines of the explanation
# @~
def capacity_report(items, robots):
    total_cpu = sum(i.cpu for i in items)
    total_mem = sum(i.memory_mb for i in items)
    lines = [f"必要量の合計: CPU {total_cpu:.1f}%, メモリ {total_mem:.1f}MB (slave マネージャの分を除く)"]
    for r in robots:
        lines.append(f"{r.name}: 空き CPU {r.cpu_free:.1f}%, メモリ {r.mem_free_mb:.1f}MB" + (f" (予約 {r.reserved_mb:.1f}MB)" if r.reserved_mb else "") + ("" if r.link_ok else " 通信状態がロボット間の制約を満たさない"))
    for i in items:
        fits = [r.name for r in robots if r.name in i.candidates and i.cpu <= r.cpu_free and i.memory_mb + i.slave_overhead_mb <= r.mem_free_mb]
        if not fits:
            lines.append(f"{i.name} (CPU {i.cpu}%, メモリ {i.memory_mb}+{i.slave_overhead_mb}MB) は単独でもどのロボットにも入らない")
    return lines


##
# @~japanese
# @brief 配置の結果のログ用の説明文を作る
#
# @param placement 配置の結果
# @param items 配置した RTC
# @param robots ロボット
# @param edges 接続
# @param primary 主ロボットの名前
# @return 説明文
# @~english
# @brief Makes a description of the placement result for logs
#
# @param placement placement result
# @param items placed RTCs
# @param robots robots
# @param edges connections
# @param primary name of the primary robot
# @return description
# @~
def describe(placement, items, robots, edges, primary):
    rmap = {r.name: r for r in robots}
    lines = []
    for r in robots:
        names = [i.name + ("*" if i.fixed else "") for i in items if placement.assign[i.name] == r.name]
        u = placement.usage[r.name]
        tag = " (primary)" if r.name == primary else ""
        lines.append(f"{r.name}{tag}: {', '.join(names) or '-'}  "
                     f"CPU {u['cpu']:.1f}/{rmap[r.name].cpu_free:.1f}%  メモリ {u['mem']:.1f}/{rmap[r.name].mem_free_mb:.1f}MB")
    if any(i.fixed for i in items):
        lines.append("(* は既存の RTC。動かさない)")
    if placement.cross:
        lines.append("ロボットをまたぐ接続: " + ", ".join(
            f"{e.a}-{e.b} ({e.kind}, {e.weight:.0f}B/s)" for e in placement.cross))
    else:
        lines.append("ロボットをまたぐ接続: なし")
    for i in items:
        if i.standby:
            lines.append(f"{i.name}: 待機モジュール {i.standby} ({placement.assign[i.name]}) を使う")
        if i.profile and i.profile.scaled_from:
            lines.append(f"{i.name}: 環境 {i.profile.scaled_from} の計測値を perfScore の比で換算 (CPU {i.cpu}%)")
    return lines
