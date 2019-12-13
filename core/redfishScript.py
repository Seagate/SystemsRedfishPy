#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of thThe MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# redfishScript.py - A module to run Systems Redfish API commands from a script file. 
#
# ******************************************************************************************
#

from os import path
from core.redfishCommand import RedfishCommand
from core.trace import TraceLevel, Trace

################################################################################
# RedfishScript
#
# Parses a script file and run the commands. There are two classes of commands:
#     !command - These commands set up the client configuration, such as '!mca <ipaddress>'
#     command  - The are Redfish API commands, such as 'redfish version' or 'show disks'
#
################################################################################
class RedfishScript:

    @classmethod
    def execute_script(cls, redfishConfig, scriptfile):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] Execute Redfish API script file ({})...'.format(scriptfile))

        # Run script mode
        if (path.exists(scriptfile) == False):
            Trace.log(TraceLevel.ERROR, 'Redfish API script file ({}) does not exist!'.format(scriptfile))
            return (-1)

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
                    RedfishCommand.execute(redfishConfig, line)

        return (lineCount) 
