#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# assert.py 
#
# ******************************************************************************************
#
# @command assert [operator]
#
# @synopsis Compare two values and fail if values do not meet the condition
#
# @description-start
#
# Use the 'assert' command in a script to verify the results of a prior operation.
#
# Usage: assert [operator] [value1] [value2]
#
# Example:
#
#     // Test whether the prior http operation was successful. In this case, the command
#     // was expected to pass.
#     assert = $httpstatus 200
#
#     // Test whether the prior http oprtation failed with a status of 400. In this case,
#     // the command was expected to fail.
#     assert = $httpstatus 400
# 
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from commands.help_common import Help
from core.argExtract import ArgExtract
from core.label import Label
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - assert """
    name = 'assert'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        return (command)

    @classmethod
    def process_json(self, redfishConfig, url):
        command = url
        _, operator = ArgExtract.get_value(command, 1)
        _, value1 = ArgExtract.get_value(command, 2)
        value1 = Label.decode(value1, value1)
        _, value2 = ArgExtract.get_value(command, 3)
        value2 = Label.decode(value2, value2)

        Trace.log(TraceLevel.DEBUG, 'Operator ({}), value1({}), value2({})'.format(operator, value1, value2))

        if (operator == '='):
            if str(value1) == str(value2):
                Trace.log(TraceLevel.INFO, 'ASSET({}): PASS value1({}) == value2({})'.format(operator, value1, value2))
            else:
                Trace.log(TraceLevel.INFO, 'ASSET({}): FAIL value1({}) != value2({})'.format(operator, value1, value2))
                exit(1)
        else:
            Trace.log(TraceLevel.INFO, 'Operator ({}) is NOT supported'.format(operator))

    @classmethod
    def display_results(self, redfishConfig):
        self.name = ''
