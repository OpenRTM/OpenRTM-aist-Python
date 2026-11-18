#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file ILPPlacementPlugin.py
# @brief Example placement plugin: decides the placement with an integer linear programming (ILP) solver
#
# @~japanese
# 配置 (placement) プラグインの例: 整数線形計画 (ILP) のソルバーで配置を決める
#
# 組み込みのソルバ (logic: optimal。RTC が少なければ全探索、多ければ貪欲法) の代わりに使う。
# @code
#   "plugins": [{"module": "ilp_placement"}],
#   "startup": {"mode": "auto", "placement_plugin": "ilp",
#               "placement_args": {"solver": "auto", "time_limit": 10, "objective": "lexicographic"}, ...}
# @endcode
# ソルバーは PuLP (CBC) か SciPy (scipy.optimize.milp、HiGHS) を使う (solver: auto なら見つかった方。PuLP を優先)。
# どちらもなければ PlacementError (システム起動失敗) になる。Ubuntu では apt の python3-pulp (coinor-cbc も入る) で使える。
# @verbatim
# モデル (i: RTC、r: ロボット、l: 言語、e: 接続 a-b)
#   変数  x[i,r] ∈ {0,1}   RTC i をロボット r に置く (r は i.candidates のロボットだけ)
#         y[r,l] ∈ {0,1}   ロボット r で言語 l の slave マネージャを新しく起動する (r で l がまだ動いていない場合だけ)
#         z[e]   ∈ [0,1]   接続 e がロボットをまたぐ (z[e] >= x[a,r] - x[b,r])
#   制約  Σr x[i,r] = 1                                        (どの RTC もどこか 1 台に置く)
#         Σi cpu_i x[i,r] <= cpu_free_r                        (CPU の空き)
#         Σi mem_i x[i,r] + Σl ovh_l y[r,l] <= mem_free_r       (メモリの空き。予約は mem_free_r に反映済み)
#         y[r,l] >= x[i,r]  (i の言語が l)                      (slave マネージャのメモリ)
#         x[a,r] = x[b,r]   (r がロボット間の制約を満たさない)  (そのロボットをまたぐ接続を置かない)
#   目的  objective: lexicographic (既定。組み込みの optimal と同じ優先順位を順に解く)
#           1. ロボットをまたぐ通信量 Σ w_e z[e] を最小
#           2. 主ロボットに置く RTC の数を最大
#           3. 主ロボットに置く CPU を最大
#           4. 主ロボット以外の CPU の使用率の最大値を最小 (t >= Σi cpu_i x[i,r] / cpu_free_r)
#         objective: weighted (1 回だけ解く。weights の重みで足し合わせる)
#           最小化  cross * Σ w_e z[e] - primary_count * 主ロボットの RTC 数 - primary_cpu * 主ロボットの CPU + balance * t
#           weights の既定は {"cross": 1, "primary_count": 0, "primary_cpu": 0, "balance": 0}
# placement_args
#   solver       auto / pulp / scipy                       (既定 auto)
#   time_limit   1 回の求解の秒数の上限                     (既定 10。時間切れでも、見つかった解があれば使う)
#   objective    lexicographic / weighted                  (既定 lexicographic)
#   weights      objective: weighted の重み
#   tolerance    lexicographic で前の段の値に許す差 (相対) (既定 1e-6)
# @endverbatim
# 制限: slave マネージャのメモリは、その言語の RTC の slave_overhead_mb の最大値で数える (組み込みのソルバは
# 最初に置いた RTC の値)。値が言語ごとに同じなら (placement.xml の通常の値)、組み込みのソルバと同じ結果になる。
# @~english
# Used instead of the built-in solver (logic: optimal; exhaustive search for few RTCs, greedy for many).
# @code
#   "plugins": [{"module": "ilp_placement"}],
#   "startup": {"mode": "auto", "placement_plugin": "ilp",
#               "placement_args": {"solver": "auto", "time_limit": 10, "objective": "lexicographic"}, ...}
# @endcode
# The solver is PuLP (CBC) or SciPy (scipy.optimize.milp, HiGHS) (with solver: auto, whichever is found; PuLP is preferred).
# If neither is available, PlacementError is raised (the system startup fails). On Ubuntu, the apt package python3-pulp (which also installs coinor-cbc) can be used.
# @verbatim
# Model (i: RTC, r: robot, l: language, e: connection a-b)
#   Variables   x[i,r] in {0,1}  RTC i is placed on robot r (r is limited to the robots in i.candidates)
#               y[r,l] in {0,1}  a new slave manager of language l is started on robot r (only if l is not running on r yet)
#               z[e]   in [0,1]  connection e crosses robots (z[e] >= x[a,r] - x[b,r])
#   Constraints sum_r x[i,r] = 1                                  (every RTC is placed on exactly one robot)
#               sum_i cpu_i x[i,r] <= cpu_free_r                  (free CPU)
#               sum_i mem_i x[i,r] + sum_l ovh_l y[r,l] <= mem_free_r  (free memory; reservations are already in mem_free_r)
#               y[r,l] >= x[i,r]  (the language of i is l)        (memory of the slave manager)
#               x[a,r] = x[b,r]   (r violates the inter-robot constraints)  (no connection crossing that robot)
#   Objective   objective: lexicographic (default; solves the same priorities as the built-in optimal in order)
#                 1. minimize the traffic across robots sum_e w_e z[e]
#                 2. maximize the number of RTCs on the primary robot
#                 3. maximize the CPU on the primary robot
#                 4. minimize the maximum CPU usage ratio of the non-primary robots (t >= sum_i cpu_i x[i,r] / cpu_free_r)
#               objective: weighted (solved once; terms are summed with the weights)
#                 minimize cross * sum_e w_e z[e] - primary_count * (RTCs on primary) - primary_cpu * (CPU on primary) + balance * t
#                 default weights: {"cross": 1, "primary_count": 0, "primary_cpu": 0, "balance": 0}
# placement_args
#   solver       auto / pulp / scipy                       (default auto)
#   time_limit   time limit of one solve in seconds        (default 10; if a solution was found, it is used even on timeout)
#   objective    lexicographic / weighted                  (default lexicographic)
#   weights      weights for objective: weighted
#   tolerance    relative slack allowed for the value of the previous stage in lexicographic (default 1e-6)
# @endverbatim
# Limitation: the memory of a slave manager is counted as the maximum slave_overhead_mb of the RTCs of that language (the built-in solver
# uses the value of the first placed RTC). If the values are the same for each language (the usual values in placement.xml), the result is the same as the built-in solver.
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

