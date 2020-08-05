#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
#  @file CORBA_IORUtil.py
#  @brief CORBA IOR utility
#  @date $Date$
#  @author Noriaki Ando
#

from omniORB import CORBA
from omniORB import *
from omniORB import any
from IORProfile_idl import *
from IORProfile_idl import _0__GlobalIDL
endian = True


class IOP:
    TAG_INTERNET_IOP = 0
    TAG_MULTIPLE_COMPONENTS = 1
    TAG_SCCP_IOP = 2
    DEFAULT_CORBALOC_PORT = 2809

    ProfileID = {TAG_INTERNET_IOP: "TAG_INTERNET_IOP",
                 TAG_MULTIPLE_COMPONENTS: "TAG_MULTIPLE_COMPONENTS",
                 TAG_SCCP_IOP: "TAG_SCCP_IOP",
                 DEFAULT_CORBALOC_PORT: "DEFAULT_CORBALOC_PORT"
                 }
    # ComponentId
    TAG_ORB_TYPE = 0
    TAG_CODE_SETS = 1
    TAG_POLICIES = 2
    TAG_ALTERNATE_IIOP_ADDRESS = 3
    TAG_COMPLETE_OBJECT_KEY = 5
    TAG_ENDPOINT_ID_POSITION = 6
    TAG_LOCATION_POLICY = 12
    TAG_ASSOCIATION_OPTIONS = 13
    TAG_SEC_NAME = 14
    TAG_SPKM_1_SEC_MECH = 15
    TAG_SPKM_2_SEC_MECH = 16
    TAG_KERBEROSV5_SEC_MECH = 17
    TAG_CSI_ECMA_SECRET_SEC_MECH = 18
    TAG_CSI_ECMA_HYBRID_SEC_MECH = 19
    TAG_SSL_SEC_TRANS = 20
    TAG_CSI_ECMA_PUBLIC_SEC_MECH = 21
    TAG_GENERIC_SEC_MECH = 22
    TAG_FIREWALL_TRANS = 23
    TAG_SCCP_CONTACT_INFO = 24
    TAG_JAVA_CODEBASE = 25
    TAG_CSI_SEC_MECH_LIST = 33
    TAG_NULL_TAG = 34
    TAG_TLS_SEC_TRANS = 36
    TAG_DCE_STRING_BINDING = 100
    TAG_DCE_BINDING_NAME = 101
    TAG_DCE_NO_PIPES = 102
    TAG_DCE_SEC_MECH = 103
    TAG_INET_SEC_TRANS = 123
    TAG_GROUP = 90001  # XXX NEED THE REAL CONSTANT !!
    TAG_PRIMARY = 90002  # XXX NEED THE REAL CONSTANT!
    TAG_HEARTBEAT_ENABLED = 90003  # XXX NEED THE REAL CONSTANT !
    # omniORB specific IDs
    TAG_OMNIORB_BIDIR = 0x41545401
    TAG_OMNIORB_UNIX_TRANS = 0x41545402
    TAG_OMNIORB_PERSISTENT_ID = 0x41545403
    TAG_OMNIORB_RESTRICTED_CONNECTION = 0x41545404
    ComponentID = {TAG_ORB_TYPE: "TAG_ORB_TYPE",
                   TAG_CODE_SETS: "TAG_CODE_SETS",
                   TAG_POLICIES: "TAG_POLICIES",
                   TAG_ALTERNATE_IIOP_ADDRESS: "TAG_ALTERNATE_IIOP_ADDRESS",
                   TAG_COMPLETE_OBJECT_KEY: "TAG_COMPLETE_OBJECT_KEY",
                   TAG_ENDPOINT_ID_POSITION: "TAG_ENDPOINT_ID_POSITION",
                   TAG_LOCATION_POLICY: "TAG_LOCATION_POLICY",
                   TAG_ASSOCIATION_OPTIONS: "TAG_ASSOCIATION_OPTIONS",
                   TAG_SEC_NAME: "TAG_SEC_NAME",
                   TAG_SPKM_1_SEC_MECH: "TAG_SPKM_1_SEC_MECH",
                   TAG_SPKM_2_SEC_MECH: "TAG_SPKM_2_SEC_MECH",
                   TAG_KERBEROSV5_SEC_MECH: "TAG_KERBEROSV5_SEC_MECH",
                   TAG_CSI_ECMA_SECRET_SEC_MECH: "TAG_CSI_ECMA_SECRET_SEC_MECH",
                   TAG_CSI_ECMA_HYBRID_SEC_MECH: "TAG_CSI_ECMA_HYBRID_SEC_MECH",
                   TAG_SSL_SEC_TRANS: "TAG_SSL_SEC_TRANS",
                   TAG_CSI_ECMA_PUBLIC_SEC_MECH: "TAG_CSI_ECMA_PUBLIC_SEC_MECH",
                   TAG_GENERIC_SEC_MECH: "TAG_GENERIC_SEC_MECH",
                   TAG_FIREWALL_TRANS: "TAG_FIREWALL_TRANS",
                   TAG_SCCP_CONTACT_INFO: "TAG_SCCP_CONTACT_INFO",
                   TAG_JAVA_CODEBASE: "TAG_JAVA_CODEBASE",
                   TAG_CSI_SEC_MECH_LIST: "TAG_CSI_SEC_MECH_LIST",
                   TAG_NULL_TAG: "TAG_NULL_TAG",
                   TAG_TLS_SEC_TRANS: "TAG_TLS_SEC_TRANS",
                   TAG_DCE_STRING_BINDING: "TAG_DCE_STRING_BINDING",
                   TAG_DCE_BINDING_NAME: "TAG_DCE_BINDING_NAME",
                   TAG_DCE_NO_PIPES: "TAG_DCE_NO_PIPES",
                   TAG_DCE_SEC_MECH: "TAG_DCE_SEC_MECH",
                   TAG_INET_SEC_TRANS: "TAG_INET_SEC_TRANS",
                   TAG_GROUP: "TAG_GROUP",
                   TAG_PRIMARY: "TAG_PRIMARY",
                   TAG_HEARTBEAT_ENABLED: "TAG_HEARTBEAT_ENABLED",
                   TAG_OMNIORB_BIDIR: "TAG_OMNIORB_BIDIR",
                   TAG_OMNIORB_UNIX_TRANS: "TAG_OMNIORB_UNIX_TRANS",
                   TAG_OMNIORB_PERSISTENT_ID: "TAG_OMNIORB_PERSISTENT_ID",
                   TAG_OMNIORB_RESTRICTED_CONNECTION: "TAG_OMNIORB_RESTRICTED_CONNECTION",
                   }

    codesets = {0x00010001: "ISO-8859-1",
                0x00010002: "ISO-8859-2",
                0x00010003: "ISO-8859-3",
                0x00010004: "ISO-8859-4",
                0x00010005: "ISO-8859-5",
                0x00010006: "ISO-8859-6",
                0x00010007: "ISO-8859-7",
                0x00010008: "ISO-8859-8",
                0x00010009: "ISO-8859-9",
                0x0001000a: "ISO-8859-10",
                0x0001000b: "ISO-8859-11",
                0x0001000d: "ISO-8859-13",
                0x0001000e: "ISO-8859-14",
                0x0001000f: "ISO-8859-15",
                0x00010010: "ISO-8859-16",
                0x00010020: "ISO-646",
                0x00010100: "UCS-2-level-1",
                0x00010101: "UCS-2-level-2",
                0x00010102: "UCS-2-level-3",
                0x00010106: "UCS-4",
                0x05010001: "UTF-8",
                0x00010109: "UTF-16",
                0x100204e2: "windows-1250",
                0x100204e3: "windows-1251",
                0x100204e4: "windows-1252",
                0x100204e5: "windows-1253",
                0x100204e6: "windows-1254",
                0x100204e7: "windows-1255",
                0x100204e8: "windows-1256",
                0x100204e9: "windows-1257",
                0x100204ea: "windows-1258",
                0x10020025: "IBM-037",
                0x100201f8: "IBM-500",
                0x10040366: "SNI-EDF-4",
                0x10020567: "GBK"
                }
    orb_type = {0x41545400: "omniORB",
                0x48500000: "HP",
                0x4e534400: "HP",
                0x49424d00: "IBM",
                0x53554e00: "Sun",
                0x4f424200: "BEA",
                0x42454100: "BEA",
                0x574C5300: "BEA",
                0x494c5500: "Xerox",
                0x58505300: "PrismTech",
                0x50544300: "PrismTech",
                0x49534900: "AdNovum Informatik",
                0x56495300: "Borland",
                0x4f495300: "Object Interface Systems",
                0x46420000: "FloorBoard Software",
                0x4e4e4e00: "Rogue Wave",
                0x4e550000: "Nihon Unisys",
                0x4a424b00: "SilverStream Software",
                0x54414f00: "TAO",
                0x4c434200: "2AB",
                0x41505800: "Univ. of Erlangen-Nuernberg",
                0x4f425400: "ORBit",
                0x47534900: "GemStone Systems",
                0x464a0000: "Fujitsu",
                0x4f425f00: "TIBCO",
                0x4f414b00: "Camros Corporation",
                0x4f4f4300: "IONA (Orbacus)",
                0x49545f00: "IONA (Orbix)",
                0x4e454300: "NEC",
                0x424c5500: "Berry Software",
                0x56495400: "Vitria",
                0x444f4700: "Exoffice Technologies",
                0xcb0e0000: "Chicago Board of Exchange",
                0x4a414300: "JacORB",
                0x58545200: "Xtradyne Technologies",
                0x54475800: "Top Graph'X",
                0x41646100: "AdaOS Project",
                0x4e4f4b00: "Nokia",
                0x45524900: "Ericsson",
                0x52415900: "RayORB",
                0x53414e00: "Sankhya Technologies",
                0x414e4400: "Androsoft",
                0x42424300: "Bionic Buffalo",
                0x522e4300: "Remoting.Corba",
                0x504f0000: "PolyORB",
                0x54494400: "Telefonica",
                }
