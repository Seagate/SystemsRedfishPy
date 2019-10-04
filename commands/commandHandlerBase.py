#
# Command Handler base class
#

from trace import TraceLevel, Trace

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
