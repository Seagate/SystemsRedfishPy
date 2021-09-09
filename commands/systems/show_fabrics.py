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
# show_fabrics.py 
#
# ******************************************************************************************
#
# @command show fabrics
#
# @synopsis Display all fabrics found in the system
#
# @description-start
#
# 'show fabrics' displays details about all fabrics and endpoints found in the system.
#
# Example:
#
# (redfish) show fabrics
# 
# Fabric     State    Health                                       Endpoint     State    Health                      Name  Description
# -----------------------------------------------------------------------------------------------------------------------------------------------------
#    SAS   Enabled        OK                                                                                                                                     
#                                                                        A0   Enabled        OK                        A0  This instance represents a port       
#                                                                        A1   Enabled        OK                        A1  This instance represents a port       
#                                                                        B0   Enabled        OK                        B0  This instance represents a port       
#                                                                        B1   Enabled        OK                        B1  This instance represents a port       
#                                                          500605b00db9a071   Enabled        OK              I0-SAS-port2  This instance represents an initiator 
#                                     iqn.1993-08.org.debian:01:112233abcde   Enabled        OK         I1-01:112233abcde  This instance represents an initiator 
#                             iqn.1992-09.com.seagate:01.array.00c0ff4ba191   Enabled        OK  I2-01-array-00c0ff4ba191  This instance represents an initiator 
#                                                          0000111122223333   Enabled        OK              I3-fakeInit1  This instance represents an initiator 
#                                                          4444555566667777   Enabled        OK              I4-fakeInit2  This instance represents an initiator 
#                                                          500605b00db9a070   Enabled        OK              I5-SAS-port1  This instance represents an initiator 
# 
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# Classes
################################################################################

class Endpoint:
    Name = ''
    Description = ''
    Id = ''
    State = ''
    Health = ''
    DurableName = ''
    valid = False

    def init_from_url(self, redfishConfig, url):
        valid = False
        Trace.log(TraceLevel.DEBUG, '   ++ Init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):

            if ('Name' in link.jsonData and 'Description' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Name, Description: ({}, {})'.format(link.jsonData['Name'], link.jsonData['Description']))

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('Description' in link.jsonData):
                self.Description = link.jsonData['Description']

            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']
                valid = True

            # Status
            if ('Status' in link.jsonData):
                healthDict = link.jsonData['Status']
                if ('State' in healthDict):
                    self.State = healthDict['State']
                if ('Health' in healthDict):
                    self.Health = healthDict['Health']

            # Identifiers
            if ('Identifiers' in link.jsonData):
                ids = link.jsonData['Identifiers']
                if ('DurableName' in healthDict):
                    self.DurableName = ids['DurableName']

        return (valid)

class Fabric:
    link = None
    Name = ''
    Description = ''
    Id = ''
    State = ''
    Health = ''
    endpoints = []
    valid = False

    def init_from_url(self, redfishConfig, url):

        Trace.log(TraceLevel.DEBUG, '   ++ Init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):

            if ('Name' in link.jsonData and 'Description' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Name, Description: ({}, {})'.format(link.jsonData['Name'], link.jsonData['Description']))

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('Description' in link.jsonData):
                self.Description = link.jsonData['Description']

            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']
                valid = True

            # Status
            if ('Status' in link.jsonData):
                healthDict = link.jsonData['Status']
                if ('State' in healthDict):
                    self.State = healthDict['State']
                if ('Health' in healthDict):
                    self.Health = healthDict['Health']
                if ('HealthRollup' in healthDict):
                    self.Health = healthDict['HealthRollup']

            # Identifiers
            if ('Identifiers' in link.jsonData):
                ids = link.jsonData['Identifiers']
                if ('DurableName' in healthDict):
                    self.DurableName = ids['DurableName']

            # Endpoints
            if ('Endpoints' in link.jsonData):
                endpoints_url = link.jsonData['Endpoints']['@odata.id']
                Trace.log(TraceLevel.VERBOSE, '++ GET collection from ({})'.format(endpoints_url))

                self.link = UrlAccess.process_request(redfishConfig, UrlStatus(endpoints_url))
        
                # Retrieve a list of all endpoints for this fabric
                if (self.link.valid and self.link.jsonData):
                    total = 0 
                    created = 0
                    urls = []

                    # Create a list of all the URLs provided under Members
                    for (key, value) in self.link.jsonData.items():
                        if (key == 'Members@odata.count'):
                            total = value
                            Trace.log(TraceLevel.VERBOSE, '   -- Total members ({})'.format(total))
                        elif (key == 'Members'):
                            for link in value:
                                Trace.log(TraceLevel.VERBOSE, '   -- Add url ({})'.format(link['@odata.id']))
                                urls.append(link['@odata.id'])
                                created += 1

                    # Create objects based on each URL
                    if (created > 0 and created == total):
                        for i in range(len(urls)):
                            Trace.log(TraceLevel.VERBOSE, '   -- GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                            item = Endpoint()
                            if (item.init_from_url(redfishConfig, urls[i])):
                                self.endpoints.append(item)
                    else:
                        Trace.log(TraceLevel.ERROR, '   ++ Fabric: Information mismatch: Members@odata.count ({}), Memebers {}'.format(total, created))

        return (valid)

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    name = 'show fabrics'
    link = None
    items = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.items = []
        return (RedfishSystem.get_uri(redfishConfig, 'Fabrics'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.VERBOSE, '++ GET collection from ({})'.format(url))
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all fabrics for this system
        if (self.link.valid and self.link.jsonData):
            total = 0 
            created = 0
            urls = []

            # Create a list of all the URLs provided under Members
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                    Trace.log(TraceLevel.VERBOSE, '   -- Total members ({})'.format(total))
                elif (key == 'Members'):
                    for link in value:
                        Trace.log(TraceLevel.VERBOSE, '   -- Add url ({})'.format(link['@odata.id']))
                        urls.append(link['@odata.id'])
                        created += 1

            # Create objects based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '   -- GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    item = Fabric()
                    if (item.init_from_url(redfishConfig, urls[i])):
                        self.items.append(item)
            else:
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Memebers {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):

        if (self.link.valid == False):
            self.link.print_status()

        else:
            # Fabric     State    Health                                       Endpoint     State    Health                      Name  Description
            # -----------------------------------------------------------------------------------------------------------------------------------------------------
            data_format = '{fabric: >6}  {state1: >8}  {health1: >8}  {endpoint: >45}  {state2: >8}  {health2: >8}  {name: >24}  {description: <38}'
            print('')
            print(data_format.format(fabric='Fabric', state1='State', health1='Health', endpoint='Endpoint', state2='State', health2='Health', name='Name', description='Description'))
            print('-'*(149))

            # Print Fabric information, then iterate over endpoints
            for i in range(len(self.items)):
                print(data_format.format(
                    fabric=self.items[i].Id,
                    state1=self.items[i].State,
                    health1=self.items[i].Health,
                    endpoint='',
                    state2='',
                    health2='',
                    name='',
                    description=''))

                fabric = self.items[i]
                for i in range(len(fabric.endpoints)):
                    print(data_format.format(
                        fabric='',
                        state1='',
                        health1='',
                        endpoint=fabric.endpoints[i].Id,
                        state2=fabric.endpoints[i].State,
                        health2=fabric.endpoints[i].Health,
                        name=fabric.endpoints[i].Name,
                        description=fabric.endpoints[i].Description))