##
# @if jp
#
# @brief コンポーネントのプロパティ取得
#
#
# @param rtc RTコンポーネント
# @return コンポーネントのプロパティ
#
# @else
#
# @brief
# @param rtc
# @return
#
# @endif
# coil::Properties get_component_profile(const RTC::RTObject_ptr rtc)


class cdrStream:
    def __init__(self, cdrdata):
        self.pos = 0
        self.cdrdata = cdrdata
        return

    def data(self, length):
        return self.iordata[self.pos:self.pos + length]

    def pos(self):
        return self.pos

    def rewind(self):
        self.pos = 0

    def incr(self, count=1):
        self.pos += count


def unmarshalBoolean(cdr):
    cdrUnmarshal(CORBA.TC_boolean, "".join(cdr.data(2)))


TAGS = ("IOP::TAG_INTERNET_IOP",
        "IOP::TAG_MULTIPLE_COMPONENTS",
        "IOP::TAG_SCCP_IOP")


def toString(ior):
    global endian

    data = cdrMarshal(any.to_any(ior).typecode(), ior, endian)
    result = [0] * (12 + len(data) * 2)
    result[0] = "I"
    result[1] = "O"
    result[2] = "R"
    result[3] = ":"

    result[4] = "0"
    if endian:
        result[5] = "1"
    else:
        result[5] = "0"
    result[6] = "0"
    result[7] = "0"
    result[8] = "0"
    result[9] = "0"
    result[10] = "0"
    result[11] = "0"

    for i,datai in enumerate(data):
        d = ord(datai)
        j = 12 + i * 2
        v = (d & 0xf0)
        v = v >> 4
        if v < 10:
            result[j] = chr(ord('0') + v)
        else:
            result[j] = chr(ord('a') + (v - 10))
        v = ((d & 0xf))
        if v < 10:
            result[j + 1] = chr(ord('0') + v)
        else:
            result[j + 1] = chr(ord('a') + (v - 10))

    iorstr = "".join(result)
    return iorstr


