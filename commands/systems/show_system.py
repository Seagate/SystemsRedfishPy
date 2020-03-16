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
# show_system.py 
#
# ******************************************************************************************
#
# @command show system
#
# @synopsis Display all storage groups, volumes, pools, and disk groups.
#
# @description-start
#
# 'show system' will display all storage groups, volumes, pools, and disk groups.
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.label import Label
from core.redfishCommand import RedfishCommand
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
import config


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - purge system"""
    name = 'purge system'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        return (None)

    @classmethod
    def process_json(self, redfishConfig, url):

        # Don't attempt to purge if a session is not active
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is None:
            Trace.log(TraceLevel.INFO, '-- A valid session ({}) was not found!'.format(sessionId))
            return

        RedfishCommand.execute(redfishConfig, 'show storagegroups', True)
        RedfishCommand.execute(redfishConfig, 'show volumes', True)
        RedfishCommand.execute(redfishConfig, 'show pools', True)
        RedfishCommand.execute(redfishConfig, 'show diskgroups', True)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
