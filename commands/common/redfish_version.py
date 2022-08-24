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
# @synopsis Display the current versions of the Redfish Service.
#
# @description-start
#
# This command reads '/redfish' and display the version information returned. It also
# reads '/redfish/v1' and displays the value of RedfishVersion and RedfishServiceVersion.
# 'RedfishVersion' is the current DMTF Redfish specification supported.
# 'RedfishServiceVersion' is the current version of the specific OEM Redfish Service, if supported.
#
# Example:
# 
# (redfish) redfish version
#
#   Property                Version
#   --------------------------------
#   /redfish/v1             v1
#   RedfishVersion          1.12.0
#   RedfishServiceVersion   2.4.10
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

    def prepare_url(self, redfishConfig, command):
        return (config.redfish)

    @classmethod
    def process_json(self, redfishConfig, url):

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False, None)

        if link.valid:
            print('')
            print('{0:<24}  {1:<8}'.format("Property", "Version"))
            print('-' * (24+2+8))

            for key in link.jsonData:
                print('{0:<24}  {1:<8}'.format(link.jsonData[key], key))

                linkv1 = UrlAccess.process_request(redfishConfig, UrlStatus(url+key), 'GET', False, None)

                if linkv1.valid:
                    if "RedfishVersion" in linkv1.jsonData:
                        print('{0:<24}  {1:<8}'.format("RedfishVersion", linkv1.jsonData["RedfishVersion"]))
                    if "Oem" in linkv1.jsonData and "Seagate" in linkv1.jsonData["Oem"] and "RedfishServiceVersion" in linkv1.jsonData["Oem"]["Seagate"]:
                        print('{0:<24}  {1:<8}'.format("RedfishServiceVersion", linkv1.jsonData["Oem"]["Seagate"]["RedfishServiceVersion"]))

        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish version // ERROR receiving data from ({}): Error {}: {}'.format(url, link.urlStatus, link.urlReason))
            

    @classmethod
    def display_results(self, redfishConfig):
        pass
