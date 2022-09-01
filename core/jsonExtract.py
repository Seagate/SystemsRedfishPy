#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# jsonExtract.py - A module used to extract key values from JSON data. 
#
# ******************************************************************************************
#

from core.trace import TraceLevel, Trace

################################################################################
# JsonExtract
################################################################################
class JsonExtract:

    indentLevel = 4

    @classmethod
    def do_extract(cls, obj, arr, parent, key, occurrence, parentFound, calls):
        """Recursively search for values of key in JSON tree."""

        if parent is None:
            parentFound = True

        Trace.log(TraceLevel.TRACE, '{}extract: {} | {} | {} | {} | {} | {}'.format(' ' * (cls.indentLevel*calls), obj, arr, parent, key, parentFound, occurrence))

        if isinstance(obj, dict):
            for k, v in obj.items():
                Trace.log(TraceLevel.TRACE, '{}   k,v: {} | {} '.format(' ' * (cls.indentLevel*calls), k, v))
                if isinstance(v, (dict, list)):
                    calls += 1
                    if k == parent:
                        parentFound = True
                    cls.do_extract(v, arr, parent, key, occurrence, parentFound, calls)
                    Trace.log(TraceLevel.TRACE, '{}arr: {}'.format(' ' * (cls.indentLevel*calls), arr))
                    calls -= 1
                elif k == key:
                    Trace.log(TraceLevel.TRACE, '{}   ++ k,key: {} | {} | {} | {}'.format(' ' * (cls.indentLevel*calls), k, key, parentFound, v))
                    if parentFound:
                        arr.append(v)
                        if parent is not None:
                            parentFound = False
        elif isinstance(obj, list):
            for item in obj:
                Trace.log(TraceLevel.TRACE, '{}   item: {} '.format(' ' * (cls.indentLevel*calls), item))
                calls += 1
                cls.do_extract(item, arr, parent, key, occurrence, parentFound, calls)
                calls -= 1
    
        Trace.log(TraceLevel.TRACE, '{}return: {}'.format(' ' * (cls.indentLevel*calls), arr))
        return arr

    @classmethod
    def get_value(cls, obj, parent, key, occurrence):
        """Extract a value from complex JSON data based on parent/key combination."""
        arr = []
        calls = 0
        results = cls.do_extract(obj, arr, parent, key, occurrence, False, calls)
        Trace.log(TraceLevel.TRACE, 'results: {}'.format(results))

        try:
            if occurrence > 0:
                result = results[occurrence-1]
            else:
                result = None
        except:
            result = None

        return result

    @classmethod
    def extract_list(cls, obj, key, valueArray):
        """Recursively extract values of key in complex JSON data."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    cls.extract_list(v, key, valueArray)
                elif k == key:
                    valueArray.append(v)
        elif isinstance(obj, list):
            for item in obj:
                cls.extract_list(item, key, valueArray)
        return valueArray

    @classmethod
    def get_values(cls, obj, key):
        """Extract all values from complex JSON data based on a key."""
        valueArray = []
        results = cls.extract_list(obj, key, valueArray)
        Trace.log(TraceLevel.TRACE, 'results: {}'.format(results))
        return results
