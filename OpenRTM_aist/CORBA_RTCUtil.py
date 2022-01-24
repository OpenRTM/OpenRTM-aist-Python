#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
#  @file CORBA_RTCUtil.py
#  @brief CORBA RTC utility
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
#

import OpenRTM_aist
import OpenRTM_aist.RTObject
from omniORB import CORBA
import RTC


##
# @if jp
#
# @brief コンポーネントのプロパティ取得
#
#
# @param rtc RTコンポーネント
# @return コンポーネントのプロパティ
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
# coil::Properties get_component_profile(const RTC::RTObject_ptr rtc)
def get_component_profile(rtc):
    prop = OpenRTM_aist.Properties()
    if CORBA.is_nil(rtc):
        return prop
    prof = rtc.get_component_profile()
    OpenRTM_aist.NVUtil.copyToProperties(prop, prof.properties)
    return prop


##
# @if jp
#
# @brief コンポーネントのオブジェクトリファレンスが存在しているかを判定
#
#
# @param rtc RTコンポーネント
# @return True:生存、False:終了済み
#
# @else
#
# @brief
# @param rtc RTコンポーネント
# @return
#
# @endif
def is_existing(rtc):
    try:
        if rtc._non_existent():
            return False
        return True
    except CORBA.SystemException:
        return False


##
# @if jp
#
# @brief RTCがデフォルトの実行コンテキストでalive状態かを判定する
#
# @param rtc RTコンポーネント
# @return True:alive状態
#
# @param
#
# @else
#
# @brief
# @param
#
# @endif
def is_alive_in_default_ec(rtc):
    ec = get_actual_ec(rtc)
    if CORBA.is_nil(ec):
        return False
    return rtc.is_alive(ec)


##
# @if jp
#
# @brief RTコンポーネントに関連付けした実行コンテキストから指定したIDの実行コンテキストを取得
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return 実行コンテキストのオブジェクトリファレンス
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif
# RTC::ExecutionContext_var get_actual_ec(const RTC::RTObject_ptr
# rtc,RTC::UniqueId ec_id = 0)
def get_actual_ec(rtc, ec_id=0):
    if ec_id < 0:
        return RTC.ExecutionContext._nil
    if CORBA.is_nil(rtc):
        return RTC.ExecutionContext._nil
    if ec_id < OpenRTM_aist.RTObject.ECOTHER_OFFSET:
        eclist = rtc.get_owned_contexts()
        if ec_id >= len(eclist):
            return RTC.ExecutionContext._nil

        if CORBA.is_nil(eclist[ec_id]):
            return RTC.ExecutionContext._nil
        return eclist[ec_id]
    elif ec_id >= OpenRTM_aist.RTObject.ECOTHER_OFFSET:
        pec_id = ec_id - OpenRTM_aist.RTObject.ECOTHER_OFFSET
        eclist = rtc.get_participating_contexts()
        if pec_id >= len(eclist):
            return RTC.ExecutionContext._nil
        if CORBA.is_nil(eclist[pec_id]):
            return RTC.ExecutionContext._nil
        return eclist[pec_id]


##
# @if jp
#
# @brief 対象のRTコンポーネントから指定した実行コンテキストのIDを取得する
#
#
# @param rtc 対象のRTコンポーネント
# @param ec 実行コンテキスト
# @return 実行コンテキストのID
# 指定した実行コンテキストがRTコンポーネントに関連付けられていなかった場合は-1を返す
#
# @else
#
# @brief
# @param
#
# @endif
def get_ec_id(rtc, ec):
    if CORBA.is_nil(rtc):
        return -1
    if CORBA.is_nil(ec):
        return -1

    eclist_own = rtc.get_owned_contexts()

    count = 0
    for e in eclist_own:
        if not CORBA.is_nil(e):
            if e._is_equivalent(ec):
                return count
        count += 1
    eclist_pec = rtc.get_participating_contexts()
    count = 0
    for e in eclist_pec:
        if not CORBA.is_nil(e):
            if e._is_equivalent(ec):
                return count + OpenRTM_aist.RTObject.ECOTHER_OFFSET
        count += 1
    return -1


##
# @if jp
#
# @brief RTCを指定した実行コンテキストでアクティベーションする
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return RTC、ECのオブジェクトリファレンスがnilの場合はBAD_PARAMETERを返す
# nilではない場合はactivate_component関数の戻り値を返す。RTC_OKの場合はアクティベーションが成功
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif
# RTC::ReturnCode_t activate(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)
def activate(rtc, ec_id=0):
    if CORBA.is_nil(rtc):
        return RTC.BAD_PARAMETER
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.activate_component(rtc)


