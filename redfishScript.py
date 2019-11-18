# *************************************************************************************
#
# redfishScript - Module to run Systems Redfish API commands from a script file.
#
# -------------------------------------------------------------------------------------

# Copyright 2019 Seagate Technology LLC or one of its affiliates.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology LLC.
# Portions may also be trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized in writing by
# Seagate Technology LLC is prohibited. All rights are expressly reserved by
# Seagate Technology LLC.
#
# -------------------------------------------------------------------------------------
#

from os import path
from redfishConfig import RedfishConfig
from redfishCommand import RedfishCommand
from trace import TraceLevel, Trace

################################################################################
# RedfishScript
#
# Parses a script file and run the commands. There are two classes of commands:
#     !command - These commands set up the client configuration, such as '!mca <ipaddress>'
#     command  - The are Redfish API commands, such as 'redfish version' or 'show disks'
#
################################################################################
class RedfishScript:

    def execute_script(self, redfishConfig, scriptfile):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] Execute Redfish API script file ({})...'.format(scriptfile))

        # Run script mode
        if (path.exists(scriptfile) == False):
            Trace.log(TraceLevel.ERROR, 'Redfish API script file ({}) does not exist!'.format(scriptfile))
            return (-1)

        # Create an object to handle all commands
        command = RedfishCommand()

        lineCount = 0

        with open(scriptfile, 'r') as fileHandle:
            for line in fileHandle:

                line = line.strip()

                if (len(line) < 2 or line.startswith('#')):
                    # Skip comments
                    lineCount += 1
                    Trace.log(TraceLevel.TRACE, '   CMT: [{0: >3}] {1}'.format(len(line), line))

                elif (line.startswith('!')):
                    lineCount += 1
                    Trace.log(TraceLevel.TRACE, '   CFG: [{0: >3}] {1}'.format(len(line), line))
                    redfishConfig.execute(line)

                else:
                    lineCount += 1

                    if (redfishConfig.get_value('annotate') == 'yes'):
                        print('')
                        print('=' * 80)
                        print('= LINE[{0}] {1}'.format(lineCount, line))
                        print('=' * 80)

                    Trace.log(TraceLevel.TRACE, '   CMD: [{0: >3}] {1}'.format(len(line), line))
                    command.execute(redfishConfig, line)

        return (lineCount) 
