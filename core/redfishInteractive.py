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
# redfishInteractive.py - A module to run Systems Redfish API commands interactively. 
#
# ******************************************************************************************
#

import os
import readline
import rlcompleter
import sys
from core.redfishCommand import RedfishCommand
from core.trace import TraceLevel, Trace

HISTORY_FILENAME = 'redfishAPI.hist'

def get_history_items():
    return [ readline.get_history_item(i)
             for i in range(1, readline.get_current_history_length() + 1)
             ]

class HistoryCompleter(object):
    
    def __init__(self):
        self.matches = []
        return

    def complete(self, text, state):
        response = None

        Trace.log(TraceLevel.TRACE, '++ history complete: text={} state={}'.format(text, state))

        if state == 0:
            history_values = get_history_items()
            Trace.log(TraceLevel.TRACE, '++ history: {}'.format(history_values))
            if text:
                self.matches = sorted(h 
                                      for h in history_values 
                                      if h and h.startswith(text))
            else:
                self.matches = []
            Trace.log(TraceLevel.TRACE, '++ history matches: {}'.format(self.matches))

        try:
            response = self.matches[state]
        except IndexError:
            response = None

        Trace.log(TraceLevel.TRACE, '++ history complete({}, {}) => {}'.format(repr(text), state, repr(response)))

        # pause
        # text = sys.stdin.readline().strip()

        return response

################################################################################
# RedfishPrompt
################################################################################
class RedfishPrompt():

    aliases = {'rf':'redfish', 'cs':'create session'}

    def cmdloop(self, redfishConfig, prompt='redfish'):

        while True:
            try:
                print('')
                line = input('(' + prompt + ') ').strip()

            except KeyboardInterrupt:
                break

            if not line:
                if (redfishConfig.get_bool('entertoexit')):
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
                Trace.log(TraceLevel.TRACE, '>> PROCESS line={}'.format(line))
                # Check for the use of any alias
                words = line.split(' ')
                if (words and len(words) > 0):
                    if (words[0] in self.aliases):
                        line = line.replace(words[0], self.aliases[words[0]], 1)

                Trace.log(TraceLevel.TRACE, '   CMD: [{0: >3}] {1}'.format(len(line), line))
                RedfishCommand.execute(redfishConfig, line)

        # Store the history before exciting
        readline.write_history_file(HISTORY_FILENAME)

################################################################################
# RedfishInteractive
################################################################################
class RedfishInteractive:

    def execute(self, redfishConfig):

        # Configure history and tab completers
        readline.parse_and_bind('tab: complete')
        readline.set_completer(HistoryCompleter().complete)

        # Read the history file if it exists
        if os.path.exists(HISTORY_FILENAME):
            lines = len(open(HISTORY_FILENAME).readlines(  ))
            Trace.log(TraceLevel.INFO, '-- Reading history ({}) [{}]'.format(HISTORY_FILENAME, lines))
            readline.read_history_file(HISTORY_FILENAME)

        Trace.log(TraceLevel.INFO, '[] Run Redfish API commands interactively...')

        RedfishPrompt().cmdloop(redfishConfig)