##
# @if jp
#
# @brief RTCを指定した実行コンテキストで非アクティベーションする
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return RTC、ECのオブジェクトリファレンスがnilの場合はBAD_PARAMETERを返す
# nilではない場合はdeactivate_component関数の戻り値を返す。RTC_OKの場合は非アクティベーションが成功
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif
# RTC::ReturnCode_t deactivate(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)
def deactivate(rtc, ec_id=0):
    if CORBA.is_nil(rtc):
        return RTC.BAD_PARAMETER
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.deactivate_component(rtc)

##
# @if jp
#
# @brief RTCを指定した実行コンテキストでリセットする
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return RTC、ECのオブジェクトリファレンスがnilの場合はBAD_PARAMETERを返す
# nilではない場合はreset_component関数の戻り値を返す。RTC_OKの場合はリセットが成功
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif
# RTC::ReturnCode_t reset(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)


def reset(rtc, ec_id=0):
    if CORBA.is_nil(rtc):
        return RTC.BAD_PARAMETER
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.reset_component(rtc)

##
# @if jp
#
# @brief 対象のRTコンポーネントの指定した実行コンテキストでの状態を取得
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return 1番目の戻り値としてrtc、ecがnilの場合はFalseを返し、それ以外の場合はTrueを返す。
# 2番目の戻り値として状態を返す。
#
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif


def get_state(rtc, ec_id=0):
    if CORBA.is_nil(rtc):
        return False, RTC.CREATED_STATE
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return False, RTC.CREATED_STATE
    state = ec.get_component_state(rtc)
    return True, state

##
# @if jp
#
# @brief 対象のRTコンポーネントの指定した実行コンテキストでINACTIVE状態かどうか判定
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return INACTIVE状態の時はTrue、それ以外はFalse
# rtc、ecがnilの場合もFalseを返す
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif


def is_in_inactive(rtc, ec_id=0):
    ret, state = get_state(rtc, ec_id)
    if ret:
        if state == RTC.INACTIVE_STATE:
            return True
    return False

##
# @if jp
#
# @brief 対象のRTコンポーネントの指定した実行コンテキストでACTIVE状態かどうか判定
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return ACTIVE状態の時はTrue、それ以外はFalse
# rtc、ecがnilの場合もFalseを返す
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif


def is_in_active(rtc, ec_id=0):
    ret, state = get_state(rtc, ec_id)
    if ret:
        if state == RTC.ACTIVE_STATE:
            return True
    return False

##
# @if jp
#
# @brief 対象のRTコンポーネントの指定した実行コンテキストでERROR状態かどうか判定
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 実行コンテキストのID
# @return ERROR状態の時はTrue、それ以外はFalse
# rtc、ecがnilの場合もFalseを返す
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return
#
# @endif


def is_in_error(rtc, ec_id=0):
    ret, state = get_state(rtc, ec_id)
    if ret:
        if state == RTC.ERROR_STATE:
            return True
    return False


##
# @if jp
#
# @brief RTCのデフォルトの実行コンテキストの実行周期を取得する
#
#
# @param rtc RTコンポーネント
# @return 実行周期
#
# @else
#
# @brief
# @param ec
# @return
#
# @endif
def get_default_rate(rtc):
    ec = get_actual_ec(rtc)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.get_rate()


##
# @if jp
#
# @brief RTCのデフォルトの実行コンテキストの実行周期を設定する
#
#
# @param rtc RTコンポーネント
# @param rate 実行周期
# @return set_rate関数の戻り値を返す。
# RTC_OKで設定が成功
#
# @else
#
# @brief
# @param ec
#
# @endif
def set_default_rate(rtc, rate):
    ec = get_actual_ec(rtc)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.set_rate(rate)


##
# @if jp
#
# @brief RTCの指定IDの実行コンテキストの周期を取得
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 指定の実行コンテキストのID
# @return 実行周期
#
# @else
#
# @brief
# @param ec
# @return
#
# @endif
def get_current_rate(rtc, ec_id):
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.get_rate()


##
# @if jp
#
# @brief RTCの指定IDの実行コンテキストの周期を設定
#
#
# @param rtc 対象のRTコンポーネント
# @param ec_id 指定の実行コンテキストのID
# @param rate 実行周期
# @return set_rate関数の戻り値を返す。
# RTC_OKで設定が成功
#
# @else
#
# @brief
# @param
#
# @endif
def set_current_rate(rtc, ec_id, rate):
    ec = get_actual_ec(rtc, ec_id)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.set_rate(rate)


##
# @if jp
#
# @brief 対象のRTCのデフォルトの実行コンテキストに指定のRTCを関連付ける
#
#
# @param localcomp 対象のRTコンポーネント
# @param othercomp 実行コンテキストに関連付けるRTコンポーネント
# @return ecの取得に失敗した場合はBAD_PARAMETERを返す
# そうでない場合はaddComponent関数の戻り値を返す。RTC_OKで接続成功。
#
# @else
#
# @brief
# @param
#
# @endif
def add_rtc_to_default_ec(localcomp, othercomp):
    if CORBA.is_nil(othercomp):
        return RTC.BAD_PARAMETER
    ec = get_actual_ec(localcomp)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.add_component(othercomp)


