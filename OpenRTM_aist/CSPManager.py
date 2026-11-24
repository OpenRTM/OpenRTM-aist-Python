#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPManager.py
# @if jp
# @brief CSPポートの選択と再走査を管理する。
# @else
# @brief Manage CSP port selection and rescanning.
# @endif
# @date $Date: 2026-11-13 15:32:20 $
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

# Copyright (C) 2019
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
import OpenRTM_aist.CSPEventPort
import copy
import CSP
import threading
import time
from contextlib import contextmanager
from OpenRTM_aist.CSPArbitration import arbiter


##
# @if jp
#
# @class CSPManager
#
# @brief CSPOutPort、CSPInPortを管理するクラス
#
#
# @since 2.0.0
#
# @else
#
# @class CSPManager
#
# @brief Manage CSP port selection and rescanning.
#
#
# @since 2.0.0
#
# @endif
#
class CSPManager:
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    #
    # @else
    #
    # @brief A constructor.
    #
    #
    # @endif
    #
    def __init__(self) -> None:
        self._outports = []
        self._inports = []
        self._ctrl = CSPManager.CSPThreadCtrl()
        self._writableOutPort = None
        self._readableInPort = None
        self._notify_flag = True
        self._current_port = None
        self._ret = False
        self._portList = []
        self._selection_active = False
        self._selection_winner = None
        self._selection_epoch = 0
        self._arbitration_parked = False
        self._rescan_ports = None
        self._arbitration_grant = None  # Assigned but not yet consumed by select.
        self._arbitration_token = None  # Grant consumed by the current rescan.
        self._arbitration_stats = {'rescan_grants': 0, 'deferred': 0, 'timeouts': 0, 'priority_rescans': 0, 'yielded': 0, 'unavailable_retained': 0}
        self._arbitration_priority = arbiter.register(self)
        self._remote_pending = {}
        self._scan_yield = False
        self._readiness_requests = threading.local()
        self.name = ""

    ##
    # @if jp
    # @brief プロセスUUIDと登録番号からなる固定Manager IDを取得する。
    # @else
    # @brief Get the fixed manager ID composed of a process UUID and registration number.
    # @endif
    def getManagerId(self):
        """Return the fixed, process-qualified manager identity."""
        return self._arbitration_priority

    ##
    # @if jp
    # @brief 辞書順で比較可能な固定優先度キーを取得する。
    # @else
    # @brief Get the fixed priority key compared in lexicographical order.
    # @endif
    def getPriority(self):
        """Return the comparable priority key; smaller keys take precedence.

        The UUID prefix distinguishes processes. The hexadecimal suffix keeps
        registration order inside each process. No global startup clock is used.
        """
        return self._arbitration_priority

    ##
    # @if jp
    #
    # @brief デストラクタ
    #
    # デストラクタ。
    #
    # @else
    #
    # @brief Destructor
    #
    # Destructor
    #
    # @endif
    #

    def __del__(self) -> None:
        pass

    ##
    # @if jp
    #
    # @brief CSPポートに設定したCSPManagerとの関連付けを解除
    #
    #
    # @else
    #
    # @brief Cancel selection and clear registered ports and pending requests.
    #
    #
    # @endif
    #
    def reset(self) -> None:
        with self._ctrl._cond:
            token = (self._arbitration_grant if self._arbitration_grant is not None
                     else self._arbitration_token)
            self._arbitration_grant = self._arbitration_token = None
            self._rescan_ports = None
            self._arbitration_parked = False
            ports = self._outports + self._inports
            self._outports = []
            self._inports = []
            self._notify_flag = True
            self._portList = []
            self._selection_active = False
            self._remote_pending = {}
            self._scan_yield = False
            self._ctrl._waiting = False
            self._ctrl._cond.notify_all()
        # Port callbacks also acquire the manager lock. Never hold it while
        # acquiring a port/listener lock.
        for port in ports:
            port.releaseManager()
        arbiter.release(self, token)

    ##
    # @if jp
    # @brief 選択結果を確定し、当該世代の再走査権を解放する。
    # @param ret `ret`の値。
    # @param outport 出力ポート。
    # @param inport 入力ポート。
    # @else
    # @brief Finalize selection and release the rescan grant for its generation.
    # @param ret Value of ret.
    # @param outport Output port.
    # @param inport Input port.
    # @endif
    def _finishSelection(self, ret: bool = False, outport=None, inport=None):
        with self._ctrl._cond:
            if ret and self._selection_winner is None:
                self._selection_winner = (outport, inport)
            winner = self._selection_winner
            token = (self._arbitration_grant if self._arbitration_grant is not None
                     else self._arbitration_token)
            self._arbitration_grant = self._arbitration_token = None
            self._rescan_ports = None
            self._arbitration_parked = False
            self._selection_active = False
            self._ctrl._waiting = False
            self._notify_flag = True
            ports = self._outports + self._inports
        selected = (winner[0] or winner[1]) if winner else None
        for port in ports:
            close = getattr(port, "endSelection", None)
            if close is not None:
                close(port is selected)
        if winner:
            arbiter.release(self, token)
            return True, winner[0], winner[1]
        arbiter.release(self, token)
        return False, None, None

    ##
    # @if jp
    # @brief `readiness State`に対応する処理を行う。
    # @else
    # @brief Perform the readiness state operation.
    # @endif
    def _readinessState(self):
        """Classify a failed ordinary request locally, without reserving data."""
        with self._ctrl._cond:
            if not self._selection_active or self._selection_winner is not None:
                return CSP.NOT_SELECTING
            return CSP.NOT_READY if self._ctrl._waiting else CSP.SCANNING

    ##
    # @if jp
    # @brief 未受付の遠隔接続を再試行候補として保持する。
    # @param port 操作対象のポート。
    # @else
    # @brief Retain unavailable remote connections as retry candidates.
    # @param port Port to operate on.
    # @endif
    def _rememberUnavailablePeers(self, port) -> None:
        for connector in list(getattr(port, '_connectors', ())):
            getter = getattr(connector, 'getPeerReadinessState', None)
            if getter is None or getter() not in (CSP.SCANNING, CSP.NOT_SELECTING):
                continue
            identity = connector.id()
            peers = getattr(port, '_csp_request_peers', {}).get(identity, ())
            with self._ctrl._cond:
                if not self._selection_active:
                    return
                for manager_id, priority in peers:
                    if manager_id == self.getManagerId():
                        continue
                    if port not in self._portList:
                        self._portList.append(port)
                    if manager_id.split(':')[0] != self.getManagerId().split(':')[0]:
                        self._remote_pending.setdefault(port, {})[identity] = priority
                        self._arbitration_stats['unavailable_retained'] += 1

    ##
    # @if jp
    # @brief 各ポートの走査境界で譲り要求を確認する。
    # @param ports 検索するポート候補。
    # @param retry 再試行の問い合わせかどうか。
    # @else
    # @brief Check for a yield request at each port scan boundary.
    # @param ports Port candidates to search.
    # @param retry Whether this query is a retry.
    # @endif
    def _probePorts(self, ports: list, retry: bool = False):
        for port in list(ports):
            with self._ctrl._cond:
                if not self._selection_active or self._scan_yield:
                    return False, None, None
                is_inport = port in self._inports
                if not is_inport and port not in self._outports:
                    continue
            # Do not hold a manager mutex across a remote readiness query.
            ready = port.reselect() if retry else port.select()
            if ready:
                return True, None if is_inport else port, port if is_inport else None
            self._rememberUnavailablePeers(port)
        return False, None, None

    ##
    # @if jp
    #
    # @brief 書き込み可能なOutPortを選択する
    #
    # @return ret, port
    # ret：True(書き込み可能なOutPortが存在する)、False(存在しない)
    # port：書き込み可能なOutPort。選択できなかった場合はNone
    #
    # @else
    #
    # @brief Select a ready output port.
    #
    # @return
    #
    # @endif
    #
    def selectOutPort(self):
        for port in self._outports:
            if port.select():
                return True, port
        return False, None

    ##
    # @if jp
    #
    # @brief 読み込み可能なInPortを選択する
    #
    # @return ret, port
    # ret：True(読み込み可能なInPortが存在する)、False(存在しない)
    # port：読み込み可能なInPort。選択できなかった場合はNone
    #
    # @else
    #
    # @brief Select a ready input port.
    #
    # @return
    #
    # @endif
    #
    def selectInPort(self):
        for port in self._inports:
            if port.select():
                return True, port
        return False, None

    ##
    # @if jp
    #
    # @brief ポートをロックモードと非ロックモードに仕分けする
    #
    # @return ports1, ports2
    # ports1:ロックモードのポート
    # ports2:非ロックモードのポート
    #
    # @else
    #
    # @brief Get the registered synchronous and asynchronous ports.
    #
    # @return
    #
    # @endif
    #
    def getPorts(self):
        ports1 = []
        ports2 = []
        for port in self._inports:
            if port.getSyncMode():
                ports1.append(port)
            else:
                ports2.append(port)

        for port in self._outports:
            if port.getSyncMode():
                ports1.append(port)
            else:
                ports2.append(port)
        return ports1, ports2

    ##
    # @if jp
    #
    # @brief ポート一覧から通信可能なポートを自動選択する
    #
    # @param ports 選択対象のポート一覧
    # @return ret, outport, inport
    # ret:True：選択成功、False：選択失敗
    # outport：選択したOutPort。OutPortを選択しなかった場合はNone
    # inport：選択したInPort。InPortを選択しなかった場合はNone
    #
    # @else
    #
    # @brief Search the supplied port candidates.
    #
    # @param ports
    # @return
    #
    # @endif
    #
    def selectPort(self, ports):
        return self._probePorts(ports)

    ##
    # @if jp
    #
    # @brief ポート一覧から通信可能なポートを再選択する
    #
    # @param ports 選択対象のポート一覧
    # @return ret, outport, inport
    # ret:True：選択成功、False：選択失敗
    # outport：選択したOutPort。OutPortを選択しなかった場合はNone
    # inport：選択したInPort。InPortを選択しなかった場合はNone
    #
    # @else
    #
    # @brief Rescan the supplied candidates.
    #
    # @param ports
    # @return
    #
    # @endif
    #
    def reselectPort(self, ports):
        return self._probePorts(ports, retry=True)

    ##
    # @if jp
    #
    # @brief 読み込み可能なInPort、もしくは書き込み可能なOutPortを選択する
    # 読み込み可能なInPort、書き込み可能なOutPortが存在しない場合はタイムアウトまで待機する
    # 待機解除後、読み込み可能なInPort、もしくは書き込み可能なOutPortを再度選択する
    #
    # @param timeout 待機のタイムアウト時間
    # @return ret, outport, inport
    # ret：Ture(書き込み、読み込み可能なポートが存在)、False(タイムアウト)
    # outport：OutPortを選択した場合に、書き込み可能なOutPortを格納
    # inport：InPortを選択した場合に、読み込み可能なInortを格納
    #
    # @else
    #
    # @brief Select one ready registered port.
    #
    # @param timeout
    # @return
    #
    # @endif
    #
    def select(self, timeout: int):
        deadline = time.monotonic() + max(timeout, 0)
        with self._ctrl._cond:
            if self._selection_active:
                raise RuntimeError("Concurrent select() on the same CSPManager")
            self._selection_active = True
            self._selection_epoch += 1
            self._portList = []
            self._remote_pending = {}
            self._scan_yield = False
            self._arbitration_parked = False
            self._rescan_ports = None
            self._arbitration_grant = self._arbitration_token = None
            self._selection_winner = None
            self._writableOutPort = None
            self._readableInPort = None
            self._notify_flag = False
            self._ctrl._waiting = False
            self._ctrl._timeout = True
        try:
            for port in self._outports + self._inports:
                begin = getattr(port, "beginSelection", None)
                if begin is not None:
                    begin()
            ports1, ports2 = self.getPorts()
            for ports, retry in [(ports2, False), (ports2, True), (ports1, False)]:
                ret, outport, inport = self._probePorts(ports, retry)
                if ret:
                    return self._finishSelection(ret, outport, inport)
            while True:
                with self._ctrl._cond:
                    if not self._selection_active:
                        break
                    if timeout < 0:
                        break
                    # Only release a grant already consumed by this thread.
                    # A grant arriving before/after park remains unconsumed.
                    token, self._arbitration_token = self._arbitration_token, None
                    self._ctrl._waiting = True
                    self._arbitration_parked = True
                # A request received during a scan is retained. A failed remote
                # retry stays queued: the peer may not have reached its wait yet.
                arbiter.release(self, token)
                self._schedulePriorityRescan()
                with self._ctrl._cond:
                    if self._selection_active and self._rescan_ports is None:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0:
                            self._arbitration_stats['timeouts'] += 1
                            break
                        self._ctrl._cond.wait(min(remaining, 0.01))
                    if not self._selection_active:
                        break
                    if self._rescan_ports is None:
                        continue
                    self._ctrl._waiting = False
                    self._arbitration_parked = False
                    self._scan_yield = False
                    pending, self._rescan_ports = self._rescan_ports, None
                    self._arbitration_token = self._arbitration_grant
                    self._arbitration_grant = None
                    if time.monotonic() >= deadline:
                        self._arbitration_stats['timeouts'] += 1
                        break
                ret, outport, inport = self._probePorts(pending)
                if ret:
                    return self._finishSelection(ret, outport, inport)
                # Retry only after a local delay, without querying remote state.
                with self._ctrl._cond:
                    if self._selection_active:
                        self._ctrl._waiting = True
                        self._arbitration_parked = True
                        self._ctrl._cond.wait(min(max(deadline - time.monotonic(), 0), 0.01))
            return self._finishSelection()
        except BaseException:
            self._finishSelection()
            raise

    ##
    # @if jp
    #
    # @brief 待機状態解除を通知
    # select関数で待機している場合に、待機を解除する
    #
    # @return True：待機状態を解除、False：待機状態ではない
    #
    # @param outport 出力ポート。
    # @param inport 入力ポート。
    # @param connector_id 要求に対応する接続ID。
    # @else
    #
    # @brief Notify the manager of a request and determine selection admission.
    #
    # @return
    #
    # @param outport Output port.
    # @param inport Input port.
    # @param connector_id Connector ID associated with the request.
    # @endif
    #

    def notify(self, outport=None, inport=None, connector_id=None):
        # Keep the boolean API used by listeners and application code. Capture
        # the immutable result of the same locked decision for the current RPC.
        state = self._notifyReadiness(outport, inport, connector_id)
        requests = getattr(self._readiness_requests, 'stack', ())
        if requests:
            response = requests[-1]
            port = outport if outport is not None else inport
            if port is response['port'] and connector_id == response['connector_id']:
                response['state'] = state
        return state == CSP.READY

    ##
    # @if jp
    # @brief 受付時に確定したReadinessを呼び出し元へ引き継ぐ。
    # @param port 操作対象のポート。
    # @param connector_id 要求に対応する接続ID。
    # @else
    # @brief Carry the Readiness captured during admission back to the caller.
    # @param port Port to operate on.
    # @param connector_id Connector ID associated with the request.
    # @endif
    @contextmanager
    def _captureReadiness(self, port, connector_id):
        """Capture only this thread's matching notify, without holding a lock.

        A stack isolates nested callbacks; finally also clears failed requests.
        No port callback or remote guard runs with the manager mutex held.
        """
        stack = getattr(self._readiness_requests, 'stack', None)
        if stack is None:
            stack = self._readiness_requests.stack = []
        response = {'port': port, 'connector_id': connector_id, 'state': None}
        stack.append(response)
        try:
            yield response
        finally:
            stack.pop()

    ##
    # @if jp
    # @brief 受付判断・保留登録・Readiness確定を同じ制御ロック内で行う。
    # @param outport 出力ポート。
    # @param inport 入力ポート。
    # @param connector_id 要求に対応する接続ID。
    # @else
    # @brief Determine admission, retain requests and capture Readiness under the same control lock.
    # @param outport Output port.
    # @param inport Input port.
    # @param connector_id Connector ID associated with the request.
    # @endif
    def _notifyReadiness(self, outport=None, inport=None, connector_id=None):
        """Decide admission, retain requests and classify the reply atomically."""
        with self._ctrl._cond:
            if (outport is None) == (inport is None):
                return CSP.NOT_READY
            port = outport if outport is not None else inport
            if (port is None or (outport is not None and outport not in self._outports) or (inport is not None and inport not in self._inports)):
                return CSP.NOT_READY
            if not self._selection_active or self._selection_winner is not None:
                return CSP.NOT_SELECTING
            if self._ctrl._waiting:
                # Membership, winner publication and disarming are atomic.
                self._selection_winner = (outport, inport)
                self._writableOutPort = outport
                self._readableInPort = inport
                self._ctrl._timeout = False
                self._ctrl._waiting = False
                self._selection_active = False
                self._ctrl._cond.notify_all()
                return CSP.READY
            # Read immutable connection-time metadata, without taking a port
            # mutex while holding the manager mutex (listeners use port->manager).
            for identity, priority in getattr(port, '_csp_request_peers', {}).get(connector_id, ()):
                if identity == self.getManagerId():
                    continue
                if priority < self.getPriority():
                    self._scan_yield = True
                    self._arbitration_stats['yielded'] += 1
                if identity.split(':')[0] != self.getManagerId().split(':')[0]:
                    self._remote_pending.setdefault(port, {})[connector_id] = priority
            if port not in self._portList:
                self._portList.append(port)
                self._arbitration_stats['deferred'] += 1
            return CSP.SCANNING

    ##
    # @if jp
    # @brief 接続時の固定優先度に基づいて遠隔候補の再走査を準備する。
    # @else
    # @brief Prepare a remote rescan using the fixed priorities exchanged at connection time.
    # @endif

    def _schedulePriorityRescan(self) -> None:
        """Retry only requests from lower-priority remote managers.

        No remote state is fetched. Receivers yield at a local scan boundary;
        a premature retry fails and remains pending until success or timeout.
        """
        with self._ctrl._cond:
            if not (self._selection_active and self._ctrl._waiting and self._arbitration_parked and self._rescan_ports is None):
                return
            for port in self._portList:
                requests = self._remote_pending.get(port, {})
                # A higher-priority request for this port must be served by waiting.
                if any(priority < self.getPriority() for priority in requests.values()):
                    continue
                current = getattr(port, '_csp_request_peers', {})
                if any(self.getPriority() < priority and connector in current
                       for connector, priority in requests.items()):
                    self._scan_yield = False
                    self._rescan_ports = [port]
                    self._ctrl._waiting = False
                    self._arbitration_parked = False
                    self._arbitration_stats['rescan_grants'] += 1
                    self._arbitration_stats['priority_rescans'] += 1
                    self._ctrl._cond.notify_all()
                    return

    ##
    # @if jp
    #
    # @brief InPortを追加
    #
    # @param port InPort
    #
    # @else
    #
    # @brief Add in port.
    #
    # @param port
    #
    # @endif
    #
    def addInPort(self, port) -> None:
        self._inports.append(port)

    ##
    # @if jp
    #
    # @brief OutPortを追加
    #
    # @param port OutPort
    #
    # @else
    #
    # @brief Add out port.
    #
    # @param port
    #
    # @endif
    #
    def addOutPort(self, port) -> None:
        self._outports.append(port)

    ##
    # @if jp
    #
    # @brief InPortを削除
    #
    # @param port InPort
    #
    # @else
    #
    # @brief Remove in port.
    #
    # @param port
    #
    # @endif
    #
    def removeInPort(self, port) -> None:
        self._inports.remove(port)

    ##
    # @if jp
    #
    # @brief Outortを削除
    #
    # @param port OutPort
    #
    # @else
    #
    # @brief Remove out port.
    #
    # @param port
    #
    # @endif
    #
    def removeOutPort(self, port) -> None:
        self._outports.remove(port)

    ##
    # @if jp
    # @brief `CSPThreadCtrl`の状態と操作をまとめる。
    # @else
    # @brief Encapsulate the state and operations of CSPThreadCtrl.
    # @endif
    class CSPThreadCtrl:
        ##
        # @if jp
        # @brief インスタンスと内部状態を初期化する。
        # @else
        # @brief Initialize the instance and its internal state.
        # @endif
        def __init__(self) -> None:
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._port = None
            self._waiting = False
            self._timeout = True
            self._select_mutex = threading.RLock()
            self._select_cond = threading.Condition(self._mutex)
