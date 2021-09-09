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
# http_push.py 
#
# ******************************************************************************************
#
# @command http push <url> <imagefile> <json | file>
#
# @synopsis Execute an HTTP multipart POST operation on a URL passing JSON data if provided
#
# @description-start
#
# This command will perform an HTTP PUSH operation on the specified URL using multipart/form-data.
# The <imagefile> specified will be read and sent to the target URL along with any specificed JSON data.
# The JSON data can be provided directly on the command line, or the JSON data will be read from a file.
#
# Parameters:
#     <url>         - The URL to send the HTTP PUSH to, http and ip address is added by this function
#     <imagefile>   - The file that will be sent to the service using HTTP multipart/form-data
#     <json | file> - Inline JSON data or a path to a JSON data file.
#
# Examples:
#     (redfish) http push mc_bundle.sfw /redfish/v1/UpdateService/FWUpdate { "Targets": [], "@Redfish.OperationApplyTime": "Immediate" }
#     (redfish) http push mc_bundle.sfw /redfish/v1/UpdateService/FWUpdate { "Targets": [], "@Redfish.OperationApplyTime": "OnReset" }
#     (redfish) http push mc_bundle.sfw /redfish/v1/UpdateService/FWUpdate json\upload.json
#
# @description-end
#

import json
import os
import requests
from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - http push """
    name = 'http push'
    link = None
    command = ''
    startingurl = ''
    fileError = False
    filename = False

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        _, self.startingurl = ArgExtract.get_value(command, 3)
        Trace.log(TraceLevel.INFO, '[] http push: url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '[] http push: url (2) ({})'.format(url))
        self.fileError = False
        _, self.filename = ArgExtract.get_value(self.command, 2)
        if os.path.exists(self.filename):
            _, jsonData = ArgExtract.get_json(self.command, 4)
            link = UrlAccess.process_push(redfishConfig, UrlStatus(url), self.filename, jsonData)
            self.link = link
        else:
            self.fileError = True

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] URL          : {}'.format(self.startingurl))

        if self.fileError:
            Trace.log(TraceLevel.INFO, '[] Status       : File ({}) does not exists'.format(self.filename))
        else:
            Trace.log(TraceLevel.INFO, '[] Status       : {}'.format(self.link.urlStatus))
            Trace.log(TraceLevel.INFO, '[] Reason       : {}'.format(self.link.urlReason))

        if self.context != '':
            print(' [] Context    : {}'.format(self.context))

        if (self.link != None and self.link.response != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] HTTP Headers : {}'.format(self.link.response.getheaders()))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] HTTP Data    : {}'.format(self.link.jsonData))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] JSON Data    : {}'.format(json.dumps(self.link.jsonData, indent=4)))
