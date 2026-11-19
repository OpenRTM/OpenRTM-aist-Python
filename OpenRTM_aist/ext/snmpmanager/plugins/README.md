# SNMPManager のプラグイン

仕様と実装方法のまとめ（構成ファイルの書き方、Python・C++ の API、ビルド、テスト）は [docs/06_reference.md](../docs/06_reference.md) にあります。

SNMPManager の動作のうち、次の5か所を Python のプラグインで差し替えたり、追加したりできます。

| 拡張ポイント | 登録 | 呼ばれるとき | 戻り値 |
|---|---|---|---|
| 条件（condition） | `ctx.register_condition(name, fn)` | `migration_conditions` の条件に `{"plugin": name, "args": {...}}` と書いたとき。組み込みの条件と AND/OR で組み合わせられる | `fn(ctx, args, now)` → True/False |
| 処理（action） | `ctx.register_action(name, fn)` | `migration`（または `startup`）に `{"plugin": name, "args": {...}}` と書いたとき。固定の計画の代わりに呼ばれる | `fn(ctx, args)` → 成功したら True |
| 配置（placement） | `ctx.register_placement(name, fn)` | 自動配置（`startup.mode: auto`）に `"placement_plugin": name` と書いたとき。組み込みのソルバの代わりに呼ばれる | `fn(ctx, items, robots, edges, primary, args)` → `{RTC 名: ロボット名}` |
| 目的関数（objective） | `ctx.register_objective(name, fn)` | 自動配置（`startup` / `migration` の `mode: auto`）に `"logic": "objective"` と `"objective_plugin": name` を書いたとき。RTC ごとに、置けるロボットの中からこの値が最大のものを選ぶ | `fn(ctx, item, robot, state, args)` → 数値（大きいほどよい） |
| イベント（event） | `ctx.subscribe(kind, fn)` | イベントが記録されたとき。`kind` はイベントの種別、`"*"` で全部 | `fn(ctx, event)`（戻り値なし） |

イベントの種別は、`started`、`discovered`、`alive`、`down`、`up`、`startup_completed`、`startup_failed`、`migration_started`、`migration_completed`、`migration_failed`、`migration_placement`、`executor_elected`、`standby_launched`、`standby_used` と、プラグインが `ctx.event()` で記録したものです。

## 書き方

プラグインは、`setup(ctx, config)` を持つ Python のファイルです。`snmp.plugin.path`（rtc.conf。カンマ区切り。既定は SNMPManager.py と同じ場所の `plugins/`）のディレクトリに置きます。`<module>.py` がないときは、大文字小文字と `_` を無視して `<module>Plugin.py` と一致するファイルを探します（例えば `"module": "least_loaded_migration"` で `LeastLoadedMigrationPlugin.py`）。サンプルのファイル名は `AliveCountPlugin.py` などですが、構成ファイルには今までどおり `alive_count` などと書けます。

```python
PLUGIN_API = 1   # 省略可。合わない場合は読み込みエラーにする

def setup(ctx, config):          # config は構成ファイルの "config" の値
    def my_condition(ctx, args, now):
        return len(ctx.alive_robots()) < int(args["value"])
    ctx.register_condition("few_robots", my_condition)
```

構成ファイル（`migration.json` など）の最上位に、読み込むプラグインを書きます。

```json
"plugins": [
  {"module": "least_loaded_migration"},
  {"module": "event_log", "config": {"path": "/var/lib/rtm/plugin_events.jsonl"}}
]
```

- `module` はファイル名（`.py` は省略可）か、絶対パスです。
- 同じプラグインを別の名前で2回読み込む場合は `"name"` を付けます（登録する名前が重なるとエラーになります）。
- 構成ファイルの `plugins` の内容が変わると、次に構成ファイルを読むときに読み込み直します。
- 構成ファイルの読み込み時に、書かれた条件、処理、配置のプラグインが登録されているかを確かめ、なければエラーにします。

## ctx で使える機能

