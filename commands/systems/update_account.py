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
# update_account.py 
#
# ******************************************************************************************
#
# @command update account
#
# @synopsis Update a user account
#
# @description-start
#
# 'update account username=[username] password=[newpassword]
#
# Parameters:
#     The 'username' parameter is required and specifies the user account to update.
#     The 'password' parameter is required and specifies the new password for the account.
#
# Example:
#     update account username=user303 password=Newuser303pwd1!
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
# POST Accounts Example Data
################################################################################
# {
#     "Password": "Newuser303pwd1!"
# }

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - update account"""
    name = 'update account'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'Accounts'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Update Account: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # UserName
        jsonType, username = JsonBuilder.getValue('username', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.ERROR, "'username' is required")
            return

        # Password
        jsonType, password = JsonBuilder.getValue('password', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Password', password)
        else:
            Trace.log(TraceLevel.ERROR, "'password' is required")
            return

        fullurl = url + username
        link = UrlAccess.process_request(redfishConfig, UrlStatus(fullurl), 'PATCH', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
