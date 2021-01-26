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
# show_initiators.py 
#
# ******************************************************************************************
#
# @command show initiators
#
# @synopsis Display all initiators found in the system
#
# @description-start
#
# 'show initiators' displays details about all initiators, including id, durable name, state, and health.
#
# Example:
#
# (redfish) show initiators
# 
#                  Id       DurableName     State  Health
#   -----------------------------------------------------
#    500605b00ab61310  500605b00ab61310   Enabled      OK
#    500605b00ab61311  500605b00ab61311   Enabled      OK
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
                self.Name = link.jsonData['Name']

            if ('Description' in link.jsonData):
                self.Description = link.jsonData['Description']

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
                if ('initiator' in link.jsonData['Description']):
                    valid = True

        return (valid)

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show initiators"""
    name = 'show initiators'
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
