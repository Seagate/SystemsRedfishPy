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
# redfishConfig.py - Redfish API global configuration data. 
#
# ******************************************************************************************
#

import json
from collections import OrderedDict
from core.trace import TraceLevel, Trace
from version import __version__

################################################################################
# RedfishConfig
#
# All JSON configuration parameters are mapped directly to commands. For example:
#     !mcip will update JSON { "mcip" : "" }
#     !username will update JSON { "username" : "" }
#     !password will update JSON { "password" : "" }
#
# See dictionary initilization below for mapping.
#
################################################################################
class RedfishConfig:

    dictionary = OrderedDict()
    sessionKey = None
    sessionValid = False
    configurationfile = ''

    @classmethod
    def __init__(self, filename):

        self.configurationfile = filename

        #
        # Add new configuration settings here, they will be automatically written to the JSON file.
        #
        self.dictionary['annotate'] = True
        self.dictionary['brand'] = 'systems'
        self.dictionary['certificatecheck'] = False
        self.dictionary['dumphttpdata'] = False
        self.dictionary['dumpjsondata'] = False
        self.dictionary['dumppostdata'] = False
        self.dictionary['entertoexit'] = False
        self.dictionary['http'] = 'https'
        self.dictionary['httpbasicauth'] = False
        self.dictionary['linktestdelay'] = 0
        self.dictionary['mcip'] = ''
        self.dictionary['password'] = ''
        self.dictionary['serviceversion'] = 2
        self.dictionary['showelapsed'] = False
        self.dictionary['trace'] = int(TraceLevel.INFO)
        self.dictionary['urltimeout'] = 30
        self.dictionary['usefinalslash'] = True
        self.dictionary['username'] = ''
        
        Trace.log(TraceLevel.DEBUG, '++ Initilize Redfish API configuration from ({})...'.format(filename))

        currentvalue = 0
        
        with open(filename, "r") as read_file:
            try:
                Trace.log(TraceLevel.VERBOSE, 'Open JSON configuration file {}'.format(read_file))
                settings = json.load(read_file)

                for key in self.dictionary:
                    if key in settings:
                        self.dictionary[key] = settings[key]
                    Trace.log(TraceLevel.DEBUG, '   -- {0: <8} : {1}'.format(key, self.dictionary[key]))

                self.update_trace('trace', currentvalue, self.dictionary['trace'])
                self.save()
            except:
                Trace.log(TraceLevel.ERROR, 'Cannot parse JSON configuration file {}'.format(read_file))

    @classmethod
    def get_value(self, key):
        return self.dictionary[key]

    @classmethod
    def get_int(self, key):
        try:
            value = int(self.dictionary[key])
        except:
            value = -1
        return value

    @classmethod
    def get_float(self, key):
        try:
            value = float(self.dictionary[key])
        except:
            value = -1.0
        return value

    @classmethod
    def get_version(self):
        try:
            value = int(self.dictionary['serviceversion'])
            if value < 0:
                value = 1
        except:
            value = 2
        return value

    @classmethod
    def get_bool(self, key):
        results = False
        try:
            if self.dictionary[key] == 'True':
                results = True
            else:
                value = int(self.dictionary[key])
                if (value == 1):
                    results = True
        except:
            results = False
        return results

    @classmethod
    def get_urltimeout(self):
        return int(self.get_value('urltimeout'))

    @classmethod
    def display(self):
        
        print('   >> configuration values:')
        for key in self.dictionary:
            print('      -- {0: <20} : {1}'.format(key, self.dictionary[key]))

    @classmethod
    def update_trace(self, parameter, currentvalue, value):
        
        Trace.log(TraceLevel.DEBUG, '   ++ CFG: update_trace \'{}\' ({}) to ({})'.format(parameter, currentvalue, value))
        parameter = parameter.replace('!', '')
        if (parameter == 'trace' and currentvalue != value):
            Trace.setlevel(int(value))
            Trace.log(TraceLevel.DEBUG, '   ++ CFG: \'{}\' updated from ({}) to ({})'.format(parameter, currentvalue, value))

    @classmethod
    def save(self):
        Trace.log(TraceLevel.VERBOSE, '-- Save Redfish API configuration to ({})'.format(self.configurationfile))
        try:
            with open(self.configurationfile, "w") as write_file:
                json.dump(self.dictionary, write_file, indent=4)
        except:
            Trace.log(TraceLevel.ERROR, '-- Unable to save configuration to ({}) - check spelling'.format(self.configurationfile))
            pass

    @classmethod
    def update(self, parameter, value):
        
        updated = False

        Trace.log(TraceLevel.VERBOSE, '   -- Update Redfish API configuration parameter ({}), value ({}), config file ({})'.format(parameter, value, self.configurationfile))

        with open(self.configurationfile, "r") as read_file:
            settings = json.load(read_file)

        try:
            currentvalue = self.dictionary[parameter]
            self.dictionary[parameter] = settings[parameter] = value
            with open(self.configurationfile, "w") as write_file:
                json.dump(settings, write_file, indent=4)
                self.update_trace(parameter, currentvalue, value)
            # Update the trace level as needed
            if (parameter == 'trace'):
                Trace.setlevel(value)
            updated = True
        except:
            Trace.log(TraceLevel.ERROR, '   -- Unable to update parameter ({}) - check spelling'.format(parameter))
            pass

        return (updated)

    @classmethod
    def execute(self, command):
        
        command = command.strip()
        
        if (command[0] == '!'):
            if (command == '!dump'):
                self.display()
                
            else:
                words = command.split(' ')
                if (len(words) > 1):
                    parameter = words[0].replace('!', '')
                    if (self.update(parameter, words[1])):
                        Trace.log(TraceLevel.INFO, '   ++ CFG: \'{}\' set to ({})'.format(parameter, self.dictionary[parameter]))


