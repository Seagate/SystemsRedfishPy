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
# storagegroup.py - Common method for StorageGroup request properies. 
#
# ******************************************************************************************
#

import config
from core.jsonBuilder import JsonBuilder, JsonType
from core.trace import TraceLevel, Trace


################################################################################
# JSON StorageGroup Request Data Example
################################################################################
#
# {
#     "ServerEndpointGroups": [
#         {
#             "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
#         },
#         {
#             "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
#         }
#     ],
#     "ClientEndpointGroups": [
#         {
#             "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00ab61310"
#         }
#     ],
#     "AccessCapabilities": [
#         "Read",
#         "Write"
#     ],
#     "MappedVolumes": [
#         {
#             "LogicalUnitNumber": "1",
#             "Volume": {
#                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/AVolume01"
#             }
#         }
#     ]
# }

################################################################################
# CreateStorageGroupRequestProperties
#
# command - The original command line with parameters and values 
# creating - True when creating a storage group, and False when mapping a volume
#
################################################################################
def CreateStorageGroupRequestProperties(command, creating):

        Trace.log(TraceLevel.DEBUG, '')
        Trace.log(TraceLevel.DEBUG, '++ Create Storage Group Request: ({})...'.format(command))

        # From the command, build up the required JSON data
        # Examples:
        #     create storagegroup lun=1 volume=00c0ff511246000026fdc35d01000000 access=read-write ports=A0,B0 initiators=500605b00ab61310
        #     map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 lun=44 access=read-write ports=A0,B0

        # Extract required parameters first, otherwise return None
        if creating:
            jsonType, volume = JsonBuilder.getValue('volume', command)
            if (jsonType is JsonType.NONE):
                Trace.log(TraceLevel.ERROR, 'The volume parameter is required, parse results (volume={})...'.format(volume))
                return None
    
            jsonType, lun = JsonBuilder.getValue('lun', command)
            if (jsonType is JsonType.NONE):
                Trace.log(TraceLevel.ERROR, 'The lun parameter is required, parse results (lun={})...'.format(lun))
                return None
    
            jsonType, initiators = JsonBuilder.getValue('initiators', command)
            if (jsonType is JsonType.NONE):
                Trace.log(TraceLevel.ERROR, 'The initiators parameter is required, parse results (initiators={})...'.format(initiators))
                return None
        else:
            jsonType, storagegroup = JsonBuilder.getValue('storagegroup', command)
            if (jsonType is JsonType.NONE):
                Trace.log(TraceLevel.ERROR, 'The storagegroup parameter is required, parse results (storagegroup={})...'.format(storagegroup))
                return None
    
            jsonType, volume = JsonBuilder.getValue('volume', command)
            if (jsonType is JsonType.NONE):
                Trace.log(TraceLevel.ERROR, 'The volume parameter is required, parse results (volume={})...'.format(volume))
                return None

#1 map_volume
        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # ServerEndpointGroups
        jsonType, ports = JsonBuilder.getValue('ports', command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(ports)):
                    JsonBuilder.newElement('dict', JsonType.DICT, True)
                    JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpointGroups + ports[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict'))
            else:
                JsonBuilder.newElement('dict', JsonType.DICT, True)
                JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpointGroups + ports)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict'))
            JsonBuilder.addElement('main', JsonType.DICT, 'ServerEndpointGroups', JsonBuilder.getElement('array'))

        # ClientEndpointGroups
        jsonType, initiators = JsonBuilder.getValue('initiators', command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            if (jsonType is JsonType.ARRAY):
                for i in range(len(initiators)):
                    JsonBuilder.newElement('dict', JsonType.DICT, True)
                    JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpoints + initiators[i])
                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict'))
            else:
                JsonBuilder.newElement('dict', JsonType.DICT, True)
                JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpoints + initiators)
                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict'))
            JsonBuilder.addElement('main', JsonType.DICT, 'ClientEndpointGroups', JsonBuilder.getElement('array'))

        # AccessCapabilities
        jsonType, access = JsonBuilder.getValue('access', command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            JsonBuilder.addElement('array', JsonType.STRING, '', 'Read')
            if (access == 'read-write'):
                JsonBuilder.addElement('array', JsonType.STRING, '', 'Write')
            JsonBuilder.addElement('main', JsonType.DICT, 'AccessCapabilities', JsonBuilder.getElement('array'))

        # MappedVolumes
        JsonBuilder.newElement('array', JsonType.ARRAY, True)
        JsonBuilder.newElement('dict', JsonType.DICT, True)

        jsonType, lun = JsonBuilder.getValue('lun', command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('dict', jsonType, 'LogicalUnitNumber', lun)

        JsonBuilder.newElement('dict2', JsonType.DICT, True)
        JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.volumes + volume)
        JsonBuilder.addElement('dict', JsonType.DICT, 'Volume', JsonBuilder.getElement('dict2'))
        JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict'))
        JsonBuilder.addElement('main', JsonType.DICT, 'MappedVolumes', JsonBuilder.getElement('array'))

        # Debug
        # JsonBuilder.displayElements()
        # JsonBuilder.displayJson('main')

        return JsonBuilder.getElement('main')
