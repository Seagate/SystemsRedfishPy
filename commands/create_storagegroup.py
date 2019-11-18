#
# @command create storagegroup
#
# @synopsis Create a storage group to map a volume making it visibile to a host or hosts.
#
# @description-start
#
# 'create diskgroup lun=[LogicalUnitNumber] volume=[serial-number] access=[read|read-write] ports=[A0,B0,A1,B1] initiators=[endpoint]
#
# Example:
# create storagegroup lun=1 volume=00c0ff511246000026fdc35d01000000 access=read-write ports=A0,B0 initiators=500605b00ab61310
#
# @description-end
#

import config
import json

from commands.commandHandlerBase import CommandHandlerBase
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
#                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff511246000026fdc35d01000000"
#             }
#         }
#     ]
# }

#
# This class creates a JSON representation of the desired request body
#
class CreateRequestBody:

    def __init__(self, lun, volume, access, ports, initiators):

        # ServerEndpointGroups
        self.ServerEndpointGroups = []
        for i in range(len(ports)):
            item = { "@odata.id": config.endpointGroups + ports[i] }
            self.ServerEndpointGroups.append(item)

        # ClientEndpointGroups
        self.ClientEndpointGroups = { "@odata.id": config.endpoints + initiators }

        # AccessCapabilities
        if (access == 'read'):
            self.AccessCapabilities = [ "Read" ]
        elif (access == 'read-write'):
            self.AccessCapabilities = [ "Read", "Write" ]
        else:
            self.AccessCapabilities = [ "Read", "Write" ]

        # MappedVolumes
        self.MappedVolumes = [ { "LogicalUnitNumber": lun, "Volume": { "@odata.id": config.volumes + volume  } }]

    def __str__(self):
        return self.Name


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create storagegroup"""
    name = 'create storagegroup'
    command = ''

    #
    #  Return a dictionary representation of an object
    #
    @classmethod
    def convert_to_dict(self, obj):
        obj_dict = {}
        obj_dict.update(obj.__dict__)
        return obj_dict
  
    @classmethod
    def prepare_url(self, command):
        self.command = command
        return (config.storageGroups)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Storage Group: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: 'create diskgroup lun=[LogicalUnitNumber] volume=[serial-number] access=[read|read-write] ports=[A0,B0,A1,B1] initiators=[endpoint]
# Example: 'create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1'
        # For now, use a simple split based on spaces
        
        lun = ''
        volume = ''
        access = ''
        ports = []
        initiators = ''

        words = self.command.split(' ')
        if (len(words) >= 3):
            for i in range(len(words)):
                if (i > 1):
                    Trace.log(TraceLevel.TRACE, '   ++ Process: {}'.format(words[i]))
                    tokens = words[i].split('=')
                    if (len(tokens) >= 2):
                        if (tokens[0] == 'lun'):
                            lun = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], lun))
                        elif (tokens[0] == 'volume'):
                            volume = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], volume))
                        elif (tokens[0] == 'access'):
                            access = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], access))
                        elif (tokens[0] == 'ports'):
                            newports = tokens[1].split(',')
                            for port in range(len(newports)):
                                ports.append(newports[port])
                        elif (tokens[0] == 'initiators'):
                            initiators = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], initiators))

        info = CreateRequestBody(lun, volume, access, ports, initiators)
        requestData = json.dumps(info, default=self.convert_to_dict, indent=4)
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, requestData)

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
