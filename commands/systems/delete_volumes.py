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
# delete_volumes.py 
#
# ******************************************************************************************
#
# @command delete volumes
#
# @synopsis Delete one or more comma-separated volumes by name or serial number
#
# @description-start
#
# 'delete volumes vol1'                              - to delete volume named 'vol1'
# 'delete volumes 00c0ff51124600006358975d01000000'  - to delete volume with serial number '00c0ff51124600006358975d01000000'
# 'delete volumes vol1, vol2, vol3                   - to delete volumes vol1, vol2, and vol3
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
    """Command - delete volumes"""
    name = 'delete volumes'
    ids = []

    @classmethod
    def prepare_url(self, command):
        Trace.log(TraceLevel.DEBUG, '++ delete volumes command:  {}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')
        
    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '++ delete volumes ids:  {}'.format(len(self.ids)))
        super().delete_id_list(self, redfishConfig, config.volumes, self.ids)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