import time

PLUGIN_API = 1

INF = float("inf")


##
# @~japanese
# @brief 線形計画のモデル (ソルバーに依存しない形)。行は ({変数の番号: 係数}, 下限, 上限)
# @~english
# @brief Linear programming model independent of the solver. Each row is ({variable index: coefficient}, lower bound, upper bound)
# @~
class _Model:

    ##
    # @~japanese
    # @brief コンストラクタ。変数と行のない空のモデルを作る
    # @~english
    # @brief Constructor. Creates an empty model without variables and rows
    # @~
    def __init__(self) -> None:
        self.names, self.lb, self.ub, self.integer = [], [], [], []
        self.rows = []

    ##
    # @~japanese
    # @brief 変数を足す
    #
    # @param name 変数の名前
    # @param lb 下限
    # @param ub 上限
    # @param integer 整数の変数なら True
    # @return 変数の番号
    # @~english
    # @brief Adds a variable
    #
    # @param name name of the variable
    # @param lb lower bound
    # @param ub upper bound
    # @param integer True for an integer variable
    # @return index of the variable
    # @~
    def var(self, name, lb=0.0, ub=1.0, integer: bool = True):
        self.names.append(name)
        self.lb.append(lb)
        self.ub.append(ub)
        self.integer.append(integer)
        return len(self.names) - 1

    ##
    # @~japanese
    # @brief 制約の行 (lo <= Σ 係数 x 変数 <= hi) を足す。係数が 0 の項は除き、意味のない行は足さない
    #
    # @param coefs {変数の番号: 係数}
    # @param lo 下限
    # @param hi 上限
    # @~english
    # @brief Adds a constraint row (lo <= sum of coefficient x variable <= hi). Zero coefficients are dropped and trivial rows are not added
    #
    # @param coefs {variable index: coefficient}
    # @param lo lower bound
    # @param hi upper bound
    # @~
    def add(self, coefs, lo=-INF, hi=INF) -> None:
        coefs = {k: v for k, v in coefs.items() if v != 0}
        if coefs or lo > 0 or hi < 0:
            self.rows.append((coefs, lo, hi))


