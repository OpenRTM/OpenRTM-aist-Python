#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
# @file SharedMemory.py
# @brief SharedMemory class
# @date $Date$
# @author Nobuhiko Miyamoto
#


import mmap, os
import ctypes
from omniORB import cdrMarshal
from omniORB import cdrUnmarshal
from omniORB import CORBA
import OpenRTM_aist
import OpenRTM__POA
import OpenRTM




##
# @if jp
#
# @class SharedMemory
#
# @brief SharedMemory ���饹
#
# ��ͭ�������饹
# CORBA�ˤ���̿��ˤ�ꡢmmap�ν��������λ�ʤɤ���⡼�Ȥ����Ǥ���
#
#
# @else
# @class SharedMemory
#
# @brief SharedMemory class
#
#
#
# @endif
#
class SharedMemory(OpenRTM__POA.PortSharedMemory):
  default_size = 8
  default_memory_size = 2097152
  

  ##
  # @if jp
  # @brief ���󥹥ȥ饯��
  #
  # ���󥹥ȥ饯��
  #
  # @param self
  #
  # @else
  # @brief Constructor
  #
  # Constructor
  #
  # @param self
  #
  # @endif
  #
  def __init__(self):
    self._rtcout = OpenRTM_aist.Manager.instance().getLogbuf("SharedMemory")
    self._shmem = None
    self._smInterface = OpenRTM.PortSharedMemory._nil
    self._shm_address = ""
    self._memory_size = SharedMemory.default_memory_size
    self._endian = True
    if os.name == "nt":
      pass
    else:
      #from ctypes.util import find_library
      #librt = find_library("librt")
      #if librt is None:
      #  raise
      #self.rt = ctypes.CDLL(librt)
      try:
        self.rt = ctypes.CDLL('librt.so')
      except:
        self.rt = ctypes.CDLL('librt.so.1')
      self.rt.shm_open.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int]
      self.rt.shm_open.restype = ctypes.c_int
      self.rt.ftruncate.argtypes = [ctypes.c_int, ctypes.c_int]
      self.rt.ftruncate.restype = ctypes.c_int
      self.rt.close.argtypes = [ctypes.c_int]
      self.rt.close.restype = ctypes.c_int
      self.rt.shm_unlink.argtypes = [ctypes.c_char_p]
      self.rt.shm_unlink.restype = ctypes.c_int

      self.fd = -1
    return



  ##
  # @if jp
  # @brief �ǥ��ȥ饯��
  #
  # �ǥ��ȥ饯��
  #
  # @param self
  #
  # @else
  # @brief Destructor
  #
  # Destructor
  #
  # @param self
  # @endif
  #
  def __del__(self):
    self._rtcout.RTC_PARANOID("~SharedMemory()")
    return

  
  ##
  # @if jp
  # @brief ʸ����ǻ��ꤷ���ǡ�������������ͤ��Ѵ�����
  # 1M �� 1048576
  # 1k �� 1024
  # 100 �� 100
  #
  #
  # @param self
  # @param size_str �ǡ���������(ʸ����)
  # @return �ǡ���������(����)
  #
  # @else
  # @brief 
  #
  # @param self
  # @param size_str 
  # @return 
  #
  # @endif
  #
  # int string_to_MemorySize(string size_str);
  def string_to_MemorySize(self, size_str):
    memory_size = SharedMemory.default_memory_size
    if size_str:
      if size_str[-1] == "M":
        memory_size = 1048576 * int(size_str[0:-1])
      elif size_str[-1] == "k":
        memory_size = 1024 * int(size_str[0:-1])
      else:
        memory_size = int(size_str)
    return memory_size



  ##
  # @if jp
  # @brief ��ͭ����ν����
  # windows�Ǥϥڡ����󥰥ե��������ΰ����ݤ���
  # Linux�Ǥ�/dev/shm�ʲ��˥ե�������������
  # ���������ե���������Ƥ��ۥ��ɥ쥹�˥ޥåԥ󥰤���
  # 
  #
  #
  # @param self
  # @param memory_size ��ͭ����Υ�����
  # @param shm_address ����̾
  #
  # @else
  # @brief 
  #
  # @param memory_size 
  # @param shm_address
  #
  # @endif
  #
  # void create_memory(int memory_size, string shm_address);
  def create_memory(self, memory_size, shm_address):
    
      
    if self._shmem is None:
      self._rtcout.RTC_TRACE("create():memory_size="+str(memory_size)+",shm_address="+str(shm_address))
      self._memory_size = memory_size
      self._shm_address = shm_address

      if os.name == "nt":
        self._shmem = mmap.mmap(0, self._memory_size, self._shm_address, mmap.ACCESS_WRITE)
      else:
        O_RDWR = 2
        O_CREAT = 64

        S_IRUSR = 256
        S_IWUSR = 128
        S_IRGRP = 32
        S_IWGRP = 16
        S_IROTH = 4

        self.fd = self.rt.shm_open(self._shm_address,O_RDWR | O_CREAT,S_IRUSR|S_IWUSR|S_IRGRP|S_IWGRP|S_IROTH)
        if self.fd < 0:
          return
        self.rt.ftruncate(self.fd, self._memory_size)
        self._shmem = mmap.mmap(self.fd, self._memory_size, mmap.MAP_SHARED)
        self.rt.close( self.fd )

      
      if not CORBA.is_nil(self._smInterface):
          self._smInterface.open_memory(self._memory_size, self._shm_address)



  ##
  # @if jp
  # @brief ��ͭ����Υޥåԥ󥰤�Ԥ�
  # 
  #
  #
  # @param self
  # @param memory_size ��ͭ����Υ�����
  # @parama shm_address ����̾
  #
  # @else
  # @brief 
  #
  # @param memory_size 
  # @parama shm_address
  #
  # @endif
  #
  # void open_memory(int memory_size, string shm_address);
  def open_memory(self, memory_size, shm_address):
    self._rtcout.RTC_TRACE("open():memory_size="+str(memory_size)+",shm_address="+str(shm_address))
    self._memory_size = memory_size
    self._shm_address = shm_address
    if self._shmem is None:
      if os.name == "nt":
        self._shmem = mmap.mmap(0, self._memory_size, self._shm_address, mmap.ACCESS_WRITE)
      else:
        O_RDWR = 2
        self.fd = self.rt.shm_open(self._shm_address,O_RDWR,0)
        if self.fd < 0:
          return
        self.rt.ftruncate(self.fd, self._memory_size)
        self._shmem = mmap.mmap(self.fd, self._memory_size, mmap.MAP_SHARED)
        self.rt.close( self.fd )
    


  ##
  # @if jp
  # @brief �ޥåԥ󥰤�����ͭ����򥢥�ޥåפ���
  # 
  #
  #
  # @param self
  # @param unlink Linux��/dev/shm�ʲ��˺��������ե���������������True�ˤ���
  #
  # @else
  # @brief 
  #
  # @param self
  # @param unlink
  #
  # @endif
  #
  # void close_memory(boolean unlink);
  def close_memory(self, unlink=False):
    self._rtcout.RTC_TRACE("open()")
    if self._shmem:
      self._shmem.close()
      if os.name == "nt":
        pass
      else:
        if unlink:
           self.rt.shm_unlink(self._shm_address)
      self._shmem = None

      try:
        if not CORBA.is_nil(self._smInterface) and self._smInterface._non_existent():
          self._smInterface.close_memory(False)
      except:
        pass
  
    


  
  ##
  # @if jp
  # @brief �ǡ�����񤭹���
  # ��Ƭ8byte�˥ǡ�����������񤭹��ߡ����θ��˥ǡ�����񤭹���
  # ���ꤷ���ǡ�������������ͭ����Υ���������ä���硢��ͭ����ν������Ԥ�
  # 
  #
  #
  # @param self
  # @param data �񤭹���ǡ���
  #
  # @else
  # @brief
  #
  # @param self
  # @param data 
  #
  #
  # @endif
  #
  # void write(const cdrMemoryStream& data);
  def write(self, data):
    self._rtcout.RTC_TRACE("write()")
    
    if self._shmem:
      data_size = len(data)

      
      if data_size + SharedMemory.default_size > self._memory_size:
        self._memory_size = data_size + SharedMemory.default_size

        if not CORBA.is_nil(self._smInterface):
          self._smInterface.close_memory(False)


        self.close_memory(True)
        self.create_memory(self._memory_size, self._shm_address)

        
        
      data_size_cdr = cdrMarshal(CORBA.TC_ulonglong, data_size, self._endian)
      
      self._shmem.seek(os.SEEK_SET)
      self._shmem.write(data_size_cdr)
      self._shmem.write(data)


  ##
  # @if jp
  # @brief �ǡ������ɤ߹���
  # 
  #
  #
  # @param self
  # @return �ǡ���
  #
  # @else
  # @brief 
  #
  # @param self
  # @return
  #
  # @endif
  #
  # cdrMemoryStream read(data);
  def read(self):
    self._rtcout.RTC_TRACE("read()")
    if self._shmem:
      
      self._shmem.seek(os.SEEK_SET)
      
      data_size_cdr = self._shmem.read(SharedMemory.default_size)
      data_size = cdrUnmarshal(CORBA.TC_ulonglong, data_size_cdr, self._endian)
      
      
      
      shm_data = self._shmem.read(data_size)
      
      return shm_data
    return ""



  ##
  # @if jp
  # @brief �̿����CORBA���󥿡��ե���������Ͽ����
  # ��Ͽ������ˤ�궦ͭ����ν���������Ȥ��ˡ��̿���Ǥ�ޥåԥ󥰤���ľ�����Ȥ��Ǥ���
  # 
  #
  #
  # @param self
  # @param sm SharedMemory�Υ��֥������ȥ�ե����
  #
  # @else
  # @brief 
  #
  #
  # @endif
  #
  # void setInterface(::OpenRTM::PortSharedMemory_var sm);
  def setInterface(self, sm):
    self._smInterface = sm


  ##
  # @if jp
  # @brief ����ǥ���������ꤹ��
  # 
  #
  #
  # @param self
  # @param endian ����ǥ�����
  #
  # @else
  # @brief 
  #
  # @param self
  # @param endian endian
  #
  # @endif
  #
  # void setEndian(bool endian);
  def setEndian(self, endian):
    self._endian = endian
    if not CORBA.is_nil(self._smInterface):
      self._smInterface.setEndian(self._endian)

  ##
  # @if jp
  # @brief �ǡ������������Τ餻��
  # 
  #
  #
  # @param self
  #
  # @else
  # @brief 
  #
  # @param self
  #
  # @endif
  #
  # PortStatus put();
  def put(self):
    return OpenRTM.UNKNOWN_ERROR

  ##
  # @if jp
  # @brief �ǡ������������׵᤹��
  # 
  #
  #
  # @param self
  #
  # @else
  # @brief 
  #
  # @param self
  #
  # @endif
  #
  # PortStatus get();
  def get(self):
    return OpenRTM.UNKNOWN_ERROR