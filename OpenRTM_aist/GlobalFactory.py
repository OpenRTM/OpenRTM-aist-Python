#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##
# @file GlobalFactory.py
# @brief generic Factory template class
# @date $Date$
# @author Noriaki Ando <n-ando@aist.go.jp> and Shinji Kurihara
#
# Copyright (C) 2009
#     Noriaki Ando
#     Task-intelligence Research Group,
#     Intelligent Systems Research Institute,
#     National Institute of
#         Advanced Industrial Science and Technology (AIST), Japan
#     All rights reserved.
#


import typing as _typing


_Identifier = _typing.TypeVar("_Identifier", bound=_typing.Hashable)
_Product = _typing.TypeVar("_Product")
_Properties = _typing.TypeVar("_Properties")


class Factory(_typing.Generic[_Identifier, _Product, _Properties]):
    """
    """

    FACTORY_OK = 0
    FACTORY_ERROR = 1
    ALREADY_EXISTS = 2
    NOT_FOUND = 3
    INVALID_ARG = 4
    UNKNOWN_ERROR = 5

    def __init__(self) -> None:
        self._creators: _typing.Dict[_Identifier, FactoryEntry[_Identifier, _Product, _Properties]] = {}

    # bool hasFactory(const Identifier& id)

    def hasFactory(self, id: _Identifier) -> bool:
        if id not in self._creators:
            return False
        return True

    # std::vector<Identifier> getIdentifiers()

    def getIdentifiers(self) -> _typing.List[_Identifier]:
        idlist = []

        for id in self._creators.keys():
            idlist.append(id)
        idlist.sort()
        return idlist

    # ReturnCode addFactory(const Identifier& id,
    # Creator creator)

    def addFactory(self, id: _Identifier, creator: _typing.Optional[_typing.Callable[[], _Product]],
                   prop: _typing.Optional[_Properties] = None) -> int:
        if not creator:
            return self.INVALID_ARG

        if id in self._creators:
            return self.ALREADY_EXISTS

        self._creators[id] = FactoryEntry(id, creator, prop)
        return self.FACTORY_OK

    # ReturnCode removeFactory(const Identifier& id)

    def removeFactory(self, id: _Identifier) -> int:
        if id not in self._creators:
            return self.NOT_FOUND

        del self._creators[id]
        return self.FACTORY_OK

    # AbstractClass* createObject(const Identifier& id)

    def createObject(self, id: _Identifier) -> _typing.Optional[_Product]:
        if id not in self._creators:
            print("Factory.createObject return None id: ", id)
            return None
        obj_ = self._creators[id].creator()
        return obj_

    def getProperties(self, id: _Identifier) -> _typing.Optional[_Properties]:
        if id not in self._creators:
            print("Factory.getProperties return None id: ", id)
            return None
        return self._creators[id].prop


class FactoryEntry(_typing.Generic[_Identifier, _Product, _Properties]):
    def __init__(self, id: _Identifier, creator: _typing.Callable[[], _Product],
                 prop: _typing.Optional[_Properties] = None) -> None:
        self._id = id
        self._creator = creator
        self._prop = prop

    @property
    def id(self) -> _Identifier:
        return self._id

    @property
    def creator(self) -> _typing.Callable[[], _Product]:
        return self._creator

    @property
    def prop(self) -> _typing.Optional[_Properties]:
        return self._prop


gfactory = None


class GlobalFactory(Factory[_typing.Any, _typing.Any, _typing.Any]):
    def __init__(self) -> None:
        Factory.__init__(self)
        pass

    def instance() -> "GlobalFactory":
        global gfactory

        if gfactory is None:
            gfactory = GlobalFactory()

        return gfactory

    instance = staticmethod(instance)

    def __del__(self) -> None:
        pass
