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
# show_diskgroups.py 
#
# ******************************************************************************************
#
# @command show diskgroups
#
# @synopsis Display all allocated disk groups and disk group infromation
#
# @description-start
#
# 'show diskgroups' displays details about all available disk groups.
#
# Example:
#
# (redfish) show diskgroups
# 
#      Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes  ConsumedBytes  Health  ClasOfService
#  ---------------------------------------------------------------------------------------------------------------------
#     dgA01  00c0ff5112460000f55a925d00000000        512         0      1283457024     1283457024      OK          RAID1
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# PoolInformation
################################################################################
class StorageGroupInformation:
    """Storage Group Information"""

    SerialNumber = ''
    Name = ''
    Description = ''
    MaxBlockSizeBytes = 0
    PoolType = ''
    AllocatedVolumes = []
    RemainingCapacityPercent = 0
    AllocatedBytes = ''
    ConsumedBytes = ''
    State = ''
    Health = ''
    ClassofService = ''

    def init_from_url(self, redfishConfig, url, cos):

        isDiskGroup = False
        Trace.log(TraceLevel.DEBUG, '   ++ Storage Group init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid):
            Trace.log(TraceLevel.DEBUG, '   ++ Storage Group: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['Description'], link.jsonData['MaxBlockSizeBytes'], link.jsonData['RemainingCapacityPercent']))

            try:
                self.Description = link.jsonData['Description']
                if (self.Description == 'DiskGroup'):
                    isDiskGroup = True
            except:
                self.Description = 'Unknown'
                isDiskGroup = False
                pass

            if (isDiskGroup):
                self.SerialNumber = link.jsonData['Id']
                self.Name = link.jsonData['Name']
                self.MaxBlockSizeBytes = link.jsonData['MaxBlockSizeBytes']
    
                try:
                    self.AllocatedVolumes = []
                    avs = link.jsonData['AllocatedVolumes']
                    for i in range(len(avs)):
                        # Example: '/redfish/v1/StorageServices/S1/StoragePools/00c0ff5112460000f55a925d00000000/Volumes/00c0ff5112460000f75a925d02000000'
                        words = avs[i].split('/')
                        if (len(words) >= 7):
                            Trace.log(TraceLevel.TRACE, '   ++ Adding allocated volume ({}) from ({})'.format(words[7], avs[i]))
                            self.AllocatedVolumes.append(words[7])
                except:
                    self.AllocatedVolumes = []
                    pass
    
                self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']
    
                capacity = link.jsonData['Capacity']
                data = capacity['Data']
                self.AllocatedBytes = data['AllocatedBytes']
                self.ConsumedBytes = data['ConsumedBytes']
                
                status = link.jsonData['Status']
                self.State = status['State']
                self.Health = status['Health']
                
                dcos = link.jsonData['DefaultClassOfService']
                self.ClassofService = dcos['@odata.id'].replace(cos, '')
                
        return (isDiskGroup)

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show diskgroups"""
    name = 'show diskgroups'
    pools = []
    link = None

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.groups = []
        return (RedfishSystem.get_uri(redfishConfig, 'StoragePools'))

    @classmethod
    def process_json(self, redfishConfig, url):

        if (not url):
            return

        # GET list of pools and disk groups
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a listing of all disk groups for this system
        # Note: Version 1.2 returns storage groups and pools, use Description to determine Pool vs DiskGroup

        if (self.link.valid and self.link.jsonData != None):

            total = 0 
            created = 0
            urls = []
            cos = RedfishSystem.get_uri(redfishConfig, 'ClassesOfService')
            
            # Create a list of all the pool URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                    Trace.log(TraceLevel.VERBOSE, '... GET total ({})'.format(total))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '... Members value ({})'.format(value))
                    if (value != None):
                        for groupLink in value:
                            url = groupLink['@odata.id']
                            Trace.log(TraceLevel.VERBOSE, '... ADD storage group url ({})'.format(url))
                            urls.append(url)
                            created += 1

            # Create object based on each drive URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET Storage Group data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    group = StorageGroupInformation()
                    if (group.init_from_url(redfishConfig, urls[i], cos)):
                        self.groups.append(group)
            elif (created > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Members {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):

        if (self.link == None):
            return 

        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            print('         Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes  ConsumedBytes  Health  ClasOfService')
            print(' -------------------------------------------------------------------------------------------------------------------------')
    
            if (self.groups != None):
                for i in range(len(self.groups)):
                    print(' {0: >12}  {1: >32}  {2: >9}  {3: >8}  {4: >14}  {5: >13}  {6: >6}  {7: >13}'.format(
                        self.groups[i].Name,
                        self.groups[i].SerialNumber,
                        self.groups[i].MaxBlockSizeBytes,
                        self.groups[i].RemainingCapacityPercent,
                        self.groups[i].AllocatedBytes,
                        self.groups[i].ConsumedBytes,
                        self.groups[i].Health,
                        self.groups[i].ClassofService
                        ))
                    
                    for volume in range(len(self.groups[i].AllocatedVolumes)):
                        print(' -- Allocated Volume: {}'.format(self.groups.AllocatedVolumes[volume]))
