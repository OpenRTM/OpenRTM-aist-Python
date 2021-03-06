#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file uuid.py
# @brief
# @date $Date: 2006/06/12 $
# @author Ka-Ping Yee <ping@zesty.ca>
#
# Copyright (C) 2008
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.

import sys

RESERVED_NCS, RFC_4122, RESERVED_MICROSOFT, RESERVED_FUTURE = [
    'reserved for NCS compatibility', 'specified in RFC 4122',
    'reserved for Microsoft compatibility', 'reserved for future definition']


if sys.version_info[0] == 3:
    long = int


##
# @if jp
# @class UUID
# @brief UUID保持クラス
#
# 生成した UUID の情報を保持するためのクラス。
#
# @since 0.4.0
#
# @else
#
# @endif
class UUID(object):

    def __init__(self, hex=None, bytes=None, fields=None, int_value=None,
                 version=None):
        r"""Create a UUID from either a string of 32 hexadecimal digits,
        a string of 16 bytes as the 'bytes' argument, a tuple of six
        integers (32-bit time_low, 16-bit time_mid, 16-bit time_hi_version,
        8-bit clock_seq_hi_variant, 8-bit clock_seq_low, 48-bit node) as
        the 'fields' argument, or a single 128-bit integer as the 'int'
        argument.  When a string of hex digits is given, curly braces,
        hyphens, and a URN prefix are all optional.  For example, these
        expressions all yield the same UUID:

        UUID('{12345678-1234-5678-1234-567812345678}')
        UUID('12345678123456781234567812345678')
        UUID('urn:uuid:12345678-1234-5678-1234-567812345678')
        UUID(bytes='\x12\x34\x56\x78'*4)
        UUID(fields=(0x12345678, 0x1234, 0x5678, 0x12, 0x34, 0x567812345678))
        UUID(int=0x12345678123456781234567812345678)

        Exactly one of 'hex', 'bytes', 'fields', or 'int' must be given.
        The 'version' argument is optional; if given, the resulting UUID
        will have its variant and version number set according to RFC 4122,
        overriding bits in the given 'hex', 'bytes', 'fields', or 'int'.
        """

        if [hex, bytes, fields, int_value].count(None) != 3:
            raise TypeError('need just one of hex, bytes, fields, or int')
        if hex:
            hex = hex.replace('urn:', '').replace('uuid:', '')
            hex = hex.strip('{}').replace('-', '')
            if len(hex) != 32:
                raise ValueError('badly formed hexadecimal UUID string')
            int_value = long(hex, 16)
        if bytes:
            if len(bytes) != 16:
                raise ValueError('bytes is not a 16-char string')
            int_value = long(('%02x' * 16) % tuple(map(ord, bytes)), 16)
        if fields:
            if len(fields) != 6:
                raise ValueError('fields is not a 6-tuple')
            (time_low, time_mid, time_hi_version,
             clock_seq_hi_variant, clock_seq_low, node) = fields
            if not 0 <= time_low < 1 << 32:
                raise ValueError('field 1 out of range (need a 32-bit value)')
            if not 0 <= time_mid < 1 << 16:
                raise ValueError('field 2 out of range (need a 16-bit value)')
            if not 0 <= time_hi_version < 1 << 16:
                raise ValueError('field 3 out of range (need a 16-bit value)')
            if not 0 <= clock_seq_hi_variant < 1 << 8:
                raise ValueError('field 4 out of range (need an 8-bit value)')
            if not 0 <= clock_seq_low < 1 << 8:
                raise ValueError('field 5 out of range (need an 8-bit value)')
            if not 0 <= node < 1 << 48:
                raise ValueError('field 6 out of range (need a 48-bit value)')
            clock_seq = (clock_seq_hi_variant << 8) | clock_seq_low
            int_value = ((time_low << 96) | (time_mid << 80) |
                         (time_hi_version << 64) | (clock_seq << 48) | node)
        if int_value:
            if not 0 <= int_value < 1 << 128:
                raise ValueError('int is out of range (need a 128-bit value)')
        if version:
            if not 1 <= version <= 5:
                raise ValueError('illegal version number')
            # Set the variant to RFC 4122.
            int_value &= ~(0xc000 << 48)
            int_value |= 0x8000 << 48
            # Set the version number.
            int_value &= ~(0xf000 << 64)
            int_value |= version << 76
        self.__dict__['int_value'] = int_value

    def __cmp__(self, other):
        if isinstance(other, UUID):
            return cmp(self.int_value, other.int_value)
        return NotImplemented

    def __hash__(self):
        return hash(self.int_value)

    def __int__(self):
        return self.int_value

    def __repr__(self):
        return 'UUID(%r)' % str(self)

    def __setattr__(self, name, value):
        raise TypeError('UUID objects are immutable')

    def __str__(self):
        hex = '%032x' % self.int_value
        return '%s-%s-%s-%s-%s' % (
            hex[:8], hex[8:12], hex[12:16], hex[16:20], hex[20:])

    def get_bytes(self):
        bytes = ''
        for shift in range(0, 128, 8):
            bytes = chr((self.int_value >> shift) & 0xff) + bytes
        return bytes

    bytes = property(get_bytes)

    def get_fields(self):
        return (self.time_low, self.time_mid, self.time_hi_version,
                self.clock_seq_hi_variant, self.clock_seq_low, self.node)

    fields = property(get_fields)

    def get_time_low(self):
        return self.int_value >> 96

    time_low = property(get_time_low)

    def get_time_mid(self):
        return (self.int_value >> 80) & 0xffff

    time_mid = property(get_time_mid)

    def get_time_hi_version(self):
        return (self.int_value >> 64) & 0xffff

    time_hi_version = property(get_time_hi_version)

    def get_clock_seq_hi_variant(self):
        return (self.int_value >> 56) & 0xff

    clock_seq_hi_variant = property(get_clock_seq_hi_variant)

    def get_clock_seq_low(self):
        return (self.int_value >> 48) & 0xff

    clock_seq_low = property(get_clock_seq_low)

    def get_time(self):
        return (((self.time_hi_version & 0x0fff) << 48) |
                (self.time_mid << 32) | self.time_low)

    time = property(get_time)

    def get_clock_seq(self):
        return (((self.clock_seq_hi_variant & 0x3f) << 8) |
                self.clock_seq_low)

    clock_seq = property(get_clock_seq)

    def get_node(self):
        return self.int_value & 0xffffffffffff

    node = property(get_node)

    def get_hex(self):
        return '%032x' % self.int_value

    hex = property(get_hex)

    def get_urn(self):
        return 'urn:uuid:' + str(self)

    urn = property(get_urn)

    def get_variant(self):
        if not self.int_value & (0x8000 << 48):
            return RESERVED_NCS
        elif not self.int_value & (0x4000 << 48):
            return RFC_4122
        elif not self.int_value & (0x2000 << 48):
            return RESERVED_MICROSOFT
        else:
            return RESERVED_FUTURE

    variant = property(get_variant)

    def get_version(self):
        # The version bits are only meaningful for RFC 4122 UUIDs.
        if self.variant == RFC_4122:
            return int((self.int_value >> 76) & 0xf)

    version = property(get_version)


