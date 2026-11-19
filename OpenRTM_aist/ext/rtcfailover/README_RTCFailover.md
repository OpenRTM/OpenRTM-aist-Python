# 設定ファイル方式 RTC フェイルオーバー

設定ファイル（JSON）で定義したグループごとに、代替候補（alternatives）の中から使える RTC の組を選んで接続し、アクティブ化します。障害が起きたら、次の候補へ切り替えます。

障害は2つの方法で検知します。

- **ComponentObserver**：RTC が ERROR 状態に遷移すると、RTC 側の ComponentObserverConsumer から通知（`RTC_STATUS` の `ERROR:<ec_id>`）が届きます。
- **生存確認（liveness）**：一定間隔で、現在使っている RTC に到達できるか（プロセスが落ちていないか）と、ERROR 状態でないかを確かめます。

## ファイル

| ファイル | 内容 |
|---|---|
| `RTCFailover.py` | 設定の読み込み、マネージャの取得、RTC の生成、候補の選択、接続と切り替え、オブザーバの登録、生存確認 |
| `RTCFailoverMain.py` | 起動処理 |
| `TestPCBGeneric.py` | プロセス終了コールバックのアダプタ。拡張マネージャ（ProcessCallback 対応）を使う場合だけ必要（下記） |
| `rtc_failover.json` | Raspberry Pi Mouse と OpenCVCamera の構成例 |
| `test/` | Docker で動作を確かめるテスト環境（下記） |

C++ 版（`rtcd_failover`）もあります。ソースは `snmpmanager-cpp/src/RTCFailover.{hpp,cpp}` と `src/RTCFailoverMain.cpp` で、SNMPManager の C++ 版と一緒にビルドします（下の「C++ 版」）。設定ファイル（JSON）と動作、ログは Python 版と同じです。

## 起動

```bash
python3 RTCFailoverMain.py --failover-config rtc_failover.json -f rtc.conf
```

OpenRTM-aist の Python バインディングが使える環境で実行してください。JSON の `managers` に書いたマネージャは、あらかじめ起動しておく必要があります。`--log-level DEBUG` で詳しいログを出せます。

コントローラの rtc.conf には、応答のない相手で止まり続けないよう、タイムアウトを設定してください（例は `test/client.conf`）。

```
corba.args: -ORBclientConnectTimeOutPeriod 2000 -ORBclientCallTimeOutPeriod 5000
```

### C++ 版

```bash
rtcd_failover --failover-config rtc_failover.json -f rtc.conf      # Windows は rtcd_failover.exe
```

- 引数は Python 版と同じです（`--failover-config`、`--log-level DEBUG|INFO|WARNING|ERROR`。そのほかは OpenRTM-aist のマネージャに渡す）。
- ビルド：`snmpmanager-cpp/build.sh`（Linux。`snmpmanager-cpp/build/rtcd_failover`）、`snmpmanager-cpp/build-win.ps1`（Windows。`build-win\bin\rtcd_failover.exe`）。OpenRTM-aist に組み込んだ場合（`openrtm-ext`、`-DSNMPMANAGER_ENABLE=ON`）は、`bin/rtcd_failover` に入ります。
- 監視する RTC の言語は問いません。Python の RTC には `IDL:OpenRTM/ComponentObserver`、C++ の RTC には `IDL:omg.org/RTC/ComponentObserver` のオブザーバーを登録します（SNMPManager の C++ 版と同じ `src/ComponentObserverServant.cpp`）。
- 手動で切り替える API は、`FailoverController::handle_failure("<グループの ID>")`（グループを指定）と `reconnect_all()`（全グループ）です（C++ のプログラムに組み込んで使う場合）。
- Python 版の `TestPCBGeneric.py`（プロセス終了のコールバック）に当たるものはありません。プロセス終了は生存確認（`liveness_interval`）で検知します。

## RTC 側の設定（必須）

監視対象の RTC が動くプロセス（マスターマネージャと、create_component で起動するスレーブ）で、次の2つを設定します。

