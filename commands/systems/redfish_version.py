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
# redfish_version.py 
#
# ******************************************************************************************
#
# @command redfish version
#
# @synopsis Display the current version of the Redfish Service.
#
# @description-start
#
# This command will read '/redfish' and display the version information returned.
#
# Example:
# 
# (redfish) redfish version
#   Version    VersionURL
#   ---------------------
#        v1  /redfish/v1/
# 
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish version """
    name = 'redfish version'
    valid = False
    version = ''
    versionUrl = ''

    def prepare_url(self, redfishConfig, command):
        return (config.redfish)

    @classmethod
    def process_json(self, redfishConfig, url):

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False, None)

        self.valid = link.valid

        if (link.valid):
            for key in link.jsonData:
                self.version = key
                self.versionUrl = link.jsonData[key]

        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish version // ERROR receiving data from ({}): Error {}: {}'.format(url, link.urlStatus, link.urlReason))
            

    @classmethod
    def display_results(self, redfishConfig):

        if (self.valid):
            print('  Version    VersionURL')
            print('  ---------------------')
            #             v1  /redfish/v1/
            print('{0: >9}  {1: >12}'.format(self.version, self.versionUrl))
