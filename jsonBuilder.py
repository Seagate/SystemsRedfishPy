# *************************************************************************************
#
# jsonBuilder - A common module used to produce JSON data objects from a flexible list of items. 
#
# The main use of this module is to create a JSON object in order to POST or PATCH it.
# To create a simple JSON object, follow these steps:
#
#     1) Clear all elements by calling startNew()
#     2) Create a new element and name it. The name is used for adding to the same element
#     3) Add as many new elements to the named object as desired
#     4) Use the same name to retirve the JSON object.
#
#     JsonBuilder.startNew()
#     JsonBuilder.newElement('main', JsonType.DICT)
#     JsonBuilder.addElement('main', JsonType.STRING, 'UserName', redfishConfig.get_value('username'))
#     JsonBuilder.addElement('main', JsonType.STRING, 'Password', redfishConfig.get_value('password'))
#     jsonData = JsonBuilder.getElement('main')
#
# There are more complex objects created by commands such as map_volume.py. To debug, use
# the '!dumppostdata 1' command to see the JSON data created and being posted or patched.
#
# -------------------------------------------------------------------------------------

# Copyright 2019 Seagate Technology LLC or one of its affiliates.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology LLC.
# Portions may also be trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized in writing by
# Seagate Technology LLC is prohibited. All rights are expressly reserved by
# Seagate Technology LLC.
#
# -------------------------------------------------------------------------------------
#

import json
from trace import TraceLevel, Trace

################################################################################
# JsonType
################################################################################
class JsonType:
    NONE      = 0
    STRING    = 1
    INTEGER   = 2
    DICT      = 3
    ARRAY     = 4

    @classmethod
    def toType(cls, i):
        switcher = {
            cls.NONE: 'NONE',
            cls.STRING: 'STRING',
            cls.INTEGER: 'INTEGER',
            cls.DICT: 'DICT',
            cls.ARRAY: 'ARRAY'
        }
        return switcher.get(i,"Invalid JsonType")

################################################################################
# JsonObject
################################################################################
class JsonObject:
    jsonType = JsonType.NONE
    label = ''
    value = ''

    def __init__(self, jsonType, label, value):
        self.jsonType = jsonType
        self.label = label
        self.value = value

################################################################################
# JsonElement
################################################################################
class JsonElement:
    name = ''
    value = None

    def __init__(self, name, value):
        self.name = name
        self.value = value

