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
#                           Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes   ConsumedBytes       Ports    RAID Drives                                          
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#                          dgA01  00c0ff51124900005ef7386100000000        512        99   1181602545664           16384          OK   RAID6 0.0,0.1,0.2,0.3   
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
    Drives = []
    RemainingCapacityPercent = 0
    AllocatedBytes = ''
    ConsumedBytes = ''
    State = ''
    Health = ''
    RAID = ''

    def init_from_url(self, redfishConfig, url, cos):

        isDiskGroup = False
        Trace.log(TraceLevel.DEBUG, '   ++ Storage Group init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):
            if ('Id' in link.jsonData and 'Name' in link.jsonData and 'Description' in link.jsonData and 'MaxBlockSizeBytes' in link.jsonData and 'RemainingCapacityPercent' in link.jsonData):
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

                if ('Id' in link.jsonData):
                    self.SerialNumber = link.jsonData['Id']

                if ('Name' in link.jsonData):
                    self.Name = link.jsonData['Name']

                if ('MaxBlockSizeBytes' in link.jsonData):
                    self.MaxBlockSizeBytes = link.jsonData['MaxBlockSizeBytes']
    
                if ('RemainingCapacityPercent' in link.jsonData):
                    self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']
    
                if ('Capacity' in link.jsonData):
                    capacity = link.jsonData['Capacity']
                    if ('Data' in capacity):
                        data = capacity['Data']
                        if ('AllocatedBytes' in data):
                            self.AllocatedBytes = data['AllocatedBytes']
                        if ('ConsumedBytes' in data):
                            self.ConsumedBytes = data['ConsumedBytes']
                
                if ('Status' in link.jsonData):
                    status = link.jsonData['Status']
                    if ('State' in status):
                        self.State = status['State']
                    if ('Health' in status):
                        self.Health = status['Health']
                
                if ('DefaultClassOfService' in link.jsonData):
                    dcos = link.jsonData['DefaultClassOfService']
                    if ('@odata.id' in dcos):
                        self.RAID = dcos['@odata.id'].replace(cos, '')

                if ('SupportedRAIDTypes' in link.jsonData):
                    self.RAID = link.jsonData['SupportedRAIDTypes'][0]

                self.Drives = []
                if ('CapacitySources' in link.jsonData):
                    cs = link.jsonData['CapacitySources'][0]
                    if ('ProvidingDrives' in cs and 'Members' in cs['ProvidingDrives']):
                        members = cs['ProvidingDrives']['Members']
                        for i in range(len(members)):
                            if ('@odata.id' in members[i]):
                                # Example: "@odata.id": "/redfish/v1/Systems/1852437ED5/Storage/controller_a/Drives/0.0"
                                words = members[i]['@odata.id'].split('/')
                                self.Drives.append(words[len(words)-1])
                
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
            self.link.print_status()

        else:
            #                           Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes   ConsumedBytes      Health    RAID  Drives
            # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #                          dgA01  00c0ff51124900005ef7386100000000        512        99   1181602545664           16384          OK   RAID6  0.0,0.1,0.2,0.3
            data_format = '{name: >30}  {sn: >32}  {blocksize: >9}  {capacity: >8}  {allocated: >14}  {consumed: >14}  {health: >10}  {raid: >6}  {drives: <48}'
            print('')
            print(data_format.format(name='Name', sn='SerialNumber', blocksize='BlockSize', capacity='Capacity', allocated='AllocatedBytes', consumed='ConsumedBytes', health='Ports', raid='RAID', drives='Drives'))
            print('-'*(186))
            if (self.groups != None):
                for i in range(len(self.groups)):
                    print(data_format.format(
                        name=self.groups[i].Name,
                        sn=self.groups[i].SerialNumber,
                        blocksize=self.groups[i].MaxBlockSizeBytes,
                        capacity=self.groups[i].RemainingCapacityPercent,
                        allocated=self.groups[i].AllocatedBytes,
                        consumed=self.groups[i].ConsumedBytes,
                        health=self.groups[i].Health,
                        raid=self.groups[i].RAID,
                        drives=",".join(self.groups[i].Drives)))
