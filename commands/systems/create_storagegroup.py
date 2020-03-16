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
# create_storagegroup.py 
#
# ******************************************************************************************
#
# @command create storagegroup
#
# @synopsis Create a storage group to map a volume making it visibile to a host or hosts.
#
# @description-start
#
# 'create storagegroup lun=[LogicalUnitNumber] volume=[serial-number] access=[read|read-write] ports=[A0,B0,A1,B1] initiators=[endpoint]
#
# Required: volume, lun, initiators
#
# Optional: access (default to read-write) and ports (defaults to all ports)
#
# Note: Only one initiator and one volume is allowed with this revision.
#
# Example:
# create storagegroup lun='1' volume=00c0ff511246000026fdc35d01000000 access=read-write ports=A0,B0 initiators=500605b00ab61310
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from commands.storagegroup import CreateStorageGroupRequestProperties
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create storagegroup"""
    name = 'create storagegroup'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'StorageGroups'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create StorageGroup: ({})...'.format(self.command))

        jsonRequest = CreateStorageGroupRequestProperties(redfishConfig, self.command, True)

        if jsonRequest is not None:
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(jsonRequest, indent=4))

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
