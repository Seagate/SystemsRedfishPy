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
# delete_pools.py 
#
# ******************************************************************************************
#
# @command delete pools
#
# @synopsis Delete one or more comma-separated pools by name or serial number
#
# @description-start
#
# 'delete pools A'                                - to delete pool named 'A'
# 'delete pools 00c0ff5112460000f75a925d01000000' - to delete pool with serial number '00c0ff5112460000f75a925d01000000'
# 'delete pools A,B                               - to delete pools A and B
#
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete pools"""
    name = 'delete pools'
    ids = []

    @classmethod
    def prepare_url(self, command):
        Trace.log(TraceLevel.DEBUG, '++ delete pools command:  {}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '++ delete pools ids:  {}'.format(len(self.ids)))
        super().delete_id_list(self, redfishConfig, config.storagePools, self.ids)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
