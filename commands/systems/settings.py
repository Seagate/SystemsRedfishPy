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
# settings.py 
#
# ******************************************************************************************
#
# @command settings ...
#
# @synopsis Display details of all configuration settings.
#
# @description-start
#
# Use the 'settings' command to display all available configuration settings, a description
# or each setting, and how to update them.
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from commands.help_common import Help
from core.redfishConfig import RedfishConfig

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - help configuration """
    name = 'help configuration'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        print('')

    @classmethod
    def display_results(self, redfishConfig):

        print('There are several configuration settings used to set up communications and tracing.')
        print('')
        print('There are two key commands:')
        print('')
        print('(redfish)!dump              - Display all settings, their current values, and a brief description.')
        print('(redfish)![setting] [value] - Change [setting] to the new [value]. For example, !ipaddress 10.1.2.3 to update the IP address of the Redfish Service.')
        print('')
        print('To begin using this client, you must update these settings:')
        print('')
        print('(redfish)!ipaddress [value] - Update the IP address of the Redfish Service.')
        print('(redfish)!username [value]  - Update the username.')
        print('(redfish)!password [value]  - Update the password.')
        print('')
        RedfishConfig.display()

