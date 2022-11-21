#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# listener_service.py
#
# ******************************************************************************************
#
# @command listener service <start | stop>
#
# @synopsis starts/ stops the Redfish event listener
#
# @description-start
#
# This command will start/ stop the Redfish event listener (using the specified IP and port via http/ https), based on the configuration
#
# 'listener service start'   - starts the event listener
# 'listener service stop'    - stops the event listener
#
# Notes,
# 1. Add this listener destination subscription in the system using below command, to see the events reaching to this listener service,
#    'http post /redfish/v1/EventService/Subscriptions json/EventDestination.json'
# 2. Show this listener destination subscription of the system,
#    'http get /redfish/v1/EventService/Subscriptions/<listener destination subscriber "Id">'
# 3. Delete this listener destination subscription from the system using below command,
#    'http delete /redfish/v1/EventService/Subscriptions/<listener destination subscriber "Id">'
# 4. Check if Test event reaching to the listener service,
#    'http post /redfish/v1/EventService/Actions/EventService.SubmitTestEvent json/testEvent.json'
#    then, look in "Events_<system IP>.txt" for the Test event
#
# Example:
#
# (redfish) listener service start
# Starting the listener service on 10.237.117.212:8080 via HTTP
#
# (redfish)
#
# @description-end
#

import traceback
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.argExtract import ArgExtract
from core.listener import Listener

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - event listener"""
    name = 'event listener'
    subcommand = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        _, self.subcommand = ArgExtract.get_value(command, 2)
        Trace.log(TraceLevel.DEBUG, '++ subcommand "{}"'.format(self.subcommand))
        return ''

    @classmethod
    def process_json(self, redfishConfig, url):
        if self.subcommand == 'start':
            if redfishConfig.listener == None:
                try:
                    Trace.log(TraceLevel.INFO, 'Starting the listener service on {}:{} via {}'.format(redfishConfig.get_value('listenerip'), redfishConfig.get_int('listenerport'), 'HTTPS' if redfishConfig.get_bool('listenerusessl') else 'HTTP'))
                    redfishConfig.listener = Listener(redfishConfig)
                    redfishConfig.listener.start()
                except Exception as err:
                    Trace.log(TraceLevel.ERROR, traceback.print_exc())
            else:
                Trace.log(TraceLevel.INFO, 'Listener service already running')
        elif self.subcommand == 'stop':
            if redfishConfig.listener != None:
                redfishConfig.listener.shutdown()
                Trace.log(TraceLevel.INFO, 'Listener service successfully stopped')
            else:
                Trace.log(TraceLevel.INFO, 'Listener service not running')

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
