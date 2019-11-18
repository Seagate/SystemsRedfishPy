#
# @command redfish metadata
#
# @synopsis GET and display the metadata reported by the Redfish Service
#
# @description-start
#
# This command will display the XML metadata returned from /redfish/v1/$metadata.
#
# Example:
# 
# (redfish) redfish metadata
# Redfish Metadata
# ---------------------
# <?xml version="1.0" ?>
# <edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
#     <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ServiceRoot_v1.xml">
#         <edmx:Include Namespace="ServiceRoot"/>
#         <edmx:Include Namespace="ServiceRoot.v1_2_0"/>
#     </edmx:Reference>
#     (... ommitted to reduce output ...) 
#     <edmx:DataServices>
#         <Schema Namespace="Service" xmlns="http://docs.oasis-open.org/odata/ns/edm">
#             <EntityContainer Extends="ServiceRoot.v1_2_0.ServiceContainer" Name="Service"/>
#         </Schema>
#     </edmx:DataServices>
# </edmx:Edmx>
# 
# @description-end
#

import config
import xml.dom.minidom

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish metadata """
    name = 'redfish metadata'
    link = None

    def prepare_url(self, command):
        return (config.metadata)
        
    @classmethod
    def process_json(self, redfishConfig, url):

        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False)

    @classmethod
    def display_results(self, redfishConfig):

        print('Redfish Metadata')
        print('---------------------')
        
        if (self.link.valid):
            dom = xml.dom.minidom.parseString(self.link.urlData)
            pretty_xml_as_string = dom.toprettyxml(indent='    ', newl='\n')
            for line in pretty_xml_as_string.splitlines():
                if (len(line.strip()) > 0):
                    print(line)              
        else:
            Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: redfish metadata // ERROR receiving data from ({}): Error {}: {}'.format(self.link.url, self.link.urlStatus, self.link.urlReason))
