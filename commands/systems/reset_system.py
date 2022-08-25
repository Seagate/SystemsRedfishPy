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
# reset_system.py 
#
# ******************************************************************************************
#
# @command reset system [<json | file>]
#
# @synopsis Reset the active storage controller based on the 'ipaddress' configuration value.
#
# @description-start
#
# 'reset system' will reset the storage controller associated with the 'ipaddress' configuration
# value. The 'SystemId' discovery value is used for this purpose. This command uses the
# following Redfish operation:
#
#     http post /redfish/v1/Systems/{SystemId}/Actions/ComputerSystem.Reset
#
# The parameter <json | file> is option. If JSON data is not supplied either inline
# using {} or through a file, then the following default JSON data will be sent:
#
#     { "ResetType": "GracefulRestart" }
#
# Examples:
#      reset system
#      reset system { "ResetType": "GracefulRestart" }
#      reset system json/reset.json
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.label import Label
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus
import config
import json


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - reset system"""
    name = 'reset system'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        uri = RedfishSystem.get_uri(redfishConfig, 'SystemId') + 'Actions/ComputerSystem.Reset'
        return (uri)

    @classmethod
    def process_json(self, redfishConfig, url):

        # Don't attempt command if a session is not active
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is None:
            return

        _, jsonData = ArgExtract.get_json(self.command, 2)
        if not jsonData:
            jsonData = { "ResetType": "GracefulRestart" }

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, jsonData)

        # Execute: http POST /redfish/v1/Systems/{SystemId}/Actions/ComputerSystem.Reset
        Trace.log(TraceLevel.INFO, '-- http post {} {}'.format(url, jsonData))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, jsonData)
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
