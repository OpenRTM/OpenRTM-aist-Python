#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file RTCFailoverMain.py
# @brief Starts configuration-driven RTC groups and attaches component observers
#
# @~japanese
# 設定ファイル方式の RTC のグループを起動し、コンポーネントオブザーバーを付ける
#
# 使い方: python3 RTCFailoverMain.py --failover-config rtc_failover.json [OpenRTM の引数 (-f rtc.conf, -o ...)]
# 監視対象の RTC が動いているプロセスでは ComponentObserverConsumer を読み込んでおくこと (README の「RTC 側の設定」を参照)。
# @~english
# Usage: python3 RTCFailoverMain.py --failover-config rtc_failover.json [OpenRTM arguments (-f rtc.conf, -o ...)]
# ComponentObserverConsumer must be loaded in the processes where the monitored RTCs run (see "RTC side settings" in README).
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

import argparse
import logging
import sys

import OpenRTM_aist
import RTCFailover

LOG = logging.getLogger(__name__)


##
# @~japanese
# @brief 入口 (マネージャを起動し、RTCFailover を始める)
# @~english
# @brief Entry point (starts the manager and RTCFailover)
# @~
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--failover-config', default=None)
    parser.add_argument('--log-level', default='INFO')
    args, rtm_args = parser.parse_known_args()
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO),
                        format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    manager = OpenRTM_aist.Manager.init([sys.argv[0]] + rtm_args)
    manager.activateManager()
    # ORB を先に動かしておき、オブザーバの通知 (update_status) を受けられるようにする
    manager.runManager(True)
    controller = RTCFailover.initialize(manager, args.failover_config)
    results = controller.start()
    LOG.info('initial connections: %s', results)
    try:
        manager.join()
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


if __name__ == '__main__':
    main()
