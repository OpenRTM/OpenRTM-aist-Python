#!/usr/bin/env python
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


class Factory:
    """
    """

    FACTORY_OK = 0
    FACTORY_ERROR = 1
    ALREADY_EXISTS = 2
    NOT_FOUND = 3
    INVALID_ARG = 4
    UNKNOWN_ERROR = 5

    ##
    # @if jp
    #
    # @class FactoryEntry
    # @brief FactoryEntry クラス
    #
    # @else
    #
    # @class FactoryEntry
    # @brief FactoryEntry class
    #
    # @endif
    class FactoryEntry:
        """
        """

        ##
        # @if jp
        #
        # @brief コンストラクタ
        #
        # コンストラクタ。
        #
        # @param creator クリエータ用ファンクタ
        # @param destructor デストラクタ用ファンクタ
        #
        # @else
        #
        # @brief Constructor
        #
        # Constructor
        #
        # @param creator Functor for creator.
        # @param destructor Functor for destructor.
        #
        # @endif
        # FactoryEntry(Identifier id, Creator creator, Destructor destructor)
        def __init__(self, id, creator, destructor):
            self.id_ = id
            self.creator_ = creator
            self.destructor_ = destructor
            return

    def __init__(self):
        self._creators = {}
        self._objects = {}

    # bool hasFactory(const Identifier& id)

    def hasFactory(self, id):
        if not id in self._creators:
            return False
        return True

    # std::vector<Identifier> getIdentifiers()

    def getIdentifiers(self):
        idlist = []

        for id in self._creators.keys():
            idlist.append(id)
        idlist.sort()
        return idlist

    # ReturnCode addFactory(const Identifier& id,
    # Creator creator,
    # Destructor destructor)

    def addFactory(self, id, creator, destructor):
        if not creator or not destructor:
            return self.INVALID_ARG

        if id in self._creators:
            return self.ALREADY_EXISTS

        self._creators[id] = Factory.FactoryEntry(id, creator, destructor)
        return self.FACTORY_OK

    # ReturnCode removeFactory(const Identifier& id)

    def removeFactory(self, id):
        if not id in self._creators:
            return self.NOT_FOUND

        del self._creators[id]
        return self.FACTORY_OK

    # AbstractClass* createObject(const Identifier& id)

    def createObject(self, id):
        if not id in self._creators:
            print("Factory.createObject return None id: ", id)
            return None
        obj_ = self._creators[id].creator_()
        #assert(not obj_ in self._objects)
        self._objects[obj_] = self._creators[id]
        return obj_

    # ReturnCode deleteObject(const Identifier& id, AbstractClass*& obj)

    def deleteObject(self, obj, id=None):
        if id:
            if id in self._creators:
                self._creators[id].destructor_(obj)
                del self._objects[obj]
                return self.FACTORY_OK

        if not obj in self._objects:
            return self.NOT_FOUND

        tmp = obj
        self._objects[obj].destructor_(obj)
        del self._objects[tmp]
        return self.FACTORY_OK

    ##
    # @if jp
    #
    # @brief 生成済みオブジェクトリストの取得
    #
    # このファクトリで生成されたオブジェクトのリストを取得する。
    #
    # @return 生成済みオブジェクトリスト
    #
    # @else
    #
    # @brief Getting created objects
    #
    # This operation returns a list of created objects by the factory.
    #
    # @return created object list
    #
    # @endif
    # std::vector<AbstractClass*> createdObjects()

    def createdObjects(self):
        objects_ = []
        for id_ in self._objects.keys():
            objects_.append(id_)

        return objects_

    ##
    # @if jp
    #
    # @brief オブジェクトがこのファクトリの生成物かどうか調べる
    #
    # @param obj 対象オブジェクト
    # @return true: このファクトリの生成物
    #         false: このファクトリの生成物ではない
    #
    # @else
    #
    # @brief Whether a object is a product of this factory
    #
    # @param obj A target object
    # @return true: The object is a product of the factory
    #         false: The object is not a product of the factory
    #
    # @return created object list
    #
    # @endif
    # bool isProducerOf(AbstractClass* obj)

    def isProducerOf(self, obj):
        return obj in self._objects

    ##
    # @if jp
    #
    # @brief オブジェクトからクラス識別子(ID)を取得する
    #
    # 当該オブジェクトのクラス識別子(ID)を取得する。
    #
    # @param obj [in] クラス識別子(ID)を取得したいオブジェクト
    # @param id [out] クラス識別子(ID)
    # @return リターンコード NOT_FOUND: 識別子が存在しない
    #                        FACTORY_OK: 正常終了
    # @else
    #
    # @brief Getting class identifier (ID) from a object
    #
    # This operation returns a class identifier (ID) from a object.
    #
    # @param obj [in] An object to investigate its class ID.
    # @param id [out] Class identifier (ID)
    # @return Return code NOT_FOUND: ID not found
    #                        FACTORY_OK: normal return
    # @endif
    # ReturnCode objectToIdentifier(AbstractClass* obj, Identifier& id)

    def objectToIdentifier(self, obj):
        if not obj in self._objects:
            return self.NOT_FOUND, -1

        id = self._objects[obj].id_
        return self.FACTORY_OK, id

    ##
    # @if jp
    #
    # @brief オブジェクトのコンストラクタを取得する
    #
    # このファクトリで生成されたオブジェクトのコンストラクタを取得する。
    # obj はこのファクトリで生成されたものでなければならない。予め
    # isProducerOf() 関数で当該オブジェクトがこのファクトリの生成物で
    # あるかどうかをチェックしなければならない。
    #
    # @return オブジェクトのデストラクタ
    #
    # @else
    #
    # @brief Getting destructor of the object
    #
    # This operation returns a constructor of the object created by
    # the factory.  obj must be a product of the factory.  User must
    # check if the object is a product of the factory by using
    # isProducerOf()-function, before using this function.
    #
    # @return destructor of the object
    #
    # @endif
    # Creator objectToCreator(AbstractClass* obj)

    def objectToCreator(self, obj):
        return self._objects[obj].creator_

    ##
    # @if jp
    #
    # @brief オブジェクトのデストラクタを取得する
    #
    # このファクトリで生成されたオブジェクトのデストラクタを取得する。
    # obj はこのファクトリで生成されたものでなければならない。予め
    # isProducerOf() 関数で当該オブジェクトがこのファクトリの生成物で
    # あるかどうかをチェックしなければならない。
    #
    # @return オブジェクトのデストラクタ
    #
    # @else
    #
    # @brief Getting destructor of the object
    #
    # This operation returns a destructor of the object created by
    # the factory.  obj must be a product of the factory.  User must
    # check if the object is a product of the factory by using
    # isProducerOf()-function, before using this function.
    #
    # @return destructor of the object
    #
    # @endif
    # Destructor objectToDestructor(AbstractClass* obj)

    def objectToDestructor(self, obj):
        return self._objects[obj].destructor_


gfactory = None


class GlobalFactory(Factory):
    def __init__(self):
        Factory.__init__(self)
        pass

    def instance():
        global gfactory

        if gfactory is None:
            gfactory = GlobalFactory()

        return gfactory

    instance = staticmethod(instance)

    def __del__(self):
        pass
