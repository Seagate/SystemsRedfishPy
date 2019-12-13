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
# redfishCommand.py - Redfish API command execution. 
#
# ******************************************************************************************
#

import importlib
import math
import sys
import time
import traceback
from core.trace import TraceLevel, Trace

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
        #              This command creates a string commands.<brand>.show_disks
        #              The  dynamic_import() will then import commands/<brand>/show_disks.py
        #                  which in turn declares the CommandHandler class
        #              Then CommandHandler methods are called:
        #                  1) prepare_url()
        #                  2) process_json()
        #                  3) display_results()
        #
        # This design allows new command handling to be added without having to change the interpreter
        # or script processor. Only the new commands\<brand>\module.py has to be added. Use an existing
        # commands\<brand>\module.py as an example.
        #
        # The !brand configuration value is what determines the <brand> used. For example, when !brand = 'systems',
        # commands/systems/show_disks.py will be used when the user types 'show disks'.
        # 
        brand = redfishConfig.get_value('brand')
        words = command.split(' ')
        if (len(words) == 1):
            handlerName = 'commands.' + brand + '.' + words[0]
        elif (len(words) >= 2):
            if (words[0] == 'help'):
                handlerName = 'commands.' + brand + '.' + words[0]
            else:
                handlerName = 'commands.' + brand + '.' + words[0] + '_' + words[1]

        try:
            Trace.log(TraceLevel.DEBUG, '++ input command handler ({})'.format(handlerName))
            handler = dynamic_import(handlerName)

            url = handler.CommandHandler().prepare_url(command)
            Trace.log(TraceLevel.DEBUG, '      ++ URL: {}'.format(url))
    
            handler.CommandHandler().process_json(redfishConfig, url)
            handler.CommandHandler().display_results(redfishConfig)

            if (redfishConfig.get_bool('showelapsed')):            
                endTime = time.time()
                elapsedSeconds = int(math.ceil((endTime - startTime)/ 1.0))
        
                if (elapsedSeconds > 0):
                    minutes = elapsedSeconds // 60
                    seconds = elapsedSeconds - (minutes * 60)        
                    Trace.log(TraceLevel.INFO, '')
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
