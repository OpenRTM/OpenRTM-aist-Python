#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file SdoServiceConsumerBase.py
# @brief SDO service consumer base class and its factory
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2011
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import OpenRTM_aist


##
# @if jp
#
# SdoServiceConsumerFactory&
#                     factory(SdoServiceConsumerFactory.instance());
#
# factory.addFactory(toRepositoryId<IDL Type>(),
#                   Creator< SdoServiceConsumerBase,
#                            your_sdo_service_consumer_subclass>);
#
# @else
#
#
#
# @endif
class SdoServiceConsumerBase:
    """
    """

    def __init__(self):
        pass

    def __del__(self):
        pass

    ##
    # @if jp
    # @brief コンシューマクラスの初期化関数
    #
    # 初期化関数。与えられた RTObject および ServiceProfile から、当該
    # オブジェクトを初期化します。このサービスが
    # ''sdo.service.provider.enabled_services'' で有効化されていれば、
    # この関数は対応するRTCがインスタンス化された直後に呼び出されます。
    #
    # ServiceProfile には以下の情報が入った状態で呼び出されます。
    #
    # - ServiceProfile.id: 当該サービスのIFR型
    # - ServiceProfile.interface_type: 当該サービスのIFR型
    # - ServiceProfile.service: 当該サービスのオブジェクト参照
    # - ServiceProfile.properties: rtc.conf や <component>.conf 等で与
    #                   えられたSDOサービス固有のオプションが渡される。
    #                   confファイル内で
    #                   は、''<pragma>.<module_name>.<interface_name>''
    #                   というプリフィックスをつけたオプションとして与
    #                   えることができ、properties 内には、このプリ
    #                   フィックスを除いたオプションがkey:value形式で
    #                   含まれている。
    #
    # 関数内では、主に properties から設定内容を読み込みサービス固有の
    # 設定等を行います。与えられた ServiceProfileの内容が不正、あるい
    # はその他の理由で当該サービスをインスタンス化しない場合は false
    # を返します。その場合、finalize() が呼び出されその後オブジェクト
    # は削除されます。それ以外の場合は true を返すと、サービスオブジェ
    # クトは RTC 内に保持されます。
    #
    # @param rtobj このオブジェクトがインスタンス化された RTC
    # @param profile 外部から与えられた SDO ServiceProfile
    # @return 与えられた SDO Service や ServiceProfile が不正の場合 false
    #
    # @else
    # @brief Initialization function of the consumer class
    #
    # @endif
    #
    # virtual bool init(RTObject_impl& rtobj,
    #                   const SDOPackage::ServiceProfile& profile) = 0;
    def init(self, rtobj, profile):
        pass

    ##
    # @if jp
    # @brief コンシューマクラスの再初期化関数
    #
    # このオブジェクトの再初期化を行う。ServiceProfile には id フィー
    # ルドにセッション固有の UUID がセットされているが、同一の id の場
    # 合、properties に設定された設定情報の変更や、service フィールド
    # のサービスの参照の変更が行われる。その際に呼ばれるのがこの
    # reinit() 関数である。実装では、service フィールドのオブジェクト
    # リファレンスの同一性を確認し、異なっている場合保持しているリファ
    # レンスを更新する必要がある。また properties には新たな設定が与え
    # られている可能性があるので、内容を読み込み設定を更新する。
    #
    # @param profile 新たに与えられた SDO ServiceProfile
    # @return 不正な ServiceProfile が与えられた場合は false
    #
    # @else
    # @brief Reinitialization function of the consumer class
    #
    # @endif
    #
    # virtual bool reinit(const SDOPackage::ServiceProfile& profile) = 0;
    def reinit(self, profile):
        pass

    ##
    # @if jp
    # @brief ServiceProfile を返す
    #
    # init()/reinit()で与えられた ServiceProfile は通常オブジェクト内
    # で保持される。SDO Service 管理フレームワークは管理上このオブジェ
    # クトに対応する ServiceProfile を必要とするので、この関数では保持
    # されている ServiceProfile を返す。
    #
    # @return このオブジェクトが保持している ServiceProfile
    #
    # @else
    # @brief Getting ServiceProfile
    # @endif
    #
    # virtual const SDOPackage::ServiceProfile& getProfile() const = 0;
    def getProfile(self):
        pass

    ##
    # @if jp
    # @brief 終了処理
    #
    # SDOサービスがでタッチされる際に呼び出される終了処理用関数。サー
    # ビスのでタッチに際して、当該オブジェクトが保持するリソースを解放
    # するなどの処理を行う。
    #
    # @else
    # @brief Finalization
    #
    # @endif
    #
    # virtual void finalize() = 0;
    def finalize(self):
        pass


sdoserviceconsumerfactory = None


class SdoServiceConsumerFactory(OpenRTM_aist.Factory, SdoServiceConsumerBase):
    def __init__(self):
        OpenRTM_aist.Factory.__init__(self)
        return

    def __del__(self):
        pass

    def instance():
        global sdoserviceconsumerfactory

        if sdoserviceconsumerfactory is None:
            sdoserviceconsumerfactory = SdoServiceConsumerFactory()

        return sdoserviceconsumerfactory

    instance = staticmethod(instance)
