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
# dump.py 
#
# ******************************************************************************************
#
# @command !dump OR [!setting value]
#
# @synopsis Display all configuration settings OR update the value of a setting.
#
# @description-start
#
# Usage:
#     !dump - to see current settings
#     !ipaddress <ipaddress> - to set the setting `ipaddress` to a new <ipaddress> value
#     !username <username> - to set the setting `username` to a new <username> value
#     !password <ipaddress> - to set the setting `password` to a new <password> value
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from commands.help_common import Help

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - dump """
    name = 'dump'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        Help.store_command(command)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Help.extract_help(redfishConfig.get_value('brand'))

    @classmethod
    def display_results(self, redfishConfig):
        Help.display_help()
