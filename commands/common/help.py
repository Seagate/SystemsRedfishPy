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
# help.py 
#
# ******************************************************************************************
#
# @command help [command]
#
# @synopsis Display a synopsys of all commands, or details for a command
#
# @description-start
#
# Use the 'help' command to display all available commands. Use
# 'help [command name]' to display details for a command. 
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from commands.help_common import Help

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - help """
    name = 'help'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        Help.store_command(command)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Help.get_help_commands(redfishConfig)

    @classmethod
    def display_results(self, redfishConfig):
        Help.display_help()