# ---------------------------------------------------------------------------
# ソルバー
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief 使えるソルバーの一覧を返す
#
# @return "pulp"、"scipy" のうち import できるもの
# @~english
# @brief Returns the list of available solvers
#
# @return those of "pulp" and "scipy" that can be imported
# @~
def available_solvers():
    out = []
    try:
        import pulp  # noqa: F401
        out.append("pulp")
    except ImportError:
        pass
    try:
        from scipy.optimize import milp  # noqa: F401
        out.append("scipy")
    except ImportError:
        pass
    return out


##
# @~japanese
# @brief PuLP (CBC) でモデルを解く
#
# @param m モデル
# @param obj 最小化する目的の式 {変数の番号: 係数}
# @param time_limit 求解の秒数の上限
# @return 変数の値のリスト (解がなければ None)
# @~english
# @brief Solves the model with PuLP (CBC)
#
# @param m model
# @param obj objective to minimize {variable index: coefficient}
# @param time_limit time limit of the solve in seconds
# @return list of variable values (None if there is no solution)
# @~
def _solve_pulp(m, obj, time_limit):
    import pulp
    prob = pulp.LpProblem("snmpmgr_placement", pulp.LpMinimize)
    v = []
    for k, name in enumerate(m.names):
        if m.integer[k] and m.lb[k] == 0 and m.ub[k] == 1:
            cat = pulp.LpBinary
        else:
            cat = pulp.LpInteger if m.integer[k] else pulp.LpContinuous
        v.append(pulp.LpVariable(f"v{k}", lowBound=None if m.lb[k] == -INF else m.lb[k],
                                 upBound=None if m.ub[k] == INF else m.ub[k], cat=cat))
    prob += pulp.lpSum(c * v[k] for k, c in obj.items()) if obj else pulp.lpSum([0 * v[0]])
    for coefs, lo, hi in m.rows:
        expr = pulp.lpSum(c * v[k] for k, c in coefs.items())
        if lo == hi:
            prob += expr == lo
        else:
            if lo > -INF:
                prob += expr >= lo
            if hi < INF:
                prob += expr <= hi
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit))
    # sol_status: 1 最適、2 時間切れだが解あり、-1 解なし
    if prob.sol_status not in (1, 2):
        return None, pulp.LpStatus.get(prob.status, str(prob.status))
    return [x.value() or 0.0 for x in v], "optimal" if prob.sol_status == 1 else "feasible (time limit)"


##
# @~japanese
# @brief SciPy (scipy.optimize.milp、HiGHS) でモデルを解く
#
# @param m モデル
# @param obj 最小化する目的の式 {変数の番号: 係数}
# @param time_limit 求解の秒数の上限
# @return 変数の値のリスト (解がなければ None)
# @~english
# @brief Solves the model with SciPy (scipy.optimize.milp, HiGHS)
#
# @param m model
# @param obj objective to minimize {variable index: coefficient}
# @param time_limit time limit of the solve in seconds
# @return list of variable values (None if there is no solution)
# @~
def _solve_scipy(m, obj, time_limit):
    import numpy as np
    from scipy.optimize import Bounds, LinearConstraint, milp
    n = len(m.names)
    c = np.zeros(n)
    for k, val in obj.items():
        c[k] = val
    cons = None
    if m.rows:
        a = np.zeros((len(m.rows), n))
        lo = np.empty(len(m.rows))
        hi = np.empty(len(m.rows))
        for j, (coefs, l, h) in enumerate(m.rows):
            for k, val in coefs.items():
                a[j, k] = val
            lo[j], hi[j] = l, h
        cons = LinearConstraint(a, lo, hi)
    res = milp(c, integrality=np.array([1 if x else 0 for x in m.integer]), bounds=Bounds(m.lb, m.ub),
               constraints=cons, options={"time_limit": time_limit})
    # status: 0 最適、1 時間切れ (x があれば解あり)、2 解なし
    if res.x is None:
        return None, res.message
    return list(res.x), "optimal" if res.status == 0 else "feasible (time limit)"


SOLVERS = {"pulp": _solve_pulp, "scipy": _solve_scipy}


