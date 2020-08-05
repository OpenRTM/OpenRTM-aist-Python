#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @file Throughput_py.py
 @brief Throughput sample
 @date $Date$

 @author 宮本 信彦 n-miyamoto@aist.go.jp
 産業技術総合研究所 ロボットイノベーション研究センター
 ロボットソフトウェアプラットフォーム研究チーム

 LGPL

"""

from __future__ import print_function
import sys
import time
sys.path.append(".")

# Import RTM module
import RTC
import OpenRTM_aist

import math


# Import Service implementation class
# <rtc-template block="service_impl">

# </rtc-template>

# Import Service stub modules
# <rtc-template block="consumer_import">
# </rtc-template>


# This module's spesification
# <rtc-template block="module_spec">
throughput_py_spec = ["implementation_id", "Throughput_py", 
		 "type_name",         "Throughput_py", 
		 "description",       "Throughput sample", 
		 "version",           "1.0.0", 
		 "vendor",            "AIST", 
		 "category",          "example", 
		 "activity_type",     "STATIC", 
		 "max_instance",      "1", 
		 "language",          "Python", 
		 "lang_type",         "SCRIPT",
		 "conf.default.datatype", "double",
		 "conf.default.outputfile", "test.dat",
		 "conf.default.increment", "100",
		 "conf.default.sleep_time", "0.1",
		 "conf.default.mode", "logincr",
		 "conf.default.maxsize", "1000000",
		 "conf.default.maxsend", "1000",
		 "conf.default.maxsample", "100",
		 "conf.default.filesuffix", "-test",

		 "conf.__widget__.datatype", "radio",
		 "conf.__widget__.outputfile", "text",
		 "conf.__widget__.increment", "text",
		 "conf.__widget__.sleep_time", "text",
		 "conf.__widget__.mode", "radio",
		 "conf.__widget__.maxsize", "text",
		 "conf.__widget__.maxsend", "text",
		 "conf.__widget__.maxsample", "text",
		 "conf.__widget__.filesuffix", "text",
		 "conf.__constraints__.datatype", "(octet,short,long,float,double)",
		 "conf.__constraints__.mode", "(logincr,incr,const)",

         "conf.__type__.datatype", "string",
         "conf.__type__.outputfile", "string",
         "conf.__type__.increment", "long",
         "conf.__type__.sleep_time", "double",
         "conf.__type__.mode", "string",
         "conf.__type__.maxsize", "long",
         "conf.__type__.maxsend", "long",
         "conf.__type__.maxsample", "long",
         "conf.__type__.filesuffix", "string",

		 ""]
# </rtc-template>

class DataListener(OpenRTM_aist.ConnectorDataListenerT):
  def __init__(self, comp, data):
    self._comp = comp
    self._data = data

  def __del__(self):
    pass

  def __call__(self, info, cdrdata):
    data = OpenRTM_aist.ConnectorDataListenerT.__call__(self, info, cdrdata, self._data)
    self._comp.receiveData(data.tm, len(data.data))



class ConnListener(OpenRTM_aist.ConnectorListener):
  def __init__(self, comp):
    self._comp = comp

  def __del__(self):
    print("dtor of ", self._name)

  def __call__(self, info):
    print("------------------------------")
    print("Profile::name:       ", info.name)
    print("Profile::id:         ", info.id)
    print("Profile::properties: ")
    print(info.properties)
    print("------------------------------")
    self._comp.setConnectorProfile(info)


##
# @class Throughput_py
# @brief Throughput sample
# 
# データポートのスループットを計測するコンポーネント。interface_type,
#	subscription_type 等 ConnectorProfile パラメータやデータサイズ、サン
#	プル数などを変更して、その際の転送時間（最大、最小、平均、標準偏差）
#	およびスループットを測定してファイルに記録することができる。
#	基本的には、以下の(a)や(b)のような接続形態で使用する。
#	<pre>
#	+-----------+
#	|  ______   |    ______     ______
#	+->|_____|>-+   >|_____|>-->|_____|>
#	(a)                 (b)
#	</pre>
#	同一コンポーネント内では(a)、同一プロセス内、同一ノード内のスループッ
#	トは (a)または(b)、異なるノード間のスループットを計測する際は (b)の
#	接続形態で計測する。計測は以下の手順で行う。
#	-# コンポーネントを起動する
#	-# コンフィグレーションパラメータを設定する
#	-# 必要なコネクタプロファイルを設定してポートを接続する
#	-# コンポーネントをアクティベートする
#	計測結果はデータを受け取ったコンポーネントがファイルに記録する。
# 
# 
class Throughput_py(OpenRTM_aist.DataFlowComponentBase):
	
	##
	# @brief constructor
	# @param manager Maneger Object
	# 
	def __init__(self, manager):
		OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)
		self._size = 0



		


		# initialize of configuration-data.
		# <rtc-template block="init_conf_param">
		"""
		データ型
		 - Name: datatype datatype
		 - DefaultValue: double
		 - Constraint: (octet,short,long,float,double)
		"""
		self._datatype = ['double']
		"""
		出力ファイル名。onActivated時、またはデータ受信時にファイルがオープンされるの
		で、それ以降にパラメータを設定した場合は反映されない。
		 - Name: outputfile outputfile
		 - DefaultValue: test.dat
		"""
		self._outputfile = ['test.dat']
		"""
		データ増分。mode が incr の場合のデータ増分を byte で指定する。
		 - Name: increment increment
		 - DefaultValue: 100
		 - Unit: byte
		"""
		self._increment = [100]
		"""
		onExecute内で待機する時間
		 - Name: sleep_time sleep_time
		 - DefaultValue: 0.1
		 - Unit: s
		"""
		self._sleep_time = [0.1]
		"""
		- mode: 計測モード名。logincr, incr, const から選択可能。
		- logincr: logスケールでデータ数を増加させ計測。実際には、1, 2, 5,
		10, .. といった間隔でデータ数を増加させ、logスケールでプ
		ロットした際にほぼ等間隔となるように計測する。
		- incr: incrementパラメータで指定されたバイト数で、一定間隔でデータ
		数を増加させる。
		- const: データは増加させず一定サイズでスループットを計測する。
		 - Name: mode mode
		 - DefaultValue: logincr
		 - Constraint: (logincr,incr,const)
		"""
		self._mode = ['logincr']
		"""
		最大データ個数を指定する。送信するシーケンスデータのサイズを指定する。実際の
		データサイズは、この個数に1データ当たりのバイト数をかけたものとなる。
		 - Name: maxsize maxsize
		 - DefaultValue: 1000000
		"""
		self._maxsize = [1000000]
		"""
		最大送信数。データ送信回数の最大値を指定する。モードがlogincr, incr
		の場合、データサイズ毎に maxsend 回数データを送信する。
		 - Name: maxsend maxsend
		 - DefaultValue: 1000
		"""
		self._maxsend = [1000]
		"""
		最大サンプリング数。データを受信し、統計情報を計算する際の最大サンプル数を指
		定する。データ送信側の送信数がサンプル数より少ない場合、受信したサンプル数で
		統計情報を計算する。データ送信側の送信数がサンプル数より多い場合、古い情報は
		破棄され、最新の maxsample 個の計測データから統計情報を計算する。
		 - Name: maxsample maxsample
		 - DefaultValue: 100
		"""
		self._maxsample = [100]
		"""
		ファイル識別子
		 - Name: filesuffix filesuffix
		 - DefaultValue: -test
		"""
		self._filesuffix = ['-test']
		
		# </rtc-template>
		self._datasize = 0
		self._fs = None
		self._record = []
		self._sendcount = 0
		self._logmulcnt = 0
		self._varsize = 0


		 
	##
	#
	# The initialize action (on CREATED->ALIVE transition)
	# formaer rtc_init_entry() 
	# 
	# @return RTC::ReturnCode_t
	# 
	#
	def onInitialize(self):
		# Bind variables and configuration variable
		self.bindParameter("datatype", self._datatype, "double")
		self.bindParameter("outputfile", self._outputfile, "test.dat")
		self.bindParameter("increment", self._increment, "100")
		self.bindParameter("sleep_time", self._sleep_time, "0.1")
		self.bindParameter("mode", self._mode, "logincr")
		self.bindParameter("maxsize", self._maxsize, "1000000")
		self.bindParameter("maxsend", self._maxsend, "1000")
		self.bindParameter("maxsample", self._maxsample, "100")
		self.bindParameter("filesuffix", self._filesuffix, "-test")
		
		# Set InPort buffers
		
		# Set OutPort buffers
		
		# Set service provider to Ports
		
		# Set service consumers to Ports
		
		# Set CORBA Service Ports
		#self.getConfigService().update()
		#print self._datatype
		self._data_type = OpenRTM_aist.normalize(self._datatype)
		if self._data_type == "octet":
			self._d_in = RTC.TimedOctetSeq(RTC.Time(0,0), [])	
			self._d_out = RTC.TimedOctetSeq(RTC.Time(0,0), [])
			self._varsize = 1
		elif self._data_type == "short":
			self._d_in = RTC.TimedShortSeq(RTC.Time(0,0), [])	
			self._d_out = RTC.TimedShortSeq(RTC.Time(0,0), [])
			self._varsize = 2
		elif self._data_type == "long":
			self._d_in = RTC.TimedLongSeq(RTC.Time(0,0), [])	
			self._d_out = RTC.TimedLongSeq(RTC.Time(0,0), [])
			self._varsize = 4
		elif self._data_type == "float":
			self._d_in = RTC.TimedFloatSeq(RTC.Time(0,0), [])	
			self._d_out = RTC.TimedFloatSeq(RTC.Time(0,0), [])
			self._varsize = 4
		elif self._data_type == "double":
			self._d_in = RTC.TimedDoubleSeq(RTC.Time(0,0), [])	
			self._d_out = RTC.TimedDoubleSeq(RTC.Time(0,0), [])
			self._varsize = 8
		else:
			return RTC.RTC_ERROR
			
			
		self._inIn = OpenRTM_aist.InPort("in", self._d_in)
		self.addInPort("in",self._inIn)
		self._outOut = OpenRTM_aist.OutPort("out", self._d_out)
		self.addOutPort("out",self._outOut)
		self._inIn.addConnectorDataListener(OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE,
											DataListener(self, self._d_in))
		self._inIn.addConnectorListener(OpenRTM_aist.ConnectorListenerType.ON_CONNECT,
										  ConnListener(self))

		return RTC.RTC_OK

	def receiveData(self, tm, seq_length):
		received_time = OpenRTM_aist.Time().getTime()
		if self._size == 0:
			self._size = seq_length
		record_num = len(self._record)
		record_ptr = record_num
		if self._size != seq_length and record_num != 0:
			
			max_latency = 0.0
			min_latency = 0.0
			mean_latency = 0.0
			variance = 0.0
			stddev = 0.0
			throughput = 0.0
			sum = 0.0
			sq_sum = 0.0
			record_len = len(self._record)
			
			#print record_len
			
			
			for d in self._record:
				tmp = d
				sum += tmp
				sq_sum += tmp * tmp
				if tmp > max_latency:
					max_latency = tmp
				elif tmp < min_latency:
					min_latency = tmp
			
			mean_latency = sum / record_len
			variance = (sq_sum / record_len) - (mean_latency * mean_latency)
			stddev = math.sqrt(variance)
			throughput = ((((self._size * self._varsize) + 8) * 8) / mean_latency) / (1024 * 1024)
			
			self._fs.write(str(self._size)+"\t")
			self._fs.write(str(min_latency)+"\t"+str(max_latency)+"\t")
			self._fs.write(str(mean_latency)+"\t"+str(stddev)+"\t")
			self._fs.write(str(throughput)+"\n")
			self._record = []
			
			if seq_length < self._size:
				async_ = OpenRTM_aist.Async_tInvoker(self, Throughput_py.exit)
				async_.invoke()
				return
		send_time = OpenRTM_aist.TimeValue(tm.sec, tm.nsec/1000)
		if record_ptr == self._maxsample[0]:
			self._record.pop(0)
		self._record.append((received_time-send_time).toDouble())
		self._size = seq_length
			
		
	def setConnectorProfile(self, info):
		outputfile = self._datatype[0] + "-" + info.properties.getProperty("interface_type") + self._filesuffix[0] + ".dat"
		if self._fs is None:
			try:
				self._fs = open(outputfile, 'w')
			except:
				print("File open failed!!")
				return
		self._fs.write("# Profile::name:      " + info.name + "\n")
		self._fs.write("# Profile::id:        " + info.id + "\n")
		self._fs.write("# Profile::properties: " + "\n")
		ss = str(info.properties)
		propv = ss.split("\n")
		for prop in propv:
			self._fs.write("# " + prop + "\n")
		self._fs.write("size[byte]\tmin[s]\tmax[s]\tmean[s]\tstddev[s]\tthroughpiut[Mbps]" + "\n")
		
		#print outputfile
		#print "setConnectorProfile"
	def setDataSize(self, size):
		self._d_out.data = [0]*size
		#print "setDataSize"
	def getDataSize(self):
		#print "getDataSize"
		return len(self._d_out.data)
	def writeData(self):
		OpenRTM_aist.setTimestamp(self._d_out)
		self._outOut.write()
		#print "writeData"
	def getInPortConnectorSize(self):
		return len(self._inIn.get_connector_profiles())

	#	##
	#	# 
	#	# The finalize action (on ALIVE->END transition)
	#	# formaer rtc_exiting_entry()
	#	# 
	#	# @return RTC::ReturnCode_t
	#
	#	# 
	#def onFinalize(self):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The startup action when ExecutionContext startup
	#	# former rtc_starting_entry()
	#	# 
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onStartup(self, ec_id):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The shutdown action when ExecutionContext stop
	#	# former rtc_stopping_entry()
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onShutdown(self, ec_id):
	#
	#	return RTC.RTC_OK
	
		##
		#
		# The activated action (Active state entry action)
		# former rtc_active_entry()
		#
		# @param ec_id target ExecutionContext Id
		# 
		# @return RTC::ReturnCode_t
		#
		#
	def onActivated(self, ec_id):
		self._datasize = 1
		self.setDataSize(int(self._datasize))
		self._sendcount = 0
		self._logmulcnt = 0
		return RTC.RTC_OK
	
		##
		#
		# The deactivated action (Active state exit action)
		# former rtc_active_exit()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onDeactivated(self, ec_id):
		if self._fs:
			self._fs.close()
			self._fs = None
		self._datasize = 1
		self.setDataSize(self._datasize)
		self._sendcount = 0
		self._logmulcnt = 0
		
		if self.getInPortConnectorSize() == 0:
			async_ = OpenRTM_aist.Async_tInvoker(self, Throughput_py.exit)
			async_.invoke()
		return RTC.RTC_OK
	
		##
		#
		# The execution action that is invoked periodically
		# former rtc_active_do()
		#
		# @param ec_id target ExecutionContext Id
		#
		# @return RTC::ReturnCode_t
		#
		#
	def onExecute(self, ec_id):
		logmul = [2.0, 2.5, 2.0]
		if self.getDataSize() != self._datasize:
			self.setDataSize(int(self._datasize))
		self.writeData()
		self._sendcount += 1
		if self._sendcount%(self._maxsample[0]+1) != 0:
			return RTC.RTC_OK
		
		if self._mode[0] == "logincr":
			self._datasize *= logmul[self._logmulcnt%3]
			self._logmulcnt += 1
			#print self._datasize, self._logmulcnt
		elif self._mode[0] == "incr":
			self._datasize += self._increment[0]
		else:
			if self._sendcount > self._maxsend[0]:
				self.deactivate(ec_id)
				return RTC.RTC_OK
		time.sleep(self._sleep_time[0])
		if self._datasize > self._maxsize[0]:
			print("Exiting")
			self.setDataSize(1)
			self.writeData()
			self.deactivate(ec_id)
			
			
		return RTC.RTC_OK
	
	#	##
	#	#
	#	# The aborting action when main logic error occurred.
	#	# former rtc_aborting_entry()
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onAborting(self, ec_id):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The error action in ERROR state
	#	# former rtc_error_do()
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onError(self, ec_id):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The reset action that is invoked resetting
	#	# This is same but different the former rtc_init_entry()
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onReset(self, ec_id):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The state update action that is invoked after onExecute() action
	#	# no corresponding operation exists in OpenRTm-aist-0.2.0
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#

	#	#
	#def onStateUpdate(self, ec_id):
	#
	#	return RTC.RTC_OK
	
	#	##
	#	#
	#	# The action that is invoked when execution context's rate is changed
	#	# no corresponding operation exists in OpenRTm-aist-0.2.0
	#	#
	#	# @param ec_id target ExecutionContext Id
	#	#
	#	# @return RTC::ReturnCode_t
	#	#
	#	#
	#def onRateChanged(self, ec_id):
	#
	#	return RTC.RTC_OK
	



def Throughput_pyInit(manager):
    profile = OpenRTM_aist.Properties(defaults_str=throughput_py_spec)
    manager.registerFactory(profile,
                            Throughput_py,
                            OpenRTM_aist.Delete)

def MyModuleInit(manager):
    Throughput_pyInit(manager)

    # Create a component
    comp = manager.createComponent("Throughput_py")

def main():
	mgr = OpenRTM_aist.Manager.init(sys.argv)
	mgr.setModuleInitProc(MyModuleInit)
	mgr.activateManager()
	mgr.runManager()

if __name__ == "__main__":
	main()

