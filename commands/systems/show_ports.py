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
# show_ports.py 
#
# ******************************************************************************************
#
# @command show ports
#
# @synopsis Display all ports found in the system
#
# @description-start
#
# 'show ports' displays details about all ports, including id, durable name, state, and health.
#
# Example:
#
# (redfish) show ports
# 
#                  Id       DurableName     State  Health
#   -----------------------------------------------------
#                  A0                A0   Enabled      OK
#                  A1                A1   Enabled      OK
#                  B0                B0   Enabled      OK
#                  B1                B1   Enabled      OK
#
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# DiskInformation
################################################################################
class EndpointInformation:
    """Endpoint Information"""

    GroupType = ''
    EndpointURI = ''

    Name = ''
    Description = ''
    State = ''
    Health = ''
    DurableName = ''
    Id = ''

    def init_from_url(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Init from URL {}'.format(url))
        valid = False

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid):
            Trace.log(TraceLevel.DEBUG, '   ++ Item: ({}, {})'.format(link.jsonData['Name'], link.jsonData['GroupType']))

            # Extract the Endpoint URI if this item has GroupType == Server

            try:
                self.GroupType = link.jsonData['GroupType']

                if ((self.GroupType == "Server") and ('All' not in link.jsonData['Id'])):
                    endpoints = link.jsonData['Endpoints']
                    for i in range(len(endpoints)):
                        # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                        self.EndpointURI = endpoints[i]['@odata.id']

                    Trace.log(TraceLevel.DEBUG, '   ++ Examine: ({})'.format(self.EndpointURI))

                    link2 = UrlAccess.process_request(redfishConfig, UrlStatus(self.EndpointURI))
                    if (link2.valid):
                        Trace.log(TraceLevel.DEBUG, '   ++ Endpoint: ({}, {})'.format(link2.jsonData['Name'], link2.jsonData['Id']))

                        self.Name = link2.jsonData['Name']
                        self.Description =link2.jsonData['Description']

                        status = link2.jsonData['Status']
                        self.State = status['State']
                        self.Health = status['Health']

                        ids = link2.jsonData['Identifiers']
                        self.DurableName = ids[0]['DurableName']

                        self.Id = link2.jsonData['Id']
                        valid = True

            except:
                self.Description = 'Unknown'                        

        return (valid)

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show ports"""
    name = 'show ports'
    link = None
    items = []

    @classmethod
    def prepare_url(self, command):
        self.items = []
        return (config.endpointGroups)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.VERBOSE, '++ GET collection from ({})'.format(url))
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all endpoints for this system
        if (self.link.valid):
            total = 0 
            created = 0
            urls = []

            # Create a list of all the URLs provided under Members
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                elif (key == 'Members'):
                    for link in value:
                        urls.append(link['@odata.id'])
                        created += 1

            # Create objects based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '   -- GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    item = EndpointInformation()
                    if (item.init_from_url(redfishConfig, urls[i])):
                        self.items.append(item)
            else:
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
            print('                 Id       DurableName     State  Health')
            print('  -----------------------------------------------------')
            #         500605b00ab61310  500605b00ab61310   Enabled      OK
            for i in range(len(self.items)):
                print('  {0: >17}  {1: >16}  {2: >8}  {3: >6}'.format(
                    self.items[i].Id,
                    self.items[i].DurableName,
                    self.items[i].State,
                    self.items[i].Health))