# ---------------------------------------------------------------------------
# モデルの組み立てと求解
# ---------------------------------------------------------------------------
##
# @~japanese
# @brief 配置の ILP のモデルを組み立てる
#
# @param items 置く RTC (placement.Item) のリスト
# @param robots ロボット (placement.Robot) のリスト
# @param edges RTC の間の接続 (placement.Edge) のリスト
# @param primary 主ロボットの名前
# @return (モデル, x の番号 {(RTC, ロボット): 番号}, 目的の式 {名前: {番号: 係数}})
# @~english
# @brief Builds the ILP model of the placement
#
# @param items list of RTCs to place (placement.Item)
# @param robots list of robots (placement.Robot)
# @param edges list of connections between RTCs (placement.Edge)
# @param primary name of the primary robot
# @return (model, indices of x {(RTC, robot): index}, objectives {name: {index: coefficient}})
# @~
def build_model(items, robots, edges, primary):
    m = _Model()
    rmap = {r.name: r for r in robots}
    x = {}
    for it in items:
        for rn in it.candidates:
            if rn in rmap:
                x[(it.name, rn)] = m.var(f"x[{it.name},{rn}]")
    for it in items:
        m.add({x[(it.name, rn)]: 1.0 for rn in it.candidates if (it.name, rn) in x}, 1.0, 1.0)
    # slave マネージャのメモリ (言語ごと)
    overhead = {}
    for it in items:
        overhead[it.language] = max(overhead.get(it.language, 0.0), it.slave_overhead_mb)
    y = {}
    for r in robots:
        cpu, mem = {}, {}
        for it in items:
            k = x.get((it.name, r.name))
            if k is None:
                continue
            cpu[k] = it.cpu
            mem[k] = it.memory_mb
            if it.language not in r.languages and overhead.get(it.language, 0.0) > 0:
                key = (r.name, it.language)
                if key not in y:
                    y[key] = m.var(f"y[{r.name},{it.language}]")
                    mem[y[key]] = overhead[it.language]
                m.add({y[key]: 1.0, k: -1.0}, 0.0)            # y >= x
        m.add(cpu, hi=r.cpu_free + 1e-9)
        m.add(mem, hi=r.mem_free_mb + 1e-9)
    # ロボットをまたぐ接続
    z = {}
    for e in edges:
        names = {rn for (i, rn) in x if i in (e.a, e.b)}
        ze = m.var(f"z[{e.a},{e.b}]", 0.0, 1.0, integer=False)
        z[(e.a, e.b)] = (ze, e.weight)
        for rn in names:
            xa, xb = x.get((e.a, rn)), x.get((e.b, rn))
            coefs = {ze: 1.0}
            if xa is not None:
                coefs[xa] = coefs.get(xa, 0.0) - 1.0
            if xb is not None:
                coefs[xb] = coefs.get(xb, 0.0) + 1.0
            m.add(coefs, 0.0)                                  # z >= xa - xb
            coefs = {ze: 1.0}
            if xb is not None:
                coefs[xb] = coefs.get(xb, 0.0) - 1.0
            if xa is not None:
                coefs[xa] = coefs.get(xa, 0.0) + 1.0
            m.add(coefs, 0.0)                                  # z >= xb - xa
            if not rmap[rn].link_ok:
                # 通信状態が制約を満たさないロボットは、またぐ接続の端にしない
                coefs = {}
                if xa is not None:
                    coefs[xa] = 1.0
                if xb is not None:
                    coefs[xb] = coefs.get(xb, 0.0) - 1.0
                m.add(coefs, 0.0, 0.0)
    # 主ロボット以外の CPU の使用率の最大値
    t = m.var("t", 0.0, INF, integer=False)
    for r in robots:
        if r.name == primary or r.cpu_free <= 0:
            continue
        coefs = {t: 1.0}
        for it in items:
            k = x.get((it.name, r.name))
            if k is not None:
                coefs[k] = -it.cpu / r.cpu_free
        m.add(coefs, 0.0)
    objectives = {
        "cross": {ze: w for (ze, w) in z.values()},
        "primary_count": {k: -1.0 for (i, rn), k in x.items() if rn == primary},
        "primary_cpu": {k: -next(it.cpu for it in items if it.name == i) for (i, rn), k in x.items() if rn == primary},
        "balance": {t: 1.0},
    }
    return m, x, objectives


##
# @~japanese
# @brief 解の値で式の値を計算する
#
# @param expr 式 {変数の番号: 係数}
# @param values 変数の値のリスト
# @return 式の値
# @~english
# @brief Evaluates an expression with the solution values
#
# @param expr expression {variable index: coefficient}
# @param values list of variable values
# @return value of the expression
# @~
def _value(expr, values):
    return sum(c * values[k] for k, c in expr.items())


