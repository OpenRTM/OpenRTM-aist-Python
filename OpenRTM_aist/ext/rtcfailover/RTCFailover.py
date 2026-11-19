#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file RTCFailover.py
# @brief Configuration-driven OpenRTM RTC creation, wiring and failover
#
# @~japanese
# 設定ファイル方式の RTC の生成・接続・フェイルオーバー
#
# 設定ファイル (JSON) で定義したグループごとに、代替候補 (alternatives) の中から使える RTC の組を選んで接続・アクティブ化し、障害時に次の候補へ切り替える。
#
# 障害の検知:
# - ComponentObserver (OpenRTM.ComponentObserver) の RTC_STATUS で ERROR を受信 (RTC 側のプロセスで ComponentObserverConsumer を読み込んでおく必要がある)
# - 定期的な生存確認 (liveness): 現在の RTC に到達できない (プロセス終了など)、または ERROR 状態になっている場合
# @~english
# For each group defined in the configuration file (JSON), a usable set of RTCs is chosen from the alternatives, connected and activated, and on failure it switches to the next candidate.
#
# Failure detection:
# - ERROR received in RTC_STATUS of ComponentObserver (OpenRTM.ComponentObserver) (ComponentObserverConsumer must be loaded in the processes of the RTCs)
# - Periodic liveness check: the current RTC is unreachable (process exit, etc.) or in the ERROR state
# @~
#
# @date $Date: 2026-11-13 16:24:19 $
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

import json
import logging
import os
import queue
import threading
import typing as _typing

LOG = logging.getLogger(__name__)
_LOCK = threading.RLock()
_CONTROLLER = None

ON_FAILURE = ("keep", "reset", "exit")


##
# @~japanese
# @brief OpenRTM_aist を返す (遅延 import)
#
# @return OpenRTM_aist モジュール
# @~english
# @brief Returns OpenRTM_aist (lazy import)
#
# @return OpenRTM_aist module
# @~
def _rtm():
    import OpenRTM_aist
    return OpenRTM_aist


##
# @~japanese
# @brief RTC を返す (遅延 import)
#
# @return RTC モジュール
# @~english
# @brief Returns RTC (lazy import)
#
# @return RTC module
# @~
def _rtc():
    import RTC
    return RTC


##
# @~japanese
# @brief CORBA の参照が nil か
#
# @param obj 参照
# @return nil (または None) なら True
# @~english
# @brief Whether a CORBA reference is nil
#
# @param obj reference
# @return True if nil (or None)
# @~
def _nil(obj):
    if obj is None:
        return True
    from omniORB import CORBA
    try:
        return CORBA.is_nil(obj)
    except Exception:
        return False


##
# @~japanese
# @brief CORBA_RTCUtil.connect などの戻り値 (RTC.ReturnCode_t) が成功か
#
# omniORBpy の列挙型は整数と等しくならない (RTC.RTC_OK == 0 は False) ので、RTC.RTC_OK と比較する。
#
# @param result 戻り値
# @return 成功なら True
# @~english
# @brief Whether a return value (RTC.ReturnCode_t) of CORBA_RTCUtil.connect etc. is success
#
# Enumerations of omniORBpy do not equal integers (RTC.RTC_OK == 0 is False), so it is compared with RTC.RTC_OK.
#
# @param result return value
# @return True on success
# @~
def _ok(result):
    return result is None or result == _rtc().RTC_OK


