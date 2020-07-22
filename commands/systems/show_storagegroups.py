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
# show_storagegroups.py 
#
# ******************************************************************************************
#
# @command show storagegroups
#
# @synopsis Display all created storage groups
#
# @description-start
#
# 'show storagegroups' displays details about all created storage groups.
#
# Example:
#
# (redfish) show storagegroups
#
#                                       Name                                                       SerialNumber    State  Health  Exposed  LUN                          Initiators                    Ports
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#  AVolume01_00c0ff51124900007db6945e01010000  00c0ff511249000066fa9f5e01000000_00c0ff51124900007db6945e01010000  Enabled      OK        1    1    00c0ff51124900007db6945e01010000              A0,B0,A1,B1
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

    Description = ''
    SerialNumber = ''
    MembersAreConsistent = ''
    VolumesAreExposed = ''
    Name = ''
    AccessState = ''

    # MappedVolumes
    LogicalUnitNumber = ''
    Volume = ''
    
    ClientEndpointGroups = []   # Initiators
    ServerEndpointGroups = []   # Ports
    
    # Status
    State = ''
    Health = ''
    HealthRollup = ''

    def init_from_url(self, redfishConfig, url):

        Trace.log(TraceLevel.DEBUG, '   ++ Storage Group init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):

            if ('Id' in link.jsonData and 'Name' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Storage Group: ({}, {})'.format(link.jsonData['Id'], link.jsonData['Name']))

            if ('Description' in link.jsonData):
                self.Description = link.jsonData['Description']

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('Id' in link.jsonData):
                self.SerialNumber = link.jsonData['Id']

            if ('VolumesAreExposed' in link.jsonData):
                self.VolumesAreExposed = link.jsonData['VolumesAreExposed']

            if ('AccessState' in link.jsonData):
                self.AccessState = link.jsonData['AccessState']

            self.ClientEndpointGroups = []
            if ('ClientEndpointGroups' in link.jsonData):
                ceg = link.jsonData['ClientEndpointGroups']

                for i in range(len(ceg)):
                    if ('@odata.id' in ceg[i]):
                        words = ceg[i]['@odata.id'].split('/')
                        endpoint_id = '?'
                        if (redfishConfig.get_version('version') < 2):
                            # Example: "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00ab61310"
                            if (len(words) >= 6):
                                endpoint_id = words[6]
                        else:
                            # Example: "@odata.id": "/redfish/v1/Systems/{SystemsId}/Storage/{StorageId}/Endpoints/500605b00ab61310"
                            if (len(words) >= 8):
                                endpoint_id = words[8]

                        self.ClientEndpointGroups.append(endpoint_id)

            self.ServerEndpointGroups = []
            if ('ServerEndpointGroups' in link.jsonData):
                seg = link.jsonData['ServerEndpointGroups']

                for i in range(len(seg)):
                    if ('@odata.id' in seg[i]):
                        words = seg[i]['@odata.id'].split('/')
                        endpoint_id = '?'
                        if (redfishConfig.get_version('version') < 2):
                            # Example: "@odata.id": "/redfish/v1/StorageServices/S1/Endpoint/A0"
                            if (len(words) >= 6):
                                endpoint_id = words[6]
                        else:
                            # Example: "@odata.id": "/redfish/v1/Systems/{SystemsId}/Storage/{StorageId}/Endpoints/A0"
                            if (len(words) >= 8):
                                endpoint_id = words[8]
                        self.ServerEndpointGroups.append(endpoint_id)

            if ('MappedVolumes' in link.jsonData):
                mv = link.jsonData['MappedVolumes']
                for i in range(len(mv)):
                    # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                    if ('LogicalUnitNumber' in mv[i]):
                        self.LogicalUnitNumber = mv[i]['LogicalUnitNumber']
                    if ('Volume' in mv[i]):
                        volume = mv[i]['Volume']
                        if ('@odata.id' in volume):
                            words = volume['@odata.id'].split('/')
                            self.Volume = words[len(words)-1]

            if ('Status' in link.jsonData):
                status = link.jsonData['Status']
                if ('State' in status):
                    self.State = status['State']
                if ('Health' in status):
                    self.Health = status['Health']
        else:
            Trace.log(TraceLevel.VERBOSE, '   ++ Storage Group: link was not valid status={} reason={}'.format(link.urlStatus, link.urlReason))

        return True

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show storagegroups"""
    name = 'show storagegroups'
    pools = []
    link = None

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.groups = []
        return (RedfishSystem.get_uri(redfishConfig, 'StorageGroups'))

    @classmethod
    def process_json(self, redfishConfig, url):

        # GET list of pools and disk groups
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a listing of all storage groups for this system

        if (self.link.valid and self.link.jsonData):

            total = 0 
            created = 0
            urls = []
            
            # Create a list of URIs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                    Trace.log(TraceLevel.TRACE, '.. GET total ({})'.format(total))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '.. Members value ({})'.format(value))
                    if (value != None):
                        for groupLink in value:
                            url = groupLink['@odata.id']
                            Trace.log(TraceLevel.VERBOSE, '.. ADD storage group url ({})'.format(url))
                            urls.append(url)
                            created += 1

            # Create object based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '.. GET Storage Group data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls)-1, urls[i]))
                    group = StorageGroupInformation()
                    if (group.init_from_url(redfishConfig, urls[i])):
                        self.groups.append(group)
            elif (created > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Memebers {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):

        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            print('                                       Name                                                       SerialNumber    State  Health  Exposed  LUN                          Initiators                    Ports')
            print(' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            #       AVolume01_00c0ff51124900007db6945e01010000  00c0ff511249000066fa9f5e01000000_00c0ff51124900007db6945e01010000  Enabled      OK        1    1    00c0ff51124900007db6945e01010000              A0,B0,A1,B1
            if (self.groups != None):
                for i in range(len(self.groups)):
                    print(' {0: >42}  {1: >49}  {2: >7}  {3: >6}  {4: >7}  {5: >3}  {6: >34}  {7: >23}'.format(
                        self.groups[i].Name,
                        self.groups[i].SerialNumber,
                        self.groups[i].State,
                        self.groups[i].Health,
                        self.groups[i].VolumesAreExposed,
                        self.groups[i].LogicalUnitNumber,
                        ",".join(self.groups[i].ClientEndpointGroups),
                        ",".join(self.groups[i].ServerEndpointGroups),
                        ))
