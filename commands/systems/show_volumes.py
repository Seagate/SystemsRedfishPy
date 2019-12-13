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
# show_volumes.py 
#
# ******************************************************************************************
#
# @command show volumes
#
# @synopsis Display all configured volumes
#
# @description-start
#
# 'show volumes' displays details about all available volumes, including
# name, serial number, class, size, and health.
#
# Example:
# 
# (redfish) show volumes
# 
#             Name                      SerialNumber            Consumed/Allocated  Remaining %       Access  Encrypted      State  Health                                      CapacitySources
#  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#      TestVolume1  00c0ff51124600006358975d01000000         146800640/99996401664           99   Read,Write       true    Enabled      OK        /redfish/v1/StorageServices/S1/StoragePools/A
#
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# VolumeInformation
################################################################################
class VolumeInformation:
    """Volume Information"""

    Name = ''
    SerialNumber = ''
    CapacityBytes = ''
    AllocatedBytes = ''
    ConsumedBytes = ''
    RemainingCapacityPercent = ''
    Encrypted = ''
    State = ''
    Health = ''
    Pool = ''
    AccessCapabilities = ''
    
    def init_from_url(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Volume init from URL {}'.format(url))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Volume: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['CapacityBytes'], link.jsonData['RemainingCapacityPercent'], link.jsonData['Encrypted']))

            self.SerialNumber = link.jsonData['Id']
            self.Name = link.jsonData['Name']
            self.CapacityBytes = link.jsonData['CapacityBytes']
            self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']
            if (link.jsonData['Encrypted']):
                self.Encrypted = 'true'
            else:
                self.Encrypted = 'false'

            # Status
            healthDict = link.jsonData['Status']
            self.State = healthDict['State']
            self.Health = healthDict['Health']

            # Capacity
            capacity = link.jsonData['Capacity']
            data = capacity['Data']
            self.AllocatedBytes = data['AllocatedBytes']
            self.ConsumedBytes = data['ConsumedBytes']

            # AccessCapabilities
            try:
                self.AccessCapabilities = ','.join(link.jsonData['AccessCapabilities'])
            except:
                self.AccessCapabilities = 'Unknown'
            
            data = capacity['Data']
            self.AllocatedBytes = data['AllocatedBytes']
            self.ConsumedBytes = data['ConsumedBytes']

            # This version assumes an array of one pool
            item = link.jsonData['CapacitySources'][0]
            ppools = item['ProvidingPools']
            self.Pool = ppools[0]['@odata.id']


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show volumes"""
    name = 'show volumes'
    link = None
    volumes = []

    @classmethod
    def prepare_url(self, command):
        self.volumes = []
        return (config.volumes)

    @classmethod
    def process_json(self, redfishConfig, url):
        
        # GET Volumes
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all volumes for this system
        if (self.link.valid):

            totalVolumes = 0 
            createdVolumes = 0
            volumeUrls = []
            
            # Create a list of all the volume URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalVolumes = value
                    Trace.log(TraceLevel.VERBOSE, '... GET volumes total ({})'.format(totalVolumes))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.VERBOSE, '... Members value ({})'.format(value))
                    if (value != None):
                        for volumeLink in value:
                            Trace.log(TraceLevel.VERBOSE, '... ADD volume url ({})'.format(volumeLink['@odata.id']))
                            volumeUrls.append(volumeLink['@odata.id'])
                            createdVolumes += 1
            
            # Create Volume object based on each drive URL
            if (createdVolumes > 0 and createdVolumes == totalVolumes):
                for i in range(len(volumeUrls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET volume data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(volumeUrls), volumeUrls[i]))
                    volume = VolumeInformation()
                    volume.init_from_url(redfishConfig, volumeUrls[i])
                    self.volumes.append(volume)
            elif (createdVolumes > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Volume information mismatch: Members@odata.count ({}), Memebers {}'.format(totalVolumes, createdVolumes))


    @classmethod
    def display_results(self, redfishConfig):
        # self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))
        else:
            print('')
                #                0                                 1                             2            3            4          5          6       7                                                    8   
                #             Name                      SerialNumber            Consumed/Allocated  Remaining %       Access  Encrypted      State  Health                                      CapacitySources
                #  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                #      TestVolume1  00c0ff51124600006358975d01000000         146800640/99996401664           99   Read,Write       true    Enabled      OK        /redfish/v1/StorageServices/S1/StoragePools/A
            print('            Name                      SerialNumber            Consumed/Allocated  Remaining %       Access  Encrypted      State  Health                                      CapacitySources')
            print(' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            
            if (self.volumes != None):
                for i in range(len(self.volumes)):
                    print('{0: >16}  {1: >31}  {2: >28}  {3: >11}  {4: >11}  {5: >9}  {6: >9}  {7: >6}  {8: >51}'.format(
                        self.volumes[i].Name,
                        self.volumes[i].SerialNumber,
                        str(self.volumes[i].ConsumedBytes) + '/' + str(self.volumes[i].AllocatedBytes),
                        self.volumes[i].RemainingCapacityPercent,
                        self.volumes[i].AccessCapabilities,
                        self.volumes[i].Encrypted,
                        self.volumes[i].State,
                        self.volumes[i].Health,
                        self.volumes[i].Pool))
