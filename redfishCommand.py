# *************************************************************************************
#
# redfishCommand - Redfish API command execution. 
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

import importlib
import math
import sys
import time
import traceback

from trace import TraceLevel, Trace

################################################################################
# dynamic_import
################################################################################
def dynamic_import(module):
    return importlib.import_module(module)


################################################################################
# RedfishCommand
################################################################################
class RedfishCommand:

    @classmethod
    def execute(cls, redfishConfig, command):
        
        Trace.log(TraceLevel.TRACE, '   -- Run command: ({})...'.format(command))
        startTime = time.time()
        
        # Use the first two words from the command to create a python module that will be instantiated.
        #
        # For example: show disks
        #              This command creates a string commands.show_disks
        #              The  dynamic_import() will then import commands/show_disks.py
        #                  which in turn declares the CommandHandler class
        #              Then CommandHandler methods are called:
        #                  CommandHandler.prepare_url(), process_json(), and display_results()
        #
        # This design allows new command handling to be added without having to change the interpreter
        # or script processor. Only the new commands\module.py has to be added. Use an existing commands\module.py
        # as an example.
        # 
        words = command.split(' ')
        if (len(words) == 1):
            handlerName = 'commands.' + words[0]
        elif (len(words) >= 2):
            if (words[0] == 'help'):
                handlerName = 'commands.' + words[0]
            else:
                handlerName = 'commands.' + words[0] + '_' + words[1]

        try:
            handler = dynamic_import(handlerName)

            url = handler.CommandHandler().prepare_url(command)
            Trace.log(TraceLevel.DEBUG, '      ++ URL: {}'.format(url))
    
            handler.CommandHandler().process_json(redfishConfig, url)
            handler.CommandHandler().display_results(redfishConfig)
            
            endTime = time.time()
            elapsedSeconds = int(math.ceil((endTime - startTime)/ 1.0))
    
            if (elapsedSeconds > 0):
                minutes = elapsedSeconds // 60
                seconds = elapsedSeconds - (minutes * 60)        
                Trace.log(TraceLevel.INFO, ''.format())
                Trace.log(TraceLevel.INFO, '[] Elapsed time: {}m {}s to execute command'.format(minutes, seconds))

        except ImportError:
            Trace.log(TraceLevel.ERROR, 'No module found for command ({}) using [{}]'.format(command, handlerName))
            pass

        except Exception as inst:
            Trace.log(TraceLevel.ERROR, 'Unexpected error while executing command ({}): {} -- {}'.format(command, sys.exc_info()[0], inst))
            Trace.log(TraceLevel.INFO, '-'*100)
            traceback.print_exc(file=sys.stdout)
            Trace.log(TraceLevel.INFO, '-'*100)
            pass
