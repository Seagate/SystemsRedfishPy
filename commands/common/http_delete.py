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
# http_delete.py 
#
# ******************************************************************************************
#
# @command http delete <url>
#
# @synopsis Execute an HTTP DELETE operation on a URI and display status
#
# @description-start
#
# This command will perform an HTTP DELETE operation on the specified URL and return HTTP
# status and any data returned.
#
# Example:
#
# (redfish) http delete /redfish/v1/StorageServices/S1/Volumes/00c0ff51125400008a4bce5e01000000
# 
# [] URL        : /redfish/v1/StorageServices/S1/Volumes/00c0ff51125400008a4bce5e01000000
# [] Status     : 200
# [] Reason     : OK
# [] HTTP Data  :
# {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully. (00c0ff51125400008a4bce5e01000000) - Volume 00c0ff51125400008a4bce5e01000000 was deleted. (2020-05-27 11:19:47)'}}
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - http delete """
    name = 'http delete'
    link = None
    startingurl = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        _, self.startingurl = ArgExtract.get_value(command, 2)
        Trace.log(TraceLevel.VERBOSE, 'http delete: url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, '[] http delete: url ({})'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'DELETE', True)
        self.link = link

    @classmethod
    def display_results(self, redfishConfig):
        if self.link != None:
            self.link.print_status()

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '[] HTTP Data  : {}'.format(self.link.jsonData))
