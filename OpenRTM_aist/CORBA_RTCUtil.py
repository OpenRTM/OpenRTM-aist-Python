#!/usr/bin/env python3
# -*- coding: euc-jp -*-

##
#  @file CORBA_RTCUtil.py
#  @brief CORBA RTC utility
#  @date $Date: 2016/01/08 $
#  @author Nobuhiko Miyamoto
# 

import OpenRTM_aist
import OpenRTM_aist.RTObject
from omniORB import CORBA
import RTC


##
# @if jp
#
# @brief ����ݡ��ͥ�ȤΥץ�ѥƥ�����
#
# 
# @param rtc RT����ݡ��ͥ��
# @return ����ݡ��ͥ�ȤΥץ�ѥƥ�
#
# @else
#
# @brief 
# @param rtc
# @return 
#
# @endif
# coil::Properties get_component_profile(const RTC::RTObject_ptr rtc)
def get_component_profile(rtc):
  prop = OpenRTM_aist.Properties()
  if CORBA.is_nil(rtc):
    return prop
  prof = rtc.get_component_profile()
  OpenRTM_aist.NVUtil.copyToProperties(prop, prof.properties)
  return prop




##
# @if jp
#
# @brief ����ݡ��ͥ�ȤΥ��֥������ȥ�ե���󥹤�¸�ߤ��Ƥ��뤫��Ƚ��
#
# 
# @param rtc RT����ݡ��ͥ��
# @return True:��¸��False:��λ�Ѥ�
#
# @else
#
# @brief 
# @param rtc RT����ݡ��ͥ��
# @return 
#
# @endif
def is_existing(rtc):
  try:
    if rtc._non_existent():
      return False
    return True
  except CORBA.SystemException:
    return False


##
# @if jp
#
# @brief RTC���ǥե���Ȥμ¹ԥ���ƥ����Ȥ�alive���֤���Ƚ�ꤹ��
#
# @param rtc RT����ݡ��ͥ��
# @return True:alive����
# 
# @param 
#
# @else
#
# @brief 
# @param 
#
# @endif
def is_alive_in_default_ec(rtc):
  ec = get_actual_ec(rtc)
  if CORBA.is_nil(ec):
    return False
  return rtc.is_alive(ec)


##
# @if jp
#
# @brief RT����ݡ��ͥ�Ȥ˴�Ϣ�դ������¹ԥ���ƥ����Ȥ�����ꤷ��ID�μ¹ԥ���ƥ����Ȥ����
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return �¹ԥ���ƥ����ȤΥ��֥������ȥ�ե����
#
# @else
#
# @brief 
# @param rtc
# @param ec_id
# @return
#
# @endif
# RTC::ExecutionContext_var get_actual_ec(const RTC::RTObject_ptr rtc,RTC::UniqueId ec_id = 0)
def get_actual_ec(rtc, ec_id=0):
  if ec_id < 0:
    return RTC.ExecutionContext._nil
  if CORBA.is_nil(rtc):
    return RTC.ExecutionContext._nil
  if ec_id < OpenRTM_aist.RTObject.ECOTHER_OFFSET:
    eclist = rtc.get_owned_contexts()
    if ec_id >= len(eclist):
      return RTC.ExecutionContext._nil
    
    if CORBA.is_nil(eclist[ec_id]):
      return RTC.ExecutionContext._nil
    return eclist[ec_id]
  elif ec_id >= OpenRTM_aist.RTObject.ECOTHER_OFFSET:
    pec_id = ec_id - OpenRTM_aist.RTObject.ECOTHER_OFFSET
    eclist = rtc.get_participating_contexts()
    if pec_id >= len(eclist):
      return RTC.ExecutionContext._nil
    if CORBA.is_nil(eclist[pec_id]):
      return RTC.ExecutionContext._nil
    return eclist[pec_id]

    


##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥ�����ꤷ���¹ԥ���ƥ����Ȥ�ID��������� 
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec �¹ԥ���ƥ�����
# @return �¹ԥ���ƥ����Ȥ�ID
# ���ꤷ���¹ԥ���ƥ����Ȥ�RT����ݡ��ͥ�Ȥ˴�Ϣ�դ����Ƥ��ʤ��ä�����-1���֤�
#
# @else
#
# @brief 
# @param 
#
# @endif
def get_ec_id(rtc, ec):
  if CORBA.is_nil(rtc):
    return -1
  if CORBA.is_nil(ec):
    return -1
  
  eclist_own = rtc.get_owned_contexts()
  
  count = 0
  for e in eclist_own:
    if not CORBA.is_nil(e):
      if e._is_equivalent(ec):
        return count
    count += 1
  eclist_pec = rtc.get_participating_contexts()
  count = 0
  for e in eclist_pec:
    if not CORBA.is_nil(e):
      if e._is_equivalent(ec):
        return count+OpenRTM_aist.RTObject.ECOTHER_OFFSET
    count += 1
  return -1
  


