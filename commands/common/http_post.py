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
# http_post.py 
#
# ******************************************************************************************
#
# @command http post <url> <json | file>
#
# @synopsis Execute an HTTP POST operation on a URL passing JSON data as provided
#
# @description-start
#
# This command will perform an HTTP POST operation on the specified URL. Either the JSON
# data provided as a parameter will be included with the HTTP operation, or the JSON data 
# provided in a file. The third parameter is the '<url>'. If the fourth parameter contains
# a left curly bracket ('{') this function will expect well-formed JSON data; otherwise,
# this function will attempt to open and read the contents of a file. 
#
# Example:
#
# Example 1:
# (redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "username", "Password": "password" }
# 
# Example 2:
# (redfish) http post /redfish/v1/SessionService/Sessions json\credentials.json
#
# Example output:
# [[ POST DATA (/redfish/v1/SessionService/Sessions) ]]
# {
#     "UserName": "username",
#     "Password": "password"
# }
# [[ POST DATA END ]]
# 
# [] URL          : /redfish/v1/SessionService/Sessions
# [] Status       : 201
# [] Reason       : Created
# 
# [] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '261'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('X-Auth-Token', '518632a17e002e678bfec0f87678111a')]
# 
# [] HTTP Data    : {'@odata.context': '/redfish/v1/$metadata#Session.Session', '@odata.id': 'SessionService/Sessions/8', '@odata.type': '#Session.v1_1_0.Session', 'Description': 'User Session', 'Id': '8', 'Name': 'User Session', 'UserName': 'manage'}
# 
# [] JSON Data    : {
#     "@odata.context": "/redfish/v1/$metadata#Session.Session",
#     "@odata.id": "SessionService/Sessions/8",
#     "@odata.type": "#Session.v1_1_0.Session",
#     "Description": "User Session",
#     "Id": "8",
#     "Name": "User Session",
#     "UserName": "manage"
# }
# 
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - http post """
    name = 'http post'
    link = None
    command = ''
    startingurl = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        _, self.startingurl = ArgExtract.get_value(command, 2)
        Trace.log(TraceLevel.VERBOSE, 'http post: url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, '[] http post: url ({})'.format(url))
        _, jsonData = ArgExtract.get_json(self.command, 3)
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, jsonData, decode=False)
        self.link = link

    @classmethod
    def display_results(self, redfishConfig):
        if self.link != None:
            self.link.print_status()

        if (self.link != None and self.link.response != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] HTTP Headers : {}'.format(self.link.response.headers))

        if (self.link != None and self.link.response != None):
            Trace.log(TraceLevel.VERBOSE, '')
            Trace.log(TraceLevel.VERBOSE, '[] HTTP Data    : {}'.format(self.link.response.text))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] JSON Data    : {}'.format(json.dumps(self.link.jsonData, indent=4)))
