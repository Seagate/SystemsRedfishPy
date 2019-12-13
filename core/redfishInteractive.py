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
# redfishInteractive.py - A module to run Systems Redfish API commands interactively. 
#
# ******************************************************************************************
#

import sys
from core.redfishCommand import RedfishCommand
from core.trace import TraceLevel, Trace

################################################################################
# RedfishPrompt
################################################################################
class RedfishPrompt():

    aliases = {'rf':'redfish'}

    def cmdloop(self, redfishConfig, prompt='redfish'):

        while 1:
            try:
                print('')
                sys.stdout.write('({}) '.format(prompt))
                sys.stdout.flush()
                line = sys.stdin.readline().strip()

            except KeyboardInterrupt:
                break

            if not line:
                break

            elif (line == 'exit' or line == 'quit'):
                break

            elif (line.startswith('alias')):
                # Add the new alias to the dictionary
                words = line.split(' ')
                if (len(words) == 3):
                    alias = words[1]
                    original = words[2]
                    Trace.log(TraceLevel.INFO, '   ++ CFG: replacing ({}) with the alias ({})'.format(alias, original))
                    self.aliases[alias] = original
                else:
                    Trace.log(TraceLevel.INFO, '   ++ usage: alias <new> <original>')

            elif (line.startswith('!')):
                Trace.log(TraceLevel.TRACE, '   CFG: [{0: >3}] {1}'.format(len(line), line))
                redfishConfig.execute(line)

            else:
                # Check for the use of any alias
                words = line.split(' ')
                if (len(words) > 1):
                    if (words[0] in self.aliases):
                        line = line.replace(words[0], self.aliases[words[0]], 1)

                Trace.log(TraceLevel.TRACE, '   CMD: [{0: >3}] {1}'.format(len(line), line))
                RedfishCommand.execute(redfishConfig, line)


################################################################################
# RedfishInteractive
################################################################################
class RedfishInteractive:

    def execute(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '[] Run Redfish API commands interactively...')

        RedfishPrompt().cmdloop(redfishConfig)