##
# @if jp
#
# @brief 対象のRTCのデフォルトの実行コンテキストの指定のRTCへの関連付けを解除する
#
#
# @param localcomp 対象のRTコンポーネント
# @param othercomp 実行コンテキストとの関連付けを解除するRTコンポーネント
# @return ecの取得に失敗した場合はBAD_PARAMETERを返す
# そうでない場合はremoveComponent関数の戻り値を返す。RTC_OKで解除成功。
#
# @else
#
# @brief
# @param
#
# @endif
def remove_rtc_to_default_ec(localcomp, othercomp):
    if CORBA.is_nil(othercomp):
        return RTC.BAD_PARAMETER
    ec = get_actual_ec(localcomp)
    if CORBA.is_nil(ec):
        return RTC.BAD_PARAMETER
    return ec.remove_component(othercomp)


##
# @if jp
#
# @brief RTCのデフォルトの実行コンテキストに参加しているRTCのリストを取得する
# 実行コンテキストがnilの場合は空のリストを返す
#
#
# @param rtc RTコンポーネント
# @return RTCのリスト
#
# @else
#
# @brief
# @param ec
# @return
#
# @endif
def get_participants_rtc(rtc):
    ec = get_actual_ec(rtc)
    if CORBA.is_nil(ec):
        return []
    profile = ec.get_profile()
    return profile.participants


##
# @if jp
#
# @brief 指定したRTCの保持するポートの名前を取得
#
#
# @param rtc 対象のRTコンポーネント
# @return ポート名のリスト
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
def get_port_names(rtc):
    names = []
    if CORBA.is_nil(rtc):
        return names
    ports = rtc.get_ports()
    for p in ports:
        pp = p.get_port_profile()
        s = pp.name
        names.append(s)
    return names


##
# @if jp
#
# @brief 指定したRTCの保持するインポートの名前を取得
#
#
# @param rtc 対象のRTコンポーネント
# @return ポート名のリスト
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
def get_inport_names(rtc):
    names = []
    if CORBA.is_nil(rtc):
        return names

    ports = rtc.get_ports()
    for p in ports:
        pp = p.get_port_profile()
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
        if prop.getProperty("port.port_type") == "DataInPort":
            s = pp.name
            names.append(s)
    return names


##
# @if jp
#
# @brief 指定したRTCの保持するアウトポートの名前を取得
#
#
# @param rtc 対象のRTコンポーネント
# @return ポート名のリスト
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
def get_outport_names(rtc):
    names = []
    if CORBA.is_nil(rtc):
        return names

    ports = rtc.get_ports()
    for p in ports:
        pp = p.get_port_profile()
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
        if prop.getProperty("port.port_type") == "DataOutPort":
            s = pp.name
            names.append(s)
    return names


##
# @if jp
#
# @brief 指定したRTCの保持するサービスポートの名前を取得
#
#
# @param rtc 対象のRTコンポーネント
# @return ポート名のリスト
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
def get_svcport_names(rtc):
    names = []
    if CORBA.is_nil(rtc):
        return names

    ports = rtc.get_ports()
    for p in ports:
        pp = p.get_port_profile()
        prop = OpenRTM_aist.Properties()
        OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
        if prop.getProperty("port.port_type") == "CorbaPort":
            s = pp.name
            names.append(s)
    return names


##
# @if jp
#
# @brief 対象のRTCから指定した名前のポートを取得
#
#
# @param rtc RTコンポーネント
# @param port_name ポート名
# @return ポート
#
# @else
#
# @brief
# @param rtc
# @param port_name
# @return
#
# @endif
#
# RTC::PortService_var get_port_by_name(const RTC::RTObject_ptr rtc,
# std::string port_name)
def get_port_by_name(rtc, port_name):
    if CORBA.is_nil(rtc):
        return RTC.PortService._nil
    ports = rtc.get_ports()
    for p in ports:
        pp = p.get_port_profile()
        s = pp.name

        if port_name == s:
            return p

    return RTC.PortService._nil


##
# @if jp
#
# @brief 指定したポートの保持しているコネクタの名前のリストを取得
#
#
# @param port 対象のポート
# @return コネクタ名のリスト
#
# @else
#
# @brief
# @param port
# @return
#
# @endif
def get_connector_names_by_portref(port):
    names = []
    if CORBA.is_nil(port):
        return names
    conprof = port.get_connector_profiles()
    for c in conprof:
        names.append(c.name)
    return names

