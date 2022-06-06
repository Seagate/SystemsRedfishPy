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
# create_session.py 
#
# ******************************************************************************************
#
# @command create session
#
# @synopsis Establish a session with the Redfish Service (using ipaddress, username, and password)
#
# @description-start
#
# This command attempts to establish a session with the Redfish Service. It will use the
# ipaddress, username, and password that are defined in the configuration settings. Use '!dump' to
# view all configuration settings. Use '!setting value' to update the setting and value.
#
# Example:
# 
# (redfish) create session
# 
# ++ Establish Redfish session: (/redfish/v1/SessionService/Sessions)...
# [] Redfish session established (key=5ecff24c0259db2b810327047538dc9f)
# 
# @description-end
#

import config
import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.label import Label
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create session """
    name = 'create session'

    def prepare_url(self, redfishConfig, command):
        Trace.log(TraceLevel.INFO, '   -- ServiceVersion: {}'.format(redfishConfig.get_version()))
        Trace.log(TraceLevel.INFO, '   -- IP Address    : {}://{}:{}'.format(redfishConfig.get_value('http'), redfishConfig.get_ipaddress(), redfishConfig.get_port()))
        return (RedfishSystem.get_uri(redfishConfig, 'Sessions'))

    @classmethod
    def process_json(self, redfishConfig, url):

        redfishConfig.sessionValid = False

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.VERBOSE, '++ Establish Redfish session: ({})...'.format(url))

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)
        JsonBuilder.addElement('main', JsonType.STRING, 'UserName', redfishConfig.get_value('username'))
        JsonBuilder.addElement('main', JsonType.STRING, 'Password', redfishConfig.get_value('password'))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', False, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.TRACE, '   -- urlStatus={} urlReason={}'.format(link.urlStatus, link.urlReason))

        # HTTP 201 Created
        if (link.urlStatus == 201):

            if (link.jsonData != None):
                Label.encode(config.sessionIdVariable, link.jsonData['Id'])
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Id', link.jsonData['Id']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Name', link.jsonData['Name']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Description', link.jsonData['Description']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('UserName', link.jsonData['UserName']))
            else:
                Trace.log(TraceLevel.TRACE, '   -- JSON data was (None)')
            
            redfishConfig.sessionKey = link.response.getheader('X-Auth-Token', '')
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('sessionKey', redfishConfig.sessionKey))
            if (redfishConfig.sessionKey != ''):
                redfishConfig.sessionValid = True

        else:
            if self.link != None:
                self.link.print_status()

    @classmethod
    def display_results(self, redfishConfig):

        if (redfishConfig.sessionValid == True):            
            Trace.log(TraceLevel.INFO, '[] Redfish session established ({}:{})'.format(Label.decode(config.sessionIdVariable), redfishConfig.sessionKey))
        else:            
            Trace.log(TraceLevel.ERROR, 'Unable to establish a Redfish session, connection, check ip address, username and password')
