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
# save_session.py 
#
# ******************************************************************************************
#
# @command save session <id> <key>
#
# @synopsis Update configuration data with established session data
#
# @description-start
#
# This command stores session data that was established using the HTTP POST command instead
# of the create session command. Storing the session credentials allows other HTTP commands
# to be executed using the credentials.
#
# After executing a http post /redfish/v1/SessionService/Sessions credentials.json json\credentials.json
#   The <id> value is returned in the JSON data as "Id"
#   The <key> value is returned in the HTTP header as "X-Auth-Token"
#
# Example:
# 
# (redfish) save session 6 5c4c19abe41c01f0a22c6a45b0ad88a0
# 
# [] Redfish session saved (6:5c4c19abe41c01f0a22c6a45b0ad88a0)
# 
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.label import Label
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - save session """
    name = 'save session'

    def prepare_url(self, redfishConfig, command):
        return (command)

    @classmethod
    def process_json(self, redfishConfig, url):
        command = url
        _, session_id = ArgExtract.get_value(command, 2)
        Label.encode(config.sessionIdVariable, session_id)
        _, session_key = ArgExtract.get_value(command, 3)
        redfishConfig.sessionKey = session_key
        if (session_key != ''):
            redfishConfig.sessionValid = True

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] Redfish session saved ({}:{})'.format(Label.decode(config.sessionIdVariable), redfishConfig.sessionKey))
