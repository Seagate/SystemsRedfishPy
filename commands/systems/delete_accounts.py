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
# delete_accounts.py 
#
# ******************************************************************************************
#
# @command delete accounts
#
# @synopsis Delete one or more comma-separated user accounts
#
# @description-start
#
# This command will delete one or more user accounts.
#  
# Parameters:
#     At least one user account is required and specifies the user account to delete.
#
# Examples:
#
# (redfish) delete accounts user1
# Delete single user account user1
#
# (redfish) delete accounts user1,user2,user3
# Delete multiple user accounts user1, user2, and user3
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete account"""
    name = 'delete account'
    ids = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        Trace.log(TraceLevel.DEBUG, '++ delete accounts: command={}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')
        
    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '++ delete accounts: ids={}'.format(self.ids))
        super().delete_id_list(self, redfishConfig, RedfishSystem.get_uri(redfishConfig, 'Accounts'), self.ids)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