def _ifconfig_getnode():
    """Get the hardware address on Unix by running ifconfig."""
    import os
    dir = '/sbin/'
    pipe = os.popen(os.path.join(dir, 'ifconfig'))

    for line in pipe:
        words = line.lower().split()
        for i in range(len(words)):
            if words[i] in ['hwaddr', 'ether']:
                return int(words[i + 1].replace(':', ''), 16)


def _ipconfig_getnode():
    """Get the hardware address on Windows by running ipconfig.exe."""
    import os
    import re
    dirs = ['', r'c:\windows\system32', r'c:\winnt\system32']
    try:
        import ctypes
        buffer = ctypes.create_string_buffer(300)
        ctypes.windll.kernel32.GetSystemDirectoryA(buffer, 300)
        dirs.insert(0, buffer.value.decode('mbcs'))
    except BaseException:
        pass
    for dir in dirs:
        try:
            pipe = os.popen(os.path.join(dir, 'ipconfig') + ' /all')
        except IOError:
            continue
        for line in pipe:
            value = line.split(':')[-1].strip().lower()
            if re.match('([0-9a-f][0-9a-f]-){5}[0-9a-f][0-9a-f]', value):
                return int(value.replace('-', ''), 16)


def _netbios_getnode():
    """Get the hardware address on Windows using NetBIOS calls.
    See http://support.microsoft.com/kb/118623 for details."""
    import win32wnet
    import netbios
    ncb = netbios.NCB()
    ncb.Command = netbios.NCBENUM
    ncb.Buffer = adapters = netbios.LANA_ENUM()
    adapters._pack()
    if win32wnet.Netbios(ncb) != 0:
        return
    adapters._unpack()
    for i in range(adapters.length):
        ncb.Reset()
        ncb.Command = netbios.NCBRESET
        ncb.Lana_num = ord(adapters.lana[i])
        if win32wnet.Netbios(ncb) != 0:
            continue
        ncb.Reset()
        ncb.Command = netbios.NCBASTAT
        ncb.Lana_num = ord(adapters.lana[i])
        ncb.Callname = '*'.ljust(16)
        ncb.Buffer = status = netbios.ADAPTER_STATUS()
        if win32wnet.Netbios(ncb) != 0:
            continue
        status._unpack()
        bytes = map(ord, status.adapter_address)
        return ((bytes[0] << 40) + (bytes[1] << 32) + (bytes[2] << 24) +
                (bytes[3] << 16) + (bytes[4] << 8) + bytes[5])

