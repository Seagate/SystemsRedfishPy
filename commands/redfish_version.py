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

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, LinkStatus

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
        return ('/redfish')

    @classmethod
    def process_json(self, config, url):

        link = UrlAccess.process_link(config, LinkStatus(url), False, None)

        self.valid = link.valid

        if (link.valid):
            for key in link.jsonData:
                self.version = key
                self.versionUrl = link.jsonData[key]

        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish version // ERROR receiving data from ({}): Error {}: {}'.format(url, link.urlStatus, link.urlReason))
            

    @classmethod
    def display_results(self, config):

        if (self.valid):
            print('  Version    VersionURL')
            print('  ---------------------')
            #             v1  /redfish/v1/
            print('{0: >9}  {1: >12}'.format(self.version, self.versionUrl))
