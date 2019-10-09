#
# @command delete sessions
#
# @synopsis Delete one or more comma-separated session ids
#
# @description-start
#
# 'delete sessions Id1'           - to delete session Id1
# 'delete sessions Id1, Id2, Id3' - to delete sessions Id1, Id2, and Id3
#
# Example:
#
# (redfish) delete sessions Id1, Id2
# 
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete sessions"""
    name = 'delete sessions'
    ids = []

    @classmethod
    def prepare_url(self, command):
        self.ids = []
        Trace.log(TraceLevel.DEBUG, '++ delete sessions command:  {}'.format(command))
        # Expecting: delete sessions 1,2,3
        words = command.split(' ')
        if (len(words) >= 3):
            
            del words[0]    # Remove 'delete'
            del words[0]    # Remove 'sessions'

            tokens = words[0].split(',')
            for i in range(len(tokens)):
                Trace.log(TraceLevel.DEBUG, '   -- Add Id ({0}) to list of ids to delete'.format(tokens[i]))
                self.ids.append(tokens[i])
        return ('')
        
    @classmethod
    def process_json(self, config, url):

        Trace.log(TraceLevel.DEBUG, '++ delete sessions ids:  {}'.format(len(self.ids)))
        
        if (len(self.ids) >= 1):
            print(' ')
            for i in range(len(self.ids)):
                url = '/redfish/v1/SessionService/Sessions/' + self.ids[i]
                Trace.log(TraceLevel.INFO, '[] DELETE ({0})'.format(url))
                link = UrlAccess.process_request(config, UrlStatus(url), 'DELETE', True)
                if (link.valid):
                    Trace.log(TraceLevel.INFO, '   -- status={}, reason={}'.format(link.urlStatus, link.urlReason))
                else:
                    Trace.log(TraceLevel.INFO, '   -- status={}, reason={}'.format(link.urlStatus, link.urlReason))

    @classmethod
    def display_results(self, config):
        # Nothing to do in this case
        print(' ')
