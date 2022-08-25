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
# show_sessions.py 
#
# ******************************************************************************************
#
# @command show sessions
#
# @synopsis Display all active sessions, requires an active session
#
# @description-start
#
# 'show sessions' displays details about all authenticated sessions.
#
# Example:
#
# (redfish) show sessions
# 
#    Id          UserName              Name       Description
#  ---------------------------------------------------------
#     7            manage      User Session      User Session
#     8            manage      User Session      User Session
#     9            manage      User Session      User Session
#    10            manage      User Session      User Session
#    11            manage      User Session      User Session
#    12            manage      User Session      User Session
#    13            manage      User Session      User Session
#    14            manage      User Session      User Session
#    15            manage      User Session      User Session
#    16            manage      User Session      User Session
#    17            manage      User Session      User Session
#    18            manage      User Session      User Session#
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# SessionInformation
################################################################################
class SessionInformation:
    """Session Information"""

    Id = None
    Name = ''
    Description = ''
    UserName = ''
    
    def init_from_url(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Init from URL {}'.format(url))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Session: ({}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['Description'], link.jsonData['UserName']))
    
            self.Id = int(link.jsonData['Id'])
            self.Name = link.jsonData['Name']
            self.Description =link.jsonData['Description']
            self.UserName = link.jsonData['UserName']

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show sessions"""
    name = 'show sessions'
    link = None
    sessions = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.sessions = []
        return (RedfishSystem.get_uri(redfishConfig, 'Sessions'))
        
    @classmethod
    def process_json(self, redfishConfig, url):

        # GET DriveCollection
        Trace.log(TraceLevel.VERBOSE, '++ GET Session collection from ({})'.format(url))
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a listing of all sessions
        if (self.link.valid and self.link.jsonData):
            
            total = 0 
            created = 0
            urls = []

            Trace.log(TraceLevel.TRACE, '   -- <<< RESPONSE >>>>')
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('status', self.link.response.status_code))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('reason', self.link.response.reason))

            # Create a list of all the URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                elif (key == 'Members'):
                    for link in value:
                        urls.append(link['@odata.id'])
                        created += 1
            
            # Create object based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '   -- GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    session = SessionInformation()
                    session.init_from_url(redfishConfig, urls[i])
                    self.sessions.append(session)
            else:
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Members {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):
        # self.print_banner(self)
        if (self.link.valid == False):
            self.link.print_status()

        else:
            # Sort the list
            self.sessions.sort(key=lambda x: x.Id, reverse=False)

            print('')
            print('   Id          UserName              Name       Description')
            print(' ---------------------------------------------------------')
            for i in range(len(self.sessions)):
                print(' {0: >4}  {1: >16}  {2: >16}  {3: >16}'.format(
                    self.sessions[i].Id,
                    self.sessions[i].UserName,
                    self.sessions[i].Name,
                    self.sessions[i].Description))