1. **ComponentObserverConsumer を読み込む**：これがないと、ERROR の通知が届きません（オブザーバの登録で「returned false」の警告が出ます）。
2. **omniORB のタイムアウトを短くする**：OpenRTM のポートは、接続情報を返すたびに接続先の生存を確かめます（`PortBase.updateConnectors` → `checkPorts`）。停止したノードとの接続が残っていると、この確認が TCP の接続タイムアウトまで止まり、生きている RTC も応答しなくなります。

```
manager.modules.load_path: <RTC のパス>, /usr/lib/python3/dist-packages/OpenRTM_aist/ext/sdo/observer
manager.modules.preload: ComponentObserverConsumer.py
corba.args: -ORBclientConnectTimeOutPeriod 2000 -ORBclientCallTimeOutPeriod 5000
```

C++ の RTC の場合は、`ComponentObserverConsumer.so`（OpenRTM-aist の `ext/sdo/observer`）を読み込みます。

## JSON の定義

| キー | 内容 |
|---|---|
| `managers` | `id`、`host`、`port`（省略時は 2810）、`name`（そのマネージャの `manager.name`。省略時は `manager`）。ローカルのマネージャは `"local": true` |
| `liveness_interval` | 生存確認の間隔（秒、既定 2.0）。0 にすると生存確認をしない |
| `observer` | `enabled`（既定 true）、`heartbeat`（ComponentObserver のハートビート。既定 false） |
| `groups[].id` | 切り替えの単位。グループはいくつでも定義できる |
| `groups[].alternatives` | グループ全体の代替候補。`priority` が小さい順に探す。`manager` は `managers.id` を参照する。どの候補も同じロールを持つ必要がある |
| `groups[].alternatives[].roles` | 候補の中で必要な RTC の論理名と、その `type`、任意の `instance`。`instance` を省略すると、型名が一致した最初の ERROR でない RTC を使う |
| `groups[].connections` | 外部との接続。`role`、`port`、`direction`（`input`/`output`）、`external`、`name`、`properties` |
| `groups[].connections[].external` | `{"url": "rtcname://..."}`（ネームサービスが必要）か、`{"manager": "<managers.id>", "component": "<インスタンス名>", "port": "<ポート名>"}`（マネージャ経由。ネームサービス不要） |
| `groups[].internal_connections` | グループ内のロールどうしの接続。`name`、`source: {role, port}`、`target: {role, port}`、`properties`。候補を選ぶたびに、その候補の RTC どうしを接続する |
| `groups[].activate` | 選んだ RTC をアクティブ化するか（既定 true） |
| `groups[].on_failure` | 切り替え前の RTC の扱い。`keep`（何もしない。既定）、`reset`（ERROR なら `reset_component` で INACTIVE に戻し、再び候補にする）、`exit`（終了させる） |

### RTC を起動時に生成する場合

最初の `alternative` に `"create": true` を追加し、`roles` の各 RTC に `create_id` と、任意で `create_options` を書きます。`instance` を書くと、`instance_name` として渡します。

```json
{
  "manager": "robot_a",
  "priority": 1,
  "create": true,
  "roles": {
    "camera": {
      "type": "OpenCVCamera",
      "instance": "OpenCVCamera0",
      "create_id": "RTC:::OpenCVCamera:C++:"
    }
  }
}
```

`create_id` には、`create_component()` が受け付ける文字列を書きます。`create_options` を付ける場合、`create_id` の末尾に `?` を含めないでください。生成先のマネージャで、その RTC のモジュールを読み込める必要があります。

## 切り替えの動作

