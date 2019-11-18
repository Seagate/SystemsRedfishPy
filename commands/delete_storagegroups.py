#
# @command delete storagegroups
#
# @synopsis Delete one or more comma-separated storage groups by serial number
#
# @description-start
#
# Use this command to delete storage groups. When a storage group is removed, that volume will no longer be visible to the host.
# 
# 'delete storagegroups 00c0ff511246000026fdc35d01000000_500605b00ab61310'                                                   - to delete a single storage group'
# 'delete storagegroups 00c0ff511246000026fdc35d01000000_500605b00ab61310,00c0ff511246000026fdc35d01000000_500605b00ab61311' - to delete two storage groups'
#
# Releated:
#     create storagegroups
#     show storagegroups
#
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - delete storagegroups"""
    name = 'delete storagegroups'
    ids = []

    @classmethod
    def prepare_url(self, command):
        Trace.log(TraceLevel.DEBUG, '++ delete storagegroups command:  {}'.format(command))
        self.ids = super().get_id_list(self, command, 2)
        return ('')

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '++ delete storagegroups ids:  {}'.format(len(self.ids)))
        super().delete_id_list(self, redfishConfig, config.storageGroups, self.ids)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        print(' ')
