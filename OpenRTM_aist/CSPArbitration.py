#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CSPArbitration.py
# @if jp
# @brief 同一プロセス内のManagerの再走査権を調停する。
# @else
# @brief Arbitrate rescan grants among managers in the same process.
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

"""Order deferred CSP rescans inside one RTC process.

No manager/port lock is held across a CORBA call. Initial scans remain
concurrent. A rescan runs only after its owner has parked and, for known
local peers, a peer has parked too. The receiver can therefore accept notify
without racing its own outgoing readiness call.
"""
import itertools
import os
import re
import uuid
import threading
import weakref


##
# @if jp
# @brief 同一プロセス内の再走査権を調停する。
# @else
# @brief Arbitrate rescan grants within one process.
# @endif
class RescanArbiter:
    ##
    # @if jp
    # @brief インスタンスと内部状態を初期化する。
    # @else
    # @brief Initialize the instance and its internal state.
    # @endif
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._sequence = itertools.count()
        self._pid = os.getpid()
        self._process_id = uuid.uuid4().hex
        self._managers = weakref.WeakValueDictionary()
        self._connections = {}
        self._owner = None
        self._owner_token = None
        self._grant_sequence = itertools.count(1)

    ##
    # @if jp
    # @brief Managerをローカル調停器へ登録し、固定キーを割り当てる。
    # @param manager 関連付けるManager。
    # @else
    # @brief Register a manager with the local arbiter and assign its fixed key.
    # @param manager Manager to associate with the object.
    # @endif
    def register(self, manager):
        with self._lock:
            if self._pid != os.getpid():
                self._pid = os.getpid()
                self._process_id = uuid.uuid4().hex
            # Globally comparable key; preserve registration order within a process.
            priority = "%s:%016x" % (self._process_id, next(self._sequence))
            self._managers[priority] = manager
            return priority

    ##
    # @if jp
    # @brief ポートの接続を確立する。
    # @param connector `connector`の値。
    # @param port 操作対象のポート。
    # @else
    # @brief Establish a port connection.
    # @param connector Value of connector.
    # @param port Port to operate on.
    # @endif
    def connect(self, connector, port) -> None:
        with self._lock:
            key = connector.id()
            ends = self._connections.setdefault(key, weakref.WeakValueDictionary())
            ends[id(port)] = port

    ##
    # @if jp
    # @brief ローカル相手が再走査を受け付けられるか調べる。
    # @param manager 関連付けるManager。
    # @param port 操作対象のポート。
    # @else
    # @brief Check whether a local peer can accept a rescan.
    # @param manager Manager to associate with the object.
    # @param port Port to operate on.
    # @endif
    def _ready_peer(self, manager, port) -> bool:
        # Never take port locks here: RPC listeners acquire port then manager.
        connectors = list(getattr(port, '_connectors', ()))
        if not connectors:  # Test/custom ports, or a remote/standalone endpoint.
            return True
        for connector in connectors:
            ends = self._connections.get(connector.id(), {})
            peers = [p for p in list(ends.values()) if p is not port]
            if not peers:
                peers_with_priority = getattr(port, '_csp_request_peers', {}).get(connector.id(), ())
                if peers_with_priority:
                    continue  # Remote requests are retried using their fixed priority.
                return True  # Legacy endpoint: retain the existing wire protocol.
            for peer in peers:
                other = getattr(peer, '_manager', None)
                if other is None:
                    return True
                if other is manager:
                    continue  # A select cannot rendezvous with itself.
                with other._ctrl._cond:
                    if other._selection_active and other._ctrl._waiting:
                        return True
        return False

    ##
    # @if jp
    # @brief 待機中のManagerへ再走査権を割り当てる。
    # @else
    # @brief Assign a rescan grant to a waiting manager.
    # @endif
    def schedule(self) -> None:
        with self._lock:
            if self._owner is not None and self._owner() is None:
                self._owner = None
                self._owner_token = None
            if self._owner is not None:
                return
            for priority, manager in sorted(list(self._managers.items())):
                with manager._ctrl._cond:
                    if not (manager._selection_active and manager._ctrl._waiting and manager._arbitration_parked and manager._portList):
                        continue
                    pending = list(manager._portList)
                eligible = [port for port in pending if self._ready_peer(manager, port)]
                if not eligible:
                    continue
                with manager._ctrl._cond:
                    # A notification may have won since the snapshot.
                    if not (manager._selection_active and manager._ctrl._waiting and manager._arbitration_parked):
                        continue
                    manager._rescan_ports = eligible
                    token = next(self._grant_sequence)
                    manager._arbitration_grant = token
                    manager._portList = [p for p in manager._portList if p not in eligible]
                    manager._ctrl._waiting = False
                    manager._arbitration_parked = False
                    self._owner = weakref.ref(manager)
                    self._owner_token = token
                    manager._arbitration_stats['rescan_grants'] += 1
                    manager._ctrl._cond.notify_all()
                    return

    ##
    # @if jp
    # @brief 対応するローカル再走査権を解放する。
    # @param manager 関連付けるManager。
    # @param token 解放対象の再走査権の世代。
    # @else
    # @brief Release the matching local rescan grant.
    # @param manager Manager to associate with the object.
    # @param token Generation of the rescan grant to release.
    # @endif
    def release(self, manager, token) -> None:
        """Release the exact consumed/cancelled grant, never a newer grant.

        The token is captured before publishing a new wait, or while closing
        the selection. None means no grant was consumed; it cannot clear one
        assigned asynchronously before this release reaches the arbiter.
        """
        with self._lock:
            if (token is not None and self._owner is not None and self._owner() is manager and self._owner_token == token):
                self._owner = None
                self._owner_token = None
        self.schedule()


