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
# delete_diskgroups.py 
#
# ******************************************************************************************
#
# @command delete diskgroups
#
# @synopsis Delete one or more comma-separated disk groups by name or serial number
#
# @description-start
#
# 'delete diskgroups dgA01'                             - to delete disk group named 'dgA01'
# 'delete diskgroups 00c0ff5112460000f55a925d00000000'  - to delete disk group with serial number '00c0ff5112460000f55a925d00000000'
# 'delete diskgroups dgA01,dgA02                        - to delete disk groups dgA01 and dgA02
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete diskgroups"""
    name = 'delete diskgroups'
    ids = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        Trace.log(TraceLevel.DEBUG, '++ delete diskgroups command:  {}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '++ delete diskgroups ids:  {}'.format(len(self.ids)))
        super().delete_id_list(self, redfishConfig, RedfishSystem.get_uri(redfishConfig, 'StoragePools'), self.ids)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        Trace.log(TraceLevel.DEBUG, ' ')