def toIOR(iorstr):
    global endian
    if len(iorstr) < 4:
        return
    if iorstr[0:4] != 'IOR:':
        return

    pos = len("IOR:")
    if sys.version_info[0] == 2:
        iorvalue = [chr(int(i + j, 16))
                    for (i, j) in zip(iorstr[pos::2], iorstr[(pos + 1)::2])]
    else:
        iorvalue = [int(i + j, 16)
                    for (i, j) in zip(iorstr[pos::2], iorstr[(pos + 1)::2])]
    # Endian flag
    pos = 0
    endian = (iorvalue[pos] != 0)
    pos += 4
    if sys.version_info[0] == 2:
        ior = cdrUnmarshal(_0__GlobalIDL._tc_IOR,
                           "".join(iorvalue[pos:]), endian)
    else:
        ior = cdrUnmarshal(_0__GlobalIDL._tc_IOR,
                           bytes(iorvalue[pos:]), endian)
    return ior


def getEndpoints(ior):
    global endian
    addr = []
    for p in ior.profiles:
        # TAG_INTERNET_IOP
        if p.tag == IOP.TAG_INTERNET_IOP:
            if sys.version_info[0] == 2:
                pbody = cdrUnmarshal(_0__GlobalIDL._tc_ProfileBody,
                                     "".join(p.profile_data), endian)
            else:
                pbody = cdrUnmarshal(_0__GlobalIDL._tc_ProfileBody,
                                     p.profile_data, endian)
            addr.append(pbody.address_)
            addr += extractAddrs(pbody.components)

        # TAG_MULTIPLE_COMPONENTS
        elif p.tag == IOP.TAG_MULTIPLE_COMPONENTS:
            if sys.version_info[0] == 2:
                profiles = cdrUnmarshal(_0__GlobalIDL._tc_MultipleComponentProfile,
                                        "".join(p.profile_data), endian)
            else:
                profiles = cdrUnmarshal(_0__GlobalIDL._tc_MultipleComponentProfile,
                                        p.profile_data, endian)
            addr += extractAddrs(profiles)
        else:
            print("Other Profile")
    return addr


