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
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish version """
    name = 'redfish version'
    valid = False
    version = ''
    versionUrl = ''

    def prepare_url(self, command):
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