##
# @if jp
#
# @brief RTC����ꤷ���¹ԥ���ƥ����Ȥǥ����ƥ��١�����󤹤�
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return RTC��EC�Υ��֥������ȥ�ե���󥹤�nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����activate_component�ؿ�������ͤ��֤���RTC_OK�ξ��ϥ����ƥ��١����������
#
# @else
#
# @brief 
# @param rtc
# @param ec_id
# @return 
#
# @endif
# RTC::ReturnCode_t activate(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)
def activate(rtc, ec_id=0):
  if CORBA.is_nil(rtc):
    return RTC.BAD_PARAMETER
  ec = get_actual_ec(rtc, ec_id)
  if CORBA.is_nil(ec):
    return RTC.BAD_PARAMETER
  return ec.activate_component(rtc)
  

##
# @if jp
#
# @brief RTC����ꤷ���¹ԥ���ƥ����Ȥ��󥢥��ƥ��١�����󤹤�
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return RTC��EC�Υ��֥������ȥ�ե���󥹤�nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����deactivate_component�ؿ�������ͤ��֤���RTC_OK�ξ����󥢥��ƥ��١����������
#
# @else
#
# @brief 
# @param rtc
# @param ec_id
# @return 
#
# @endif
# RTC::ReturnCode_t deactivate(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)
def deactivate(rtc, ec_id=0):
  if CORBA.is_nil(rtc):
    return RTC.BAD_PARAMETER
  ec = get_actual_ec(rtc, ec_id)
  if CORBA.is_nil(ec):
    return RTC.BAD_PARAMETER
  return ec.deactivate_component(rtc)

##
# @if jp
#
# @brief RTC����ꤷ���¹ԥ���ƥ����Ȥǥꥻ�åȤ���
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return RTC��EC�Υ��֥������ȥ�ե���󥹤�nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����reset_component�ؿ�������ͤ��֤���RTC_OK�ξ��ϥꥻ�åȤ�����
#
# @else
#
# @brief 
# @param rtc
# @param ec_id
# @return 
#
# @endif
# RTC::ReturnCode_t reset(RTC::RTObject_ptr rtc, RTC::UniqueId ec_id = 0)
def reset(rtc, ec_id=0):
  if CORBA.is_nil(rtc):
    return RTC.BAD_PARAMETER
  ec = get_actual_ec(rtc, ec_id)
  if CORBA.is_nil(ec):
    return RTC.BAD_PARAMETER
  return ec.reset_component(rtc)

##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥλ��ꤷ���¹ԥ���ƥ����ȤǤξ��֤����
#
#
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return 1���ܤ�����ͤȤ���rtc��ec��nil�ξ���False���֤�������ʳ��ξ���True���֤���
# 2���ܤ�����ͤȤ��ƾ��֤��֤���
# 
#
# @else
#
# @brief
# @param rtc
# @param ec_id
# @return 
#
# @endif
def get_state(rtc, ec_id=0):
  if CORBA.is_nil(rtc):
    return False, RTC.CREATED_STATE
  ec = get_actual_ec(rtc, ec_id)
  if CORBA.is_nil(ec):
    return False, RTC.CREATED_STATE
  state = ec.get_component_state(rtc)
  return True, state

##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥλ��ꤷ���¹ԥ���ƥ����Ȥ�INACTIVE���֤��ɤ���Ƚ��
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return INACTIVE���֤λ���True������ʳ���False
# rtc��ec��nil�ξ���False���֤�
#
# @else
#
# @brief 
# @param rtc 
# @param ec_id
# @return 
#
# @endif
def is_in_inactive(rtc, ec_id=0):
  ret, state = get_state(rtc, ec_id)
  if ret:
    if state == RTC.INACTIVE_STATE:
      return True
  return False

##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥλ��ꤷ���¹ԥ���ƥ����Ȥ�ACTIVE���֤��ɤ���Ƚ��
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return ACTIVE���֤λ���True������ʳ���False
# rtc��ec��nil�ξ���False���֤�
#
# @else
#
# @brief 
# @param rtc 
# @param ec_id
# @return 
#
# @endif
def is_in_active(rtc, ec_id=0):
  ret, state = get_state(rtc, ec_id)
  if ret:
    if state == RTC.ACTIVE_STATE:
      return True
  return False

##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥλ��ꤷ���¹ԥ���ƥ����Ȥ�ERROR���֤��ɤ���Ƚ��
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id �¹ԥ���ƥ����Ȥ�ID
# @return ERROR���֤λ���True������ʳ���False
# rtc��ec��nil�ξ���False���֤�
#
# @else
#
# @brief 
# @param rtc 
# @param ec_id
# @return 
#
# @endif
def is_in_error(rtc, ec_id=0):
  ret, state = get_state(rtc, ec_id)
  if ret:
    if state == RTC.ERROR_STATE:
      return True
  return False



