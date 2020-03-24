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
# commandHandlerBase.py - Command Handler base class. 
#
# ******************************************************************************************
#

from core.label import Label
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandlerBase
################################################################################
class CommandHandlerBase():
    """The base command handler class"""
    name = 'unknown'

    def print_banner(self):
        Trace.log(TraceLevel.DEBUG, '#')
        Trace.log(TraceLevel.DEBUG, '# Command ({})'.format(self.name))
        Trace.log(TraceLevel.DEBUG, '#')

    #
    # Return a list of command-separated ids
    # The command is expected to be of the format: 'word0 word1 id1,id2,id3'
    # The startId will indicate which word contains the comma-separated list
    # 
    def get_id_list(self, command, startWord):

        ids = []
        Trace.log(TraceLevel.DEBUG, '   ++ get_id_list from string: ({}) using start position {}'.format(command, startWord))

        words = command.split(' ')
        if (len(words) >= startWord+1):
            tokens = words[startWord].split(',')
            for i in range(len(tokens)):
                Trace.log(TraceLevel.TRACE, '      -- Add Id ({}) to list of ids'.format(tokens[i]))
                ids.append(tokens[i])

        Trace.log(TraceLevel.DEBUG, '      -- get_id_list found ({}) ids'.format(len(ids)))
        return (ids)

    #
    # Return a list of command-separated ids by requesting a collection
    # 
    def get_members_list(self, redfishConfig, collection, qualifier = ''):

        ids = []
        Trace.log(TraceLevel.DEBUG, '   ++ get_members_list from Redfish service: collection={}'.format(collection))

        itemUrl = RedfishSystem.get_uri(redfishConfig, collection)
        if (not itemUrl):
            return 

        Trace.log(TraceLevel.TRACE, '  Checking ({})'.format(itemUrl))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(itemUrl))
        if (link.valid and link.jsonData is not None):
            if ('Members' in link.jsonData and 'Members@odata.count' in link.jsonData and int(link.jsonData['Members@odata.count']) > 0):
                members =  link.jsonData['Members']
                for member in members:
                    if ('@odata.id' in member):
                        item = member['@odata.id']
                        words = item.split('/')
                        if (len(words) > 1):
                            itemId =  words[len(words) - 1]
                            if (qualifier == '' or itemId in qualifier):
                                Trace.log(TraceLevel.TRACE, '      -- adding ({})'.format(itemId))
                                ids.append(itemId)

        Trace.log(TraceLevel.DEBUG, '      -- get_members_list returning ({})'.format(ids))
        return (ids)

    #
    # Execute a DELETE action for a list of ids.
    # The caller must pass in the baseUrl to be used for all DELETE calls.
    # This routine returns a count of successful DELETE calls.
    # 
    def delete_id_list(self, redfishConfig, startUrl, ids):

        Trace.log(TraceLevel.DEBUG, '   ++ delete_id_list ids ({}) using start URL ({})'.format(len(ids), startUrl))
        
        successes = 0
        
        if (len(ids) >= 1):
            Trace.log(TraceLevel.INFO, ' ')
            for i in range(len(ids)):
                url = startUrl + Label.decode(ids[i], ids[i], 0)
                Trace.log(TraceLevel.INFO, '[] DELETE ({0})'.format(url))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'DELETE', True)
                Trace.log(TraceLevel.INFO, '   -- status={}, reason={}'.format(link.urlStatus, link.urlReason))
                if (redfishConfig.get_bool('dumphttpdata') and link.jsonData is not None):
                    Trace.log(TraceLevel.INFO, '   -- httpData {}'.format(link.jsonData))
                
                if (link.urlStatus == 200):
                    successes += 1
                else:
                    Trace.log(TraceLevel.DEBUG, '   -- response {}'.format(link.response))
                    Trace.log(TraceLevel.DEBUG, '   -- urlData {}'.format(link.urlData))
                    Trace.log(TraceLevel.DEBUG, '   -- jsonData {}'.format(link.jsonData))

        if (successes > 1):
            Trace.log(TraceLevel.INFO, '({}) DELETE commands were successful'.format(successes))

        return (successes)