| 機能 | 内容 |
|---|---|
| `ctx.name` | 自分のロボット（マネージャ）の名前 |
| `ctx.log(msg)` | ログに出す（`[plugin 名前]` が付く） |
| `ctx.robots()` / `ctx.robot(name)` / `ctx.alive_robots()` | ロボットの状態のスナップショット。`name`、`ip`、`status`（alive/dead/unknown）、`is_local`、`cpu_usage`、`memory_usage`、`network_in`、`network_out`、`wifi_signal_dbm`、`latency_ms`、`jitter_ms`、`packet_loss`、`cgroup`（`cpu_usage_pct`、`cpu_limit_pct`、`mem_usage_mb`、`mem_limit_mb`）、`inventory`（動いている RTC の一覧：`name`、`impl`、`type`、`language`、`state`）、`base_mem_mb`（RTC がないときのメモリ使用量）、`metrics`（追加の監視の値。rtc.conf の `snmp.metrics`：`{名前: 値}`） |
| `ctx.manager(name)` | そのロボットのマスターマネージャ（`RTM.Manager` の CORBA 参照）。OpenRTM の API を直接使う場合に |
| `ctx.find_component(instance, manager)` | インスタンス名で RTC を探す（スレーブも含む）。なければ None |
| `ctx.apply_plan(plan, label)` | `migration` と同じ形式の計画（`components`、`connections`、`remove`）を適用する。生成、接続、アクティベート、削除の順に行い、ほかの構成変更とは排他される |
| `ctx.conf(key, default)` | rtc.conf の値 |
| `ctx.migration_config()` | 構成ファイルの内容 |
| `ctx.event(robot, kind, detail)` | イベントを記録する（ログ、SQLite、ほかのプラグインの subscribe） |

配置のプラグインには、`RTCPlacement.py` の `Item`（`name`、`module`、`language`、`cpu`、`memory_mb`、`slave_overhead_mb`、`candidates`、`profile`）、`Robot`（`name`、`cpu_free`、`mem_free_mb`、`tags`、`languages`、`link_ok`、`link`、`reserved_mb`）、`Edge`（`a`、`b`、`weight`、`kind`）のリストが渡されます。`Item` の `standby`（使う待機モジュールの名前）と `fixed`（動かさない既存の RTC）が付いたものは、`candidates` が1つに決まっています。`Robot.mem_free_mb` は、メモリの予約を差し引いた後の値です。

目的関数のプラグインには、置こうとしている `Item` 1つ、候補の `Robot` 1つと、`state`（`assign`：ここまでの割り当て、`usage`：ロボットごとの使用量 `cpu`/`mem`/`langs`、`edges`、`primary`、`robots`）が渡されます。制約（空き容量、置けるロボット、ロボット間の通信の制約）を満たすロボットについてだけ呼ばれます。返した割り当ては、SNMPManager が「置けるロボットか（`candidates`）」と「空き容量に収まるか」を確かめ、満たさなければシステム起動失敗にします。

## 実行のされ方

- 条件のプラグインは、条件を判定するたびに（2秒ごと）、判定を担当するマネージャ（`executor`）で呼ばれます。例外が起きた場合は False として扱います。
- 処理のプラグインは、マイグレーション用のスレッドで呼ばれます。False を返すか例外を投げると、`migration_failed` になります。
- イベントのプラグインは、専用のスレッドで順に呼ばれるので、監視の処理を待たせません。
- プラグインは、SNMPManager と同じプロセスの中で動きます。プラグインの中で時間のかかる処理（長い待ちなど）をすると、その間は同じ種類の処理が止まります。

## サンプル

| ファイル | 種類 | 内容 |
|---|---|---|
| `LeastLoadedMigrationPlugin.py` | 処理 | 移す RTC を、その時点で負荷（cgroup の CPU 使用率 / 制限）が最も低い、生きているロボットへ移す。接続先の RTC は、生きているロボットから自動で探す |
| `AliveCountPlugin.py` | 条件 | 生きているロボットの数で判定する（`{"op": ">=", "value": 3}`） |
| `EventLogPlugin.py` | イベント | イベントを JSON Lines のファイルに追記する |
| `FirstFitPlacementPlugin.py` | 配置 | RTC を順に、ロボットの一覧の順で最初に入るところへ置く。現在は組み込みの `"logic": "first_fit"` でも同じことができる |
| `ILPPlacementPlugin.py` | 配置 | 整数線形計画 (ILP) のソルバー (PuLP の CBC か SciPy の HiGHS) で配置を決める。下の「ILP のソルバーの配置プラグイン」 |
| `LinkAwareObjectivePlugin.py` | 目的関数 | `logic: objective` の目的関数の例。残る空きの割合から、ロボットをまたぐ通信量（そのロボットのレイテンシで重みを付ける）とパケットロスを引いた値 |

単体テストは `../TestPlugins.py` にあります（`python -m unittest TestPlugins`。OpenRTM 不要。ILP のテストは、ソルバーがなければ飛ばす）。

## ILP のソルバーの配置プラグイン（`ILPPlacementPlugin.py`）

自動配置を、整数線形計画として解きます。

