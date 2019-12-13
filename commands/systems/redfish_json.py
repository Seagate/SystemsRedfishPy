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
# redfish_json.py 
#
# ******************************************************************************************
#
# @command redfish json <url>
#
# @synopsis GET and display JSON data for a given URL
#
# @description-start
#
# This command will display the JSON data returned for a specified URL.
# Example: redfish json /redfish
# 
# [] URL : /redfish
# [] JSON:
#{
#    "v1": "/redfish/v1/"
#}
# 
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish json """
    name = 'redfish json'
    link = None
    startingurl = ''


    @classmethod
    def prepare_url(self, command):
        # Usage: redfish json <url>
        words = command.split(' ')
        if (len(words) > 2):
            self.startingurl = words[2]
        else:
            self.startingurl = ''
        Trace.log(TraceLevel.VERBOSE, '   ++ CommandHandler: redfish json // url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.VERBOSE, '   ++ CommandHandler: redfish json // process_url ({})'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True)
        self.link = link

    @classmethod
    def display_results(self, redfishConfig):

        print('')
        print('[] URL        : {}'.format(self.startingurl))
        print('[] Status     : {}'.format(self.link.urlStatus))
        print('[] Reason     : {}'.format(self.link.urlReason))
        print('[] JSON Data  :')
        if (self.link != None and self.link.jsonData != None):
            print(json.dumps(self.link.jsonData, indent=4))