##
# @if jp
#
# @brief 対象のRTCの指定したポートのコネクタの名前のリストを取得
#
# @param rtc RTコンポーネント
# @param port_name ポート名
# @return コネクタ名のリスト
#
# @else
#
# @brief
# @param rtc
# @param port_name
# @return
#
# @endif


def get_connector_names(rtc, port_name):
    names = []
    port = get_port_by_name(rtc, port_name)
    if CORBA.is_nil(port):
        return names
    conprof = port.get_connector_profiles()
    for c in conprof:
        names.append(c.name)
    return names


##
# @if jp
#
# @brief 指定したポートの保持しているコネクタのIDのリストを取得
#
#
# @param port 対象のポート
# @return コネクタのIDのリスト
#
# @else
#
# @brief
# @param port
# @return
#
# @endif
def get_connector_ids_by_portref(port):
    ids = []
    if CORBA.is_nil(port):
        return ids
    conprof = port.get_connector_profiles()
    for c in conprof:
        ids.append(c.connector_id)
    return ids


##
# @if jp
#
# @brief 対象のRTCの指定したポートのコネクタのIDのリストを取得
#
#
# @param rtc RTコンポーネント
# @param port_name ポート名
# @return コネクタのIDのリスト
#
# @else
#
# @brief
# @param rtc
# @param port_name
# @return
#
# @endif
def get_connector_ids(rtc, port_name):
    ids = []
    port = get_port_by_name(rtc, port_name)
    if CORBA.is_nil(port):
        return ids
    conprof = port.get_connector_profiles()
    for c in conprof:
        ids.append(c.connector_id)
    return ids

##
# @if jp
#
# @brief 指定したポートを接続するためのコネクタプロファイルを取得
#
#
# @param name コネクタ名
# @param prop_arg 設定
# @param port0 対象のポート1
# @param port1 対象のポート2
# @return コネクタプロファイル
#
# @else
#
# @brief
# @param name
# @param prop_arg
# @param port0
# @param port1
# @return
#
# @endif
# RTC::ConnectorProfile_var create_connector(const std::string name,const
# coil::Properties prop_arg,const RTC::PortService_ptr port0,const
# RTC::PortService_ptr port1)


def create_connector(name, prop_arg, port0, port1):
    prop = prop_arg
    if CORBA.is_nil(port1):
        conn_prof = RTC.ConnectorProfile(name, "", [port0], [])
    else:
        conn_prof = RTC.ConnectorProfile(name, "", [port0, port1], [])

    if not str(prop.getProperty("dataport.dataflow_type")):
        prop.setProperty("dataport.dataflow_type", "push")

    if not str(prop.getProperty("dataport.interface_type")):
        prop.setProperty("dataport.interface_type", "corba_cdr")

    conn_prof.properties = []
    OpenRTM_aist.NVUtil.copyFromProperties(conn_prof.properties, prop)

    return conn_prof


##
# @if jp
#
# @brief 指定したポート同士が接続されているかを判定
#
#
# @param localport 対象のポート1
# @param otherport 対象のポート2
# @return True: 接続済み、False: 未接続
#
# @else
#
# @brief
# @param name
# @param prop_arg
# @param port0
# @param port1
# @return
#
# @endif

def already_connected(localport, otherport):
    if localport._is_equivalent(otherport):
        return False
    conprof = localport.get_connector_profiles()
    for c in conprof:
        for p in c.ports:
            if p._is_equivalent(otherport):
                return True

    return False


##
# @if jp
#
# @brief 指定したポートを接続する
#
#
# @param name コネクタ名
# @param prop 設定
# @param port0 対象のポート1
# @param port1 対象のポート2
# @return ポートのオブジェクトリファレンスがnilの場合はBAD_PARAMETERを返す
# nilではない場合はport0.connect関数の戻り値を返す。RTC_OKの場合は接続が成功
#
# @else
#
# @brief
# @param name
# @param prop
# @param port0
# @param port1
# @return
#
# @endif
# RTC::ReturnCode_t connect(const std::string name,const coil::Properties
# prop,const RTC::PortService_ptr port0,const RTC::PortService_ptr port1)
def connect(name, prop, port0, port1):
    if CORBA.is_nil(port0):
        return RTC.BAD_PARAMETER
    # if CORBA.is_nil(port1):
    #  return RTC.BAD_PARAMETER
    if not CORBA.is_nil(port1):
        if port0._is_equivalent(port1):
            return RTC.BAD_PARAMETER
    cprof = create_connector(name, prop, port0, port1)
    return port0.connect(cprof)[0]