##
# @~japanese
# @brief 設定ファイルを読んで確かめる
#
# @param path 設定ファイルのパス
# @return 設定
# @~english
# @brief Reads and validates the configuration file
#
# @param path path of the configuration file
# @return configuration
# @~
def load_config(path=None):
    path = path or os.environ.get('RTC_FAILOVER_CONFIG', 'rtc_failover.json')
    with open(path, encoding='utf-8') as stream:
        cfg = json.load(stream)
    if not isinstance(cfg.get('groups'), list) or not cfg['groups']:
        raise ValueError('groups must be a nonempty list')
    if not isinstance(cfg.get('managers'), list) or not cfg['managers']:
        raise ValueError('managers must be a nonempty list')
    ids = [m['id'] for m in cfg['managers']]
    if len(ids) != len(set(ids)):
        raise ValueError('manager ids must be unique')
    gids = [g.get('id') for g in cfg['groups']]
    if None in gids or len(gids) != len(set(gids)):
        raise ValueError('group ids must be present and unique')
    for group in cfg['groups']:
        if not group.get('alternatives') or not (group.get('connections') or group.get('internal_connections')):
            raise ValueError('group requires alternatives and connections: %s' % group.get('id'))
        if group.get('on_failure', 'keep') not in ON_FAILURE:
            raise ValueError('on_failure must be one of %s' % (ON_FAILURE,))
        roles = set(group['alternatives'][0]['roles'])
        for alt in group['alternatives']:
            if alt['manager'] not in ids:
                raise ValueError('unknown manager: %s' % alt['manager'])
            if not alt.get('roles'):
                raise ValueError('alternative requires roles')
            if set(alt['roles']) != roles:
                raise ValueError('all alternatives of group %s must define the same roles' % group['id'])
        for conn in group.get('connections', []):
            if conn['role'] not in roles:
                raise ValueError('connection role absent from first alternative: %s' % conn['role'])
            if conn.get('direction') not in ('input', 'output'):
                raise ValueError('direction must be input or output')
            ext = conn.get('external', {})
            if not ext.get('url') and not (ext.get('manager') and ext.get('component') and ext.get('port')):
                raise ValueError('external needs url or manager/component/port: %s' % conn.get('name'))
            if ext.get('manager') and ext['manager'] not in ids:
                raise ValueError('unknown manager in external: %s' % ext['manager'])
        for conn in group.get('internal_connections', []):
            for end in ('source', 'target'):
                if conn.get(end, {}).get('role') not in roles or not conn[end].get('port'):
                    raise ValueError('internal connection %s needs %s.role/port' % (conn.get('name'), end))
    return cfg


##
# @~japanese
# @brief ComponentObserver のサーバントを作る (OpenRTM__POA が必要なので遅延 import)
# @~english
# @brief Makes ComponentObserver servants (lazy import since OpenRTM__POA is required)
# @~
class _ObserverFactory:
    _cls = None

    ##
    # @~japanese
    # @brief グループの RTC のサーバントを作る
    #
    # @param controller FailoverController
    # @param group_id グループの ID
    # @param key RTC のキー
    # @return サーバント
    # @~english
    # @brief Makes a servant for an RTC of a group
    #
    # @param controller FailoverController
    # @param group_id group ID
    # @param key key of the RTC
    # @return servant
    # @~
    @classmethod
    def make(cls, controller, group_id, key):
        if cls._cls is None:
            import OpenRTM
            import OpenRTM__POA

            class FailoverObserver(OpenRTM__POA.ComponentObserver):
                def __init__(self, ctrl, gid, comp_key) -> None:
                    self.ctrl, self.group_id, self.key = ctrl, gid, comp_key

                def update_status(self, status_kind, hint) -> None:  # oneway
                    if status_kind == OpenRTM.RTC_STATUS and hint.split(':', 1)[0] == 'ERROR':
                        self.ctrl.notify_error(self.group_id, self.key, hint)

            cls._cls = FailoverObserver
        return cls._cls(controller, group_id, key)


