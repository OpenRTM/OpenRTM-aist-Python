#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file FiniteStateMachineComponentBase.py
# @brief Finite StateMachine Component Base class
# @date  $Date: 2017-06-09 07:49:59 $
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2017
#     Nobuhiko Miyamoto
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist
import RTC


##
# @if jp
# @brief
# FiniteStateMachineのベースクラス。
# ユーザが新たなRTコンポーネントを作成する場合は、このクラスを拡張する。
# 各RTコンポーネントのベースとなるクラス。}
#
#
# @else
# @brief
# This is a class to be a base of each RT-Component.
# This is a implementation class of lightweightRTComponent in Robotic
# Technology Component specification
#
# @endif
class FiniteStateMachineComponentBase(OpenRTM_aist.RTObject_impl):
    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    #
    # @param self
    #
    # @else
    #
    # @brief Consructor
    #
    #
    # @endif
    def __init__(self, manager):
        OpenRTM_aist.RTObject_impl.__init__(self, manager)
        self._rtcout = self._manager.getLogbuf(
            "FiniteStateMachineComponentBase")
        self._ref = None

    ##
    # @if jp
    #
    # @brief [CORBA interface] RTCを初期化する
    #
    # このオペレーション呼び出しの結果として、ComponentAction::on_initialize
    # コールバック関数が呼ばれる。
    #
    # 制約
    # - RTC は Created状態の場合み初期化が行われる。他の状態にいる場合には
    #   ReturnCode_t::PRECONDITION_NOT_MET が返され呼び出しは失敗する。
    # - このオペレーションは RTC のミドルウエアから呼ばれることを想定しており、
    #   アプリケーション開発者は直接このオペレーションを呼ぶことは想定
    #   されていない。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Initialize the RTC that realizes this interface.
    #
    # The invocation of this operation shall result in the invocation of the
    # callback ComponentAction::on_initialize.
    #
    # Constraints
    # - An RTC may be initialized only while it is in the Created state. Any
    #   attempt to invoke this operation while in another state shall fail
    #   with ReturnCode_t::PRECONDITION_NOT_MET.
    # - Application developers are not expected to call this operation
    #   directly; it exists for use by the RTC infrastructure.
    #
    # @return
    #
    # @endif
    def initialize(self):
        return OpenRTM_aist.RTObject_impl.initialize(self)

    ##
    # @if jp
    #
    # @brief [CORBA interface] RTC を終了する
    #
    # このオペレーション呼び出しの結果として ComponentAction::on_finalize()
    # を呼び出す。
    #
    # 制約
    # - RTC が ExecutionContext に所属している間は終了されない。この場合は、
    #   まず最初に ExecutionContextOperations::remove_component によって参加を
    #   解除しなければならない。これ以外の場合は、このオペレーション呼び出しは
    #   いかなる場合も ReturnCode_t::PRECONDITION_NOT_ME で失敗する。
    # - RTC が Created 状態である場合、終了処理は行われない。
    #   この場合、このオペレーション呼び出しはいかなる場合も
    #   ReturnCode_t::PRECONDITION_NOT_MET で失敗する。
    # - このオペレーションはRTCのミドルウエアから呼ばれることを想定しており、
    #   アプリケーション開発者は直接このオペレーションを呼ぶことは想定
    #   されていない。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Finalize the RTC for preparing it for destruction
    #
    # This invocation of this operation shall result in the invocation of the
    # callback ComponentAction::on_finalize.
    #
    # Constraints
    # - An RTC may not be finalized while it is participating in any execution
    #   context. It must first be removed with
    #   ExecutionContextOperations::remove_component. Otherwise, this operation
    #   shall fail with ReturnCode_t::PRECONDITION_NOT_MET.
    # - An RTC may not be finalized while it is in the Created state. Any
    #   attempt to invoke this operation while in that state shall fail with
    #   ReturnCode_t::PRECONDITION_NOT_MET.
    # - Application developers are not expected to call this operation directly;
    #  it exists for use by the RTC infrastructure.
    #
    # @return
    #
    # @endif

    def finalize(self):
        return OpenRTM_aist.RTObject_impl.finalize(self)

    ##
    # @if jp
    #
    # @brief [CORBA interface] RTC がオーナーである ExecutionContext を
    #        停止させ、そのコンテンツと共に終了させる
    #
    # この RTC がオーナーであるすべての実行コンテキストを停止する。
    # この RTC が他の実行コンテキストを所有する RTC に属する実行コンテキスト
    # (i.e. 実行コンテキストを所有する RTC はすなわちその実行コンテキストの
    # オーナーである。)に参加している場合、当該 RTC はそれらのコンテキスト上
    # で非活性化されなければならない。
    # RTC が実行中のどの ExecutionContext でも Active 状態ではなくなった後、
    # この RTC とこれに含まれる RTC が終了する。
    #
    # 制約
    # - RTC が初期化されていなければ、終了させることはできない。
    #   Created 状態にある RTC に exit() を呼び出した場合、
    #   ReturnCode_t::PRECONDITION_NOT_MET で失敗する。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief Stop the RTC's execution context(s) and finalize it along with its
    #        contents.
    #
    # Any execution contexts for which the RTC is the owner shall be stopped.
    # If the RTC participates in any execution contexts belonging to another
    # RTC that contains it, directly or indirectly (i.e. the containing RTC
    # is the owner of the ExecutionContext), it shall be deactivated in those
    # contexts.
    # After the RTC is no longer Active in any Running execution context, it
    # and any RTCs contained transitively within it shall be finalized.
    #
    # Constraints
    # - An RTC cannot be exited if it has not yet been initialized. Any
    #   attempt to exit an RTC that is in the Created state shall fail with
    #   ReturnCode_t::PRECONDITION_NOT_MET.
    #
    # @return
    #
    # @endif

    def exit(self):
        return OpenRTM_aist.RTObject_impl.exit(self)

    ##
    # @if jp
    #
    # @brief [CORBA interface] RTC が Alive 状態であるかどうか確認する。
    #
    # RTC が指定した ExecutionContext に対して Alive状態であるかどうか確認する。
    # RTC の状態が Active であるか、Inactive であるか、Error であるかは実行中の
    # ExecutionContext に依存する。すなわち、ある ExecutionContext に対しては
    # Active  状態であっても、他の ExecutionContext に対しては Inactive 状態と
    # なる場合もありえる。従って、このオペレーションは指定された
    # ExecutionContext に問い合わせて、この RTC の状態が Active、Inactive、
    # Error の場合には Alive 状態として返す。
    #
    # @param self
    #
    # @param exec_context 取得対象 ExecutionContext ハンドル
    #
    # @return Alive 状態確認結果
    #
    # @else
    #
    # @brief Confirm whether RTC is an Alive state or NOT.
    #
    # A component is alive or not regardless of the execution context from
    # which it is observed. However, whether or not it is Active, Inactive,
    # or in Error is dependent on the execution context(s) in which it is
    # running. That is, it may be Active in one context but Inactive in
    # another. Therefore, this operation shall report whether this RTC is
    # either Active, Inactive or in Error; which of those states a component
    # is in with respect to a particular context may be queried from the
    # context itself.
    #
    # @return Result of Alive state confirmation
    #
    # @endif
    # virtual CORBA::Boolean is_alive(ExecutionContext_ptr exec_context)

    def is_alive(self, exec_context):
        return OpenRTM_aist.RTObject_impl.is_alive(self, exec_context)

    ##
    # @if jp
    # @brief [CORBA interface] 所有する ExecutionContextListを 取得する
    #
    # この RTC が所有する ExecutionContext のリストを取得する。
    #
    # @return ExecutionContext リスト
    #
    # @else
    # @brief [CORBA interface] Get ExecutionContextList.
    #
    # This operation returns a list of all execution contexts owned by this
    # RTC.
    #
    # @return ExecutionContext List
    #
    # @endif
    # virtual ExecutionContextList* get_owned_contexts()

    def get_owned_contexts(self):
        return OpenRTM_aist.RTObject_impl.get_owned_contexts(self)

    ##
    # @if jp
    # @brief [CORBA interface] ExecutionContextを取得する
    #
    # 指定したハンドルの ExecutionContext を取得する。
    # ハンドルから ExecutionContext へのマッピングは、特定の RTC インスタンスに
    # 固有である。ハンドルはこの RTC を attach_context した際に取得できる。
    #
    # @param self
    # @param ec_id 取得対象 ExecutionContext ハンドル
    #
    # @return ExecutionContext
    #
    # @else
    # @brief [CORBA interface] Get ExecutionContext.
    #
    # Obtain a reference to the execution context represented by the given
    # handle.
    # The mapping from handle to context is specific to a particular RTC
    # instance. The given handle must have been obtained by a previous call to
    # attach_context on this RTC.
    #
    # @param ec_id ExecutionContext handle
    #
    # @return ExecutionContext
    #
    # @endif
    # virtual ExecutionContext_ptr get_context(UniqueId exec_handle)

    def get_owned_contexts(self):
        return OpenRTM_aist.RTObject_impl.get_owned_contexts(self)

    ##
    # @if jp
    # @brief [CORBA interface] ExecutionContextを取得する
    #
    # 指定したハンドルの ExecutionContext を取得する。
    # ハンドルから ExecutionContext へのマッピングは、特定の RTC インスタンスに
    # 固有である。ハンドルはこの RTC を attach_context した際に取得できる。
    #
    # @param self
    # @param ec_id 取得対象 ExecutionContext ハンドル
    #
    # @return ExecutionContext
    #
    # @else
    # @brief [CORBA interface] Get ExecutionContext.
    #
    # Obtain a reference to the execution context represented by the given
    # handle.
    # The mapping from handle to context is specific to a particular RTC
    # instance. The given handle must have been obtained by a previous call to
    # attach_context on this RTC.
    #
    # @param ec_id ExecutionContext handle
    #
    # @return ExecutionContext
    #
    # @endif
    # virtual ExecutionContext_ptr get_context(UniqueId exec_handle)

    def get_context(self, ec_id):
        return OpenRTM_aist.RTObject_impl.get_context(self, ec_id)

    ##
    # @if jp
    # @brief [CORBA interface] 参加している ExecutionContextList を取得する
    #
    # この RTC が参加している ExecutionContext のリストを取得する。
    #
    # @return ExecutionContext リスト
    #
    # @else
    # @brief [CORBA interface] Get participating ExecutionContextList.
    #
    # This operation returns a list of all execution contexts in
    # which this RTC participates.
    #
    # @return ExecutionContext List
    #
    # @endif
    # virtual ExecutionContextList* get_participating_contexts()

    def get_participating_contexts(self):
        return OpenRTM_aist.RTObject_impl.get_participating_contexts(self)

    ##
    # @if jp
    # @brief [CORBA interface] ExecutionContext のハンドルを返す
    #
    # @param ExecutionContext 実行コンテキスト
    #
    # @return ExecutionContextHandle
    #
    # 与えられた実行コンテキストに関連付けられたハンドルを返す。
    #
    # @else
    # @brief [CORBA interface] Return a handle of a ExecutionContext
    #
    # @param ExecutionContext
    #
    # @return ExecutionContextHandle
    #
    # This operation returns a handle that is associated with the given
    # execution context.
    #
    # @endif
    #
    # virtual ExecutionContextHandle_t
    #   get_context_handle(ExecutionContext_ptr cxt)

    def get_context_handle(self, cxt):
        return OpenRTM_aist.RTObject_impl.get_context_handle(self, cxt)

    ##
    # @if jp
    #
    # @brief [RTObject CORBA interface] コンポーネントプロファイルを取得する
    #
    # 当該コンポーネントのプロファイル情報を返す。
    #
    # @param self
    #
    # @return コンポーネントプロファイル
    #
    # @else
    #
    # @brief [RTObject CORBA interface] Get RTC's profile
    #
    # This operation returns the ComponentProfile of the RTC
    #
    # @return ComponentProfile
    #
    # @endif
    # virtual ComponentProfile* get_component_profile()

    def get_component_profile(self):
        return OpenRTM_aist.RTObject_impl.get_component_profile(self)

    ##
    # @if jp
    #
    # @brief [RTObject CORBA interface] ポートを取得する
    #
    # 当該コンポーネントが保有するポートの参照を返す。
    #
    # @param self
    #
    # @return ポートリスト
    #
    # @else
    #
    # @brief [RTObject CORBA interface] Get Ports
    #
    # This operation returns a list of the RTCs ports.
    #
    # @return PortList
    #
    # @endif
    # virtual PortServiceList* get_ports()

    def get_ports(self):
        return OpenRTM_aist.RTObject_impl.get_ports(self)

    ##
    # @if jp
    # @brief [CORBA interface] ExecutionContextをattachする
    #
    # 指定した ExecutionContext にこの RTC を所属させる。この RTC と関連する
    # ExecutionContext のハンドルを返す。
    # このオペレーションは、ExecutionContextOperations::add_component が呼ばれた
    # 際に呼び出される。返されたハンドルは他のクライアントで使用することを想定
    # していない。
    #
    # @param self
    # @param exec_context 所属先 ExecutionContext
    #
    # @return ExecutionContext ハンドル
    #
    # @else
    # @brief [CORBA interface] Attach ExecutionContext.
    #
    # Inform this RTC that it is participating in the given execution context.
    # Return a handle that represents the association of this RTC with the
    # context.
    # This operation is intended to be invoked by
    # ExecutionContextOperations::add_component. It is not intended for use by
    # other clients.
    #
    # @param exec_context Prticipating ExecutionContext
    #
    # @return ExecutionContext Handle
    #
    # @endif
    # UniqueId attach_context(ExecutionContext_ptr exec_context)

    def attach_context(self, exec_context):
        return OpenRTM_aist.RTObject_impl.attach_context(self, exec_context)

    ##
    # @if jp
    # @brief [CORBA interface] ExecutionContextをdetachする
    #
    # 指定した ExecutionContext からこの RTC の所属を解除する。
    # このオペレーションは、ExecutionContextOperations::remove_component が呼ば
    # れた際に呼び出される。返されたハンドルは他のクライアントで使用することを
    # 想定していない。
    #
    # 制約
    # - 指定された ExecutionContext に RTC がすでに所属していない場合には、
    #   ReturnCode_t::PRECONDITION_NOT_MET が返される。
    # - 指定された ExecutionContext にたしいて対して RTC がActive 状態である場
    #   合には、 ReturnCode_t::PRECONDITION_NOT_MET が返される。
    #
    # @param self
    # @param ec_id 解除対象 ExecutionContextハンドル
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    # @brief [CORBA interface] Attach ExecutionContext.
    #
    # Inform this RTC that it is no longer participating in the given execution
    # context.
    # This operation is intended to be invoked by
    # ExecutionContextOperations::remove_component. It is not intended for use
    # by other clients.
    # Constraints
    # - This operation may not be invoked if this RTC is not already
    #   participating in the execution context. Such a call shall fail with
    #   ReturnCode_t::PRECONDITION_NOT_MET.
    # - This operation may not be invoked if this RTC is Active in the indicated
    #   execution context. Otherwise, it shall fail with
    #   ReturnCode_t::PRECONDITION_NOT_MET.
    #
    # @param ec_id Dettaching ExecutionContext Handle
    #
    # @return
    #
    # @endif
    # ReturnCode_t detach_context(UniqueId exec_handle)

    def detach_context(self, ec_id):
        return OpenRTM_aist.RTObject_impl.detach_context(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の初期化
    #
    # RTC が初期化され、Alive 状態に遷移する。
    # RTC 固有の初期化処理はここで実行する。
    # このオペレーション呼び出しの結果として onInitialize() コールバック関数が
    # 呼び出される。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Initialize RTC
    #
    # The RTC has been initialized and entered the Alive state.
    # Any RTC-specific initialization logic should be performed here.
    #
    # @return
    #
    # @endif

    def on_initialize(self):
        return OpenRTM_aist.RTObject_impl.on_initialize(self)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の終了
    #
    # RTC が破棄される。
    # RTC 固有の終了処理はここで実行する。
    # このオペレーション呼び出しの結果として onFinalize() コールバック関数が
    # 呼び出される。
    #
    # @param self
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Finalize RTC
    #
    # The RTC is being destroyed.
    # Any final RTC-specific tear-down logic should be performed here.
    #
    # @return
    #
    # @endif

    def on_finalize(self):
        return OpenRTM_aist.RTObject_impl.on_finalize(self)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の開始
    #
    # RTC が所属する ExecutionContext が Stopped 状態から Running 状態へ遷移
    # した場合に呼び出される。
    # このオペレーション呼び出しの結果として onStartup() コールバック関数が
    # 呼び出される。
    #
    # @param self
    # @param ec_id 状態遷移した ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] StartUp RTC
    #
    # The given execution context, in which the RTC is participating, has
    # transitioned from Stopped to Running.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_startup(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_startup(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の停止
    #
    # RTC が所属する ExecutionContext が Running 状態から Stopped 状態へ遷移
    # した場合に呼び出される。
    # このオペレーション呼び出しの結果として onShutdown() コールバック関数が
    # 呼び出される。
    #
    # @param self
    # @param ec_id 状態遷移した ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] ShutDown RTC
    #
    # The given execution context, in which the RTC is participating, has
    # transitioned from Running to Stopped.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_shutdown(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_shutdown(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の活性化
    #
    # 所属する ExecutionContext から RTC が活性化された際に呼び出される。
    # このオペレーション呼び出しの結果として onActivated() コールバック関数が
    # 呼び出される。
    #
    # @param self
    # @param ec_id 活性化 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Activate RTC
    #
    # The RTC has been activated in the given execution context.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_activated(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_activated(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC の非活性化
    #
    # 所属する ExecutionContext から RTC が非活性化された際に呼び出される。
    # このオペレーション呼び出しの結果として onDeactivated() コールバック関数が
    # 呼び出される。
    #
    # @param self
    # @param ec_id 非活性化 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Deactivate RTC
    #
    # The RTC has been deactivated in the given execution context.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_deactivated(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_deactivated(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC のエラー処理
    #
    # RTC がエラー状態にいる際に呼び出される。
    # RTC がエラー状態の場合に、対象となる ExecutionContext のExecutionKind に
    # 応じたタイミングで呼び出される。例えば、
    # - ExecutionKind が PERIODIC の場合、本オペレーションは
    #   DataFlowComponentAction::on_execute と on_state_update の替わりに、
    #   設定された順番、設定された周期で呼び出される。
    # - ExecutionKind が EVENT_DRIVEN の場合、本オペレーションは
    #   FsmParticipantAction::on_action が呼ばれた際に、替わりに呼び出される。
    # このオペレーション呼び出しの結果として onError() コールバック関数が呼び出
    # される。
    #
    # @param self
    # @param ec_id 対象 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Error Processing of RTC
    #
    # The RTC remains in the Error state.
    # If the RTC is in the Error state relative to some execution context when
    # it would otherwise be invoked from that context (according to the
    # context’s ExecutionKind), this callback shall be invoked instead.
    # For example,
    # - If the ExecutionKind is PERIODIC, this operation shall be invoked in
    #   sorted order at the rate of the context instead of
    #   DataFlowComponentAction::on_execute and on_state_update.
    # - If the ExecutionKind is EVENT_DRIVEN, this operation shall be invoked
    #   whenever FsmParticipantAction::on_action would otherwise have been
    #   invoked.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_error(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_error(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC のエラー状態への遷移
    #
    # RTC が所属する ExecutionContext が Active 状態から Error 状態へ遷移した
    # 場合に呼び出される。
    # このオペレーションは RTC が Error 状態に遷移した際に一度だけ呼び出される。
    # このオペレーション呼び出しの結果として onAborting() コールバック関数が
    # 呼び出される。
    #
    # @param self
    # @param ec_id 状態遷移した ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Transition Error State
    #
    # The RTC is transitioning from the Active state to the Error state in some
    # execution context.
    # This callback is invoked only a single time for time that the RTC
    # transitions into the Error state from another state. This behavior is in
    # contrast to that of on_error.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_aborting(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_aborting(self, ec_id)

    ##
    # @if jp
    #
    # @brief [ComponentAction CORBA interface] RTC のリセット
    #
    # Error 状態にある RTC のリカバリ処理を実行し、Inactive 状態に復帰させる
    # 場合に呼び出される。
    # RTC のリカバリ処理が成功した場合は Inactive 状態に復帰するが、それ以外の
    # 場合には Error 状態に留まる。
    # このオペレーション呼び出しの結果として onReset() コールバック関数が呼び
    # 出される。
    #
    # @param self
    # @param ec_id リセット対象 ExecutionContext の ID
    #
    # @return ReturnCode_t 型のリターンコード
    #
    # @else
    #
    # @brief [ComponentAction CORBA interface] Resetting RTC
    #
    # The RTC is in the Error state. An attempt is being made to recover it such
    # that it can return to the Inactive state.
    # If the RTC was successfully recovered and can safely return to the
    # Inactive state, this method shall complete with ReturnCode_t::OK. Any
    # other result shall indicate that the RTC should remain in the Error state.
    #
    # @param ec_id
    #
    # @return
    #
    # @endif

    def on_reset(self, ec_id):
        return OpenRTM_aist.RTObject_impl.on_reset(self, ec_id)

    ##
    # @if jp
    # @brief
    #
    #
    #
    # @param self
    #
    # @else
    #
    # @brief Consructor
    #
    #
    # @endif

    def on_action(self, ec_id):
        return RTC.RTC_OK