arbiter = RescanArbiter()


##
# @if jp
# @brief 接続時の固定ID・優先度情報を交換・保持する。
# @else
# @brief Exchange and retain fixed IDs and priorities at connection time.
# @endif
class CSPConnectionInfo:
    """Exchange fixed manager identities during the standard connect handshake.

    Fixed properties advertise request-time priority arbitration support.
    Missing/unknown metadata denotes a legacy peer.
    """
    _PREFIX = "dataport.csp.arbitration."
    _KEY = re.compile(r"[0-9a-f]{32}:[0-9a-f]{16,}\Z")

    ##
    # @if jp
    # @brief インスタンスと内部状態を初期化する。
    # @param args `args`の値。
    # @param kwargs `kwargs`の値。
    # @else
    # @brief Initialize the instance and its internal state.
    # @param args Value of args.
    # @param kwargs Value of kwargs.
    # @endif
    def __init__(self, *args, **kwargs) -> None:
        self._csp_peer_priorities = {}
        self._csp_request_peers = {}
        super(CSPConnectionInfo, self).__init__(*args, **kwargs)

    ##
    # @if jp
    # @brief 接続プロファイルへ提供インターフェースの情報を公開する。
    # @param profile 接続プロファイル。
    # @else
    # @brief Publish provided interface information in the connector profile.
    # @param profile Connector profile.
    # @endif
    def publishInterfaces(self, profile):
        import RTC
        import OpenRTM_aist
        result = super(CSPConnectionInfo, self).publishInterfaces(profile)
        if result != RTC.RTC_OK:
            return result
        for index, reference in enumerate(profile.ports):
            if not reference._is_equivalent(self.getPortRef()):
                continue
            prefix = self._PREFIX + str(index) + "."
            # Replace this endpoint's metadata, including stale caller-supplied keys.
            profile.properties[:] = [nv for nv in profile.properties
                                     if not nv.name.startswith(prefix)]
            manager = self._manager
            if manager is not None:
                profile.properties.extend([
                    OpenRTM_aist.NVUtil.newNV(prefix + "version", "1"),
                    OpenRTM_aist.NVUtil.newNV(prefix + "manager_id", manager.getManagerId()),
                    OpenRTM_aist.NVUtil.newNV(prefix + "priority", manager.getPriority()),
                    OpenRTM_aist.NVUtil.newNV(prefix + "request_arbitration", "1")])
        return result

    ##
    # @if jp
    # @brief 相手のインターフェースと固定メタデータを購読する。
    # @param profile 接続プロファイル。
    # @else
    # @brief Subscribe to peer interfaces and fixed metadata.
    # @param profile Connector profile.
    # @endif
    def subscribeInterfaces(self, profile):
        import RTC
        import OpenRTM_aist
        result = super(CSPConnectionInfo, self).subscribeInterfaces(profile)
        peers = []
        request_peers = []
        if result == RTC.RTC_OK:
            values = {nv.name: nv.value.value() for nv in profile.properties
                      if nv.name.startswith(self._PREFIX) and isinstance(nv.value.value(), str)}
            for index, reference in enumerate(profile.ports):
                if reference._is_equivalent(self.getPortRef()):
                    continue
                prefix = self._PREFIX + str(index) + "."
                version = values.get(prefix + "version", "")
                identity = values.get(prefix + "manager_id", "")
                priority = values.get(prefix + "priority", "")
                if version == "1" and self._KEY.fullmatch(identity) and self._KEY.fullmatch(priority):
                    peers.append({"port_index": index, "manager_id": identity, "priority": priority})
                    if values.get(prefix + "request_arbitration") == "1":
                        request_peers.append((identity, priority))

        with self._connector_mutex:
            if result == RTC.RTC_OK:
                self._csp_peer_priorities[profile.connector_id] = tuple(peers)
                self._csp_request_peers[profile.connector_id] = tuple(request_peers)
            else:
                self._csp_peer_priorities.pop(profile.connector_id, None)
                self._csp_request_peers.pop(profile.connector_id, None)
        return result

    ##
    # @if jp
    # @brief 接続通知を処理し、接続情報を確定する。
    # @param profile 接続プロファイル。
    # @else
    # @brief Process a connection notification and finalize connector information.
    # @param profile Connector profile.
    # @endif
    def notify_connect(self, profile):
        import RTC
        result, profile = super(CSPConnectionInfo, self).notify_connect(profile)
        with self._connector_mutex:
            if result != RTC.RTC_OK:
                self._csp_peer_priorities.pop(profile.connector_id, None)
                self._csp_request_peers.pop(profile.connector_id, None)
            else:
                for connector in self._connectors:
                    arbiter.connect(connector, self)
        return result, profile

    ##
    # @if jp
    # @brief 接続に対応する購読情報を解除する。
    # @param profile 接続プロファイル。
    # @else
    # @brief Remove subscriptions associated with the connection.
    # @param profile Connector profile.
    # @endif
    def unsubscribeInterfaces(self, profile):
        try:
            return super(CSPConnectionInfo, self).unsubscribeInterfaces(profile)
        finally:
            with self._connector_mutex:
                self._csp_peer_priorities.pop(profile.connector_id, None)
                self._csp_request_peers.pop(profile.connector_id, None)

    ##
    # @if jp
    # @brief 接続時に保存した相手の固定優先度情報を取得する。
    # @param connector_id 要求に対応する接続ID。
    # @else
    # @brief Get the fixed peer priority information stored at connection time.
    # @param connector_id Connector ID associated with the request.
    # @endif
    def getPeerPriorities(self, connector_id=None):
        """Return copies of the connection-time metadata, never live scan state.

        With an ID return a tuple of peer endpoint dictionaries; without one
        return a dictionary keyed by connector ID. Unknown peers have no entries.
        Changing managers after connection requires disconnect/reconnect.
        """
        with self._connector_mutex:
            snapshot = {key: tuple(dict(peer) for peer in peers)
                        for key, peers in self._csp_peer_priorities.items()}
        return snapshot if connector_id is None else snapshot.get(connector_id, ())
