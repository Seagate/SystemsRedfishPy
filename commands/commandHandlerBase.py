#
# Command Handler base class
#

import json

from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

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
    # Execute a DELETE action for a list of ids.
    # The caller must pass in the baseUrl to be used for all DELETE calls.
    # This routine returns a count of successful DELETE calls.
    # 
    def delete_id_list(self, config, startUrl, ids):

        Trace.log(TraceLevel.DEBUG, '   ++ delete_id_list ids ({}) using start URL ({})'.format(len(ids), startUrl))
        
        successes = 0
        
        if (len(ids) >= 1):
            print(' ')
            for i in range(len(self.ids)):
                url = startUrl + self.ids[i]
                Trace.log(TraceLevel.INFO, '[] DELETE ({0})'.format(url))
                link = UrlAccess.process_request(config, UrlStatus(url), 'DELETE', True)
                Trace.log(TraceLevel.INFO, '   -- status={}, reason={}'.format(link.urlStatus, link.urlReason))
                if (link.urlStatus == 200):
                    successes += 1
                else:
                    Trace.log(TraceLevel.DEBUG, '   -- response {}'.format(link.response))
                    Trace.log(TraceLevel.DEBUG, '   -- urlData {}'.format(link.urlData))
                    Trace.log(TraceLevel.DEBUG, '   -- jsonData {}'.format(link.jsonData))

                    Trace.log(TraceLevel.INFO, json.dumps(link.jsonData, indent=4))

        Trace.log(TraceLevel.INFO, '({}) DELETE commands were successful'.format(successes))
        return (successes)