```json
"plugins": [{"module": "ilp_placement"}],
"startup": {"mode": "auto", "placement_plugin": "ilp",
            "placement_args": {"solver": "auto", "time_limit": 10, "objective": "lexicographic"}, ...}
```

**モデル**（i: RTC、r: ロボット、l: 言語、e: 接続 a-b）

| | 内容 |
|---|---|
| 変数 | `x[i,r]`（0/1。RTC i をロボット r に置く。r は `candidates` だけ）、`y[r,l]`（0/1。r で言語 l の slave マネージャを新しく起動する）、`z[e]`（0〜1。接続 e がロボットをまたぐ）、`t`（主ロボット以外の CPU の使用率の最大値） |
| 制約 | 各 RTC を 1 台に置く。CPU の空き。メモリの空き（slave マネージャの分 `y` を含む。予約は `mem_free_mb` に反映済み）。`z[e] >= x[a,r] - x[b,r]`。ロボット間の制約を満たさないロボット r では `x[a,r] = x[b,r]`（またぐ接続の端にしない） |
| 目的（`lexicographic`、既定） | 組み込みの `optimal` と同じ優先順位で、4 回順に解く: ①ロボットをまたぐ通信量 `Σ w_e z[e]` を最小、②主ロボットの RTC の数を最大、③主ロボットの CPU を最大、④ `t` を最小。各段の値は、次の段で制約として保つ |
| 目的（`weighted`） | 1 回だけ解く。`weights` の `cross`・`primary_count`・`primary_cpu`・`balance` の重みで足し合わせる（既定は `cross` だけ 1） |

**placement_args**

| キー | 既定 | 内容 |
|---|---|---|
| `solver` | `auto` | `pulp`（CBC）、`scipy`（`scipy.optimize.milp`、HiGHS）、`auto`（見つかった方。PuLP を優先） |
| `time_limit` | 10 | 1 回の求解の秒数の上限。時間切れでも、見つかった解があれば使う |
| `objective` | `lexicographic` | `lexicographic` か `weighted` |
| `weights` | `{"cross": 1}` | `weighted` の重み |
| `tolerance` | 1e-6 | `lexicographic` で、前の段の値に許す差（相対） |

- ソルバーがなければ `PlacementError`（システム起動失敗）になります。Ubuntu では `apt install python3-pulp`（CBC も入る）、pip なら `pip install pulp` か `pip install scipy` です。docker-test のイメージには `python3-pulp` を入れています。
- ログに `ILP (pulp, lexicographic): optimal, 25 variables, 54 constraints, 0.17s; ...` のように、ソルバー・状態・規模・時間が出ます。
- 返した割り当ては、組み込みと同じ評価（`placement._evaluate`）で、空き容量と通信の制約を満たすかを確かめます。
- 単体テストで、5 通りのロボットの空きについて、組み込みの `optimal`（全探索）と評価が同じになることを確かめています。ソルバーごとの確認は次のとおりです。
  - PuLP 2.7（CBC）：docker-test のイメージ
  - SciPy 1.18.1（HiGHS）：Windows の Python 3.12（0.46 秒）
  - SciPy 1.11.4（HiGHS）：WSL2 の Ubuntu 24.04
- **制限**：slave マネージャのメモリは、その言語の RTC の `slave_overhead_mb` の最大値で数えます（組み込みのソルバは、最初に置いた RTC の値）。言語ごとに同じ値なら（`placement.xml` の通常の値）、結果は同じです。
- **C++ 版**：同じモデルの C++ 版が `snmpmanager-cpp/plugins/ILPPlacementPlugin.cpp` にあります。ソルバーは GLPK（`libglpk-dev`）で、構成ファイルの書き方は同じです（`solver` は `auto` か `glpk`）。GLPK が見つかったときだけビルドします。Windows は winglpk 4.65 を使います（既定の場所は `%LOCALAPPDATA%\glpk\glpk-4.65`。ほかの場所なら `-DGLPK_DIR=`）。Linux（GLPK 5.0）と Windows（GLPK 4.65）の両方で、単体テストで組み込みの `optimal` と評価が一致することを確かめています。

## 対応していないこと

- C++ のプラグイン（共有ライブラリ）は、C++ 版の SNMPManager だけが読み込みます（`snmpmanager-cpp/README.md`）。Python 版が読み込むのは Python のプラグインだけです。
- 自動復旧の各段階（リセット、再起動、待機モジュールへの切り替え）を個別に差し替える拡張ポイントはありません。必要な場合は、処理のプラグインの中で `ctx.manager()` と OpenRTM の API を使って書きます。
