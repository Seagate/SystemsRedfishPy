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
# redfish_services.py 
#
# ******************************************************************************************
#
# @command redfish services
#
# @synopsis GET and display the JSON data reported by the Redfish Service root
#
# @description-start
#
# This command will display the JSON odata returned from /redfish/v1.
#
# Example:
# 
# (redfish) redfish services
# Redfish Services
# ---------------------
# {
#     "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
#     "@odata.id": "/redfish/v1/",
#     "@odata.type": "#ServiceRoot.v1_2_0.ServiceRoot",
#     "Id": "RootService",
#     "Name": "Root Service",
#     "RedfishVersion": "1.0.2",
#     "UUID": "92384634-2938-2342-8820-489239905423",
#     "Systems": {
#         "@odata.id": "/redfish/v1/ComputerSystem"
#     },
#     "Chassis": {
#         "@odata.id": "/redfish/v1/Chassis"
#     },
#     "StorageServices": {
#         "@odata.id": "/redfish/v1/StorageServices"
#     },
#     "Managers": {
#         "@odata.id": "/redfish/v1/Managers"
#     },
#     "Tasks": {
#         "@odata.id": "/redfish/v1/TaskService"
#     },
#     "SessionService": {
#         "@odata.id": "/redfish/v1/SessionService"
#     },
#     "Links": {
#         "Oem": {},
#         "Sessions": {
#             "@odata.id": "/redfish/v1/SessionService/Sessions"
#         }
#     }
# }
# 
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish services """
    name = 'redfish services'
    link = None

    def prepare_url(self, redfishConfig, command):
        RedfishSystem.initialize_service_root_uris(redfishConfig)
        return (RedfishSystem.get_uri(redfishConfig, 'Root'))
        
    @classmethod
    def process_json(self, redfishConfig, url):

        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False)

    @classmethod
    def display_results(self, redfishConfig):

        print('Redfish Services')
        print('---------------------')

        if (self.link.valid):
            print(json.dumps(self.link.jsonData, indent=4))
        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish services // ERROR receiving data from ({}): Error {}: {}'.format(self.link.url, self.link.urlStatus, self.link.urlReason))