##
# @if jp
#
# @brief RTC�Υǥե���Ȥμ¹ԥ���ƥ����Ȥμ¹Լ������������
#
# 
# @param rtc RT����ݡ��ͥ��
# @return �¹Լ���
#
# @else
#
# @brief 
# @param ec 
# @return
#
# @endif
def get_default_rate(rtc):
  ec = get_actual_ec(rtc)
  return ec.get_rate()


##
# @if jp
#
# @brief RTC�Υǥե���Ȥμ¹ԥ���ƥ����Ȥμ¹Լ��������ꤹ��
#
# 
# @param rtc RT����ݡ��ͥ��
# @param rate �¹Լ���
# @return set_rate�ؿ�������ͤ��֤���
# RTC_OK�����꤬����
#
# @else
#
# @brief 
# @param ec
#
# @endif
def set_default_rate(rtc, rate):
  ec = get_actual_ec(rtc)
  return ec.set_rate(rate)


##
# @if jp
#
# @brief RTC�λ���ID�μ¹ԥ���ƥ����Ȥμ��������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id ����μ¹ԥ���ƥ����Ȥ�ID
# @return �¹Լ���
#
# @else
#
# @brief 
# @param ec
# @return
#
# @endif
def get_current_rate(rtc, ec_id):
  ec = get_actual_ec(rtc, ec_id)
  return ec.get_rate()


##
# @if jp
#
# @brief RTC�λ���ID�μ¹ԥ���ƥ����Ȥμ���������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param ec_id ����μ¹ԥ���ƥ����Ȥ�ID
# @param rate �¹Լ���
# @return set_rate�ؿ�������ͤ��֤���
# RTC_OK�����꤬����
#
# @else
#
# @brief 
# @param  
#
# @endif
def set_current_rate(rtc, ec_id, rate):
  ec = get_actual_ec(rtc, ec_id)
  return ec.set_rate(rate)


##
# @if jp
#
# @brief �оݤ�RTC�Υǥե���Ȥμ¹ԥ���ƥ����Ȥ˻����RTC���Ϣ�դ���
#
# 
# @param localcomp �оݤ�RT����ݡ��ͥ��
# @param othercomp �¹ԥ���ƥ����Ȥ˴�Ϣ�դ���RT����ݡ��ͥ��
# @return ec�μ����˼��Ԥ�������BAD_PARAMETER���֤�
# �����Ǥʤ�����addComponent�ؿ�������ͤ��֤���RTC_OK����³������
#
# @else
#
# @brief 
# @param 
#
# @endif
def add_rtc_to_default_ec(localcomp, othercomp):
  if CORBA.is_nil(othercomp):
    return RTC.BAD_PARAMETER
  ec = get_actual_ec(localcomp)
  if CORBA.is_nil(ec):
    return RTC.BAD_PARAMETER
  return ec.add_component(othercomp)


##
# @if jp
#
# @brief �оݤ�RTC�Υǥե���Ȥμ¹ԥ���ƥ����Ȥλ����RTC�ؤδ�Ϣ�դ���������
#
# 
# @param localcomp �оݤ�RT����ݡ��ͥ��
# @param othercomp �¹ԥ���ƥ����ȤȤδ�Ϣ�դ���������RT����ݡ��ͥ��
# @return ec�μ����˼��Ԥ�������BAD_PARAMETER���֤�
# �����Ǥʤ�����removeComponent�ؿ�������ͤ��֤���RTC_OK�ǲ��������
#
# @else
#
# @brief 
# @param 
#
# @endif
def remove_rtc_to_default_ec(localcomp, othercomp):
  if CORBA.is_nil(othercomp):
    return RTC.BAD_PARAMETER
  ec = get_actual_ec(localcomp)
  if CORBA.is_nil(ec):
    return RTC.BAD_PARAMETER
  return ec.remove_component(othercomp)


##
# @if jp
#
# @brief RTC�Υǥե���Ȥμ¹ԥ���ƥ����Ȥ˻��ä��Ƥ���RTC�Υꥹ�Ȥ��������
# �¹ԥ���ƥ����Ȥ�nil�ξ��϶��Υꥹ�Ȥ��֤�
#
# 
# @param rtc RT����ݡ��ͥ��
# @return RTC�Υꥹ��
#
# @else
#
# @brief 
# @param ec
# @return 
#
# @endif
def get_participants_rtc(rtc):
  ec = get_actual_ec(rtc)
  if CORBA.is_nil(ec):
    return []
  profile = ec.get_profile()
  return profile.participants


