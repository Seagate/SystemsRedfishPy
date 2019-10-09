#
# @command redfish urls
#
# @synopsis Test all URLs reported by this REST API
#
# @description-start
#
# This command will traverse and validate all links reported by this service.
# The query begins with '/redfish/v1/' and then parses the JSON data and adds
# all new '@odata.id' URLs to an ordered dictionary. The process recursively
# queries each unchecked URL and adds any new URLs to the dictionary. Once
# all URLs have been checked, a summary is reported along with the link status.
#
# Example: redfish urls /redfish/v1
#
#  Redfish Link Validation
#
#  [] Starting URL: /redfish/v1/
#  [] Total URLs  :  177
#  [] Total OK    :  171
#  [] Total Errors:    6
#
#  Valid    Status        Reason  URL
# ------------------------------------------------------------------------------------------------------------------------------------
#   True       200                OK  /redfish/v1/
#   True       200                OK  /redfish/v1/Chassis# -- This will validate every URL used by this Redfish service provider and provide a summary.
#  False       501       Bad Request  /redfish/v1/Chassis//ComputerSystem/00C0FF43C844/Storage/
#  False       501         Not Found  /redfish/v1/Chassis/controller_a
#  False       501         Not Found  /redfish/v1/Chassis/controller_b
#   True       200                OK  /redfish/v1/Chassis/enclosure_0
# Etc.
# 
# @description-end
#
#

import time

from collections import OrderedDict
from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - redfish urls """
    name = 'redfish urls'
    data = ''
    allLinks = OrderedDict()
    startingurl = ''


    def total_links_to_check(self):
        total = 0
        for key in self.allLinks:
            link = self.allLinks[key]
            if (link.checked == False):
                total += 1
        return total


    def links_to_check(self):
        for key in self.allLinks:
            link = self.allLinks[key]
            if (link.checked == False):
                return True
        return False


    def get_next_link(self):
        for key in sorted (self.allLinks.keys()):
            link = self.allLinks[key]
            if (link.checked == False):
                return link
        return None

    def dump_links(self):
        Trace.log(TraceLevel.TRACE, '   // allLinks -- count={}'.format(len(self.allLinks)))
        index = 0
        for key in self.allLinks:
            link = self.allLinks[key]
            index += 1
            Trace.log(TraceLevel.TRACE, '   // allLinks -- [{}/{}] key={} checked={} url={}'.format(index, len(self.allLinks), key, link.checked, link.url))


    def add_links(self, data, parent):

        Trace.log(TraceLevel.TRACE, '   ++ CommandHandler: add_links ({}) parent ({})'.format(data, parent))

        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    Trace.log(TraceLevel.TRACE, '   ++ add_links dict ({})'.format(v))
                    self.add_links(self, v, k)
                elif isinstance(v, list):
                    for i in v:
                        Trace.log(TraceLevel.TRACE, '   ++ add_links list ({})'.format(i))
                        self.add_links(self, i, k)
                else:
                    Trace.log(TraceLevel.TRACE, '   @@ {0: >20} : {1: >24} -- {2}'.format(parent, k, v))
                    if (k == '@odata.id'):
                        if (v not in self.allLinks):
                            Trace.log(TraceLevel.DEBUG, '   @@ ++ New Link: ({})'.format(v))
                            link = UrlStatus(v)
                            self.allLinks[v] = link
                            self.dump_links(self)


    @classmethod
    def process_next_url(self, config, link):
        Trace.log(TraceLevel.TRACE, '   ++ CommandHandler: redfish urls // process_next_url ({}) session ({})'.format(link.url, config.sessionKey))
        UrlAccess.process_request(config, link)
        self.add_links(self, link.jsonData, '')


    @classmethod
    def prepare_url(self, command):
        # Usage: redfish urls [startingurl]
        words = command.split(' ')
        if (len(words) > 2):
            self.startingurl = words[2]
        else:
            self.startingurl = '/redfish/v1/'
            
        Trace.log(TraceLevel.INFO, '   ++ CommandHandler: redfish urls // starting url ({})'.format(self.startingurl))

        return (self.startingurl)

    @classmethod
    def process_json(self, config, url):

        Trace.log(TraceLevel.TRACE, '   ++ CommandHandler: redfish urls // process_json url ({})'.format(url))

        link = UrlAccess.process_request(config, UrlStatus(url), 'GET', True)
        self.allLinks[url] = link
        self.dump_links(self)
        self.add_links(self, link.jsonData, '')

        # While there are still URLs to check, continue to GET links and process until all links have been checked
        while self.links_to_check(self):

            sleepTime = config.get_value('linktestdelay')
            if (sleepTime):
                time.sleep(sleepTime)
            Trace.log(TraceLevel.INFO, '   .. urls total ({}) urls to process ({})'.format(len(self.allLinks), self.total_links_to_check(self)))
            
            nextLink = self.get_next_link(self)
            if (nextLink != None):
                Trace.log(TraceLevel.DEBUG, '... process_url ({})'.format(nextLink.url))
                self.process_next_url(config, nextLink)

    @classmethod
    def display_results(self, config):

        print('')
        print(' Redfish URL Validation')
        print('')

        totalUrls = len(self.allLinks)
        totalOk = 0
        totalErrors = 0
        
        for key in self.allLinks.keys():
            link = self.allLinks[key]
            if (link.urlReason == 'OK'):
                totalOk += 1
            else:
                totalErrors += 1
            
        print(' [] Starting URL: {}'.format(self.startingurl))
        print(' [] Total URLs  : {0: >4}'.format(totalUrls))
        print(' [] Total OK    : {0: >4}'.format(totalOk))
        print(' [] Total Errors: {0: >4}'.format(totalErrors))
        
        print('')
        print(' Valid    Status        Reason  URL')
        print('-' * (32 + 80 + 20))

        for key in sorted (self.allLinks.keys()):
            link = self.allLinks[key]
            marker = ''
            if (link.checked == False):
                marker = '** Not checked!'
            print('{0: >6}  {1: >8}  {2: >16}  {3: <80}  {4}'.format(str(link.valid), str(link.urlStatus), str(link.urlReason), link.url, marker))

