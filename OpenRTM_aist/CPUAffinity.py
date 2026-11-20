#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file CPUAffinity.py
# @brief
# @date $Date$
# @author Nobuhiko Miyamoto
#


import os
import ctypes


##
# @if jp
# @brief CPUの番号リストを変換
#
# @param cpu_num_list CPUの番号リスト
# @return 数値
#
# @else
# @brief
#
# @param cpu_num_list
# @return
#
# @endif
#
def listToCUPNUM(cpu_num_list: list):
    cpu_num = 0
    try:
        for num in cpu_num_list:
            p = 0x01 << (int(num))
            cpu_num += p
    except ValueError:
        pass
    return cpu_num


##
# @if jp
# @brief プロセスのCPUアフィニティを設定
#
# @param cpu_num_list CPUの番号リスト
# @return 成功でTrue、失敗でFalse
#
# @else
# @brief
#
# @param cpu_num_list
# @return
#
# @endif
#
def setProcessAffinity(cpu_num_list: list) -> bool:
    cpu_num = listToCUPNUM(cpu_num_list)
    if cpu_num == 0:
        return False
    pid = os.getpid()

    if os.name == "nt":

        if cpu_num >= 1 << (ctypes.sizeof(ctypes.c_size_t) * 8):
            return False

        kernel32 = ctypes.windll.kernel32
        kernel32.GetCurrentProcess.argtypes = []
        kernel32.GetCurrentProcess.restype = ctypes.c_void_p
        kernel32.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        kernel32.SetProcessAffinityMask.restype = ctypes.c_int
        kernel32.GetProcessAffinityMask.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_size_t)]
        kernel32.GetProcessAffinityMask.restype = ctypes.c_int

        process = kernel32.GetCurrentProcess()
        if not kernel32.SetProcessAffinityMask(process, cpu_num):
            return False
        process_mask = ctypes.c_size_t()
        system_mask = ctypes.c_size_t()
        if not kernel32.GetProcessAffinityMask(
                process, ctypes.byref(process_mask), ctypes.byref(system_mask)):
            return False
        return process_mask.value == cpu_num

    else:
        from ctypes.util import find_library
        pthread = find_library("pthread")
        if pthread is None:
            return False
        pthread = ctypes.CDLL(pthread)

        mask = ctypes.c_long()
        mask.value = cpu_num
        result = pthread.sched_setaffinity(
            pid, ctypes.sizeof(mask), ctypes.byref(mask))
        if result != 0:
            return False
        mask = ctypes.c_long()
        result = pthread.sched_getaffinity(
            pid, ctypes.sizeof(mask), ctypes.byref(mask))
        if mask.value != cpu_num:
            return False
        else:
            return True


##
# @if jp
# @brief スレッドのCPUアフィニティを設定
#
# @param cpu_num_list CPUの番号リスト
# @return 成功でTrue、失敗でFalse
#
# @else
# @brief
#
# @param cpu_num_list
# @return
#
# @endif
#
def setThreadAffinity(cpu_num_list: list) -> bool:
    cpu_num = listToCUPNUM(cpu_num_list)
    if cpu_num == 0:
        return False

    if os.name == "nt":

        if cpu_num >= 1 << (ctypes.sizeof(ctypes.c_size_t) * 8):
            return False

        kernel32 = ctypes.windll.kernel32
        kernel32.GetCurrentThread.argtypes = []
        kernel32.GetCurrentThread.restype = ctypes.c_void_p
        kernel32.SetThreadAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        kernel32.SetThreadAffinityMask.restype = ctypes.c_size_t

        thread = kernel32.GetCurrentThread()
        # Windows returns the previous mask, or zero on failure.
        return kernel32.SetThreadAffinityMask(thread, cpu_num) != 0

    else:
        from ctypes.util import find_library
        pthread = find_library("pthread")
        if pthread is None:
            return False
        pthread = ctypes.CDLL(pthread)
        libc = find_library("libc")
        libc = ctypes.CDLL(libc)

        mask = ctypes.c_long()
        mask.value = cpu_num
        tid = libc.syscall(186)
        result = pthread.sched_setaffinity(
            tid, ctypes.sizeof(mask), ctypes.byref(mask))
        if result != 0:
            return False
        mask = ctypes.c_long()
        result = pthread.sched_getaffinity(
            tid, ctypes.sizeof(mask), ctypes.byref(mask))
        if mask.value != cpu_num:
            return False
        else:
            return True
