#
# @command run script [filename]
#
# @synopsis Run a script file
#
# @description-start
#
# Use the 'run script' command to run a script file.
#
# Example:
#     run script scripts/create_volumes.rfs
# 
# @description-end
#

import glob

from commands.commandHandlerBase import CommandHandlerBase
from redfishScript import RedfishScript
from trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - run script """
    name = 'run script'

    @classmethod
    def prepare_url(self, command):
        commandFull = command.strip()
        Trace.log(TraceLevel.DEBUG, '   SET commandFull: ({})'.format(commandFull))
        filename = commandFull.replace('run script ', '', 1)
        Trace.log(TraceLevel.DEBUG, '   SET filename: ({})'.format(filename))
        return (filename)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, 'run script...START ({})'.format(url))
        RedfishScript.execute_script(redfishConfig, url)

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
