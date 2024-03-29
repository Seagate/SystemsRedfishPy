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
#                                            Id                                    DurableName     State    Health
# ----------------------------------------------------------------------------------------------------------------
#                                            A0                                    hostport_A0   Enabled        OK
#                                            A1                                    hostport_A1   Enabled        OK
#                                            B0                                    hostport_B0   Enabled        OK
#                                            B1                                    hostport_B1   Enabled        OK
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
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

            if ('Name' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Item: ({})'.format(link.jsonData['Name']))
                self.Description = link.jsonData['Name']
                
            if ('Status' in link.jsonData):
                status = link.jsonData['Status']
                if ('State' in status):
                    self.State = status['State']
                if ('Health' in status):
                    self.Health = status['Health']

            if ('Identifiers' in link.jsonData):
                ids = link.jsonData['Identifiers']
                self.DurableName = ids[0]['DurableName']

            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']

            if ('Description' in link.jsonData):
                if ('port' in link.jsonData['Description']):
                    valid = True

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
    def prepare_url(self, redfishConfig, command):
        self.items = []
        return (RedfishSystem.get_uri(redfishConfig, 'Endpoints'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.VERBOSE, '++ GET collection from ({})'.format(url))
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all endpoints for this system
        if (self.link.valid and self.link.jsonData):
            total = 0 
            created = 0
            urls = []

            # Create a list of all the URLs provided under Members
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                elif (key == 'Members'):
                    for link in value:
                        Trace.log(TraceLevel.VERBOSE, '   -- Add url ({})'.format(link['@odata.id']))
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
            self.link.print_status()

        else:
            #                                           Id                                    DurableName     State    Health
            # ---------------------------------------------------------------------------------------------------------------
            data_format = '{id: >45}  {name: >45}  {state: >8}  {health: >8}'
            print('')
            print(data_format.format(id='Id', name='DurableName', state='State', health='Health'))
            print('-'*(112))
            for i in range(len(self.items)):
                print(data_format.format(
                    id=self.items[i].Id,
                    name=self.items[i].DurableName,
                    state=self.items[i].State,
                    health=self.items[i].Health))