- ERROR の通知は CORBA のスレッドで受け取り、切り替えはワーカースレッドで行います。同じグループの通知が続けて届いても、切り替えは1回にまとめます。
- 待機中の RTC で起きた ERROR は、切り替えのきっかけにしません（その RTC は候補から外れるだけです）。
- オブザーバは、現在の RTC だけでなく待機中の候補にも登録します。生存確認のたびに、新しく現れた候補にも登録します。そのため、切り替えた後でも障害を検知できます。
- 切り替えでは、外部ポート上の、名前が一致するコネクタだけを切断してから、新しい候補を接続します。外部ポートの参照は、起動時に取得したものを使い回します。
- 手動で切り替える場合は、`RTCFailover.reconnect('robot_system')`（グループを指定）、または `RTCFailover.reconnect()`（全グループ）を呼びます。

## プロセス終了の検知と TestPCBGeneric

`TestPCBGeneric.py` が使う `ProcessCallbackBase` と `ProcessCallbackFactory` は、拡張マネージャの機能で、OpenRTM-aist の master にはありません。master の OpenRTM-aist では、生存確認（`liveness_interval`）がプロセス終了の検知を代わりに行います。`TestPCBGeneric` は、ProcessCallback がない環境では登録せずに警告だけを出します。

## テスト（test/）

`docker-test` の `rtm-snmp-test` イメージを使い、3つのコンテナで確かめます（WSL2 の Ubuntu で実行）。

```bash
bash test/run_test.sh              # Python 版のコントローラ (RTCFailoverMain.py)
IMPL=cpp bash test/run_test.sh     # C++ 版のコントローラ (snmpmanager-cpp/build/rtcd_failover。先に build.sh でビルドする)
```

C++ 版では、コントローラを動かす node_c だけを、C++ の OpenRTM-aist が入った `rtm-snmp-cpp` イメージにします（`compose.yaml` の `NODE_C_IMAGE`）。

| コンテナ | 役割 |
|---|---|
| node_a | 主系。FaultyRTC0 を `create_initial` で生成する |
| node_b | 待機系。FaultyRTC0 を起動時から用意しておく |
| node_c | 出力先の ConsoleOut0。コントローラもここで動かす |

テスト用の `FaultyRTC` は、`/tmp/fault_<インスタンス名>` があると ERROR になります。出力する値は、node_a なら1000番台、node_b なら2000番台です。

| 手順 | 確認すること | 結果 |
|---|---|---|
| 1 | 起動時に node_a の FaultyRTC0 を生成し、ConsoleOut0 に接続する | PASS（1000番台が届く） |
| 2 | node_a を ERROR にすると、ComponentObserver の通知で node_b へ切り替わる | PASS（約0.2秒で切り替わる） |
| 3 | node_a を直して node_b を ERROR にすると、reset 済みの node_a へ戻る（待機中の RTC のオブザーバ） | PASS |
| 4 | node_a のコンテナを強制終了すると、生存確認で検知して node_b へ切り替わる | PASS（約8秒。最初の試行は外部ポートのタイムアウトで失敗し、再試行で成功） |

C++ 版のコントローラ（`IMPL=cpp`）でも、4 つとも PASS でした（2 は約 0.2 秒、4 は約 10 秒。4 の最初の試行がタイムアウトで失敗し、再試行で成功するのも Python 版と同じ）。Windows では、`rtcd_failover.exe` のビルドと、起動・設定の確かめ・マネージャに届かないときの動きまでを確かめています。

## 注意・未対応

- **接続の後始末**：接続に失敗したときのロールバックや、複数のマネージャをまたぐ分散トランザクションはありません。
- **未対応の機能**：サービスポートの外部接続と、通信品質に基づく候補の自動選択はありません。
- **フェイルバック**：優先順位の高い候補が復旧しても、自動で元に戻す処理はありません。
- **プロセス停止の検知時間**：ノードやプロセスの停止は、生存確認の間隔と omniORB のタイムアウトの分だけ、検知と切り替えが遅れます（テストでは約8秒）。
- **同じ型の RTC が複数ある場合**：同じマネージャに同じ型の RTC が複数ある場合は、`instance` を明示してください。
- **ERROR への遷移**：RTC が障害を検出して ERROR に遷移する処理は、各 RTC の実装しだいです。
