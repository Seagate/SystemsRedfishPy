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
# trace.py - A module used to display various levels of information, info and debug. 
#
# ******************************************************************************************
#

from enum import IntEnum

class TraceLevel(IntEnum):
    ALWAYS  = 0
    FATAL   = 1
    ERROR   = 2
    WARN    = 3
    INFO    = 4
    VERBOSE = 5
    DEBUG   = 6
    TRACE   = 7

################################################################################
# Trace
################################################################################
class Trace:

    tracelevel = TraceLevel.ALWAYS
    tracelabels = ["ALWAYS", "FATAL", "ERROR", "WARN", "INFO", "VERBOSE", "DEBUG", "TRACE"]

    preface = {
        TraceLevel.ALWAYS  : '',
        TraceLevel.FATAL   : 'FATAL: ',
        TraceLevel.ERROR   : 'ERROR: ',
        TraceLevel.WARN    : 'WARNING: ',
        TraceLevel.INFO    : '',
        TraceLevel.VERBOSE : '',
        TraceLevel.DEBUG   : '',
        TraceLevel.TRACE   : ''
    }

    @classmethod
    def setlevel(cls, level):

        newlevel = int(level)
        try:
            if (newlevel < TraceLevel.ALWAYS):
                cls.tracelevel = TraceLevel.ALWAYS
            elif (newlevel > TraceLevel.TRACE):
                cls.tracelevel = TraceLevel.TRACE
            else:
                cls.tracelevel = newlevel
        except Exception as e:
            Trace.log(TraceLevel.ERROR, '   -- Unable to set trace level ({}) for cls {}: Exception: {}'.format(newlevel, cls, str(e)))

    @classmethod
    def getlevel(cls):
        return cls.tracelevel, cls.tracelabels[cls.tracelevel]

    @classmethod
    def getlevelint(cls):
        return cls.tracelevel

    @classmethod
    def log(cls, level, entry):

        if (level == TraceLevel.ALWAYS or cls.tracelevel >= level):
            print("{}{}".format(cls.preface[level], entry))
