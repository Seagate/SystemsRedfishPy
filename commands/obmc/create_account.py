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
# create_account.py 
#
# ******************************************************************************************
#
# @command create account
#
# @synopsis Create a new user account
#
# @description-start
#
# 'create account username=[username] password=[password]
#
# Parameters:
#     The 'username' parameter is required and specifies the new user account to create.
#     The 'password' parameter is required and specifies the password for the new account.
#
# Example:
#     create account username=user303 password=User303pwd1!
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
#     "UserName": "user303",
#     "Password": "User303pwd1!"
# }

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create account"""
    name = 'create account'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'Accounts'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Account: ({})...'.format(self.command))

        # From the command, build up the required JSON data
        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # UserName
        jsonType, username = JsonBuilder.getValue('username', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'UserName', username)
        else:
            Trace.log(TraceLevel.ERROR, "'username' is required")
            return

        # Password
        jsonType, password = JsonBuilder.getValue('password', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'Password', password)
        else:
            Trace.log(TraceLevel.ERROR, "'password' is required")
            return

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
