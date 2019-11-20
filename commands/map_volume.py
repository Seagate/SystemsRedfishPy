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
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 initiators=500605b00ab61310,500605b00ab61311
#
# map volume storagegroup=00c0ff51124600006391d25d01000000_500605b00ab61310 volume=00c0ff51124600006391d25d01000000 lun=44 access=read-write ports=A0,B0
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
#                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff511246000026fdc35d01000000"
#             }
#         }
#     ]
# }
################################################################################


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
        Trace.log(TraceLevel.INFO, '++ map volume: ({})...'.format(self.command))

        jsonType, storagegroup = JsonBuilder.getValue('storagegroup', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.ERROR, 'The storagegroup paramter is required, parse results (storagegroup={})...'.format(storagegroup))
            return

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
            JsonBuilder.newElement('dict', JsonType.DICT, True)
            JsonBuilder.addElement('dict', JsonType.STRING, '@odata.id', config.endpoints + str(initiators))
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

        url = url + storagegroup
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'PATCH', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

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