##
# @if jp
#
# @brief 指定したポートと指定したリスト内のポート全てと接続する
#
#
# @param name コネクタ名
# @param prop 設定
# @param port 対象のポート
# @param target_ports 対象のポートのリスト
# @return 全ての接続が成功した場合はRTC_OKを返す。
# connect関数がRTC_OK以外を返した場合はBAD_PARAMETERを返す。
#
#
# @else
#
# @brief
# @param name
# @param prop
# @param port0
# @param port1
# @return
#
# @endif
# RTC::ReturnCode_t connect_multi(const std::string name,const
# coil::Properties prop,const RTC::PortService_ptr
# port,RTC::PortServiceList_var& target_ports)
def connect_multi(name, prop, port, target_ports):
    ret = RTC.RTC_OK
    if CORBA.is_nil(port):
        return RTC.BAD_PARAMETER
    for p in target_ports:
        if CORBA.is_nil(p):
            ret = RTC.BAD_PARAMETER
            continue
        if p._is_equivalent(port):
            ret = RTC.BAD_PARAMETER
            continue
        if already_connected(port, p):
            ret = RTC.BAD_PARAMETER
            continue
        if RTC.RTC_OK != connect(name, prop, port, p):
            ret = RTC.BAD_PARAMETER

    return ret


##
# @if jp
# @class find_port
# @brief ポートを名前から検索
#
# @else
# @class find_port
# @brief
#
# @endif
#
class find_port:
    ##
    # @if jp
    #
    # @brief コンストラクタ
    # 検索するポート名を指定する
    #
    #
    # @param self
    # @param name ポート名
    #
    # @else
    #
    # @brief
    # @param self
    # @param name
    #
    # @endif
    # find_port(const std::string name)
    def __init__(self, name):
        self._name = name
    ##
    # @if jp
    #
    # @brief 対象のポートの名前と指定したポート名が一致するか判定
    #
    #
    # @param self
    # @param p 対象のポート
    # @return True: 名前が一致、False:　名前が不一致
    #
    # @else
    #
    # @brief
    # @param self
    # @param p
    # @return
    #
    # @endif
    # bool operator()(RTC::PortService_var p)

    def __call__(self, p):
        prof = p.get_port_profile()
        c = prof.name

        return (self._name == c)

##
# @if jp
#
# @brief 対象のRTCの指定した名前のポートを接続する
#
#
# @param name コネクタ名
# @param prop 設定
# @param rtc0 対象のRTCコンポーネント1
# @param portName0 対象のポート名1
# @param rtc1 対象のRTCコンポーネント2
# @param portName1 対象のRTCコンポーネント2
# @return RTC、ポートがnilの場合はBAD_PARAMETERを返す。
# nilではない場合はport0.connect関数の戻り値を返す。RTC_OKの場合は接続が成功
#
# @else
#
# @brief
# @param name
# @param prop_arg
# @param port0
# @param port1
#
# @endif
#
# RTC::ReturnCode_t connect_by_name(std::string name, coil::Properties
# prop,RTC::RTObject_ptr rtc0,const std::string
# port_name0,RTC::RTObject_ptr rtc1,const std::string port_name1)


def connect_by_name(name, prop, rtc0, port_name0, rtc1, port_name1):
    if CORBA.is_nil(rtc0):
        return RTC.BAD_PARAMETER
    if CORBA.is_nil(rtc1):
        return RTC.BAD_PARAMETER

    port0 = get_port_by_name(rtc0, port_name0)
    if CORBA.is_nil(port0):
        return RTC.BAD_PARAMETER

    port1 = get_port_by_name(rtc1, port_name1)
    if CORBA.is_nil(port1):
        return RTC.BAD_PARAMETER

    return connect(name, prop, port0, port1)


##
# @if jp
#
# @brief 指定のコネクタを切断する
#
#
# @param connector_prof コネクタプロファイル
# @return コネクタプロファイルで保持しているポートのオブジェクトリファレンスがnilの場合はBAD_PARAMETERを返す
# nilではない場合はports[0].disconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param connector_prof
# @return
#
# @endif
def disconnect(connector_prof):
    ports = connector_prof.ports
    return disconnect_by_portref_connector_id(
        ports[0], connector_prof.connector_id)


##
# @if jp
#
# @brief 対象のポートで指定した名前のコネクタを切断
#
#
# @param port_ref 対象のポート
# @param conn_name コネクタ名
# @return portがnilの場合はBAD_PARAMETERを返す
# nilではない場合はdisconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param port_ref
# @param conn_name
# @return
#
# @endif
def disconnect_by_portref_connector_name(port_ref, conn_name):
    if CORBA.is_nil(port_ref):
        return RTC.BAD_PARAMETER
    conprof = port_ref.get_connector_profiles()
    for c in conprof:
        if c.name == conn_name:
            return disconnect(c)
    return RTC.BAD_PARAMETER


