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

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
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

        if (link.valid and link.jsonData is not None):
            if ('Id' in link.jsonData and 'Name' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Volume: ({}, {})'.format(link.jsonData['Id'], link.jsonData['Name']))

            if ('Id' in link.jsonData):
                self.SerialNumber = link.jsonData['Id']

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('CapacityBytes' in link.jsonData):
                self.CapacityBytes = link.jsonData['CapacityBytes']

            if ('RemainingCapacityPercent' in link.jsonData):
                self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']

            if ('Encrypted' in link.jsonData):
                if (link.jsonData['Encrypted']):
                    self.Encrypted = 'true'
                else:
                    self.Encrypted = 'false'

            # Status
            if ('Status' in link.jsonData):
                healthDict = link.jsonData['Status']
                if ('State' in healthDict):
                    self.State = healthDict['State']
                if ('Health' in healthDict):
                    self.Health = healthDict['Health']

            # Capacity
            if ('Capacity' in link.jsonData):
                capacity = link.jsonData['Capacity']
                if ('Data' in capacity):
                    data = capacity['Data']
                    if ('AllocatedBytes' in data):
                        self.AllocatedBytes = data['AllocatedBytes']
                    if ('ConsumedBytes' in data):
                        self.ConsumedBytes = data['ConsumedBytes']

            # AccessCapabilities
            if ('AccessCapabilities' in link.jsonData):
                try:
                    self.AccessCapabilities = ','.join(link.jsonData['AccessCapabilities'])
                except:
                    self.AccessCapabilities = 'Unknown'

            # This version assumes an array of one pool
            if ('CapacitySources' in link.jsonData):
                item = link.jsonData['CapacitySources'][0]
                Trace.log(TraceLevel.TRACE, '   ++ Volume: item={}'.format(item))
                
                if ('ProvidingPools' in item):
                    ppobj = item['ProvidingPools']
                    if isinstance(ppobj, list):                    
                        ppools = ppobj[0]
                    else:
                        ppools = ppobj
                    Trace.log(TraceLevel.TRACE, '   ++ Volume: ppools={}'.format(ppools))
                    if ('Members' in ppools):
                        self.Pool = ppools['Members'][0]['@odata.id']

                    words = self.Pool.split('/')
                    Trace.log(TraceLevel.TRACE, '   ++ Volume: self.Pool={}'.format(self.Pool))
                    Trace.log(TraceLevel.TRACE, '   ++ Volume: words={}, index={}, token={}'.format(len(words), len(words)-1, words[len(words)-1]))
                    
                    if (len(words) > 0):
                        self.Pool = words[len(words)-1]

                    Trace.log(TraceLevel.TRACE, '   ++ Volume: @odata.id={}'.format(self.Pool))


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show volumes"""
    name = 'show volumes'
    link = None
    volumes = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.volumes = []
        return (RedfishSystem.get_uri(redfishConfig, 'Volumes'))

    @classmethod
    def process_json(self, redfishConfig, url):
        
        # GET Volumes
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all volumes for this system
        if (self.link.valid and self.link.jsonData is not None):

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

        if (self.link.valid == False):
            self.link.print_status()
        else:
            print('')
                #                0                                 1                             2            3            4          5          6       7                                                    8   
                #             Name                      SerialNumber            Consumed/Allocated  Remaining %       Access  Encrypted      State  Health                                      CapacitySources
                #  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
                #      TestVolume1  00c0ff51124600006358975d01000000         146800640/99996401664           99   Read,Write       true    Enabled      OK        /redfish/v1/StorageServices/S1/StoragePools/A
            print('            Name                      SerialNumber            Consumed/Allocated  Remaining %       Access  Encrypted      State  Health                                      CapacitySources')
            print(' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')

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
