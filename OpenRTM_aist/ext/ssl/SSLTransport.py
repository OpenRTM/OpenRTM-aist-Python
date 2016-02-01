#!/usr/bin/env python
# -*- coding: euc-jp -*-

import os
from omniORB import sslTP
import OpenRTM_aist



def SSLTransportInit(manager):

    

    os.environ['ORBsslVerifyMode'] = "none"


    prop = manager.getConfig()
    certificate_authority_file = prop.getProperty("corba.ssl.certificate_authority_file")
    key_file = prop.getProperty("corba.ssl.key_file")
    key_file_password = prop.getProperty("corba.ssl.key_file_password")

    corba_args = prop.getProperty("corba.args")
    corba_args += " -ORBendPoint giop:ssl::"
    if not OpenRTM_aist.toBool(prop.getProperty("manager.is_master"), "YES", "NO", True):
        if len(prop.getProperty("corba.endpoints")) == 0:
            if len(prop.getProperty("corba.endpoint")) == 0:
                if str(prop.getProperty("corba.args")).find("-ORBendPoint") == -1:
                    corba_args += " -ORBendPoint giop:tcp::"

    
    prop.setProperty("corba.args",corba_args)

    
    
    
    sslTP.certificate_authority_file(certificate_authority_file)
    sslTP.key_file(key_file)
    sslTP.key_file_password(key_file_password)
    