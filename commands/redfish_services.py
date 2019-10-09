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
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish services """
    name = 'redfish services'
    link = None

    def prepare_url(self, command):
        return ('/redfish/v1')
        
    @classmethod
    def process_json(self, config, url):

        self.link = UrlAccess.process_request(config, UrlStatus(url), 'GET', False)

    @classmethod
    def display_results(self, config):

        print('Redfish Services')
        print('---------------------')

        if (self.link.valid):
            print(json.dumps(self.link.jsonData, indent=4))
        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish services // ERROR receiving data from ({}): Error {}: {}'.format(self.link.url, self.link.urlStatus, self.link.urlReason))
