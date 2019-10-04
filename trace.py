# *************************************************************************************
#
# redfishConstants - Redfish API global values 
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

from enum import IntEnum
from collections import OrderedDict

class TraceLevel(IntEnum):
    NONE    = 0
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

    tracelevel = TraceLevel.NONE

    preface = {
        TraceLevel.NONE  : '',
        TraceLevel.FATAL : 'FATAL: ',
        TraceLevel.ERROR : 'ERROR: ',
        TraceLevel.WARN  : 'WARNING: ',
        TraceLevel.INFO  : '',
        TraceLevel.VERBOSE : '',
        TraceLevel.DEBUG  : '',
        TraceLevel.TRACE  : ''
    }

    @classmethod
    def setlevel(cls, level):

        if (level < TraceLevel.NONE):
            cls.tracelevel = TraceLevel.NONE
        elif (level > TraceLevel.TRACE):
            cls.tracelevel = TraceLevel.TRACE
        else:
            cls.tracelevel = level

    @classmethod
    def log(cls, level, entry):

        if (cls.tracelevel >= level):
            print("{}{}".format(cls.preface[level], entry))
