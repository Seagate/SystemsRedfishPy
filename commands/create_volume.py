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

import json

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


################################################################################
# CreateVolumeRequestBody
################################################################################

#
# Example of desired JSON data
#
# {
#     "name": "TestVol01",
#     "size": 100000000000,
#     "CapacitySources" : [
#             {
#                 "@odata.id": "/redfish/v1/StoragePools/A
#             }
#     ],
#     "Links": {
#         "ClassOfService":
#             {
#                 "@odata.id": "/redfish/v1/StorageServices(1)/ClassesOfService(Default)"
#             }
#     }         
# }

#
# This class creates a JSON representation of the desired request body
#
class CreateVolumeRequestBody:

    def __init__(self, name, size, pools):

        # Name
        self.name = name

        # Size
        self.size = size

        # CapacitySources / ProvidingDrives
        # Build a list of dictionary items
        self.CapacitySources = []
        for i in range(len(pools)):
            item = { "@odata.id": "/redfish/v1/StoragePools/" + pools[i] }
            self.CapacitySources.append(item)

        # Links / ClassOfService
        # Build a dictionary of a dictionary
        self.Links = {
            "ClassOfService" : { "@odata.id" : "/redfish/v1/StorageServices(1)/ClassesOfService(Default)" }
        }

    def __str__(self):
        return self.Name


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create volume"""
    name = 'create volume'
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
        return ('/redfish/v1/StorageServices/S1/Volumes')

    @classmethod
    def process_json(self, config, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Volume: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: create volume name=[name] size=[size] lun=[lun] pool=[A|B] diskgroup=[group]
        # For now, use a simple split based on spaces
        
        name = ''
        size = 0
        pools = []

        words = self.command.split(' ')
        if (len(words) >= 3):
            for i in range(len(words)):
                if (i > 1):
                    Trace.log(TraceLevel.TRACE, '   ++ Process: {}'.format(words[i]))
                    tokens = words[i].split('=')
                    if (len(tokens) >= 2):
                        if (tokens[0] == 'name'):
                            name = tokens[1]
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], name))
                        elif (tokens[0] == 'size'):
                            size = int(tokens[1])
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], size))
                        elif (tokens[0] == 'pool'):
                            pools.append(tokens[1])

        info = CreateVolumeRequestBody(name, size, pools)
        requestData = json.dumps(info, default=self.convert_to_dict, indent=4)
        link = UrlAccess.process_request(config, UrlStatus(url), 'POST', True, requestData)

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

        # HTTP 201 Created
        if (link.urlStatus == 201):

            if (link.jsonData != None):
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('SerialNumber', link.jsonData['Name']))
                Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Id', link.jsonData['Id']))
            else:
                Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')


    @classmethod
    def display_results(self, config):
        # Nothing to do in this case
        print(' ')