# Thanks to Thomas Heller for ctypes and for his help with its use here.


# If ctypes is available, use it to find system routines for UUID generation.
_uuid_generate_random = _uuid_generate_time = _UuidCreate = None
try:
    import ctypes
    import ctypes.util
    _buffer = ctypes.create_string_buffer(16)

    # The uuid_generate_* routines are provided by libuuid on at least
    # Linux and FreeBSD, and provided by libc on Mac OS X.
    for libname in ['uuid', 'c']:
        try:
            lib = ctypes.CDLL(ctypes.util.find_library(libname))
        except BaseException:
            continue
        if hasattr(lib, 'uuid_generate_random'):
            _uuid_generate_random = lib.uuid_generate_random
        if hasattr(lib, 'uuid_generate_time'):
            _uuid_generate_time = lib.uuid_generate_time

    # On Windows prior to 2000, UuidCreate gives a UUID containing the
    # hardware address.  On Windows 2000 and later, UuidCreate makes a
    # random UUID and UuidCreateSequential gives a UUID containing the
    # hardware address.  These routines are provided by the RPC runtime.
    try:
        lib = ctypes.windll.rpcrt4
    except BaseException:
        lib = None
    _UuidCreate = getattr(lib, 'UuidCreateSequential',
                          getattr(lib, 'UuidCreate', None))
except BaseException:
    pass


def _unixdll_getnode():
    """Get the hardware address on Unix using ctypes."""
    _uuid_generate_time(_buffer)
    return UUID(bytes=_buffer.raw).node


def _windll_getnode():
    """Get the hardware address on Windows using ctypes."""
    if _UuidCreate(_buffer) == 0:
        return UUID(bytes=_buffer.raw).node


def _random_getnode():
    """Get a random node ID, with eighth bit set as suggested by RFC 4122."""
    import random
    return random.randrange(0, 1 << 48) | 0x010000000000


_node = None


def getnode():
    """Get the hardware address as a 48-bit integer.  The first time this
    runs, it may launch a separate program, which could be quite slow.  If
    all attempts to obtain the hardware address fail, we choose a random
    48-bit number with its eighth bit set to 1 as recommended in RFC 4122."""

    global _node
    if _node:
        return _node

    import sys
    if sys.platform == 'win32':
        getters = [_windll_getnode, _netbios_getnode, _ipconfig_getnode]
    else:
        getters = [_unixdll_getnode, _ifconfig_getnode]

    for getter in getters + [_random_getnode]:
        try:
            _node = getter()
        except BaseException:
            continue
        if _node:
            return _node


def uuid1(node=None, clock_seq=None):
    """Generate a UUID from a host ID, sequence number, and the current time.
    If 'node' is not given, getnode() is used to obtain the hardware
    address.  If 'clock_seq' is given, it is used as the sequence number;
    otherwise a random 14-bit sequence number is chosen."""

    # When the system provides a version-1 UUID generator, use it (but don't
    # use UuidCreate here because its UUIDs don't conform to RFC 4122).
    if _uuid_generate_time and node is clock_seq is None:
        _uuid_generate_time(_buffer)
        return UUID(bytes=_buffer.raw)

    import time
    nanoseconds = int(time.time() * 1e9)
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = int(nanoseconds / 100) + 0x01b21dd213814000
    if clock_seq is None:
        import random
        clock_seq = random.randrange(1 << 14)  # instead of stable storage
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    clock_seq_low = clock_seq & 0xff
    clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
    if node is None:
        node = getnode()
    return UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)


def uuid3(namespace, name):
    """Generate a UUID from the MD5 hash of a namespace UUID and a name."""
    import md5
    hash = md5.md5(namespace.bytes + name).digest()
    return UUID(bytes=hash[:16], version=3)


def uuid4():
    """Generate a random UUID."""

    # When the system provides a version-4 UUID generator, use it.
    if _uuid_generate_random:
        _uuid_generate_random(_buffer)
        return UUID(bytes=_buffer.raw)

    # Otherwise, get randomness from urandom or the 'random' module.
    try:
        import os
        return UUID(bytes=os.urandom(16), version=4)
    except BaseException:
        import random
        bytes = [chr(random.randrange(256)) for i in range(16)]
        return UUID(bytes=bytes, version=4)


def uuid5(namespace, name):
    """Generate a UUID from the SHA-1 hash of a namespace UUID and a name."""
    import sha
    hash = sha.sha(namespace.bytes + name).digest()
    return UUID(bytes=hash[:16], version=5)

# The following standard UUIDs are for use with uuid3() or uuid5().


NAMESPACE_DNS = UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_URL = UUID('6ba7b811-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_OID = UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
NAMESPACE_X500 = UUID('6ba7b814-9dad-11d1-80b4-00c04fd430c8')