##
# @~japanese
# @brief ILP で配置を決める
#
# @param items 置く RTC (placement.Item) のリスト
# @param robots ロボット (placement.Robot) のリスト
# @param edges RTC の間の接続 (placement.Edge) のリスト
# @param primary 主ロボットの名前
# @param args placement_args (solver、time_limit、objective、weights、tolerance)
# @param log ログを出す関数 (省略時は出さない)
# @return {RTC 名: ロボット名}。置けなければ placement.PlacementError を投げる
# @~english
# @brief Decides the placement with ILP
#
# @param items list of RTCs to place (placement.Item)
# @param robots list of robots (placement.Robot)
# @param edges list of connections between RTCs (placement.Edge)
# @param primary name of the primary robot
# @param args placement_args (solver, time_limit, objective, weights, tolerance)
# @param log function to output logs (none if omitted)
# @return {RTC name: robot name}; raises placement.PlacementError if it cannot be placed
# @~
def solve_ilp(items, robots, edges, primary, args=None, log=None):
    import RTCPlacement as pl
    args = args or {}
    log = log or (lambda msg: None)
    missing = [f"{it.name} ({it.module}) を置けるロボットがない" for it in items if not it.candidates]
    if missing:
        raise pl.PlacementError("配置できない RTC があります", missing)
    have = available_solvers()
    want = args.get("solver", "auto")
    if want == "auto":
        if not have:
            raise pl.PlacementError("ILP のソルバーがありません (PuLP か SciPy を入れてください。"
                                    "Ubuntu: apt install python3-pulp)")
        backend = have[0]
    elif want in SOLVERS:
        if want not in have:
            raise pl.PlacementError(f"ILP のソルバー {want} が見つかりません")
        backend = want
    else:
        raise pl.PlacementError(f"未知の ILP のソルバー {want} (使えるのは auto, pulp, scipy)")
    time_limit = float(args.get("time_limit", 10))
    tol = float(args.get("tolerance", 1e-6))
    mode = args.get("objective", "lexicographic")
    m, x, objs = build_model(items, robots, edges, primary)
    solve = SOLVERS[backend]
    t0 = time.monotonic()
    status = ""
    if mode == "weighted":
        w = {"cross": 1.0, "primary_count": 0.0, "primary_cpu": 0.0, "balance": 0.0}
        w.update(args.get("weights") or {})
        obj = {}
        for name, weight in w.items():
            for k, c in objs.get(name, {}).items():
                obj[k] = obj.get(k, 0.0) + float(weight) * c
        values, status = solve(m, obj, time_limit)
    elif mode == "lexicographic":
        values = None
        for name in ("cross", "primary_count", "primary_cpu", "balance"):
            values, status = solve(m, objs[name], time_limit)
            if values is None:
                break
            best = _value(objs[name], values)
            m.add(objs[name], hi=best + tol * max(1.0, abs(best)))    # 次の段では、この段の値を保つ
    else:
        raise pl.PlacementError(f"未知の目的 {mode} (使えるのは lexicographic, weighted)")
    if values is None:
        raise pl.PlacementError(f"ILP ({backend}): リソースの制限内に全 RTC を配置できません ({status})",
                                pl.capacity_report(items, robots))
    assign = {}
    for (i, rn), k in x.items():
        if values[k] > 0.5:
            assign[i] = rn
    p = pl._evaluate(assign, items, robots, edges, primary) if len(assign) == len(items) else None
    if p is None:
        raise pl.PlacementError(f"ILP ({backend}): ソルバーの解が制約を満たしません ({status})",
                                pl.capacity_report(items, robots))
    log(f"ILP ({backend}, {mode}): {status}, {len(m.names)} variables, {len(m.rows)} constraints, "
        f"{time.monotonic() - t0:.2f}s; cross traffic {p.score[0]}, {-p.score[1]} RTCs on {primary}")
    return assign


##
# @~japanese
# @brief プラグインを登録する (配置のロジック ilp を登録する)
#
# @param ctx プラグインのコンテキスト
# @param config プラグインの設定 (使わない)
# @~english
# @brief Registers the plugin (registers the placement logic ilp)
#
# @param ctx plugin context
# @param config plugin configuration (not used)
# @~
def setup(ctx, config) -> None:
    def ilp(ctx, items, robots, edges, primary, args):
        return solve_ilp(items, robots, edges, primary, args, ctx.log)

    ctx.register_placement("ilp", ilp)
