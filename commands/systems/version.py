#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# version.py 
#
# ******************************************************************************************
#
# @command version
#
# @synopsis Display the current version of this tool
#
# @description-start
#
# Use the 'version' command to display the version of this tool.
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from commands.help_common import Help
from core.trace import TraceLevel, Trace
from version import __version__

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - version """
    name = 'version'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        Help.store_command(command)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, '[] SystemsRedfishPy v{}'.format(__version__))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