##
# @if jp
#
# @brief ���ꤷ��RTC���ݻ�����ݡ��Ȥ�̾�������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @return �ݡ���̾�Υꥹ��
#
# @else
#
# @brief 
# @param rtc
# @return
#
# @endif
def get_port_names(rtc):
  names = []
  if CORBA.is_nil(rtc):
    return names
  ports = rtc.get_ports()
  for p in ports:
    pp = p.get_port_profile()
    s = pp.name
    names.append(s)
  return names


##
# @if jp
#
# @brief ���ꤷ��RTC���ݻ����륤��ݡ��Ȥ�̾�������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @return �ݡ���̾�Υꥹ��
#
# @else
#
# @brief 
# @param rtc
# @return
#
# @endif
def get_inport_names(rtc):
  names = []
  if CORBA.is_nil(rtc):
    return names
  
  ports = rtc.get_ports()
  for p in ports:
    pp = p.get_port_profile()
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
    if prop.getProperty("port.port_type") == "DataInPort":
      s = pp.name
      names.append(s)
  return names


##
# @if jp
#
# @brief ���ꤷ��RTC���ݻ����륢���ȥݡ��Ȥ�̾�������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @return �ݡ���̾�Υꥹ��
#
# @else
#
# @brief 
# @param rtc
# @return
#
# @endif
def get_outport_names(rtc):
  names = []
  if CORBA.is_nil(rtc):
    return names
  
  ports = rtc.get_ports()
  for p in ports:
    pp = p.get_port_profile()
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
    if prop.getProperty("port.port_type") == "DataOutPort":
      s = pp.name
      names.append(s)
  return names



##
# @if jp
#
# @brief ���ꤷ��RTC���ݻ����륵���ӥ��ݡ��Ȥ�̾�������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @return �ݡ���̾�Υꥹ��
#
# @else
#
# @brief 
# @param rtc
# @return
#
# @endif
def get_svcport_names(rtc):
  names = []
  if CORBA.is_nil(rtc):
    return names
  
  ports = rtc.get_ports()
  for p in ports:
    pp = p.get_port_profile()
    prop = OpenRTM_aist.Properties()
    OpenRTM_aist.NVUtil.copyToProperties(prop, pp.properties)
    if prop.getProperty("port.port_type") == "CorbaPort":
      s = pp.name
      names.append(s)
  return names


##
# @if jp
#
# @brief �оݤ�RTC������ꤷ��̾���Υݡ��Ȥ����
#
# 
# @param rtc RT����ݡ��ͥ��
# @param port_name �ݡ���̾
# @return �ݡ���
#
# @else
#
# @brief 
# @param rtc 
# @param port_name
# @return 
#
# @endif
#
# RTC::PortService_var get_port_by_name(const RTC::RTObject_ptr rtc, std::string port_name)
def get_port_by_name(rtc, port_name):
  if CORBA.is_nil(rtc):
    return RTC.PortService._nil
  ports = rtc.get_ports()
  for p in ports:
    pp = p.get_port_profile()
    s = pp.name
    
    if port_name == s:
      return p

  return RTC.PortService._nil



##
# @if jp
#
# @brief ���ꤷ���ݡ��Ȥ��ݻ����Ƥ��륳�ͥ�����̾���Υꥹ�Ȥ����
#
# 
# @param port �оݤΥݡ���
# @return ���ͥ���̾�Υꥹ��
#
# @else
#
# @brief 
# @param port
# @return
#
# @endif
def get_connector_names_by_portref(port):
  names = []
  if CORBA.is_nil(port):
    return names
  conprof = port.get_connector_profiles()
  for c in conprof:
    names.append(c.name)
  return names

##
# @if jp
#
# @brief �оݤ�RTC�λ��ꤷ���ݡ��ȤΥ��ͥ�����̾���Υꥹ�Ȥ����
#
# @param rtc RT����ݡ��ͥ��
# @param port_name �ݡ���̾
# @return ���ͥ���̾�Υꥹ��
#
# @else
#
# @brief
# @param rtc
# @param port_name
# @return
#
# @endif
def get_connector_names(rtc, port_name):
  names = []
  port = get_port_by_name(rtc, port_name)
  if CORBA.is_nil(port):
    return names
  conprof = port.get_connector_profiles()
  for c in conprof:
    names.append(c.name)
  return names


  


##
# @if jp
#
# @brief ���ꤷ���ݡ��Ȥ��ݻ����Ƥ��륳�ͥ�����ID�Υꥹ�Ȥ����
#
# 
# @param port �оݤΥݡ���
# @return ���ͥ�����ID�Υꥹ��
#
# @else
#
# @brief 
# @param port
# @return
#
# @endif
def get_connector_ids_by_portref(port):
  ids = []
  if CORBA.is_nil(port):
    return ids
  conprof = port.get_connector_profiles()
  for c in conprof:
    ids.append(c.connector_id)
  return ids




