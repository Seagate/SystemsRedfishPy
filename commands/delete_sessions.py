#
# @command delete sessions
#
# @synopsis Delete one or more comma-separated session ids
#
# @description-start
#
# 'delete sessions Id1'          - to delete session Id1
# 'delete sessions Id1,Id2,Id3'  - to delete sessions Id1, Id2, and Id3
#
# Example:
#
# (redfish) delete sessions Id1,Id2
# 
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete sessions"""
    name = 'delete sessions'
    ids = []

    @classmethod
    def prepare_url(self, command):
        Trace.log(TraceLevel.DEBUG, '++ delete sessions command: {}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')
        
    @classmethod
    def process_json(self, config, url):
        Trace.log(TraceLevel.DEBUG, '++ delete sessions ids:  {}'.format(len(self.ids)))
        super().delete_id_list(self, config, '/redfish/v1/SessionService/Sessions/', self.ids)

    @classmethod
    def display_results(self, config):
        # Nothing to do in this case
        print(' ')
