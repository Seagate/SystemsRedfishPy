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
# redfish_odata.py 
#
# ******************************************************************************************
#
# @command redfish odata
#
# @synopsis GET and display the odata reported by the Redfish Service
#
# @description-start
#
# This command will display the JSON odata returned from /redfish/v1/odata.
#
# Example:
# 
# (redfish) redfish odata
# Redfish Odata
# ---------------------
# {
#     "@odata.context": "/redfish/v1/$metadata",
#     "value": [
#         {
#             "name": "Service",
#             "kind": "Singleton",
#             "url": "/redfish/v1/"
#         },
#         {
#             "name": "Chassis",
#             "kind": "Singleton",
#             "url": "/redfish/v1/Chassis"
#         },
#         {
#             "name": "Managers",
#             "kind": "Singleton",
#             "url": "/redfish/v1/Managers"
#         },
#         {
#             "name": "SessionService",
#             "kind": "Singleton",
#             "url": "/redfish/v1/SessionService"
#         },
#         {
#             "name": "Sessions",
#             "kind": "Singleton",
#             "url": "/redfish/v1/SessionService/Sessions"
#         }
#     ]
# }
# 
# @description-end
#

import config
import json
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish odata """
    name = 'redfish odata'
    link = None

    def prepare_url(self, command):
        return (config.odata)
        
    @classmethod
    def process_json(self, redfishConfig, url):
        
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False)

    @classmethod
    def display_results(self, redfishConfig):

        print('Redfish Odata')
        print('---------------------')

        if (self.link.valid):
            print(json.dumps(self.link.jsonData, indent=4))
        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish odata // ERROR receiving data from ({}): Error {}: {}'.format(self.link.url, self.link.urlStatus, self.link.urlReason))