##
# @if jp
#
# @brief �оݤ�RTC�λ��ꤷ���ݡ��ȤΥ��ͥ�����ID�Υꥹ�Ȥ����
#
# 
# @param rtc RT����ݡ��ͥ��
# @param port_name �ݡ���̾
# @return ���ͥ�����ID�Υꥹ��
#
# @else
#
# @brief 
# @param rtc
# @param port_name
# @return
#
# @endif
def get_connector_ids(rtc, port_name):
  ids = []
  port = get_port_by_name(rtc, port_name)
  if CORBA.is_nil(port):
    return ids
  conprof = port.get_connector_profiles()
  for c in conprof:
    ids.append(c.connector_id)
  return ids

##
# @if jp
#
# @brief ���ꤷ���ݡ��Ȥ���³���뤿��Υ��ͥ����ץ�ե���������
#
# 
# @param name ���ͥ���̾
# @param prop_arg ����
# @param port0 �оݤΥݡ���1
# @param port1 �оݤΥݡ���2
# @return ���ͥ����ץ�ե�����
#
# @else
#
# @brief 
# @param name
# @param prop_arg
# @param port0
# @param port1
# @return
#
# @endif
# RTC::ConnectorProfile_var create_connector(const std::string name,const coil::Properties prop_arg,const RTC::PortService_ptr port0,const RTC::PortService_ptr port1)
def create_connector(name, prop_arg, port0, port1):
  prop = prop_arg
  if CORBA.is_nil(port1):
    conn_prof = RTC.ConnectorProfile(name, "", [port0],[])
  else:
    conn_prof = RTC.ConnectorProfile(name, "", [port0, port1],[])



  if not str(prop.getProperty("dataport.dataflow_type")):
    prop.setProperty("dataport.dataflow_type","push")

 

  if not str(prop.getProperty("dataport.interface_type")):
    prop.setProperty("dataport.interface_type","corba_cdr")


  conn_prof.properties = []
  OpenRTM_aist.NVUtil.copyFromProperties(conn_prof.properties, prop)
  
  return conn_prof
  

  
                                            

##
# @if jp
#
# @brief ���ꤷ���ݡ���Ʊ�Τ���³����Ƥ��뤫��Ƚ��
#
# 
# @param localport �оݤΥݡ���1
# @param otherport �оݤΥݡ���2
# @return True: ��³�Ѥߡ�False: ̤��³
#
# @else
#
# @brief 
# @param name
# @param prop_arg
# @param port0
# @param port1
# @return
#
# @endif

def already_connected(localport, otherport):
  conprof = localport.get_connector_profiles()
  for c in conprof:
    for p in c.ports:
      if p._is_equivalent(otherport):
        return True

  return False


##
# @if jp
#
# @brief ���ꤷ���ݡ��Ȥ���³����
#
# 
# @param name ���ͥ���̾
# @param prop ����
# @param port0 �оݤΥݡ���1
# @param port1 �оݤΥݡ���2
# @return �ݡ��ȤΥ��֥������ȥ�ե���󥹤�nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����port0.connect�ؿ�������ͤ��֤���RTC_OK�ξ�����³������
#
# @else
#
# @brief 
# @param name
# @param prop
# @param port0
# @param port1
# @return 
#
# @endif
# RTC::ReturnCode_t connect(const std::string name,const coil::Properties prop,const RTC::PortService_ptr port0,const RTC::PortService_ptr port1)
def connect(name, prop, port0, port1):
  if CORBA.is_nil(port0):
    return RTC.BAD_PARAMETER
  #if CORBA.is_nil(port1):
  #  return RTC.BAD_PARAMETER
  if not CORBA.is_nil(port1):
    if port0._is_equivalent(port1):
      return RTC.BAD_PARAMETER
  cprof = create_connector(name, prop, port0, port1)
  return port0.connect(cprof)[0]



##
# @if jp
#
# @brief ���ꤷ���ݡ��ȤȻ��ꤷ���ꥹ����Υݡ������Ƥ���³����
#
# 
# @param name ���ͥ���̾
# @param prop ����
# @param port �оݤΥݡ���
# @param target_ports �оݤΥݡ��ȤΥꥹ��
# @return ���Ƥ���³��������������RTC_OK���֤���
# connect�ؿ���RTC_OK�ʳ����֤�������BAD_PARAMETER���֤���
#
#
# @else
#
# @brief 
# @param name
# @param prop
# @param port0
# @param port1
# @return 
#
# @endif
# RTC::ReturnCode_t connect_multi(const std::string name,const coil::Properties prop,const RTC::PortService_ptr port,RTC::PortServiceList_var& target_ports)
def connect_multi(name, prop, port, target_ports):
  ret = RTC.RTC_OK
  if CORBA.is_nil(port):
    return RTC.BAD_PARAMETER
  for p in target_ports:
    if CORBA.is_nil(p):
      continue
    if p._is_equivalent(port):
      continue
    if already_connected(port, p):
      continue
    if RTC.RTC_OK != connect(name, prop, port, p):
      ret = RTC.BAD_PARAMETER

  return ret


