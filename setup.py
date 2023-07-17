#!/usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-

import setuptools
from setuptools.command.build import build

build.sub_commands.append(('build_idl', None))

setuptools.setup()
