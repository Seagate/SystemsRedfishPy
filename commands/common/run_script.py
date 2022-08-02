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
# run_script.py 
#
# ******************************************************************************************
#
# @command run script [filename]
#
# @synopsis Run a script file
#
# @description-start
#
# Use the 'run script' command to run a script file.
#
# Example:
#     run script scripts/create_volumes.rfs
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishScript import RedfishScript
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - run script """
    name = 'run script'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        commandFull = command.strip()
        Trace.log(TraceLevel.DEBUG, '   SET commandFull: ({})'.format(commandFull))
        filename = commandFull.replace('run script ', '', 1)
        Trace.log(TraceLevel.DEBUG, '   SET filename: ({})'.format(filename))
        return (filename)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, 'run script...START ({})'.format(url))
        RedfishScript.execute_script(redfishConfig, url)

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