##
# @if jp
# @class find_port
# @brief �ݡ��Ȥ�̾�����鸡��
#
# @else
# @class find_port
# @brief 
#
# @endif
#
class find_port:
  ##
  # @if jp
  #
  # @brief ���󥹥ȥ饯��
  # ��������ݡ���̾����ꤹ��
  #
  # 
  # @param self
  # @param name �ݡ���̾
  #
  # @else
  #
  # @brief 
  # @param self
  # @param name
  #
  # @endif
  # find_port(const std::string name)
  def __init__(self, name):
    self._name = name
  ##
  # @if jp
  #
  # @brief �оݤΥݡ��Ȥ�̾���Ȼ��ꤷ���ݡ���̾�����פ��뤫Ƚ��
  #
  # 
  # @param self
  # @param p �оݤΥݡ���
  # @return True: ̾�������ס�False:��̾�����԰���
  #
  # @else
  #
  # @brief 
  # @param self
  # @param p
  # @return
  #
  # @endif
  # bool operator()(RTC::PortService_var p)
  def __call__(self, p):
    prof = p.get_port_profile()
    c = prof.name
    
    return (self._name == c)
  
##
# @if jp
#
# @brief �оݤ�RTC�λ��ꤷ��̾���Υݡ��Ȥ���³����
#
# 
# @param name ���ͥ���̾
# @param prop ����
# @param rtc0 �оݤ�RTC����ݡ��ͥ��1
# @param portName0 �оݤΥݡ���̾1
# @param rtc1 �оݤ�RTC����ݡ��ͥ��2
# @param portName1 �оݤ�RTC����ݡ��ͥ��2
# @return RTC���ݡ��Ȥ�nil�ξ���BAD_PARAMETER���֤���
# nil�ǤϤʤ�����port0.connect�ؿ�������ͤ��֤���RTC_OK�ξ�����³������
#
# @else
#
# @brief 
# @param name
# @param prop_arg
# @param port0
# @param port1 
#
# @endif
#
# RTC::ReturnCode_t connect_by_name(std::string name, coil::Properties prop,RTC::RTObject_ptr rtc0,const std::string port_name0,RTC::RTObject_ptr rtc1,const std::string port_name1)
def connect_by_name(name, prop, rtc0, port_name0, rtc1, port_name1):
  if CORBA.is_nil(rtc0):
    return RTC.BAD_PARAMETER
  if CORBA.is_nil(rtc1):
    return RTC.BAD_PARAMETER

  port0 = get_port_by_name(rtc0, port_name0)
  if CORBA.is_nil(port0):
    return RTC.BAD_PARAMETER

  port1 = get_port_by_name(rtc1, port_name1)
  if CORBA.is_nil(port1):
    return RTC.BAD_PARAMETER

  return connect(name, prop, port0, port1)


##
# @if jp
#
# @brief ����Υ��ͥ��������Ǥ���
#
# 
# @param connector_prof ���ͥ����ץ�ե�����
# @return ���ͥ����ץ�ե�������ݻ����Ƥ���ݡ��ȤΥ��֥������ȥ�ե���󥹤�nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����ports[0].disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param connector_prof
# @return
#
# @endif
def disconnect(connector_prof):
  ports = connector_prof.ports
  return disconnect_by_portref_connector_id(ports[0], connector_prof.connector_id)
  
  

##
# @if jp
#
# @brief �оݤΥݡ��Ȥǻ��ꤷ��̾���Υ��ͥ���������
#
# 
# @param port_ref �оݤΥݡ���
# @param conn_name ���ͥ���̾
# @return port��nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param port_ref 
# @param conn_name 
# @return 
#
# @endif
def disconnect_by_portref_connector_name(port_ref, conn_name):
  if CORBA.is_nil(port_ref):
    return RTC.BAD_PARAMETER
  conprof = port_ref.get_connector_profiles()
  for c in conprof:
    if c.name == conn_name:
      return disconnect(c)
  return RTC.BAD_PARAMETER



##
# @if jp
#
# @brief �оݤ�̾���Υݡ��Ȥǻ��ꤷ��̾���Υ��ͥ���������
#
# 
# @param port_name �оݤΥݡ���̾
# @param conn_name ���ͥ���̾
# @return port��¸�ߤ��ʤ�����BAD_PARAMETER���֤�
# nil�ǤϤʤ�����disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param 
#
# @endif
def disconnect_by_portname_connector_name(port_name, conn_name):
  port_ref = get_port_by_url(port_name)
  if CORBA.is_nil(port_ref):
    return RTC.BAD_PARAMETER
  
  conprof = port_ref.get_connector_profiles()
  for c in conprof:
    if c.name == conn_name:
      return disconnect(c)
    
  return RTC.BAD_PARAMETER


