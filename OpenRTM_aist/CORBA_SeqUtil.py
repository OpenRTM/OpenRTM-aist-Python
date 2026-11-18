#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
#  @file CORBA_SeqUtil.py
#  @brief CORBA sequence utility template functions
#  @date $Date: 2007/09/03 $
#  @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
#  Copyright (C) 2006-2008
#      Task-intelligence Research Group,
#      Intelligent Systems Research Institute,
#      National Institute of
#          Advanced Industrial Science and Technology (AIST), Japan
#      All rights reserved.

import typing as _typing

import OpenRTM_aist


_Element = _typing.TypeVar("_Element")
_Function = _typing.TypeVar("_Function", bound=_typing.Callable)

##
# @if jp
#
# @brief CORBA sequence に対して functor を適用する
#
# CORBA sequence 全ての要素に対して、与えられた functor を適用する。
# functor は void functor(CORBA sequence の要素) の形式をとる必要がある。
#
# @param seq Functor を適用する CORBA sequence
# @param f CORBA sequence の要素を処理する Functor
#
# @return 全ての要素を処理した Functor
#
# @since 0.4.0
#
# @else
#
# @brief Apply the functor to all CORBA sequence elements
#
# Apply the given functor to the given CORBA sequence.
# functor should be void functor(CORBA sequence element).
#
# @param seq CORBA sequence to be applied the functor
# @param functor A functor to process CORBA sequence elements
#
# @return Functor that processed all CORBA sequence elements
#
# @endif


def for_each(seq: _typing.Iterable[_Element], f: _Function) -> _Function:
    for s in seq:
        f(s)
    return f


##
# @if jp
# @brief CORBA sequence の中から functor に適合する要素のインデックスを返す
#
# CORBA sequence 全ての要素に対して、与えられた functor を適用し、
# functor が true を返すようそのインデックスを返す。
# functor は bool functor(const CORBA sequence の要素) の形式をとり、
# 適合する要素に対して true を返す必要がある。
#
# @param seq Functor を適用する CORBA sequence
# @param f CORBA sequence から要素を見つける Functor
#
# @return Functor に適合する要素のインデックス。見つからないときは -1 を返す。
#
# @else
#
# @brief Return the index of CORBA sequence element that functor matches
#
# This operation applies the given functor to the given CORBA sequence,
# and returns the index of the sequence element that the functor matches.
# The functor should be bool functor(const CORBA sequence element) type,
# and it would return true, if the element matched the functor.
#
# @param seq CORBA sequence to be applied the functor
# @param functor A functor to process CORBA sequence elements
#
# @return The index of the element that functor matches.
#          If no element found, it would return -1.
#
# @endif
def find(seq: _typing.Iterable[_Element], f: _typing.Callable[[_Element], object]) -> int:
    for i, s in enumerate(seq):
        if f(s):
            return i
    return -1


##
# @if jp
# @brief CORBA sequence の最後に要素を追加する
#
# CORBA sequence の最後に与えられた要素を追加する。
# CORBA sequence の長さは自動的に拡張される。
#
# @param seq 要素を追加する CORBA sequence
# @param elem 追加する要素
#
# @else
#
# @brief Push the new element back to the CORBA sequence
#
# Add the given element to the last of CORBA sequence.
# The length of the CORBA sequence will be expanded automatically.
#
# @param seq CORBA sequence to be added a new element
# @param elem The new element to be added to the CORBA sequence
#
# @endif
def push_back(seq: _typing.MutableSequence[_Element], elem: _Element) -> None:
    seq.append(elem)


##
# @if jp
# @brief CORBA sequence をマージする
#
# 与えられた CORBA sequence をマージする。
#
# @param seq1 マージされる CORBA sequence
# @param seq2 マージされる CORBA sequence
#
# @else
#
# @endif
def push_back_list(seq1: _typing.MutableSequence[_Element], seq2: _typing.Iterable[_Element]) -> None:
    for elem in seq2:
        seq1.append(elem)


