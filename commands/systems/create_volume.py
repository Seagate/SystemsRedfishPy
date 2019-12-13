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
# create_volume.py 
#
# ******************************************************************************************
#
# @command create volume
#
# @synopsis Create a volume
#
# @description-start
#
# 'create volume name=[name] size=[size] lun=[lun] pool=[A|B] diskgroup=[group]
#
# Example:
# create volume name=TestVol01 size=100000000000 pool=A
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
# CreateVolumeRequestBody
################################################################################

#
# Example of desired JSON data
#
# {
#     "Name": "AVolume01",
#     "CapacityBytes": 100000000000,
#     "CapacitySources": [
#         {
#             "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
#         }
#     ],
#     "Links": {
#         "ClassOfService": {
#             "@odata.id": "/redfish/v1/StorageServices(1)/ClassesOfService(Default)"
#         }
#     }
# }


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create volume"""
    name = 'create volume'
    command = ''

    @classmethod
    def prepare_url(self, command):
        self.command = command
        return (config.volumes)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Volume: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: create volume name=[name] size=[size] lun=[lun] pool=[A|B] diskgroup=[group]
        # For now, use a simple split based on spaces

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # Name
        jsonType, name = JsonBuilder.getValue('name', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Name', name)

        # CapacityBytes
        jsonType, size = JsonBuilder.getValue('size', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.INTEGER, 'CapacityBytes', size)

        # CapacitySources
        jsonType, pool = JsonBuilder.getValue('pool', self.command)
        if (jsonType is not JsonType.NONE):
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
            JsonBuilder.addElement('main', JsonType.DICT, 'CapacitySources', JsonBuilder.getElement('array'))

        # Links / ClassOfService
        JsonBuilder.newElement('dict', JsonType.DICT, True)
        JsonBuilder.newElement('dict2', JsonType.DICT, True)
        JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.classesOfServiceDefault)
        JsonBuilder.addElement('dict', JsonType.DICT, 'ClassOfService', JsonBuilder.getElement('dict2'))
        JsonBuilder.addElement('main', JsonType.DICT, 'Links', JsonBuilder.getElement('dict'))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

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