##
# @~japanese
# @brief グループごとに RTC を生成・接続し、障害時に代替候補へ切り替える
# @~english
# @brief Creates and connects RTCs for each group and switches to alternatives on failure
# @~
class FailoverController:
    ##
    # @~japanese
    # @brief コンストラクタ
    #
    # @param manager マネージャ
    # @param config 設定
    # @~english
    # @brief Constructor
    #
    # @param manager manager
    # @param config configuration
    # @~
    def __init__(self, manager, config) -> None:
        self.manager = manager
        self.config = config
        self.groups = {g['id']: g for g in config['groups']}
        self.manager_configs = {m['id']: m for m in config['managers']}
        self.current = {}
        self._created = {}
        self._observers = {}          # comp key -> (servant, provider, profile id, comp)
        self._ext_ports = {}          # external endpoint -> PortService (キャッシュ)
        self._queue = queue.Queue()
        self._pending = set()
        self._stop = threading.Event()
        self._threads = []
        obs = config.get('observer', {})
        self.observer_enabled = obs.get('enabled', True)
        self.observer_heartbeat = obs.get('heartbeat', False)
        self.liveness_interval = float(config.get('liveness_interval', 2.0))

    # ------------------------------------------------------------ managers
    ##
    # @~japanese
    # @brief マネージャの参照を返す
    #
    # @param manager_id マネージャの ID (なければ自分)
    # @return マネージャの参照
    # @~english
    # @brief Returns a manager reference
    #
    # @param manager_id manager ID (this manager if omitted)
    # @return manager reference
    # @~
    def _manager(self, manager_id):
        spec = self.manager_configs[manager_id]
        if spec.get('local'):
            return self.manager.getManagerServant().getObjRef()
        # findManager() は自分の manager.name で corbaloc を作るので、
        # マネージャ名がロボットごとに違う構成では使えない。相手の名前で作る。
        url = 'corbaloc:iiop:%s:%s/%s' % (spec['host'], spec.get('port', 2810), spec.get('name', 'manager'))
        import RTM
        obj = self.manager.getORB().string_to_object(url)
        ref = obj._narrow(RTM.Manager) if not _nil(obj) else None
        if _nil(ref):
            raise RuntimeError('manager not found: ' + url)
        return ref

    ##
    # @~japanese
    # @brief マネージャの RTC の一覧を返す
    #
    # @param manager_id マネージャの ID
    # @return RTC のリスト
    # @~english
    # @brief Returns the RTCs of a manager
    #
    # @param manager_id manager ID
    # @return list of RTCs
    # @~
    def _components(self, manager_id):
        return self._manager(manager_id).get_components()

    ##
    # @~japanese
    # @brief RTC が候補の指定に合うか
    #
    # @param comp RTC
    # @param spec 候補の指定
    # @param allow_error ERROR の RTC も許すか
    # @return 合えば True
    # @~english
    # @brief Whether an RTC matches the candidate specification
    #
    # @param comp RTC
    # @param spec candidate specification
    # @param allow_error whether RTCs in ERROR are allowed
    # @return True if it matches
    # @~
    @staticmethod
    def _matches(comp, spec, allow_error: bool = False):
        profile = comp.get_component_profile()
        if profile.type_name != spec['type']:
            return False
        if spec.get('instance') and profile.instance_name != spec['instance']:
            return False
        return allow_error or not _rtm().CORBA_RTCUtil.is_in_error(comp)

    ##
    # @~japanese
    # @brief マネージャから、指定に合う RTC を探す
    #
    # @param manager_id マネージャの ID
    # @param spec 候補の指定
    # @param allow_error ERROR の RTC も許すか
    # @return RTC (なければ None)
    # @~english
    # @brief Finds an RTC matching the specification in a manager
    #
    # @param manager_id manager ID
    # @param spec candidate specification
    # @param allow_error whether RTCs in ERROR are allowed
    # @return RTC (None if not found)
    # @~
    def _find(self, manager_id, spec, allow_error: bool = False):
        for comp in self._components(manager_id):
            try:
                if self._matches(comp, spec, allow_error):
                    return comp
            except Exception:
                LOG.debug('component inspection failed', exc_info=True)
        return None

    ##
    # @~japanese
    # @brief RTC のキー (IOR) を返す
    #
    # @param comp RTC
    # @return IOR
    # @~english
    # @brief Returns the key (IOR) of an RTC
    #
    # @param comp RTC
    # @return IOR
    # @~
    def _key(self, comp):
        return self.manager.getORB().object_to_string(comp)

    # ------------------------------------------------------------ creation
    ##
    # @~japanese
    # @brief 設定の RTC を生成する (create のある候補)
    # @~english
    # @brief Creates the RTCs in the configuration (candidates with create)
    # @~
    def create_initial(self) -> None:
        for group in self.groups.values():
            first = group['alternatives'][0]
            if not first.get('create', False):
                continue
            manager = self._manager(first['manager'])
            for role, spec in first['roles'].items():
                if self._find(first['manager'], spec, allow_error=True) is not None:
                    continue
                creation = spec.get('create_id')
                if not creation:
                    raise ValueError('missing create_id for role ' + role)
                options = dict(spec.get('create_options', {}))
                if spec.get('instance'):
                    options.setdefault('instance_name', spec['instance'])
                suffix = '&'.join('%s=%s' % (k, v) for k, v in options.items())
                request = creation + ('?' + suffix if suffix else '')
                comp = manager.create_component(request)
                if _nil(comp):
                    raise RuntimeError('create_component failed: ' + request)
                LOG.info('created %s on %s', request, first['manager'])
                self._created[(group['id'], role)] = comp

    # ------------------------------------------------------------ ports
    ##
    # @~japanese
    # @brief RTC のポートを名前で返す
    #
    # @param comp RTC
    # @param port_name ポートの名前
    # @return ポートの参照
    # @~english
    # @brief Returns a port of an RTC by name
    #
    # @param comp RTC
    # @param port_name port name
    # @return port reference
    # @~
    def _port(self, comp, port_name):
        profile = comp.get_component_profile()
        full_name = port_name if port_name.startswith(profile.instance_name + '.') \
            else profile.instance_name + '.' + port_name
        port = _rtm().CORBA_RTCUtil.get_port_by_name(comp, full_name)
        if _nil(port):
            raise RuntimeError('port not found: ' + full_name)
        return port

    ##
    # @~japanese
    # @brief 外部ポートの参照を返す (一度取れたらキャッシュして使い回す)
    #
    # 外部 RTC を毎回 get_components() / get_component_profile() で探し直すと、外部 RTC が停止したノードの RTC と接続している間は、OpenRTM のポートが接続先の生存確認 (checkPorts) で応答しなくなることがあるため。
    #
    # @param endpoint 接続の端
    # @return ポートの参照
    # @~english
    # @brief Returns the reference of an external port (cached once obtained)
    #
    # Because searching for the external RTC with get_components() / get_component_profile() each time may stop responding while OpenRTM ports check the liveness of their peers (checkPorts) when connected to RTCs on a stopped node.
    #
    # @param endpoint endpoint
    # @return port reference
    # @~
    def _external_port(self, endpoint):
        key = json.dumps(endpoint, sort_keys=True)
        port = self._ext_ports.get(key)
        if port is not None:
            try:
                if not port._non_existent():
                    return port
            except Exception:
                pass
            self._ext_ports.pop(key, None)
        port = self._resolve_external_port(endpoint)
        self._ext_ports[key] = port
        return port

    ##
    # @~japanese
    # @brief rtcname:// (ネームサービス) か、manager/component/port (マネージャ経由) で外部ポートを得る
    #
    # @param endpoint 接続の端
    # @return ポートの参照
    # @~english
    # @brief Obtains an external port by rtcname:// (name service) or manager/component/port (via a manager)
    #
    # @param endpoint endpoint
    # @return port reference
    # @~
    def _resolve_external_port(self, endpoint):
        if endpoint.get('url'):
            port = _rtm().CORBA_RTCUtil.get_port_by_url(endpoint['url'])
            if _nil(port):
                raise RuntimeError('external port not found: ' + endpoint['url'])
            return port
        comp = None
        for c in self._components(endpoint['manager']):
            try:
                if c.get_component_profile().instance_name == endpoint['component']:
                    comp = c
                    break
            except Exception:
                continue
        if comp is None:
            raise RuntimeError('external component not found: %s on %s' % (endpoint['component'], endpoint['manager']))
        return self._port(comp, endpoint['port'])

    ##
    # @~japanese
    # @brief 接続のプロパティを作る
    #
    # @param conn 接続の設定
    # @return プロパティ
    # @~english
    # @brief Makes the connector properties
    #
    # @param conn connection settings
    # @return properties
    # @~
    @staticmethod
    def _props(conn):
        props = _rtm().Properties()
        for key, value in conn.get('properties', {}).items():
            props.setProperty(str(key), str(value))
        return props

    ##
    # @~japanese
    # @brief グループの RTC と外部ポートを接続する
    #
    # @param conn 接続の設定
    # @param comp RTC
    # @~english
    # @brief Connects an RTC of the group with an external port
    #
    # @param conn connection settings
    # @param comp RTC
    # @~
    def _connect(self, conn, comp) -> None:
        local_port = self._port(comp, conn['port'])
        external = self._external_port(conn['external'])
        left, right = (local_port, external) if conn['direction'] == 'output' else (external, local_port)
        name = conn.get('name', 'failover_' + conn['role'])
        result = _rtm().CORBA_RTCUtil.connect(name, self._props(conn), left, right)
        if not _ok(result):
            raise RuntimeError('connect failed for %s: %r' % (conn['role'], result))

    ##
    # @~japanese
    # @brief グループの中の RTC どうしを接続する
    #
    # @param conn 接続の設定
    # @param components グループの RTC
    # @~english
    # @brief Connects RTCs within a group
    #
    # @param conn connection settings
    # @param components RTCs of the group
    # @~
    def _connect_internal(self, conn, components) -> None:
        src = self._port(components[conn['source']['role']], conn['source']['port'])
        dst = self._port(components[conn['target']['role']], conn['target']['port'])
        name = conn.get('name', 'failover_internal')
        for profile in src.get_connector_profiles():  # 既に同名で接続済みなら何もしない
            if profile.name == name and any(p._is_equivalent(dst) for p in profile.ports):
                return
        result = _rtm().CORBA_RTCUtil.connect(name, self._props(conn), src, dst)
        if not _ok(result):
            raise RuntimeError('internal connect failed: %s (%r)' % (name, result))

    ##
    # @~japanese
    # @brief 切り替え前の RTC の接続を切る
    #
    # @param group グループ
    # @param old_components 切り替え前の RTC
    # @~english
    # @brief Disconnects the RTCs before switching
    #
    # @param group group
    # @param old_components RTCs before switching
    # @~
    def _disconnect(self, group, old_components) -> None:
        # 外部ポート上の、名前が一致するコネクタだけを切断する (他の接続は残す)。
        # 古い RTC のプロセスが落ちていても、外部側から切れば片付く。
        for conn in group.get('connections', []):
            try:
                port = self._external_port(conn['external'])
            except Exception:
                LOG.warning('external port unavailable while disconnecting %s', conn.get('name'), exc_info=True)
                continue
            target = conn.get('name', 'failover_' + conn['role'])
            for profile in list(port.get_connector_profiles()):
                if profile.name == target:
                    result = port.disconnect(profile.connector_id)
                    if not _ok(result):
                        LOG.warning('disconnect %s returned %r', target, result)

    # ------------------------------------------------------------ switching
    ##
    # @~japanese
    # @brief 代替候補の RTC の組を探す (なければ生成する)
    #
    # @param group グループ
    # @param alt 代替候補
    # @return RTC の組 (使えなければ None)
    # @~english
    # @brief Finds the set of RTCs of an alternative (creates them if needed)
    #
    # @param group group
    # @param alt alternative
    # @return set of RTCs (None if unusable)
    # @~
    def _candidate(self, group, alt):
        components = {}
        for role, spec in alt['roles'].items():
            comp = self._find(alt['manager'], spec)
            if comp is None:
                return None
            components[role] = comp
        for conn in group.get('connections', []):
            try:
                self._port(components[conn['role']], conn['port'])
            except Exception:
                return None
        return components

    ##
    # @~japanese
    # @brief グループを次の使える候補に切り替える (接続・アクティブ化)
    #
    # @param group_id グループの ID
    # @param skip_current 現在の候補を飛ばすか
    # @return 切り替えたら True
    # @~english
    # @brief Switches a group to the next usable candidate (connect and activate)
    #
    # @param group_id group ID
    # @param skip_current whether to skip the current candidate
    # @return True if switched
    # @~
    def switch(self, group_id, skip_current: bool = True) -> '_typing.Optional[bool]':
        with _LOCK:
            group = self.groups[group_id]
            alternatives = sorted(enumerate(group['alternatives']),
                                  key=lambda x: (x[1].get('priority', x[0]), x[0]))
            old = self.current.get(group_id)
            for index, alt in alternatives:
                if skip_current and old is not None and index == old['index']:
                    continue
                try:
                    components = self._candidate(group, alt)
                    if components is None:
                        continue
                    if old is not None:
                        self._disconnect(group, old['components'])
                    for conn in group.get('internal_connections', []):
                        self._connect_internal(conn, components)
                    for conn in group.get('connections', []):
                        self._connect(conn, components[conn['role']])
                    if group.get('activate', True):
                        for comp in components.values():
                            if not _rtm().CORBA_RTCUtil.is_in_active(comp):
                                if not _ok(_rtm().CORBA_RTCUtil.activate(comp)):
                                    raise RuntimeError('activate failed')
                    self.current[group_id] = {'index': index, 'components': components,
                                              'keys': {self._key(c) for c in components.values()}}
                    LOG.info('group %s selected alternative %d on %s', group_id, index, alt['manager'])
                    if old is not None:
                        self._handle_old(group, old)
                    self.register_observers(group_id)
                    return True
                except Exception:
                    LOG.exception('alternative %d failed for group %s', index, group_id)
            LOG.error('no usable alternative for group %s', group_id)
            return False

    ##
    # @~japanese
    # @brief 切り替え前の RTC の後始末 (on_failure: keep / reset / exit)
    #
    # @param group グループ
    # @param old 切り替え前の RTC
    # @~english
    # @brief Cleans up the RTCs before switching (on_failure: keep / reset / exit)
    #
    # @param group group
    # @param old RTCs before switching
    # @~
    def _handle_old(self, group, old) -> None:
        action = group.get('on_failure', 'keep')
        if action == 'keep':
            return
        for role, comp in old['components'].items():
            try:
                if action == 'reset':
                    for ec in comp.get_owned_contexts():
                        if ec.get_component_state(comp) == _rtc().ERROR_STATE:
                            LOG.info('reset %s (%s): %r', role, group['id'], ec.reset_component(comp))
                elif action == 'exit':
                    LOG.info('exit %s (%s): %r', role, group['id'], comp.exit())
            except Exception:
                LOG.info('old %s of group %s is unreachable (%s skipped)', role, group['id'], action)

    # ------------------------------------------------------------ observers
    ##
    # @~japanese
    # @brief 現在と待機中のすべての候補 RTC に ComponentObserver を登録する (登録済みは飛ばす)
    #
    # @param group_id グループの ID (省略時は全部)
    # @~english
    # @brief Registers ComponentObserver to all current and standby candidate RTCs (registered ones are skipped)
    #
    # @param group_id group ID (all if omitted)
    # @~
    def register_observers(self, group_id=None) -> None:
        if not self.observer_enabled:
            return
        groups = [group_id] if group_id else list(self.groups)
        for gid in groups:
            for alt in self.groups[gid]['alternatives']:
                for role, spec in alt['roles'].items():
                    try:
                        comp = self._find(alt['manager'], spec, allow_error=True)
                    except Exception:
                        continue
                    if comp is not None:
                        self._add_observer(gid, comp)

    ##
    # @~japanese
    # @brief RTC に ComponentObserver を登録する
    #
    # @param group_id グループの ID
    # @param comp RTC
    # @~english
    # @brief Registers ComponentObserver to an RTC
    #
    # @param group_id group ID
    # @param comp RTC
    # @~
    def _add_observer(self, group_id, comp) -> None:
        import SDOPackage
        try:
            key = self._key(comp)
            if key in self._observers:
                return
            servant = _ObserverFactory.make(self, group_id, key)
            poa = self.manager.getPOA()
            provider = poa.id_to_reference(poa.activate_object(servant))
            name = comp.get_component_profile().instance_name
            props = [_rtm().NVUtil.newNV('heartbeat.enable', 'YES' if self.observer_heartbeat else 'NO'),
                     _rtm().NVUtil.newNV('observed_status', 'RTC_STATUS')]
            profile_id = 'failover_%s_%s_%d' % (group_id, name, len(self._observers))
            profile = SDOPackage.ServiceProfile(profile_id, _rtm().toTypename(servant), props, provider)
            if not comp.get_configuration().add_service_profile(profile):
                LOG.warning('observer registration for %s returned false '
                            '(ComponentObserverConsumer が RTC 側で読み込まれていない可能性)', name)
                return
            self._observers[key] = (servant, provider, profile_id, comp)
            LOG.info('observer registered on %s (group %s)', name, group_id)
        except Exception:
            LOG.warning('observer registration failed', exc_info=True)

    ##
    # @~japanese
    # @brief ComponentObserver から (CORBA のスレッドで) 呼ばれる。処理はワーカースレッドへ回す
    #
    # @param group_id グループの ID
    # @param key RTC のキー
    # @param hint 詳細
    # @~english
    # @brief Called by ComponentObserver (on a CORBA thread). The handling is passed to the worker thread
    #
    # @param group_id group ID
    # @param key key of the RTC
    # @param hint hint
    # @~
    def notify_error(self, group_id, key, hint) -> None:
        state = self.current.get(group_id)
        if state is None or key not in state['keys']:
            LOG.info('ERROR on a standby RTC of group %s ignored (%s)', group_id, hint)
            return
        LOG.warning('RTC ERROR in group %s: %s', group_id, hint)
        self._enqueue(group_id, 'observer: ' + hint)

    ##
    # @~japanese
    # @brief 切り替えの要求をワーカースレッドに渡す
    #
    # @param group_id グループの ID
    # @param reason 理由
    # @~english
    # @brief Passes a switching request to the worker thread
    #
    # @param group_id group ID
    # @param reason reason
    # @~
    def _enqueue(self, group_id, reason) -> None:
        with _LOCK:
            if group_id in self._pending:
                return  # 同じ障害の通知が続けて届いた場合は 1 回にまとめる
            self._pending.add(group_id)
        self._queue.put((group_id, reason))

    ##
    # @~japanese
    # @brief 切り替えの要求を処理するスレッドの本体
    # @~english
    # @brief Body of the thread that handles switching requests
    # @~
    def _worker(self) -> None:
        while not self._stop.is_set():
            try:
                group_id, reason = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                LOG.warning('failover of group %s (%s)', group_id, reason)
                self.handle_failure(group_id)
            except Exception:
                LOG.exception('failover of group %s failed', group_id)
            finally:
                with _LOCK:
                    self._pending.discard(group_id)

    # ------------------------------------------------------------ liveness
    ##
    # @~japanese
    # @brief 生存確認のスレッドの本体。現在の RTC に到達できない (プロセス終了) / ERROR を見逃した場合にも切り替える
    # @~english
    # @brief Body of the liveness thread. Also switches when the current RTC is unreachable (process exit) or an ERROR was missed
    # @~
    def _liveness(self) -> None:
        while not self._stop.wait(self.liveness_interval):
            for group_id, state in list(self.current.items()):
                for role, comp in state['components'].items():
                    try:
                        if comp._non_existent():
                            raise RuntimeError('non existent')
                        if _rtm().CORBA_RTCUtil.is_in_error(comp):
                            self._enqueue(group_id, 'liveness: %s in ERROR' % role)
                            break
                    except Exception:
                        self._enqueue(group_id, 'liveness: %s unreachable' % role)
                        break
            # 新しく現れた待機 RTC にもオブザーバを付ける
            try:
                self.register_observers()
            except Exception:
                LOG.debug('observer refresh failed', exc_info=True)

    # ------------------------------------------------------------ lifecycle
    ##
    # @~japanese
    # @brief すべてのグループを始める (切り替え、オブザーバーの登録、スレッドの起動)
    #
    # @return {グループの ID: 結果}
    # @~english
    # @brief Starts all groups (switching, observer registration and threads)
    #
    # @return {group ID: result}
    # @~
    def start(self):
        self.create_initial()
        results = {group_id: self.switch(group_id, skip_current=False) for group_id in self.groups}
        # 外部ポートは起動時 (全ノードが生きている間) に解決してキャッシュしておく
        for group in self.groups.values():
            for conn in group.get('connections', []):
                try:
                    self._external_port(conn['external'])
                except Exception:
                    LOG.warning('external port %s not resolved yet', conn.get('name'))
        self.register_observers()
        for target in (self._worker, self._liveness) if self.liveness_interval > 0 else (self._worker,):
            t = threading.Thread(target=target, daemon=True)
            t.start()
            self._threads.append(t)
        return results

    ##
    # @~japanese
    # @brief スレッドを止める
    # @~english
    # @brief Stops the threads
    # @~
    def stop(self) -> None:
        self._stop.set()

    ##
    # @~japanese
    # @brief グループの障害を処理する (次の候補に切り替える)
    #
    # @param group_id グループの ID
    # @return 切り替えたら True
    # @~english
    # @brief Handles a failure of a group (switches to the next candidate)
    #
    # @param group_id group ID
    # @return True if switched
    # @~
    def handle_failure(self, group_id):
        return self.switch(group_id, skip_current=True)

    ##
    # @~japanese
    # @brief オブザーバーを登録した RTC の一覧を返す
    #
    # @return RTC の一覧
    # @~english
    # @brief Returns the RTCs with registered observers
    #
    # @return list of RTCs
    # @~
    def observed_components(self):
        result = []
        for group_id, state in self.current.items():
            for role, comp in state['components'].items():
                result.append((group_id, role, comp))
        return result