def extractAddrs(comps):
    global endian
    addr = []
    for c in comps:
        # print("TAG component type: ", IOP.ComponentID[c.tag])
        if c.tag == IOP.TAG_ALTERNATE_IIOP_ADDRESS:
            if sys.version_info[0] == 2:
                size = cdrUnmarshal(CORBA.TC_ulong,
                                    "".join(c.component_data[0:4]), endian)
                address = cdrUnmarshal(_0__GlobalIDL._tc_Address,
                                       "".join(c.component_data[4:]), endian)
            else:
                size = cdrUnmarshal(CORBA.TC_ulong,
                                    c.component_data[0:4], endian)
                address = cdrUnmarshal(_0__GlobalIDL._tc_Address,
                                       c.component_data[4:], endian)
            addr.append(address)
        elif c.tag == IOP.TAG_ORB_TYPE:
            if sys.version_info[0] == 2:
                size = cdrUnmarshal(CORBA.TC_ulong,
                                    "".join(c.component_data[0:4]), endian)
                orb_type = cdrUnmarshal(CORBA.TC_ulong,
                                        "".join(c.component_data[4:8]), endian)
            else:
                size = cdrUnmarshal(CORBA.TC_ulong,
                                    c.component_data[0:4], endian)
                orb_type = cdrUnmarshal(CORBA.TC_ulong,
                                        c.component_data[4:8], endian)
    return addr

##
# @if jp
#
# @brief IROのエンドポイント置き換え
#
#
# @param iorstr IOR文字列
# @param endpoint エンドポイント
# @return 置き換え後の文字列
#
# @else
#
# @brief
#
# @param iorstr
# @param endpoint
# @return
#
# @endif


def replaceEndpoint(iorstr, endpoint):
    global endian
    ior = toIOR(iorstr)
    for p in ior.profiles:
        # TAG_INTERNET_IOP
        if p.tag == IOP.TAG_INTERNET_IOP:
            if sys.version_info[0] == 2:
                pbody = cdrUnmarshal(_0__GlobalIDL._tc_ProfileBody,
                                     "".join(p.profile_data), endian)
            else:
                pbody = cdrUnmarshal(_0__GlobalIDL._tc_ProfileBody,
                                     p.profile_data, endian)

            pbody.address_.host = endpoint
            p.profile_data = cdrMarshal(
                any.to_any(pbody).typecode(), pbody, endian)

        # TAG_MULTIPLE_COMPONENTS
        elif p.tag == IOP.TAG_MULTIPLE_COMPONENTS:
            pass
        else:
            print("Other Profile")
    iorstr = toString(ior)
    return iorstr


iorstr = "IOR:000000000000003549444c3a6f70656e72746d2e616973742e676f2e6a702f4f70656e52544d2f44617461466c6f77436f6d706f6e656e743a312e3000000000000000010000000000000064000102000000000d31302e3231312e35352e31350000ffa90000000efed593815800002090000000000100000000000200000000000000080000000041545400000000010000001c00000000000100010000000105010001000101090000000100010109"

iorstr = "IOR:010000002b00000049444c3a6f6d672e6f72672f436f734e616d696e672f4e616d696e67436f6e746578744578743a312e300000010000000000000070000000010102000c00000031302e3231312e35352e3400f90a00000b0000004e616d6553657276696365000300000000000000080000000100000000545441010000001c0000000100000001000100010000000100010509010100010000000901010003545441080000006158825801000c55"

iorstr = "IOR:010000002b00000049444c3a6f6d672e6f72672f436f734e616d696e672f4e616d696e67436f6e746578744578743a312e3000000100000000000000b0010000010102000c00000031302e3231312e35352e3400f90a00000b0000004e616d6553657276696365000a00000000000000080000000100000000545441010000001c000000010000000100010001000000010001050901010001000000090101000300000016000000010000000c00000031302e33372e3132392e3400f90a00000300000018000000010000000d0000003139322e3136382e302e31350000f90a0300000018000000010000000e0000003139322e3136382e3132322e3100f90a03000000300000000100000025000000666462323a326332363a663465343a303a646434643a363731393a383431353a323262340000f90a030000002e0000000100000024000000666462323a326332363a663465343a303a3231633a343266663a666565343a3265656300f90a000003000000300000000100000025000000666462323a326332363a663465343a313a633465383a313565343a336232383a343530380000f90a030000002e0000000100000024000000666462323a326332363a663465343a313a3231633a343266663a666566353a6437653900f90a00000354544108000000385a82580100125b"

# orb = CORBA.ORB_init()
# ior = toIOR(iorstr)
# print(getEndpoints(ior))
