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
import socket
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
    fileSettings = {}

    @classmethod
    def __init__(self, filename):

        #
        # Add new configuration settings here, they will be automatically written to the JSON file.
        # The configuration data is stored in a dictionary, with each entry being a tuple of (value, description)
        # self.dictionary['key'][0] = value
        # self.dictionary['key'][1] = description
        #
        self.dictionary['annotate']         = [True, 'True|False  Provides a banner for every line of script file processed. Default is True.']
        self.dictionary['brand']            = ['systems', '<string>    Specifies the subfolder of commands to use. Default is systems, but example is provided.']
        self.dictionary['certificatecheck'] = [False, 'True|False  When False, the URL will be opened using context=ssl._create_unverified_context. Default is False.']
        self.dictionary['dumphttpdata']     = [False, 'True|False  Display all HTTP data read from the Redfish Service. Useful for additional info. Default is False.']
        self.dictionary['dumpjsondata']     = [False, 'True|False  Display all JSON data read from the Redfish Service. Default is False.']
        self.dictionary['dumppostdata']     = [False, 'True|False  Display all data that is sent via an HTTP POST operation. Default is False.']
        self.dictionary['entertoexit']      = [False, 'True|False  When True, pressing Enter in interactive mode will exit the tool. Default is False.']
        self.dictionary['http']             = ['http', 'http|https  Switch between use http:// and https://. Default is https.']
        self.dictionary['httpbasicauth']    = [False, 'True|False  When True, use Redfish basic authentication, when False use a session. Default is False.']
        self.dictionary['linktestdelay']    = [0, '<int>       How long to delay between URLs when running the <redfish urls> command. Default is 0.']
        self.dictionary['mcip']             = ['', '<string>    Change all HTTP communications to use this new IP address.']
        self.dictionary['password']         = ['', '<string>    Change the password to [password] that is used to log in to the Redfish Service.']
        self.dictionary['serviceversion']   = [2, '1|2         Specify the Redfish Service version. This changes command behavior based on supported schemas. Default is 2.']
        self.dictionary['showelapsed']      = [False, 'True|False  Display how long each command took. Default is False.']
        self.dictionary['trace']            = [int(TraceLevel.INFO), '4-7         Turn on additional tracing. 4=INFO, 5=VERBOSE, 6=DEBUG, 7=TRACE. Default is 4=INFO.']
        self.dictionary['urltimeout']       = [300, '<int>       How long to wait for a URL request before timing out. Default is 300.']
        self.dictionary['usefinalslash']    = [True, 'True|False  When True, all Redfish URIs will have a slash as the final character in the URL. Default is True.']
        self.dictionary['username']         = ['', '<string>    Change the username to [name] that is used to log in to the Redfish Service.']

        self.load_config(filename)


    @classmethod
    def load_config(self, filename):

        self.configurationfile = filename

        Trace.log(TraceLevel.ALWAYS, '-- Using settings from ({})'.format(filename))

        currentvalue = 0
        
        with open(filename, "r") as read_file:
            try:            
                Trace.log(TraceLevel.VERBOSE, 'Open JSON configuration file {}'.format(filename))
                self.fileSettings = json.load(read_file)

                for key in self.dictionary:
                    if key in self.fileSettings:
                        Trace.log(TraceLevel.DEBUG, '   >> key={}, value={}'.format(key, self.fileSettings[key]))
                        self.dictionary[key][0] = self.fileSettings[key]
                    Trace.log(TraceLevel.DEBUG, '   -- {0: <8} : {1}'.format(key, self.dictionary[key][0]))

                self.update_trace('trace', currentvalue, self.dictionary['trace'][0])
                self.save()
            except:
                Trace.log(TraceLevel.ERROR, 'Cannot parse JSON configuration file {}'.format(read_file))

    @classmethod
    def get_value(self, key):
        #Trace.log(TraceLevel.DEBUG, 'get_value({})={}'.format(key, self.dictionary[key][0]))
        return self.dictionary[key][0]

    @classmethod
    def get_int(self, key):
        #Trace.log(TraceLevel.DEBUG, 'get_int({}) = {}'.format(key, self.get_value(key)))
        try:
            value = int(self.get_value(key))
        except:
            value = -1
        return value

    @classmethod
    def get_float(self, key):
        #Trace.log(TraceLevel.DEBUG, 'get_float({}) = {}'.format(key, self.get_value(key)))
        try:
            value = float(self.get_value(key))
        except:
            value = -1.0
        return value

    @classmethod
    def get_version(self):
        try:
            value = int(self.dictionary['serviceversion'][0])
            if value < 0:
                value = 1
        except:
            value = 2
        return value

    @classmethod
    def get_bool(self, key):
        results = False
        try:
            if self.dictionary[key][0] == 'True':
                results = True
            else:
                value = int(self.dictionary[key][0])
                if (value == 1):
                    results = True
        except:
            results = False
        return results

    @classmethod
    def get_urltimeout(self):
        return int(self.get_value('urltimeout'))

    @classmethod
    def get_mcip(self):
        mcip = socket.gethostbyname(self.get_value('mcip'))
        Trace.log(TraceLevel.DEBUG, 'get_mcip() = {}'.format(mcip))
        return mcip

    @classmethod
    def get_tracelevel(self):
        return Trace.getlevel()

    @classmethod
    def display(self):
        # self.dictionary[key][0]
        # self.dictionary[key][1]
        print('   >> configuration values:')
        print('{}{}'.format('   ', '-'*100))
        for key in self.dictionary:
            print('   -- {0: <20} : {1: <18} {2:}'.format(key, self.dictionary[key][0], self.dictionary[key][1]))

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
                # Sync file settings with current class values
                for key in self.dictionary:
                    self.fileSettings[key] = self.dictionary[key][0]
                json.dump(self.fileSettings, write_file, indent=4)
        except:
            Trace.log(TraceLevel.ERROR, '-- Unable to save configuration to ({}) - check spelling'.format(self.configurationfile))
            pass

    @classmethod
    def update(self, parameter, value):
        
        updated = False

        Trace.log(TraceLevel.VERBOSE, '   -- Update Redfish API configuration parameter ({}), value ({}), config file ({})'.format(parameter, value, self.configurationfile))

        with open(self.configurationfile, "r") as read_file:
            self.fileSettings = json.load(read_file)

        try:
            currentvalue = self.dictionary[parameter][0]
            self.dictionary[parameter][0] = value
            self.fileSettings[parameter] = value
            with open(self.configurationfile, "w") as write_file:
                json.dump(self.fileSettings, write_file, indent=4)
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
                        Trace.log(TraceLevel.INFO, '   ++ CFG: \'{}\' set to ({})'.format(parameter, self.dictionary[parameter][0]))
