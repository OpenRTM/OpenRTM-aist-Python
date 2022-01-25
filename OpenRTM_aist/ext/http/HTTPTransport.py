#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file HTTPTransport.py
# @brief HTTP Transport module
# @date $Date: $
# @author Nobuhiko Miyamoto


import os
from omniORB import httpTP
import OpenRTM_aist


def HTTPTransportInit(manager):

    #os.environ['ORBtraceLevel'] = '25'
    #os.environ['ORBendPoint'] = 'giop:http:ws://127.0.0.1:2810/ws'
    #os.environ['ORBsslVerifyMode'] = "none"

    prop = manager.getConfig()
    certificate_authority_file = prop.getProperty(
        "corba.http.certificate_authority_file")
    key_file = prop.getProperty("corba.http.key_file")
    key_file_password = prop.getProperty("corba.http.key_file_password")

    corba_args = prop.getProperty("corba.args")

    if not ("giop:http" in corba_args):
        corba_args += " -ORBendPoint giop:http:ws://127.0.0.1:8001/ws"
        
    if not OpenRTM_aist.toBool(prop.getProperty(
            "manager.is_master"), "YES", "NO", True):
        if not prop.getProperty("corba.endpoints"):
            if not prop.getProperty("corba.endpoint"):
                if str(prop.getProperty("corba.args")).find(
                        "-ORBendPoint") == -1:
                    corba_args += " -ORBendPoint giop:tcp::"

    prop.setProperty("corba.args", corba_args)

    if certificate_authority_file:
        httpTP.set_CA(certificate_authority_file, None)
    if key_file or key_file_password:
        httpTP.set_key(key_file, key_file_password)
