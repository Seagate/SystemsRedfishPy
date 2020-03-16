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
# map_volume.py 
#
# ******************************************************************************************
#
# @command map volume
#
# @synopsis Create or update a storage group to map a volume making it visibile to a host or hosts.
#
# @description-start
#
# 'map volume storagegroup=[serial-number] lun=[LogicalUnitNumber] volume=[serial-number] access=[read|read-write] ports=[A0,B0,A1,B1] initiators=[endpoint]
#
# Required: storagegroup, volume
#
# Optional: lun, access, ports, and initiators (but you have to provide at least one to invoke an update)
#
# Examples:
#
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 lun=44
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 access=read
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 ports=A0,B0
#
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 lun=44 access=read-write ports=A0,B0
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from commands.storagegroup import CreateStorageGroupRequestProperties
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - map volume"""
    name = 'map volume'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'StorageGroups'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ map volume: ({})...'.format(self.command))

        jsonType, storagegroup = JsonBuilder.getValue('storagegroup', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.ERROR, 'The storagegroup parameter is required, parse results (storagegroup={})...'.format(storagegroup))
            return

        jsonRequest = CreateStorageGroupRequestProperties(redfishConfig, self.command, False)

        if jsonRequest is not None:
            url = url + storagegroup
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'PATCH', True, json.dumps(jsonRequest, indent=4))
    
            Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
            Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))
    
            # HTTP 201 Created
            if (link.urlStatus == 201):
                if (link.jsonData != None):
                    Trace.log(TraceLevel.TRACE, '   -- {0: <14}: {1}'.format('Id', link.jsonData['Id']))
                else:
                    Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')
            else:
                Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))
        else:
            Trace.log(TraceLevel.INFO, 'Unable to create JSON request data from command line: {}'.format(self.command))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
