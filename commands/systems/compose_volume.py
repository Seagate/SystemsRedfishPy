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
# compose_volume.py 
#
# ******************************************************************************************
#
# @command compose volume
#
# @synopsis Compose a volume using the Redfish Composition Service
#
# @description-start
#
# 'compose volume name=[name] size=[size] raid=[type] lun=[0-1023] access=[read|read-write] blocks=[disk1,disk2,disk3,disk4] fabric=[type] ports=[A0,B0,A1,B1] initiators=[endpoint]'
#
# Note:
#     This command is only valid for Redfish Serversion Version 2.
#
# Parameters:
#     The 'name' parameter must be unique amongst all volumes, for example ComposedVolume01
#     The 'size' or 'CapacityBytes' parameter specifies the desired size of the 
#     The 'raid' parameter specifies RAIDType with possible values: raid0|raid1|raid5|raid6|adapt
#     The 'lun' parameter specifies LogicalUnitNumber and is used to map the volume to a host. Zero may be reserved on some systems.
#     The 'access' parameter specifies AccessCapabilities and is used to map the volume to a host. 
#     The 'blocks' parameter specifies ResourceBlocks and is used to create the storage disk group.
#     The 'fabric' parameter specifies one of the presented /redfish/v1/Fabrics - SAS, FC, iSCSI
#     The 'ports' parameter specifies ServerEndpointGroups and is used to map the volume to the host initiator.
#     The 'initiators' parameter specifies ClientEndpointGroups and is used to map the volume to the host initiator.
#
#     Note: Use 'http get http get /redfish/v1/Systems/Capabilities' to determine which parameters are required.
#
# Examples:
#     compose volume name=ComposedVolume01 size=100000000000 raid=raid6 lun=1 access=read-write blocks=0.0,0.1,0.2,0.3 fabric=SAS ports=A0,A1,B0,B1 initiators=500605b00db9a070
#     compose volume name=ComposedVolume02 size=100000000000 raid=raid5 lun=2 access=read-write blocks=0.4,0.5,0.6,0.7 fabric=SAS ports=A0,A1,B0,B1 initiators=500605b00db9a071
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
#     "Name": "ComposedVolume01",
#     "Description": "Composed Volume 01",
#     "RAIDType": "RAID6",
#     "CapacityBytes": 1000000000,
#     "LogicalUnitNumber": 0,
#     "AccessCapabilities": [
#         "Read",
#         "Write"
#     ],
#     "Links": {
#         "ClientEndpointGroups": [
#             {
#                 "@odata.id": "/redfish/v1/Fabrics/SAS/Endpoints/500605b00db9a070"
#             }
#         ],
#         "ResourceBlocks": [
#             {
#                 "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0"
#             },
#             {
#                 "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.1"
#             },
#             {
#                 "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.2"
#             },
#             {
#                 "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.3"
#             }
#         ],
#         "ServerEndpointGroups": [
#             {
#                 "@odata.id": "/redfish/v1/Fabrics/SAS/Endpoints/A0"
#             },
#             {
#                 "@odata.id": "/redfish/v1/Fabrics/SAS/Endpoints/A1"
#             },
#             {
#                 "@odata.id": "/redfish/v1/Fabrics/SAS/Endpoints/B0"
#             },
#             {
#                 "@odata.id": "/redfish/v1/Fabrics/SAS/Endpoints/B1"
#             }
#         ]
#     }
# }

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - compose volume"""
    name = 'compose volume'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'Systems'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Compose Volume: ({})...'.format(self.command))

        if (redfishConfig.get_version() < 2):
            Trace.log(TraceLevel.INFO, 'ERROR: compose volume is only supported in service version 2: (ServiceVersion={})'.format(redfishConfig.get_version()))
            return

        compServiceUrl = RedfishSystem.get_uri(redfishConfig, 'CompositionService')
        fabricsUrl = RedfishSystem.get_uri(redfishConfig, 'Fabrics')

        jsonType, fabric = JsonBuilder.getValue('name', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.INFO, 'ERROR: compose volume requires that you provide a fabric (SAS, FC, iSCSI, etc.)')
            return

        # From the command, build up the required JSON data

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # Name & Description
        jsonType, name = JsonBuilder.getValue('name', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Name', name)
            JsonBuilder.addElement('main', JsonType.STRING, 'Description', 'Composed Volume ' + name)

        # RAIDType
        jsonType, level = JsonBuilder.getValue('raid', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'RAIDType', level)

        # CapacityBytes
        jsonType, size = JsonBuilder.getValue('size', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.INTEGER, 'CapacityBytes', size)

        # LogicalUnitNumber
        jsonType, lun = JsonBuilder.getValue('lun', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.INTEGER, 'LogicalUnitNumber', lun)

        # AccessCapabilities
        jsonType, access = JsonBuilder.getValue('access', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            JsonBuilder.addElement('array', JsonType.STRING, '', 'Read')
            if (access == 'read-write'):
                JsonBuilder.addElement('array', JsonType.STRING, '', 'Write')
            JsonBuilder.addElement('main', JsonType.DICT, 'AccessCapabilities', JsonBuilder.getElement('array'))

        # Create a commin Links dictionary for ResourceBlocks, ServerEndpointGroups, and ClientEndpointGroups
        JsonBuilder.newElement('links', JsonType.DICT, True)

        # ResourceBlocks
        jsonType, blocks = JsonBuilder.getValue('blocks', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(blocks)):
                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', compServiceUrl + 'ResourceBlocks/DriveBlock-' + blocks[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            else:
                JsonBuilder.newElement('dict2', JsonType.DICT, True)
                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', compServiceUrl + 'ResourceBlocks/DriveBlock-' + blocks)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            JsonBuilder.addElement('links', JsonType.DICT, 'ResourceBlocks', JsonBuilder.getElement('array'))

        # ServerEndpointGroups
        jsonType, ports = JsonBuilder.getValue('ports', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(ports)):
                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', fabricsUrl + '/' + fabric + '/Endpoints/' + ports[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            else:
                JsonBuilder.newElement('dict2', JsonType.DICT, True)
                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', fabricsUrl + '/' + fabric + '/Endpoints/' + ports)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            JsonBuilder.addElement('links', JsonType.DICT, 'ServerEndpointGroups', JsonBuilder.getElement('array'))

        # ClientEndpointGroups
        jsonType, initiators = JsonBuilder.getValue('initiators', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(initiators)):
                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', fabricsUrl + '/' + fabric + '/Endpoints/' + initiators[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            else:
                JsonBuilder.newElement('dict2', JsonType.DICT, True)
                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', fabricsUrl + '/' + fabric + '/Endpoints/' + initiators)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
            JsonBuilder.addElement('links', JsonType.DICT, 'ClientEndpointGroups', JsonBuilder.getElement('array'))

        JsonBuilder.addElement('main', JsonType.DICT, 'Links', JsonBuilder.getElement('links'))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

        # HTTP 201 Created
        if (link.jsonData != None):
            Trace.log(TraceLevel.INFO, '[[ JSON DATA ]]')
            Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))
            Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')
        else:
            Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        Trace.log(TraceLevel.INFO, ' ')