##
# @if jp
#
# @brief �оݤΥݡ��Ȥǻ��ꤷ��ID�Υ��ͥ���������
#
# 
# @param port �оݤΥݡ���
# @param name ���ͥ���ID
# @return port��nil�ξ���BAD_PARAMETER���֤�
# nil�ǤϤʤ�����disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param 
#
# @endif
def disconnect_by_portref_connector_id(port_ref, conn_id):
  if CORBA.is_nil(port_ref):
    return RTC.BAD_PARAMETER
  return port_ref.disconnect(conn_id)


##
# @if jp
#
# @brief �оݤ�̾���Υݡ��Ȥǻ��ꤷ��ID�Υ��ͥ���������
#
# 
# @param port_name �оݤΥݡ���̾
# @param name ���ͥ���ID
# @return port��¸�ߤ��ʤ�����BAD_PARAMETER���֤�
# nil�ǤϤʤ�����disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param port_name 
# @param name 
# @return 
#
# @endif
def disconnect_by_portname_connector_id(port_name, conn_id):
  port_ref = get_port_by_url(port_name)
  if port_ref == RTC.PortService._nil:
    return RTC.BAD_PARAMETER
  
  return port_ref.disconnect(conn_id)
  

##
# @if jp
#
# @brief �оݤΥݡ��ȤΥ��ͥ�������������
#
# 
# @param port_ref �ݡ��ȤΥ��֥������ȥ�ե����
# @return port��nil�ξ���BAD_PARAMETER���֤�
# ���ǤǤ�������RTC_OK���֤�
#
# @else
#
# @brief 
# @param port
# @return 
#
# @endif
def disconnect_all_by_ref(port_ref):
  if CORBA.is_nil(port_ref):
    return RTC.BAD_PARAMETER
  return port_ref.disconnect_all()


##
# @if jp
#
# @brief ����ݡ���̾�Υݡ��ȤΥ��ͥ�������������
#
# 
# @param port_name �ݡ���̾
# @return port��¸�ߤ��ʤ�����BAD_PARAMETER���֤�
# ���ǤǤ�������RTC_OK���֤�
#
# @else
#
# @brief 
# @param port
# @return 
#
# @endif
def disconnect_all_by_name(port_name):
  port_ref = get_port_by_url(port_name)
  if port_ref == RTC.PortService._nil:
    return RTC.BAD_PARAMETER
  return port_ref.disconnect_all()


##
# @if jp
#
# @brief ���ꤷ��̾���Υݡ��Ȥ����
#
# 
# @param port_name �ݡ���̾
# @return �ݡ��ȤΥ��֥������ȥ�ե����
# port��¸�ߤ��ʤ�����nil���֤�
#
# @else
#
# @brief 
# @param port_name
# @return 
#
# @endif
def get_port_by_url(port_name):
  mgr = OpenRTM_aist.Manager.instance()
  nm = mgr.getNaming()
  p = port_name.split(".")
  if len(p) < 2:
    return RTC.PortService._nil
  
  rtcs = nm.string_to_component(port_name.rstrip("."+p[-1]))
  
  if len(rtcs) < 1:
    return RTC.PortService._nil
  pn = port_name.split("/")
  
  return get_port_by_name(rtcs[0],pn[-1])

##
# @if jp
#
# @brief �оݥݡ��Ȥ���³���Ƥ���ݡ��Ȥǻ��ꤷ���ݡ���̾�Ȱ��פ�����������
#
# 
# @param localport �оݤΥݡ���
# @param othername ��³���Ƥ���ݡ���̾
# @return �ݡ��Ȥ�nil�ξ�硢localport��̾����othername�����פ����硢��³���Ƥ���ݡ��Ȥ�̾����othername�Ȱ��פ����Τ��ʤ�����BAD_PARAMETER���֤�
# �嵭�ξ������ƤϤޤ�ʤ�����disconnect�ؿ�������ͤ��֤���RTC_OK�ξ������Ǥ�����
#
# @else
#
# @brief 
# @param 
#
# @endif
def disconnect_by_port_name(localport, othername):
  if CORBA.is_nil(localport):
    return RTC.BAD_PARAMETER
  prof = localport.get_port_profile()
  if prof.name == othername:
    return RTC.BAD_PARAMETER
  
  conprof = localport.get_connector_profiles()
  for c in conprof:
    for p in c.ports:
      if not CORBA.is_nil(p):
        pp = p.get_port_profile()
        if pp.name == othername:
          return disconnect(c)
  return RTC.BAD_PARAMETER


