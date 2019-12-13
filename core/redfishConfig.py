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
    sessionKey = ''
    sessionValid = False

    @classmethod
    def __init__(self, filename):

        #
        # Add new configuration settings here, they will be automatically written to the JSON file.
        #
        self.dictionary['configurationfile'] = filename
        self.dictionary['version'] = __version__
        self.dictionary['http'] = ''
        self.dictionary['mcip'] = ''
        self.dictionary['username'] = ''
        self.dictionary['password'] = ''
        self.dictionary['annotate'] = 'yes'
        self.dictionary['urltimeout'] = 10
        self.dictionary['linktestdelay'] = 0
        self.dictionary['dumpjsondata'] = 0
        self.dictionary['dumppostdata'] = 0
        self.dictionary['trace'] = int(TraceLevel.INFO)
        self.dictionary['brand'] = 'systems'
        self.dictionary['showelapsed'] = False
        self.dictionary['CertificateCheck'] = False
        
        Trace.log(TraceLevel.DEBUG, '++ Initilize Redfish API configuration from ({})...'.format(filename))

        currentvalue = 0
        
        with open(filename, "r") as read_file:
            settings = json.load(read_file)

            for key in self.dictionary:
                if key in settings:
                    self.dictionary[key] = settings[key]
                Trace.log(TraceLevel.DEBUG, '   -- {0: <8} : {1}'.format(key, self.dictionary[key]))

        self.update_trace('trace', currentvalue, self.dictionary['trace'])

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
    def get_bool(self, key):
        results = False
        try:
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
    def update(self, parameter, value):
        
        updated = False
        configurationfile = self.dictionary['configurationfile']

        Trace.log(TraceLevel.INFO, '   -- Update Redfish API configuration parameter ({}), value ({}), config file ({})'.format(parameter, value, configurationfile))

        with open(configurationfile, "r") as read_file:
            settings = json.load(read_file)

        try:
            currentvalue = self.dictionary[parameter]
            self.dictionary[parameter] = settings[parameter] = value
            with open(configurationfile, "w") as write_file:
                json.dump(settings, write_file, indent=4)
                self.update_trace(parameter, currentvalue, value)
            # Update the trace level as needed
            if (parameter == 'trace'):
                Trace.setlevel(value)
            updated = True
        except:
            Trace.log(TraceLevel.INFO, '   -- Unable to update parameter ({}) - check spelling'.format(parameter))
            pass

        return (updated)

    @classmethod
    def execute(self, command):
        
        command = command.strip()
        
        if (command[0] == '!'):
            if (command == '!version'):
                Trace.log(TraceLevel.INFO, '   ++ CFG: Version ({})'.format(self.dictionary['version']))
            elif (command == '!dump'):
                self.display()
                
            else:
                words = command.split(' ')
                if (len(words) > 1):
                    parameter = words[0].replace('!', '')
                    if (self.update(parameter, words[1])):
                        Trace.log(TraceLevel.INFO, '   ++ CFG: \'{}\' set to ({})'.format(parameter, self.dictionary[parameter]))