##
# @~japanese
# @brief 設定ファイルを読み、FailoverController を作って始める
#
# @param manager マネージャ
# @param path 設定ファイルのパス
# @return FailoverController
# @~english
# @brief Reads the configuration file, creates FailoverController and starts it
#
# @param manager manager
# @param path path of the configuration file
# @return FailoverController
# @~
def initialize(manager, path=None):
    global _CONTROLLER
    _CONTROLLER = FailoverController(manager, load_config(path))
    return _CONTROLLER


##
# @~japanese
# @brief 作った FailoverController を返す
#
# @return FailoverController (なければ None)
# @~english
# @brief Returns the created FailoverController
#
# @return FailoverController (None if not created)
# @~
def controller():
    if _CONTROLLER is None:
        raise RuntimeError('RTCFailover.initialize() has not been called')
    return _CONTROLLER


##
# @~japanese
# @brief グループ (省略時は全部) の障害を処理する
#
# @param group_id グループの ID
# @return 結果
# @~english
# @brief Handles failures of a group (all groups if omitted)
#
# @param group_id group ID
# @return result
# @~
def reconnect(group_id=None):
    instance = controller()
    if group_id is not None:
        return instance.handle_failure(group_id)
    return {name: instance.handle_failure(name) for name in instance.groups}
