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
# http_get.py 
#
# ******************************************************************************************
#
# @command http get <url>
#
# @synopsis Execute an HTTP GET and display JSON data for a given URL
#
# @description-start
#
# This command will perform an HTTP GET operation on the specified URL and return HTTP
# status and any JSON data returned.
#
# Example:
#
# (redfish) http get /redfish
# 
# [] URL        : /redfish
# [] Status     : 200
# [] Reason     : OK
# [] HTTP Data  : {'v1': '/redfish/v1'}
# [] JSON Data  :
# {
#     "v1": "/redfish/v1"
# }
# 
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - http get """
    name = 'http get'
    link = None
    startingurl = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        _, self.startingurl = ArgExtract.get_value(command, 2)
        Trace.log(TraceLevel.VERBOSE, 'http get: url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, '[] http get: url ({})'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True)
        self.link = link

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] URL        : {}'.format(self.startingurl))
        Trace.log(TraceLevel.INFO, '[] Status     : {}'.format(self.link.urlStatus))
        Trace.log(TraceLevel.INFO, '[] Reason     : {}'.format(self.link.urlReason))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '[] HTTP Data  : {}'.format(self.link.jsonData))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '[] JSON Data  : {}'.format(json.dumps(self.link.jsonData, indent=4)))