##
# @if jp
#
# @brief 対象の名前のポートで指定した名前のコネクタを切断
#
#
# @param port_name 対象のポート名
# @param conn_name コネクタ名
# @return portが存在しない場合はBAD_PARAMETERを返す
# nilではない場合はdisconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param
#
# @endif
def disconnect_by_portname_connector_name(port_name, conn_name):
    port_ref = get_port_by_url(port_name)
    if CORBA.is_nil(port_ref):
        return RTC.BAD_PARAMETER

    conprof = port_ref.get_connector_profiles()
    for c in conprof:
        if c.name == conn_name:
            return disconnect(c)

    return RTC.BAD_PARAMETER


##
# @if jp
#
# @brief 対象のポートで指定したIDのコネクタを切断
#
#
# @param port 対象のポート
# @param name コネクタID
# @return portがnilの場合はBAD_PARAMETERを返す
# nilではない場合はdisconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param
#
# @endif
def disconnect_by_portref_connector_id(port_ref, conn_id):
    if CORBA.is_nil(port_ref):
        return RTC.BAD_PARAMETER
    return port_ref.disconnect(conn_id)


##
# @if jp
#
# @brief 対象の名前のポートで指定したIDのコネクタを切断
#
#
# @param port_name 対象のポート名
# @param name コネクタID
# @return portが存在しない場合はBAD_PARAMETERを返す
# nilではない場合はdisconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param port_name
# @param name
# @return
#
# @endif
def disconnect_by_portname_connector_id(port_name, conn_id):
    port_ref = get_port_by_url(port_name)
    if port_ref == RTC.PortService._nil:
        return RTC.BAD_PARAMETER

    return port_ref.disconnect(conn_id)


##
# @if jp
#
# @brief 対象のポートのコネクタを全て切断
#
#
# @param port_ref ポートのオブジェクトリファレンス
# @return portがnilの場合はBAD_PARAMETERを返す
# 切断できた場合はRTC_OKを返す
#
# @else
#
# @brief
# @param port
# @return
#
# @endif
def disconnect_all_by_ref(port_ref):
    if CORBA.is_nil(port_ref):
        return RTC.BAD_PARAMETER
    return port_ref.disconnect_all()


##
# @if jp
#
# @brief 指定ポート名のポートのコネクタを全て切断
#
#
# @param port_name ポート名
# @return portが存在しない場合はBAD_PARAMETERを返す
# 切断できた場合はRTC_OKを返す
#
# @else
#
# @brief
# @param port
# @return
#
# @endif
def disconnect_all_by_name(port_name):
    port_ref = get_port_by_url(port_name)
    if port_ref == RTC.PortService._nil:
        return RTC.BAD_PARAMETER
    return port_ref.disconnect_all()


##
# @if jp
#
# @brief 指定した名前のポートを取得
#
#
# @param port_name ポート名
# @return ポートのオブジェクトリファレンス
# portが存在しない場合はnilを返す
#
# @else
#
# @brief
# @param port_name
# @return
#
# @endif
def get_port_by_url(port_name):
    mgr = OpenRTM_aist.Manager.instance()
    nm = mgr.getNaming()
    p = port_name.split(".")
    if len(p) < 2:
        return RTC.PortService._nil

    rtcs = nm.string_to_component(port_name.rstrip("." + p[-1]))

    if not rtcs:
        return RTC.PortService._nil
    pn = port_name.split("/")

    return get_port_by_name(rtcs[0], pn[-1])

##
# @if jp
#
# @brief 対象ポートと接続しているポートで指定したポート名と一致した場合に切断
#
#
# @param localport 対象のポート
# @param othername 接続しているポート名
# @return ポートがnilの場合、localportの名前とothernameが一致する場合、接続しているポートの名前でothernameと一致するものがない場合にBAD_PARAMETERを返す
# 上記の条件に当てはまらない場合はdisconnect関数の戻り値を返す。RTC_OKの場合は切断が成功
#
# @else
#
# @brief
# @param
#
# @endif


def disconnect_by_port_name(localport, othername):
    if CORBA.is_nil(localport):
        return RTC.BAD_PARAMETER
    prof = localport.get_port_profile()
    if prof.name == othername:
        return RTC.BAD_PARAMETER

    conprof = localport.get_connector_profiles()
    for c in conprof:
        for p in c.ports:
            if not CORBA.is_nil(p):
                pp = p.get_port_profile()
                if pp.name == othername:
                    return disconnect(c)
    return RTC.BAD_PARAMETER


##
# @if jp
#
# @brief 対象のRTコンポーネントの指定した名前のコンフィギュレーションセットをkey-valueで取得
#
#
# @param rtc 対象のRTコンポーネント
# @param conf_name コンフィギュレーションセット名
# @return コンフィギュレーションセット
#
# @else
#
# @brief
# @param rtc
# @param conf_name
# @return
#
# @endif
def get_configuration(rtc, conf_name):
    conf = rtc.get_configuration()

    confset = conf.get_configuration_set(conf_name)
    confData = confset.configuration_data
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
    return prop


