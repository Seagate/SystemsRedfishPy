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
# help_common.py 
#
# ******************************************************************************************
#

import glob
from core.trace import TraceLevel, Trace


################################################################################
# CommandHandler
################################################################################
class Help():
    """Help Command"""
    valid = False
    command = None
    commandFull = None
    commands = {}
    synopses = {}
    descriptions = {}

    @classmethod
    def store_command(cls, command):
        cls.valid = False
        cls.command = None
        cls.commands = {}
        cls.synopses = {}
        cls.descriptions = {}
        
        cls.commandFull = command.strip()
        Trace.log(TraceLevel.DEBUG, 'store_command: ({}) fill ({})'.format(command, cls.commandFull))
        
        # Handle both 'help' and 'show help' variations
        command = cls.commandFull.replace('show help ', '', 1)
        command = command.replace('help ', '', 1)
        words = command.split(' ')
        if (len(words) >= 2):
            cls.command = words[0] + ' ' + words[1]
        else:
            cls.command = command

        Trace.log(TraceLevel.DEBUG, '   SET command: ({})'.format(cls.command))

    @classmethod
    def extract_help_file(cls, filename):

        Trace.log(TraceLevel.DEBUG, '++ Check ({}) for command help...'.format(filename))
        lineCount = 1
        atcommand = None
        processing = False
        helptext = []
        
        with open(filename, 'r') as fileHandle:
            for line in fileHandle:
                lineCount += 1
                line = line.strip()
                
                if (line.startswith('# @command')):
                    # Example: '# @command redfish links'
                    commandFromFile = line.replace('# ', '', 1).replace('@command ', '', 1).strip()
                    Trace.log(TraceLevel.DEBUG, '   commandFromFile: [{}]'.format(commandFromFile))
                    words = commandFromFile.split(' ')

                    if (len(words) > 1):
                        atcommand = words[0] + ' ' + words[1]
                        cls.valid = True
                    Trace.log(TraceLevel.DEBUG, '   @command: [{}]'.format(atcommand))

                    if (atcommand != None):
                        cls.commands[atcommand] = commandFromFile

                elif (line.startswith('# @synopsis')):
                    # Example: '# @synopsis Test all URLs reported by this REST API'
                    text = line.replace('# ', '', 1)
                    text = text.replace('@synopsis ', '', 1).strip()
                    if (atcommand != None):
                        Trace.log(TraceLevel.DEBUG, '   @synopsis: [{}]'.format(text))
                        cls.synopses[atcommand] = text
                        
                elif (line.startswith('# @description-start')):
                    processing = True
                    
                elif (line.startswith('# @description-end')):
                    processing = False
                    if (atcommand != None):
                        cls.descriptions[atcommand] = helptext
                        Trace.log(TraceLevel.TRACE, '   @descriptions: total [{}]'.format(len(helptext)))

                elif (processing):
                    text = line.replace('# ', '', 1)
                    text = text.replace('#', '', 1)
                    if (atcommand != None):
                        helptext.append(text)
                        Trace.log(TraceLevel.TRACE, '   @description: [{}]'.format(text))
                    

    @classmethod
    def extract_help(cls, brand):
        Trace.log(TraceLevel.DEBUG, 'extract_help_file: START ({})'.format(brand))

        folder = 'commands/' + brand + '/*.py'
        list_of_files = glob.glob(folder)

        if (len(list_of_files) > 0):
            for filename in list_of_files: 
                cls.extract_help_file(filename)

    @classmethod
    def command_found(cls, command):

        Trace.log(TraceLevel.TRACE, 'command_found: command={}'.format(command))
        Trace.log(TraceLevel.TRACE, 'command_found: synopses={}'.format(cls.synopses))

        if (len(cls.synopses) > 0):
            for s in cls.synopses: 
                if (command == s):
                    Trace.log(TraceLevel.DEBUG, '-- show help...command_found: True'.format())
                    return True

        Trace.log(TraceLevel.DEBUG, '-- show help...command_found: False'.format())
        return False

    @classmethod
    def display_help(cls):

        Trace.log(TraceLevel.DEBUG, 'show help...DISPLAY valid={}'.format(cls.valid))

        if (cls.valid and cls.command != None):
            
            if (cls.commandFull == 'help' or cls.commandFull == 'show help'):
                # Display the synopses for all commands
                print('')
                print(' {0: <24}  {1}'.format('Command', 'Synopsis'))
                print(' ' + '='*170)
                for key in cls.synopses:
                    print(' {0: <24}  {1}'.format(key, cls.synopses[key]))

            elif (cls.command_found(cls.command)):
                print('')
                print(' ' + '='*170)
                print('')
                print(' Command: {}'.format(cls.commands[cls.command]))
                print('')
                print(' Description:')
                try:
                    for text in cls.descriptions[cls.command]:
                        print(' {}'.format(text))
                except:
                    print(' ERROR: command ({}) was not found in descriptions'.format(cls.command))
                    Trace.log(TraceLevel.TRACE, 'show help... descriptions={}'.format(cls.descriptions))
                    pass
                print(' ' + '='*170)

            else:
                print('')
                print('Did not find any help for ({})'.format(cls.command))

        Trace.log(TraceLevel.DEBUG, 'show help...END ({})'.format(cls.valid))
