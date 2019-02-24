#!/usr/bin/env python
# -*- coding: euc-jp -*-

##
# @file ROSMessageInfo.py
# @brief ROS Message Info class
# @date $Date$
# @author Nobuhiko Miyamoto <n-miyamoto@aist.go.jp>
#
# Copyright (C) 2019
#     Noriaki Ando
#     Robot Innovation Research Center,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#
# $Id$
#

import OpenRTM_aist

##
# @if jp
# @class ROSMessageInfoBase
# @brief ROSメッセージ情報格納オブジェクトの基底クラス
#
# @else
# @class ROSOutPort
# @brief 
#
#
# @endif
class ROSMessageInfoBase(object):
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
  #
  # @param self
  #
  # @endif
  def __init__(self):
    pass
  ##
  # @if jp
  # @brief デストラクタ
  #
  # デストラクタ
  #
  # @param self
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  #
  # @endif
  #
  def __del__(self):
    pass

  ##
  # @if jp
  # @brief メッセージの型名を取得
  #
  # @param self
  # @return 型名
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @return
  #
  # @endif
  #
  def datatype(self):
    return ""

  ##
  # @if jp
  # @brief メッセージのMD5チェックサムを取得
  #
  # @param self
  # @return MD5チェックサム
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @return
  #
  # @endif
  #
  def md5sum(self):
    return ""

  ##
  # @if jp
  # @brief メッセージの詳細説明を取得
  #
  # @param self
  # @return 詳細説明
  #
  # @else
  # @brief 
  #
  #
  # @param self
  # @return
  #
  # @endif
  #
  def message_definition(self):
    return ""
  

##
# @if jp
# @brief メッセージの情報格納オブジェクト生成関数
#
# @param data_class ROSメッセージ型
# @return メッセージの情報格納オブジェクト
#
# @else
# @brief 
#
# @param data_class 
# @return 
#
# @endif
#
def ros_message_info(data_class):
  ##
  # @if jp
  # @class ROSMessageInfo
  # @brief メッセージの情報格納クラス
  #
  #
  # @else
  # @class ROSMessageInfo
  # @brief 
  #
  #
  # @endif
  class ROSMessageInfo(ROSMessageInfoBase):
    """
    """

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
    #
    # @param self
    #
    # @endif
    def __init__(self):
      super(ROSMessageInfo, self).__init__()
      

    ##
    # @if jp
    # @brief デストラクタ
    #
    #
    # @param self
    #
    # @else
    #
    # @brief self
    #
    # @endif
    def __del__(self):
      pass

    ##
    # @if jp
    # @brief メッセージの型名を取得
    #
    # @param self
    # @return 型名
    #
    # @else
    # @brief 
    #
    #
    # @param self
    # @return
    #
    # @endif
    #
    def datatype(self):
      return data_class._type

    ##
    # @if jp
    # @brief メッセージのMD5チェックサムを取得
    #
    # @param self
    # @return MD5チェックサム
    #
    # @else
    # @brief 
    #
    #
    # @param self
    # @return
    #
    # @endif
    #
    def md5sum(self):
      return data_class._md5sum

    ##
    # @if jp
    # @brief メッセージのMD5チェックサムを取得
    #
    # @param self
    # @return MD5チェックサム
    #
    # @else
    # @brief 
    #
    #
    # @param self
    # @return
    #
    # @endif
    #
    def message_definition(self):
      return data_class._full_text
  return ROSMessageInfo



rosmessageinfofactory = None


##
# @if jp
# @class ROSMessageInfoFactory
# @brief ROSメッセージ情報格納オブジェクト生成ファクトリ
#
# @else
# @class ROSMessageInfoFactory
# @brief 
#
#
# @endif
class ROSMessageInfoFactory(OpenRTM_aist.Factory,ROSMessageInfoBase):
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
  #
  # @param self
  #
  # @endif
  def __init__(self):
    OpenRTM_aist.Factory.__init__(self)

  ##
  # @if jp
  # @brief デストラクタ
  #
  # デストラクタ
  #
  # @param self
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  #
  # @endif
  #
  def __del__(self):
    pass

  ##
  # @if jp
  # @brief インスタンス取得
  #
  #
  # @return インスタンス
  #
  # @else
  # @brief 
  #
  #
  # @return
  #
  # @endif
  #
  def instance():
    global rosmessageinfofactory

    if rosmessageinfofactory is None:
      rosmessageinfofactory = ROSMessageInfoFactory()

    return rosmessageinfofactory

  instance = staticmethod(instance)

