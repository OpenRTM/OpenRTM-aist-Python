#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# @file ROS2MessageInfo.py
# @brief ROS2 Message Info class
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
# @class ROS2MessageInfoBase
# @brief ROS2メッセージ情報格納オブジェクトの基底クラス
# ROS2データ型名、IDLファイルパスを登録する
#
# @else
# @class ROS2OutPort
# @brief 
#
#
# @endif
class ROS2MessageInfoBase(object):
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
  # @brief データの型名を取得
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
    return None



  

##
# @if jp
# @brief メッセージの情報格納オブジェクト生成関数
#
# @param data_class ROS2データ型
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
def ros2_message_info(datatype):
  ##
  # @if jp
  # @class ROS2MessageInfo
  # @brief メッセージの情報格納クラス
  #
  #
  # @else
  # @class ROS2MessageInfo
  # @brief 
  #
  #
  # @endif
  class ROS2MessageInfo(ROS2MessageInfoBase):
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
      super(ROS2MessageInfo, self).__init__()
      

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
      return datatype


  return ROS2MessageInfo



ros2messageinfofactory = None


##
# @if jp
# @class ROS2MessageInfoFactory
# @brief ROS2メッセージ情報格納オブジェクト生成ファクトリ
#
# @else
# @class ROS2MessageInfoFactory
# @brief 
#
#
# @endif
class ROS2MessageInfoFactory(OpenRTM_aist.Factory,ROS2MessageInfoBase):
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
    global ros2messageinfofactory

    if ros2messageinfofactory is None:
      ros2messageinfofactory = ROS2MessageInfoFactory()

    return ros2messageinfofactory

  instance = staticmethod(instance)

