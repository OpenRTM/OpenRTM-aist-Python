#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file MultilayerCompositeEC.py
# @brief MultilayerCompositeEC class
# @date $Date: 2018/09/18$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2006-2018
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.


import threading
import time


from omniORB import CORBA

import OpenRTM_aist

import OpenRTM
import RTC
import RTC__POA

DEFAULT_PERIOD = 0.000001

##
# @if jp
# @class MultilayerCompositeEC
# @brief MultilayerCompositeEC クラス
#
# Periodic Sampled Data Processing(周期実行用)ExecutionContextクラス。
#
# @since 0.4.0
#
# @else
# @class MultilayerCompositeEC
# @brief MultilayerCompositeEC class
# @endif


class MultilayerCompositeEC(OpenRTM_aist.PeriodicExecutionContext):
    """
    """

    ##
    # @if jp
    # @brief コンストラクタ
    #
    # コンストラクタ
    # 設定された値をプロファイルに設定する。
    #
    # @else
    # @brief Constructor
    # @endif
    def __init__(self):

        OpenRTM_aist.PeriodicExecutionContext.__init__(self)
        self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf(
            "rtobject.multilayercomposite_ec")
        self._rtcout.RTC_TRACE("MultilayerCompositeEC.__init__()")

        self._tasklist = []
        self._ownersm = None

        return

    ##
    # @if jp
    # @brief 終了関数
    #
    # @param self　
    # @param Task　
    #
    # @else
    # @brief
    # @param self　
    # @param Task　
    # @endif
    def exit(self, Task=OpenRTM_aist.Task):
        OpenRTM_aist.PeriodicExecutionContext.exit(self)
        for task in self._tasklist:
            task.finalize()
        return

    ##
    # @if jp
    # @brief 初期化関数
    #
    # @param self　
    # @param props プロパティ
    #
    # @else
    # @brief
    # @param self　
    # @param props
    # @endif
    def init(self, props):
        OpenRTM_aist.PeriodicExecutionContext.init(self, props)
        #prop.getProperty("thread_type", "default")

    ##
    # @if jp
    # @brief コンポーネントをバインドする。
    #
    # @param self
    # @param rtc RTC
    #
    # @else
    # @brief Bind the component.
    #
    # @param self
    # @param rtc RTC
    #
    # @endif

    def bindComponent(self, rtc):
        ret = OpenRTM_aist.ExecutionContextBase.bindComponent(self, rtc)

        mgr = OpenRTM_aist.Manager.instance()

        threads_str = rtc.getProperties().getProperty("conf.default.members")
        str = [threads_str]
        threads = str[0].split("|")
        for thread in threads:
            rtcs = []
            members = thread.split(",")

            for member in members:
                member = member.strip()
                if member == "":
                    continue
                comp = mgr.getComponent(member)

                if comp is None:
                    self._rtcout.RTC_ERROR("no RTC found: %s", member)
                    continue

                rtobj = comp.getObjRef()
                if CORBA.is_nil(rtobj):
                    continue
                rtcs.append(rtobj)

            self.addTask(rtcs)

        return ret

    ##
    # @if jp
    # @class
    # @brief worker 用状態変数クラス
    # @else
    # @brief
    #
    # @endif
    class WorkerThreadCtrl:
        ##
        # @if jp
        # @brief コンストラクタ
        #
        # コンストラクタ
        #
        # @param self
        #
        # @else
        # @brief Constructor
        # @endif
        def __init__(self):
            self._mutex = threading.RLock()
            self._cond = threading.Condition(self._mutex)
            self._running = False

    ##
    # @if jp
    # @class
    # @brief RTC周期実行スレッド
    # @else
    # @brief
    #
    # @endif
    class ChildTask:
        ##
        # @if jp
        # @brief コンストラクタ
        #
        # @param self
        # @param task 周期実行スレッド
        # @param ec 実行コンテキスト
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param task
        # @param ec
        #
        # @endif
        def __init__(self, task, ec):
            self._rtcs = []
            self._task = task
            self._ec = ec
            self._comps = []
            self._worker = MultilayerCompositeEC.WorkerThreadCtrl()
            self._signal_worker = MultilayerCompositeEC.WorkerThreadCtrl()

        ##
        # @if jp
        # @brief 実行するRTCを追加
        #
        # @param self
        # @param rtc RTC
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param rtc RTC
        #
        # @endif
        def addComponent(self, rtc):
            self._rtcs.append(rtc)

        ##
        # @if jp
        # @brief ステートマシンのリストを更新
        #
        # @param self
        # @param return
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param return
        #
        # @endif
        def updateCompList(self):
            for rtc in self._rtcs[:]:
                comp = self._ec.findComponent(rtc)
                if comp:
                    self._rtcs.remove(rtc)
                    self._comps.append(comp)

        ##
        # @if jp
        # @brief スレッド実行関数
        #
        # @param self
        # @param return
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @param return
        #
        # @endif
        def svc(self):
            self._worker._running = True

            self._signal_worker._cond.acquire()
            while not self._signal_worker._running:
                self._signal_worker._cond.wait()
            self._signal_worker._cond.release()
            self._signal_worker._running = False

            self.updateCompList()
            for comp in self._comps:
                comp.workerPreDo()
                comp.workerDo()
                comp.workerPostDo()
            self._worker._running = False
            self._worker._cond.acquire()
            self._worker._cond.notify()
            self._worker._cond.release()

            self._signal_worker._cond.acquire()
            while not self._signal_worker._running:
                self._signal_worker._cond.wait()
            self._signal_worker._cond.release()
            self._signal_worker._running = False

            return 0

        ##
        # @if jp
        # @brief 1回の処理を実行
        #
        # @param self
        #
        # @else
        #
        # @brief
        #
        # @param self
        #
        # @endif
        def signal(self):

            while not self._worker._running:
                self._task.signal()

            self._signal_worker._running = True
            self._signal_worker._cond.acquire()
            self._signal_worker._cond.notify()
            self._signal_worker._cond.release()

        ##
        # @if jp
        # @brief 1回の処理終了まで待機
        #
        # @param self
        #
        # @else
        #
        # @brief
        #
        # @param self
        #
        # @endif
        def join(self):

            self._worker._cond.acquire()
            while self._worker._running:
                self._worker._cond.wait()
            self._worker._cond.release()

            self._signal_worker._running = True
            self._signal_worker._cond.acquire()
            self._signal_worker._cond.notify()
            self._signal_worker._cond.release()

        ##
        # @if jp
        # @brief タスク周期時間計測結果を取得
        #
        # @param self
        # @return 計測結果
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @return
        #
        # @endif

        def getPeriodStat(self):
            return self._task.getPeriodStat()

        ##
        # @if jp
        # @brief タスク関数実行時間計測結果を取得
        #
        # @param self
        # @return 計測結果
        #
        # @else
        #
        # @brief
        #
        # @param self
        # @return
        #
        # @endif

        def getExecStat(self):
            return self._task.getExecStat()

        ##
        # @if jp
        # @brief RTC実行スレッド終了関数
        #
        # @param self
        #
        # @else
        #
        # @brief
        #
        # @param self
        #
        # @endif
        def finalize(self):
            self._task.resume()
            self._task.finalize()

    ##
    # @if jp
    # @brief RTC実行スレッド作成
    #
    # @param self
    # @param rtcs スレッドに関連付けるRTC一覧
    # @return ステートマシン
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param rtcs
    #
    # @endif
    def addTask(self, rtcs):
        prop = self._profile.getProperties().getNode("ec" + str(len(self._tasklist)))
        factory = OpenRTM_aist.PeriodicTaskFactory.instance()

        task = factory.createObject(prop.getProperty("thread_type", "default"))
        if not task:
            self._rtcout.RTC_ERROR(
                "Task creation failed: %s", prop.getProperty(
                    "thread_type", "default"))
            return

        ct = MultilayerCompositeEC.ChildTask(task, self)

        mprop = prop.getNode("measurement")
        task.setTask(ct.svc)
        task.setPeriod(0.0)
        task.executionMeasure(OpenRTM_aist.toBool(mprop.getProperty("exec_time"),
                                                  "enable", "disable", True))
        ecount = 0
        ret, ecount = OpenRTM_aist.stringTo(
            ecount, mprop.getProperty("exec_count"))
        if ret:
            task.executionMeasureCount(ecount)

        task.periodicMeasure(OpenRTM_aist.toBool(mprop.getProperty("period_time"),
                                                 "enable", "disable", True))
        pcount = 0
        ret, pcount = OpenRTM_aist.stringTo(
            pcount, mprop.getProperty("period_count"))
        if ret:
            task.periodicMeasureCount(pcount)

        for rtc in rtcs:
            self.addRTCToTask(ct, rtc)

        self._tasklist.append(ct)

        task.suspend()
        task.activate()
        task.suspend()

    ##
    # @if jp
    # @brief コンポーネント探索関数
    #
    # @param self
    # @param rtobj RTC
    # @return ステートマシン
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param rtobj
    # @return
    #
    # @endif

    def findComponent(self, rtobj):
        return self._worker.findComponent(rtobj)

    ##
    # @if jp
    # @brief RTC実行スレッドにRTCを追加
    # 複合コンポーネントの場合は子コンポーネントも追加
    #
    # @param self
    # @param task RTC実行スレッド
    # @param rtobj RTC
    #
    # @else
    #
    # @brief
    #
    # @param self
    # @param task
    # @param rtobj
    #
    # @endif
    def addRTCToTask(self, task, rtobj):
        #comp = self._worker.findComponent(rtobj)
        orglist = rtobj.get_owned_organizations()
        if not orglist:
            task.addComponent(rtobj)

        for org in orglist:
            sdos = org.get_members()
            for sdo in sdos:
                dfc = sdo._narrow(OpenRTM.DataFlowComponent)
                self.addRTCToTask(task, dfc)

    ##
    # @if jp
    # @brief コンポーネントのアクティビティスレッド関数
    #
    # コンポーネントの内部アクティビティスレッドの実行関数。
    # ACE_Task サービスクラスメソッドのオーバーライド。
    #
    # @else
    #
    # @brief Create internal activity thread
    #
    # Run by a daemon thread to handle deferred processing.
    # ACE_Task class method override.
    #
    # @endif

    def svc(self):
        self._rtcout.RTC_TRACE("svc()")
        count_ = 0
        owner = self.getOwner()
        self._ownersm = self._worker.findComponent(owner)

        # if len(self._cpu) > 0:
        #  ret = OpenRTM_aist.setThreadAffinity(self._cpu)
        #  if ret == False:
        #    self._rtcout.RTC_ERROR("CPU affinity mask setting failed")

        while self.threadRunning():

            self._ownersm.workerPreDo()
            # OpenRTM_aist.ExecutionContextBase.invokeWorkerPreDo(self)
            # Thread will stopped when all RTCs are INACTIVE.
            # Therefore WorkerPreDo(updating state) have to be invoked
            # before stopping thread.

            guard = OpenRTM_aist.ScopedLock(self._workerthread._mutex)
            while not self._workerthread._running:
                self._workerthread._cond.wait()
            del guard

            t0_ = OpenRTM_aist.Time()

            # OpenRTM_aist.ExecutionContextBase.invokeWorkerDo(self)
            self._ownersm.workerDo()
            # OpenRTM_aist.ExecutionContextBase.invokeWorkerPostDo(self)
            self._ownersm.workerPostDo()

            for task in self._tasklist:
                task.signal()

            # time.sleep(0.1)

            for task in self._tasklist:
                task.join()
                # print task._task.getExecStat()._max_interval
                # print task._task.getExecStat()._min_interval
                # print task._task.getExecStat()._mean_interval
                # print task._task.getExecStat()._std_deviation

            t1_ = OpenRTM_aist.Time()

            period_ = self.getPeriod()

            if count_ > 1000:
                exctm_ = (t1_ - t0_).getTime().toDouble()
                slptm_ = period_.toDouble() - exctm_
                self._rtcout.RTC_PARANOID(
                    "Period:    %f [s]", period_.toDouble())
                self._rtcout.RTC_PARANOID("Execution: %f [s]", exctm_)
                self._rtcout.RTC_PARANOID("Sleep:     %f [s]", slptm_)

                for i, task in enumerate(self._tasklist):
                    stat = task.getExecStat()
                    self._rtcout.RTC_PARANOID(
                        "MAX(%d):   %f [s]", (i, stat._max_interval))
                    self._rtcout.RTC_PARANOID(
                        "MIN(%d):   %f [s]", (i, stat._min_interval))
                    self._rtcout.RTC_PARANOID(
                        "MEAN(%d):  %f [s]", (i, stat._mean_interval))
                    self._rtcout.RTC_PARANOID(
                        "SD(%d):    %f [s]", (i, stat._std_deviation))

            t2_ = OpenRTM_aist.Time()

            if not self._nowait and period_.toDouble() > ((t1_ - t0_).getTime().toDouble()):
                if count_ > 1000:
                    self._rtcout.RTC_PARANOID("sleeping...")
                slptm_ = period_.toDouble() - (t1_ - t0_).getTime().toDouble()
                time.sleep(slptm_)

            if count_ > 1000:
                t3_ = OpenRTM_aist.Time()
                self._rtcout.RTC_PARANOID(
                    "Slept:     %f [s]", (t3_ - t2_).getTime().toDouble())
                count_ = 0
            count_ += 1

        self._rtcout.RTC_DEBUG("Thread terminated.")
        return 0


##
# @if jp
# @brief ExecutionContext を初期化する
#
# ExecutionContext 起動用ファクトリを登録する。
#
# @param manager マネージャオブジェクト
#
# @else
#
# @endif
def MultilayerCompositeECInit(manager):
    OpenRTM_aist.ExecutionContextFactory.instance().addFactory("MultilayerCompositeEC",
                                                               OpenRTM_aist.MultilayerCompositeEC)
    return
