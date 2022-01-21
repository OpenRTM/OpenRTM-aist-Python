#!/usr/bin/env python3
# -*- coding: utf-8 -*-


##
# @file SSLTransport.py
# @brief SSL Transport module
# @date $Date: $
# @author Nobuhiko Miyamoto


import os
from omniORB import sslTP
import OpenRTM_aist


def SSLTransportInit(manager):

    #os.environ['ORBtraceLevel'] = '25'
    #os.environ['ORBendPoint'] = 'giop:ssl::'
    #os.environ['ORBsslVerifyMode'] = "none"

    prop = manager.getConfig()
    certificate_authority_file = prop.getProperty(
        "corba.ssl.certificate_authority_file")
    key_file = prop.getProperty("corba.ssl.key_file")
    key_file_password = prop.getProperty("corba.ssl.key_file_password")

    corba_args = prop.getProperty("corba.args")

    if not ("giop:ssl" in corba_args):
        corba_args += " -ORBendPoint giop:ssl::"

    if not OpenRTM_aist.toBool(prop.getProperty(
            "manager.is_master"), "YES", "NO", True):
        if not prop.getProperty("corba.endpoints"):
            if not prop.getProperty("corba.endpoint"):
                if str(prop.getProperty("corba.args")).find(
                        "-ORBendPoint") == -1:
                    corba_args += " -ORBendPoint giop:tcp::"

    prop.setProperty("corba.args", corba_args)

    sslTP.certificate_authority_file(certificate_authority_file)
    sslTP.key_file(key_file)
    sslTP.key_file_password(key_file_password)