################################################################################
# JsonBuilder
################################################################################
class JsonBuilder:

    elements = []

    @classmethod
    def startNew(cls):
        cls.elements = []

    @classmethod
    def getElement(cls, name):
        element = None
        for i in range(len(cls.elements)):
            if (cls.elements[i].name == name):
                element = cls.elements[i].value
        return element

    @classmethod
    def resetElement(cls, name):
        for i in range(len(cls.elements)):
            if (cls.elements[i].name == name):
                if (isinstance(cls.elements[i].value, dict)):
                    cls.elements[i].value = {}
                elif (isinstance(cls.elements[i].value, list)):
                    cls.elements[i].value = []
                else:
                    Trace.log(TraceLevel.WARN, 'resetElement with name ({}) was not handled, type is ({})'.format(name, str(type(cls.elements[i].value))))

    @classmethod
    def newElement(cls, name, jsonType, force=False):

        exists = cls.getElement(name)

        if (force is True):
            cls.resetElement(name)
        elif (cls.getElement(name) is not None):
            Trace.log(TraceLevel.ERROR, 'Element with name ({}) already exists, choose a unique name or force ({})'.format(name, force))
            return

        if (jsonType == JsonType.ARRAY):
            element = []
        elif (jsonType == JsonType.DICT):
            element = {}
        else:
            element = None

        if (exists is None):
            cls.elements.append(JsonElement(name, element))

    @classmethod
    def addElement(cls, name, jsonType, label, value):

        jsonEntity = cls.getElement(name)
        if (jsonEntity is None):
            Trace.log(TraceLevel.ERROR, 'Could not find JSON element with name ({})'.format(name))
            return

        Trace.log(TraceLevel.DEBUG, '++ addElement: name={} type={} label={} value={}'.format(name, JsonType.toType(jsonType), label, value))

        # DICT
        if (isinstance(jsonEntity, dict)):
            Trace.log(TraceLevel.DEBUG, '++ addElement: DICT ({}) label={} value={}'.format(JsonType.toType(jsonType), label, value))
            if (jsonType == JsonType.STRING):
                jsonEntity.update({label: value})
            elif (jsonType == JsonType.INTEGER):
                jsonEntity.update({label: value})
            elif (jsonType == JsonType.DICT):
                if (label == ''):
                    jsonEntity.update(value)
                else:
                    jsonEntity.update({label: value})

        # LIST
        elif (isinstance(jsonEntity, list)):
            Trace.log(TraceLevel.DEBUG, '++ addElement: LIST ({}) label={} value={}'.format(JsonType.toType(jsonType), label, value))
            if (jsonType == JsonType.STRING):
                jsonEntity.append(value)
            elif (jsonType == JsonType.DICT):
                if (label == ''):
                    jsonEntity.append(value)
                else:
                    jsonEntity.update({label: value})

    @classmethod
    def displayElements(cls):

        Trace.log(TraceLevel.INFO, 'JsonBuilder displayElements (elements={})'.format(len(cls.elements)))
        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '  Item      Name              Type')
        Trace.log(TraceLevel.INFO, '  --------------------------------')

        for i in range(len(cls.elements)):
            Trace.log(TraceLevel.INFO, '  {0: >4}  {1: >8}  {2: >16}'.format(i, cls.elements[i].name, str(type(cls.elements[i].value))))

        Trace.log(TraceLevel.INFO, '')

    @classmethod
    def displayJson(cls, name):

        Trace.log(TraceLevel.INFO, 'JsonBuilder displayJson (name={})'.format(name))

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[[ JSON DATA ]]')

        jsonEntity = cls.getElement(name)
        if (jsonEntity is not None):
            print(json.dumps(jsonEntity, indent=4))
        else:
            Trace.log(TraceLevel.INFO, 'Could not find JSON element with name ({})'.format(name))
        Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')

    @classmethod
    def getValue(cls, label, command):
        jsonType = JsonType.NONE
        jsonValue = None

        # The command is split based on spaces between ordered pairs
        # There are three types of possible types:
        # Type 1 - STRING: label="value" or label='value'
        # Type 2 - INTEGER: label=value
        # Type 3 - ARRAY: label=value1,value2,value3

        words = command.split(' ')
        for i in range(len(words)):
            if ('=' in words[i]):
                tokens = words[i].split('=')
                if (len(tokens) >= 2):
                    if (tokens[0] == label):
                        if ("'" in tokens[1]):
                            jsonType = JsonType.STRING
                            jsonValue = tokens[1].replace("'", "")
                            Trace.log(TraceLevel.TRACE, '      -- Adding STRING {}={}'.format(tokens[0], jsonValue))

                        elif ('"' in tokens[1]):
                            jsonType = JsonType.STRING
                            jsonValue = tokens[1].replace('"', '')
                            Trace.log(TraceLevel.TRACE, '      -- Adding STRING {}={}'.format(tokens[0], jsonValue))

                        elif (',' in tokens[1]):
                            jsonType = JsonType.ARRAY
                            jsonValue = []
                            arrayItems = tokens[1].split(',')
                            for item in range(len(arrayItems)):
                                Trace.log(TraceLevel.TRACE, '      -- Adding ARRAY ITEM[{}] {}={}'.format(item, tokens[0], arrayItems[item]))
                                jsonValue.append(arrayItems[item])

                        else:
                            jsonType = JsonType.INTEGER
                            jsonValue = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding INTEGER {}={}'.format(tokens[0], jsonValue))
        
        return jsonType, jsonValue