##
# @if jp
#
# @brief 指定したコンフィギュレーションセット名、パラメータ名のコンフィギュレーションパラメータを取得
#
#
# @param rtc RTコンポーネント
# @param confset_name コンフィギュレーションセット名
# @param value_name パラメータ名
# @return パラメータ
#
# @else
#
# @brief
# @param rtc
# @param confset_name
# @param value_name
# @param ret
# @return
#
# @endif
def get_parameter_by_key(rtc, confset_name, value_name):
    conf = rtc.get_configuration()

    confset = conf.get_configuration_set(confset_name)
    confData = confset.configuration_data
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
    return prop.getProperty(value_name)


##
# @if jp
#
# @brief 対象のRTCのアクティブなコンフィギュレーションセット名を取得する
#
# @param rtc RTコンポーネント
# @return コンフィギュレーションセット名
# コンフィギュレーションの取得に失敗した場合は空の文字列を返す
#
# @param
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
def get_active_configuration_name(rtc):
    conf = rtc.get_configuration()
    confset = conf.get_active_configuration_set()
    return confset.id

##
# @if jp
#
# @brief アクティブなコンフィギュレーションセットをkey-valueで取得する
#
#
# @param rtc 対象のRTコンポーネント
# @return アクティブなコンフィギュレーションセット
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif


def get_active_configuration(rtc):
    conf = rtc.get_configuration()

    confset = conf.get_active_configuration_set()
    confData = confset.configuration_data
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
    return prop


##
# @if jp
#
# @brief コンフィギュレーションパラメータを設定
#
#
# @param rtc 対象のRTコンポーネント
# @param confset_name コンフィギュレーションセット名
# @param value_name パラメータ名
# @param value パラメータ
# @return True:設定に成功、False:設定に失敗
#
# @else
#
# @brief
# @param rtc
# @param confset_name
# @param value_name
# @param value
# @return
#
# @endif
def set_configuration(rtc, confset_name, value_name, value):
    conf = rtc.get_configuration()

    confset = conf.get_configuration_set(confset_name)

    set_configuration_parameter(conf, confset, value_name, value)

    conf.activate_configuration_set(confset_name)
    return True


##
# @if jp
#
# @brief アクティブなコンフィギュレーションセットのパラメータを設定
#
#
# @param rtc 対象のRTコンポーネント
# @param value_name パラメータ名
# @param value パラメータ
# @return True:設定に成功、False:設定に失敗
#
# @else
#
# @brief
# @param rtc
# @param confset_name
# @param value_name
# @param value
# @return
#
# @endif
def set_active_configuration(rtc, value_name, value):
    conf = rtc.get_configuration()

    confset = conf.get_active_configuration_set()
    set_configuration_parameter(conf, confset, value_name, value)

    conf.activate_configuration_set(confset.id)
    return True


##
# @if jp
#
# @brief コンフィギュレーションパラメータの設定
#
#
# @param conf コンフィギュレーション
# @param confset コンフィギュレーションセット
# @param value_name パラメータ名
# @param value パラメータ
# @return True:設定に成功、False:設定に失敗
#
# @else
#
# @brief
# @param conf
# @param confset
# @param value_name
# @param value
# @return
#
# @endif
def set_configuration_parameter(conf, confset, value_name, value):
    confData = confset.configuration_data
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
    prop.setProperty(value_name, value)
    OpenRTM_aist.NVUtil.copyFromProperties(confData, prop)
    confset.configuration_data = confData
    conf.set_configuration_set_values(confset)
    return True


