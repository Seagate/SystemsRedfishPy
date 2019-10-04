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

import json

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, LinkStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish odata """
    name = 'redfish odata'
    link = None

    def prepare_url(self, command):
        return ('/redfish/v1/odata')
        
    @classmethod
    def process_json(self, config, url):
        
        self.link = UrlAccess.process_link(config, LinkStatus(url), False)

    @classmethod
    def display_results(self, config):

        print('Redfish Odata')
        print('---------------------')

        if (self.link.valid):
            print(json.dumps(self.link.jsonData, indent=4))
        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish odata // ERROR receiving data from ({}): Error {}: {}'.format(self.link.url, self.link.urlStatus, self.link.urlReason))
