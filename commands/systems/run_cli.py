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
# run_cli.py 
#
# ******************************************************************************************
#
# @command run cli <command>
#
# @synopsis Run a management controller CLI command
#
# @description-start
#
# Use the 'run cli' command to run any management controller CLI command. The 'run cli ' is
# removed from the passed in string and the entire remaining substring is sent to the
# management controller. Any JSON data returned from the controller is displayed.
#
# Examples:
#
#     (1) (redfish) run cli show controller-date
#
#     [] URL        : /redfish/v1/Systems/00C0FF437ED5/Actions/ComputerSystem.ExecuteMCCommand
#     [] Status     : 201
#     [] Reason     : Created
# 
#     [[ JSON DATA START ]]
#     {
#         "status": [
#             {
#                 "component-id": "",
#                 "meta": "/meta/status",
#                 "object-name": "status",
#                 "response": "Command completed successfully. (2020-11-30 16:40:07)",
#                 "response-type": "Success",
#                 "response-type-numeric": 0,
#                 "return-code": 0,
#                 "time-stamp": "2020-11-30 16:40:07",
#                 "time-stamp-numeric": 1606754407
#             }
#         ],
#         "time-settings-table": [
#             {
#                 "date-time": "2020-11-30 16:40:07",
#                 "date-time-numeric": 1606754407,
#                 "meta": "/meta/time-settings-table",
#                 "ntp-address": "10.30.127.102",
#                 "ntp-state": "Enabled",
#                 "object-name": "time-settings-table",
#                 "time-zone-offset": "-06:00"
#             }
#         ]
#     }
#     [[ JSON DATA END ]]
#
#     (2) (redfish) run cli add disk-group type virtual level RAID5 disks 0.0,0.1,0.2,0.3 pool A
# 
#     [] URL        : /redfish/v1/Systems/00C0FF437ED5/Actions/ComputerSystem.ExecuteMCCommand
#     [] Status     : 201
#     [] Reason     : Created
#     
#     [[ JSON DATA START ]]
#     {
#         "status": [
#             {
#                 "component-id": "",
#                 "meta": "/meta/status",
#                 "object-name": "status",
#                 "response": "Command completed successfully. (2020-11-30 16:47:41)",
#                 "response-type": "Success",
#                 "response-type-numeric": 0,
#                 "return-code": 0,
#                 "time-stamp": "2020-11-30 16:47:41",
#                 "time-stamp-numeric": 1606754861
#             }
#         ]
#     }
#     [[ JSON DATA END ]]
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishScript import RedfishScript
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus
import json

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - run cli """
    name = 'run cli'
    commandFull = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.commandFull = command.strip().replace('run cli ', '')
        url = RedfishSystem.get_uri(redfishConfig, 'SystemId') + 'Actions/ComputerSystem.ExecuteMCCommand'
        Trace.log(TraceLevel.DEBUG, 'Run CLI Command ({}) to ({})'.format(self.commandFull, url))
        return (url)

    @classmethod
    def process_json(self, redfishConfig, url):

        # Example: http post /redfish/v1/Systems/00C0FF437ED5/Actions/ComputerSystem.ExecuteMCCommand { "Command": "show volumes" }

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)
        JsonBuilder.addElement('main', JsonType.STRING, 'Command', self.commandFull)

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, JsonBuilder.getElement('main'))

        if link != None:
            link.print_status()

        print('')

        if (link.jsonData != None):
            Trace.log(TraceLevel.INFO, '[[ JSON DATA START ]]')
            print(json.dumps(link.jsonData, indent=4))
            Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
