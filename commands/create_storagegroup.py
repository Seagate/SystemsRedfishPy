#
# @command create storagegroup
#
# @synopsis Create a storage group to map a volume making it visibile to a host or hosts.
#
# @description-start
#
# 'create storagegroup lun=[LogicalUnitNumber] volume=[serial-number] access=[read|read-write] ports=[A0,B0,A1,B1] initiators=[endpoint]
#
# Example:
# create storagegroup lun=1 volume=00c0ff511246000026fdc35d01000000 access=read-write ports=A0,B0 initiators=500605b00ab61310
#
# @description-end
#

import config
import json

from commands.commandHandlerBase import CommandHandlerBase
from jsonBuilder import JsonBuilder, JsonType
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


################################################################################
# CreateRequestBody
################################################################################

#
# Example of desired JSON data
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
#     "ClientEndpointGroups": {
#         "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00ab61310"
#     },
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
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create storagegroup"""
    name = 'create storagegroup'
    command = ''

    @classmethod
    def prepare_url(self, command):
        self.command = command
        return (config.storageGroups)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Storage Group: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: create storagegroup lun=1 volume=00c0ff511246000026fdc35d01000000 access=read-write ports=A0,B0 initiators=500605b00ab61310
        # For now, use a simple split based on spaces

        jsonType, volume = JsonBuilder.getValue('volume', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.ERROR, 'The volume paramter is required, parse results (volume={})...'.format(volume))
            return

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # ServerEndpointGroups
        jsonType, ports = JsonBuilder.getValue('ports', self.command)
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
        jsonType, initiators = JsonBuilder.getValue('initiators', self.command)
        if (jsonType is not JsonType.NONE):

# Use ARRAY (should be)
#            JsonBuilder.newElement('array', JsonType.ARRAY, True)
#            if (jsonType is JsonType.ARRAY):
#                for i in range(len(initiators)):
#                    JsonBuilder.newElement('dict2', JsonType.DICT, True)
#                    JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.endpoints + initiators[i])
#                    JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
#            else:
#                JsonBuilder.newElement('dict2', JsonType.DICT, True)
#                JsonBuilder.addElement('dict2', JsonType.STRING, '@odata.id', config.endpoints + initiators)
#                JsonBuilder.addElement('array', JsonType.DICT, '', JsonBuilder.getElement('dict2'))
#            JsonBuilder.addElement('main', JsonType.DICT, 'ClientEndpointGroups', JsonBuilder.getElement('array'))

# Use DICT (current)
            JsonBuilder.newElement('dict', JsonType.DICT, True)
            JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpoints + initiators)
            JsonBuilder.addElement('main', JsonType.DICT, 'ClientEndpointGroups', JsonBuilder.getElement('dict'))

        # AccessCapabilities
        jsonType, access = JsonBuilder.getValue('access', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.newElement('array', JsonType.ARRAY, True)
            JsonBuilder.addElement('array', JsonType.STRING, '', 'Read')
            if (access == 'read-write'):
                JsonBuilder.addElement('array', JsonType.STRING, '', 'Write')
            JsonBuilder.addElement('main', JsonType.DICT, 'AccessCapabilities', JsonBuilder.getElement('array'))

        # MappedVolumes
        JsonBuilder.newElement('array', JsonType.ARRAY, True)
        JsonBuilder.newElement('dict', JsonType.DICT, True)

        jsonType, lun = JsonBuilder.getValue('lun', self.command)
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

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

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

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