##
# @if jp
# @class CorbaURI
# @brief 指定のCORBAオブジェクト参照用URLから参照形式、ホスト名、ポート番号、
#        パス、オブジェクトキーを取得する機能を提供するクラス
#
# @since 2.0.0
#
# @else
# @class CorbaURI
# @brief
#
# @since 2.0.0
#
# @endif
class CorbaURI:
    ##
    # @if jp
    #
    # @brief コンストラクタ
    #
    #  uriには以下の形式のURLを指定できる
    #  - corbaloc形式(例：corbaloc:iiop:192.168.11.1:2809/Nameservice)
    #  - corbaname形式(例：corbaname::192.168.11.1:2809#ConsoleOut0.rtc)
    #  - HTTP(例：http://192.168.11.1:2809/call#Nameservice)
    #  - HTTPS(例：https://192.168.11.1:2809/call#Nameservice)
    #  - WS(例：ws://192.168.11.1:2809/ws#Nameservice)
    #  - WSS(例：wss://192.168.11.1:2809/ws#Nameservice)
    #
    #  また、giop:ではじまるエンドポイントを指定することもできる
    #  この場合は上記のcorbaloc形式、corbaname形式、HTTP、HTTPS、WS、WSSのURLに変換する
    #  - giop::192.168.11.1:2809 -> corbaloc:iiop:192.168.11.1:2809
    #  - giop:tcp:192.168.11.1:2809 -> corbaloc:iiop:192.168.11.1:2809
    #  - giop:ssl:192.168.11.1:2809 -> corbaloc:ssliop:192.168.11.1:2809
    #  - giop:http:http://192.168.11.1:2809/call ->
    #                   http://192.168.11.1:2809/call
    #
    #  アドレス、ポート番号を指定した場合はcorbaloc形式URLに変換する。
    #  - 192.168.11.1:2809 -> corbaloc:iiop:192.168.11.1:2809
    #
    #  objkeyを指定した場合はURIの末尾に追加する。
    #  - corbaloc:iiop:192.168.11.1:2809 ->
    #        corbaloc:iiop:192.168.11.1:2809/Nameservice
    #  - corbaname::192.168.11.1:2809 ->
    #     corbaloc:iiop:192.168.11.1:2809#ConsoleOut0.rtc
    #  - http://192.168.11.1:2809/call ->
    #     http://192.168.11.1:2809/call#Nameservice
    #
    # @param self
    # @param uri CORBAオブジェクト参照用URL
    # @param objkey オブジェクト名
    #
    # @else
    #
    # @brief Consructor
    #
    #
    # @param self
    # @param uri
    # @param objkey
    #
    # @endif
    def __init__(self, uri, objkey=""):
        import urllib.parse
        protocols_str = {"giop:tcp:": "corbaloc:iiop:",
                         "giop:ssl:": "corbaloc:ssliop:",
                         "giop:http:": "",
                         "giop::": "corbaloc:iiop:",
                         "iiop://": "corbaloc:iiop:",
                         "diop://": "corbaloc:diop:",
                         "uiop://": "corbaloc:uiop:",
                         "ssliop://": "corbaloc:ssliop:",
                         "shmiop://": "corbaloc:shmiop:",
                         "htiop://": "corbaloc:htiop:",
                         "inet:": "corbaloc:iiop:"}

        converted = False
        for k, v in protocols_str.items():
            if uri.find(k) == 0:
                uri = uri.replace(k, v)
                converted = True
                break

        protocols_o_str = {"iiop:": "corbaloc:iiop:",
                           "ssliop:": "corbaloc:ssliop:",
                           "diop:": "corbaloc:diop:",
                           "shmiop:": "corbaloc:shmiop:",
                           "htiop:": "corbaloc:htiop:"}

        if not converted:
            for k, v in protocols_o_str.items():
                if uri.find(k) == 0:
                    uri = uri.replace(k, v)
                    break

        self._uri = ""
        self._port = None
        self._addressonly = False
        ret = urllib.parse.urlparse(uri)
        self._protocol = ret.scheme

        loc = [s.strip() for s in ret.netloc.split(":")]
        if len(loc) >= 2:
            self._host = loc[0]
            self._port = int(loc[1])
        else:
            self._host = ret.netloc
        self._path = ret.path
        self._fragment = ret.fragment

        if self._fragment:
            self._uri = uri
            return
        else:
            self._fragment = objkey
            if self._protocol == "corbaloc":
                self._uri = uri + "/"
                self._uri += self._fragment
            elif self._protocol:
                self._uri = uri + "#"
                self._uri += self._fragment
            else:
                self._uri = "corbaloc:iiop:"
                self._uri += uri + "/"
                self._uri += self._fragment
                self._protocol = "corbaloc"
                self._addressonly = True
                host_port = [s.strip() for s in uri.split(":")]
                if len(host_port) == 2:
                    self._host = host_port[0]
                    try:
                        self._port = int(host_port[1])
                    except BaseException:
                        pass
    ##
    # @if jp
    #
    # @brief  CORBAオブジェクト参照用URLを取得する
    #
    # @param self
    # @return CORBAオブジェクト参照用URL
    #
    # @else
    #
    # @brief Consructor
    #
    # @param self
    # @return
    #
    # @endif

    def toString(self):
        return self._uri

    ##
    # @if jp
    #
    # @brief  参照形式を取得する
    # 例：corbaloc、corbaname、http、https、ws、wss
    #
    # @param self
    # @return 参照形式
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getProtocol(self):
        return self._protocol

    ##
    # @if jp
    #
    # @brief  ホスト名を取得する
    #
    # @param self
    # @return ホスト名
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getHost(self):
        return self._host

    ##
    # @if jp
    #
    # @brief  ポート番号を取得する
    #
    # @param self
    # @return ポート番号
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def getPort(self):
        return self._port

    ##
    # @if jp
    #
    # @brief  初期化時にCORBAオブジェクト参照用URLを指定した場合はfalse、
    # ホスト名、ポート番号のみを指定した場合はtrueを返す。
    #
    # @param self
    # @return 参照先の指定方法
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @return
    #
    # @endif
    def isAddressOnly(self):
        return self._addressonly