##
# @if jp
#
# @brief �оݤ�RT����ݡ��ͥ�Ȥλ��ꤷ��̾���Υ���ե�����졼����󥻥åȤ�key-value�Ǽ���
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param conf_name ����ե�����졼����󥻥å�̾
# @return ����ե�����졼����󥻥å�
#
# @else
#
# @brief 
# @param rtc 
# @param conf_name 
# @return 
#
# @endif
def get_configuration(rtc, conf_name):
  conf = rtc.get_configuration()
  
  confset = conf.get_configuration_set(conf_name)
  confData = confset.configuration_data
  prop = OpenRTM_aist.Properties()
  OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
  return prop


##
# @if jp
#
# @brief ���ꤷ������ե�����졼����󥻥å�̾���ѥ�᡼��̾�Υ���ե�����졼�����ѥ�᡼�������
#
# 
# @param rtc RT����ݡ��ͥ��
# @param confset_name ����ե�����졼����󥻥å�̾
# @param value_name �ѥ�᡼��̾
# @return �ѥ�᡼��
#
# @else
#
# @brief 
# @param rtc
# @param confset_name
# @param value_name
# @param ret
# @return
#
# @endif
def get_parameter_by_key(rtc, confset_name, value_name):
  conf = rtc.get_configuration()
  
    
  confset = conf.get_configuration_set(confset_name)
  confData = confset.configuration_data
  prop = OpenRTM_aist.Properties()
  OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
  return prop.getProperty(value_name)
    
  


##
# @if jp
#
# @brief �оݤ�RTC�Υ����ƥ��֤ʥ���ե�����졼����󥻥å�̾���������
#
# @param rtc RT����ݡ��ͥ��
# @return ����ե�����졼����󥻥å�̾
# ����ե�����졼�����μ����˼��Ԥ������϶���ʸ������֤�
# 
# @param 
#
# @else
#
# @brief 
# @param rtc
# @return 
#
# @endif
def get_active_configuration_name(rtc):
  conf = rtc.get_configuration()
  confset = conf.get_active_configuration_set()
  return confset.id

##
# @if jp
#
# @brief �����ƥ��֤ʥ���ե�����졼����󥻥åȤ�key-value�Ǽ�������
#
# 
# @param rtc �оݤ�RT����ݡ��ͥ��
# @return �����ƥ��֤ʥ���ե�����졼����󥻥å�
#
# @else
#
# @brief 
# @param rtc
# @return
#
# @endif
def get_active_configuration(rtc):
  conf = rtc.get_configuration()

  confset = conf.get_active_configuration_set()
  confData = confset.configuration_data
  prop = OpenRTM_aist.Properties()
  OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
  return prop
    




##
# @if jp
#
# @brief ����ե�����졼�����ѥ�᡼��������
#
#
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param confset_name ����ե�����졼����󥻥å�̾
# @param value_name �ѥ�᡼��̾
# @param value �ѥ�᡼��
# @return True:�����������False:����˼���
#
# @else
#
# @brief
# @param rtc
# @param confset_name
# @param value_name
# @param value
# @return
#
# @endif
def set_configuration(rtc, confset_name, value_name, value):
  conf = rtc.get_configuration()
  
  confset = conf.get_configuration_set(confset_name)

  set_configuration_parameter(conf, confset, value_name, value)
  
  conf.activate_configuration_set(confset_name)
  return True


##
# @if jp
#
# @brief �����ƥ��֤ʥ���ե�����졼����󥻥åȤΥѥ�᡼��������
#
#
# @param rtc �оݤ�RT����ݡ��ͥ��
# @param value_name �ѥ�᡼��̾
# @param value �ѥ�᡼��
# @return True:�����������False:����˼���
#
# @else
#
# @brief
# @param rtc 
# @param confset_name
# @param value_name
# @param value
# @return
#
# @endif
def set_active_configuration(rtc, value_name, value):
  conf = rtc.get_configuration()
  
  confset = conf.get_active_configuration_set()
  set_configuration_parameter(conf, confset, value_name, value)
   
  conf.activate_configuration_set(confset.id)
  return True


##
# @if jp
#
# @brief ����ե�����졼�����ѥ�᡼��������
#
#
# @param conf ����ե�����졼�����
# @param confset ����ե�����졼����󥻥å�
# @param value_name �ѥ�᡼��̾
# @param value �ѥ�᡼��
# @return True:�����������False:����˼���
#
# @else
#
# @brief
# @param conf
# @param confset
# @param value_name
# @param value
# @return
#
# @endif
def set_configuration_parameter(conf, confset, value_name, value):
  confData = confset.configuration_data
  prop = OpenRTM_aist.Properties()
  OpenRTM_aist.NVUtil.copyToProperties(prop, confData)
  prop.setProperty(value_name,value)
  OpenRTM_aist.NVUtil.copyFromProperties(confData,prop)
  confset.configuration_data = confData
  conf.set_configuration_set_values(confset)
  return True
  