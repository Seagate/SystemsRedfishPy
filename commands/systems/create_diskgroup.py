#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of thThe MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# create_diskgroup.py 
#
# ******************************************************************************************
#
# @command create diskgroup
#
# @synopsis Create a disk group and add it to a pool
#
# @description-start
#
# 'create diskgroup name=[name] disks=[disk1,disk2,disk3,disk4] pool=[A|B] level=[raid0|raid1|raid5|raid6|adapt]'
#
# Example:
# create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1
#
# @description-end
#

import config
import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CreateDiskGroupRequestBody
################################################################################

#
# Example of desired JSON data
#
# {
#     "Name": "dgA01",
#     "CapacitySources": {
#         "ProvidingDrives": [
#             {
#                 "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.7"
#             },
#             {
#                 "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.8"
#             }
#         ]
#     },
#     "AllocatedPools": {
#         "Members": [
#             {
#                 "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
#             }
#         ]
#     },
#     "ClassesOfService": {
#         "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID1"
#     }
# }

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create diskgroup"""
    name = 'create diskgroup'
    command = ''
  
    @classmethod
    def prepare_url(self, command):
        self.command = command
        return (config.storagePools)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Disk Group: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: 'create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1'
        # For now, use a simple split based on spaces

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)
        
        # Name
        jsonType, name = JsonBuilder.getValue('name', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Name', name)

        # CapacitySources
        jsonType, disks = JsonBuilder.getValue('disks', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('dict', JsonType.DICT, True)
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(disks)):
                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.drives + disks[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            else:
                JsonBuilder.newElement('dict2', JsonType.DICT, True)
                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.drives + disks)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))

            JsonBuilder.addElement('dict', JsonType.DICT, 'ProvidingDrives', JsonBuilder.getElement('array'))
            JsonBuilder.addElement('main', JsonType.DICT, 'CapacitySources', JsonBuilder.getElement('dict'))

        # AllocatedPools
        jsonType, pool = JsonBuilder.getValue('pool', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('dict', JsonType.ARRAY, True)
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(pool)):
                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.storagePools + pool[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            else:
                JsonBuilder.newElement('dict2', JsonType.DICT, True)
                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.storagePools + pool)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))

            JsonBuilder.addElement('dict', JsonType.DICT, 'Members', JsonBuilder.getElement('array'))
            JsonBuilder.addElement('main', JsonType.DICT, 'AllocatedPools', JsonBuilder.getElement('dict'))

        # ClassesOfService
        jsonType, level = JsonBuilder.getValue('level', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('dict', JsonType.DICT, True)
            JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.classesOfService + level.upper())
            JsonBuilder.addElement('main', JsonType.DICT, 'ClassesOfService', JsonBuilder.getElement('dict'))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

        # HTTP 201 Created
        if (link.urlStatus == 201):
            if (link.jsonData != None):
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('SerialNumber', link.jsonData['Name']))
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Id', link.jsonData['Id']))
            else:
                Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')
        elif (link.urlStatus == 204):
                Trace.log(TraceLevel.TRACE, '   -- No representation of the created resource')
        else:
            Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
