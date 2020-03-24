#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# set_volume.py 
#
# ******************************************************************************************
#
# @command set volume
#
# @synopsis Update volume attributes
#
# @description-start
#
# 'set volume name=[new-name] volume=[serial-number]
#
# Example:
# set volume name=NewTestVol01 volume=00c0ff51124600000e00755e01000000
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CreateRequestBody
################################################################################

#
# Example of desired JSON data
#
# {
#     "Name": "NewTestVol01",
# }


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - set volume"""
    name = 'set volume'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'Volumes'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Set Volume: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: set volume name=[name] volume=[serial-number]
        # For now, use a simple split based on spaces

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # Name
        jsonType, name = JsonBuilder.getValue('name', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Name', name)

        # Volume Serial Number
        jsonType, volume = JsonBuilder.getValue('volume', self.command)
        if (jsonType is JsonType.NONE):
            volume = ''

        url = url + volume
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'PATCH', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

        # HTTP 201 Created
        if (link.urlStatus == 201):

            if (link.jsonData != None):
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Name', link.jsonData['Name']))
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('SerialNumber', link.jsonData['Id']))
            else:
                Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')
        else:
            Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))


    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
