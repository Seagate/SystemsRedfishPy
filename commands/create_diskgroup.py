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

import json

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


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

#
# This class creates a JSON representation of the desired request body
#
class CreateDiskGroupRequestBody:

    def __init__(self, name, drives, pools, level):

        # Name
        self.Name = name

        # CapacitySources / ProvidingDrives
        # Build a list of dictionary items, then add to a dictionary
        driveList = []
        for i in range(len(drives)):
            item = { "@odata.id": "/redfish/v1/StorageServices/S1/Drives/" + drives[i] }
            driveList.append(item)
        self.CapacitySources = { "ProvidingDrives": driveList }

        # AllocatedPools / Members
        # Build a list of dictionary items, then add to a dictionary
        poolList = []
        for i in range(len(pools)):
            item = { "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/" + pools[i].upper() }
            poolList.append(item)
        self.AllocatedPools = { "Members": poolList }

        # ClassesOfService
        self.ClassesOfService = { "@odata.id": '/redfish/v1/StorageServices/S1/ClassesOfService/' + level.upper() }
        
    def __str__(self):
        return self.Name


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create diskgroup"""
    name = 'create diskgroup'
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
        return ('/redfish/v1/StorageServices/S1/StoragePools')

    @classmethod
    def process_json(self, config, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Disk Group: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        # Example: 'create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1'
        # For now, use a simple split based on spaces
        
        name = ''
        drives = []
        pools = []
        level = ''

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
                        elif (tokens[0] == 'disks'):
                            disks = tokens[1].split(',')
                            for disk in range(len(disks)):
                                drives.append(disks[disk])
                        elif (tokens[0] == 'pool'):
                            pools.append(tokens[1])
                        elif (tokens[0] == 'level'):
                            level = tokens[1].upper()
                            Trace.log(TraceLevel.TRACE, '      -- Adding {}={}'.format(tokens[0], level))

        info = CreateDiskGroupRequestBody(name, drives, pools, level)
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
        else:
            Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))

    @classmethod
    def display_results(self, config):
        # Nothing to do in this case
        print(' ')