##
# @if jp
# @brief CORBA sequence に要素を挿入する
#
# CORBA sequence の index の位置に要素を加える。
# index が 与えられた　CORBA sequence の最大の index より大きい場合
# 最後の要素として加えられる。
# CORBA sequence の長さは自動的に拡張される。
#
# @param seq 要素を追加する CORBA sequence
# @param elem 追加する要素
# @param index 要素を追加する位置
#
# @else
#
# @brief Insert the element to the CORBA sequence
#
# Insert a new element in the given position to the CORBA sequence.
# If the given index is greater than the length of the sequence,
# the given element is pushed back to the last of the sequence.
# The length of the CORBA sequence will be expanded automatically.
#
# @param seq The CORBA sequence to be inserted a new element
# @param elem The new element to be inserted the sequence
# @param index The inserting position
#
# @endif
def insert(seq: _typing.MutableSequence[_Element], elem: _Element, index: int) -> None:
    len_ = len(seq)
    if index > len_:
        seq.append(elem)
        return
    seq.insert(index, elem)


##
# @if jp
# @brief CORBA sequence の先頭要素を取得する
#
# CORBA sequence の先頭要素を取得する。
# seq[0] と同じ。
#
# @param seq 要素を取得する CORBA sequence
#
# @return 取得した要素
#
# @else
#
# @brief Get the front element of the CORBA sequence
#
# This operation returns seq[0].
#
# @param seq The CORBA sequence to be get the element
#
# @endif
def front(seq: _typing.Sequence[_Element]) -> _Element:
    return seq[0]


##
# @if jp
# @brief CORBA sequence の末尾要素を取得する
#
# CORBA sequence の末尾要素を取得する。
# seq[seq.length() - 1] と同じ。
#
# @param seq 要素を取得する CORBA sequence
#
# @return 取得した要素
#
# @else
#
# @brief Get the last element of the CORBA sequence
#
# This operation returns seq[seq.length() - 1].
#
# @param seq The CORBA sequence to be get the element
#
# @endif
def back(seq: _typing.Sequence[_Element]) -> _Element:
    if seq:
        return seq[-1]


##
# @if jp
# @brief CORBA sequence の指定された位置の要素を削除する
#
# 指定されたインデックスの要素を削除する。
# 削除された要素は詰められ、sequence の長さは1減る。
#
# @param seq 要素を削除する CORBA sequence
# @param index 削除する要素のインデックス
#
# @else
#
# @brief Erase the element of the specified index
#
# This operation removes the element of the given index.
# The other elements are closed up around the hole.
#
# @param seq The CORBA sequence to be get the element
# @param index The index of the element to be removed
#
# @endif
def erase(seq: _typing.MutableSequence[_Element], index: int) -> None:
    if index > len(seq):
        return

    del seq[index]

##
# @if jp
#
# @brief シーケンスの要素を述語にしたがって削除する
#
# このオペレーションは述語として与えられた関数オブジェクトの
# 条件が真のとき、そのシーケンスの要素を削除する。
#
# @param seq 要素検索対象の CORBA sequence
# @param f 削除するシーケンスを決定する術語
#
# @else
#
# @endif


def erase_if(seq: _typing.MutableSequence[_Element], f: _typing.Callable[[_Element], object]) -> None:
    index = find(seq, f)
    if index < 0:
        return
    del seq[index]


##
# @if jp
# @brief CORBA sequence の全要素を削除
#
# CORBA sequence の全要素を削除する。
# seq.length(0) と同じ。
#
# @else
#
# @brief Erase all the elements of the CORBA sequence
#
# same as seq.length(0).
#
# @endif
def clear(seq: _typing.MutableSequence[_Element]) -> None:
    del seq[0:]


# coil::vstring refToVstring(const CorbaRefSequence& objlist)
def refToVstring(objlist: list):
    iorlist = []
    orb = OpenRTM_aist.Manager.instance().getORB()

    for obj in objlist:
        iorlist.append(orb.object_to_string(obj))

    return iorlist
