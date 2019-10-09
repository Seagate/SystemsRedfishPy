#
# @command help [command]
#
# @synopsis Display a synopsys of all commands, or details for a command
#
# @description-start
#
# Use the 'help' command to display all available commands. Use
# 'help [command name]' to display details for a command. 
# 
# @description-end
#

import glob

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - help """
    name = 'help'
    valid = False
    command = None
    commandFull = None

    commands = {}
    synopses = {}
    descriptions = {}

    @classmethod
    def extract_help(self, filename):

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
                        self.valid = True
                    Trace.log(TraceLevel.DEBUG, '   @command: [{}]'.format(atcommand))

                    if (atcommand != None):
                        self.commands[atcommand] = commandFromFile

                elif (line.startswith('# @synopsis')):
                    # Example: '# @synopsis Test all URLs reported by this REST API'
                    text = line.replace('# ', '', 1)
                    text = text.replace('@synopsis ', '', 1).strip()
                    if (atcommand != None):
                        Trace.log(TraceLevel.DEBUG, '   @synopsis: [{}]'.format(text))
                        self.synopses[atcommand] = text
                        
                elif (line.startswith('# @description-start')):
                    processing = True
                    
                elif (line.startswith('# @description-end')):
                    processing = False
                    if (atcommand != None):
                        self.descriptions[atcommand] = helptext
                        Trace.log(TraceLevel.TRACE, '   @descriptions: total [{}]'.format(len(helptext)))

                elif (processing):
                    text = line.replace('# ', '', 1)
                    text = text.replace('#', '', 1)
                    if (atcommand != None):
                        helptext.append(text)
                        Trace.log(TraceLevel.TRACE, '   @description: [{}]'.format(text))
                    

    @classmethod
    def prepare_url(self, command):
        self.commandFull = command.strip()
        Trace.log(TraceLevel.DEBUG, '   SET commandFull: ({})'.format(self.commandFull))
        
        # Handle both 'help' and 'show help' variations
        command = self.commandFull.replace('show help ', '', 1)
        command = command.replace('help ', '', 1)
        words = command.split(' ')
        if (len(words) >= 2):
            self.command = words[0] + ' ' + words[1]
        else:
            self.command = command

        Trace.log(TraceLevel.DEBUG, '   SET command: ({})'.format(self.command))
        return ('')

    @classmethod
    def process_json(self, config, url):
        Trace.log(TraceLevel.DEBUG, 'show help...START ({})'.format(url))

        list_of_files = glob.glob('commands/*.py')

        if (len(list_of_files) > 0):
            for filename in list_of_files: 
                self.extract_help(filename)

    @classmethod
    def command_found(self, command):

        Trace.log(TraceLevel.TRACE, '-- show help...command_found: command={}'.format(self.command))
        Trace.log(TraceLevel.TRACE, '-- show help...command_found: synopses={}'.format(self.synopses))

        if (len(self.synopses) > 0):
            for s in self.synopses: 
                if (command == s):
                    Trace.log(TraceLevel.DEBUG, '-- show help...command_found: True'.format())
                    return True

        Trace.log(TraceLevel.DEBUG, '-- show help...command_found: False'.format())
        return False

    @classmethod
    def display_results(self, config):

        Trace.log(TraceLevel.DEBUG, 'show help...DISPLAY valid={}'.format(self.valid))

        if (self.valid and self.command != None):
            
            if (self.commandFull == 'help' or self.commandFull == 'show help'):
                # Display the synopses for all commands
                print('')
                print(' {0: <24}  {1}'.format('Command', 'Synopsis'))
                print(' ' + '='*170)
                for key in self.synopses:
                    print(' {0: <24}  {1}'.format(key, self.synopses[key]))

            elif (self.command_found(self.command)):
                print('')
                print(' ' + '='*170)
                print('')
                print(' Command: {}'.format(self.commands[self.command]))
                print('')
                print(' Description:')
                try:
                    for text in self.descriptions[self.command]:
                        print(' {}'.format(text))
                except:
                    print(' ERROR: command ({}) was not found in descriptions'.format(self.command))
                    Trace.log(TraceLevel.TRACE, 'show help... descriptions={}'.format(self.descriptions))
                    pass
                print(' ' + '='*170)

            else:
                print('')
                print('Did not find any help for ({})'.format(self.command))

        Trace.log(TraceLevel.DEBUG, 'show help...END ({})'.format(self.valid))
