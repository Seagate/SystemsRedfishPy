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
# run_loop.py 
#
# ******************************************************************************************
#
# @command run loop [count] [uri]
#
# @synopsis Run an HTTP GET operation on a URI N times. Used to analyze performance.
#
# @description-start
#
# Use the 'run loop' command to run an HTTP GET command 'count' times.
#
# Command line options:
#    [count] - Must be 0 to N. The number of times to run the operation on the URI.
#    [uri]   - The URI to perform the HTTP operation on, such as /redfish/v1 
#
# Example:
#     run loop 100 /redfish/v1/StorageServices/S1/Volumes/AVolume01
#
# Output:
#     A message for each iteration of the operation, plus timing for each, and
#     a summary of all operations. 
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - run script """
    name = 'run script'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        commandFull = command.strip()
        Trace.log(TraceLevel.DEBUG, '   SET commandFull: ({})'.format(commandFull))
        return (commandFull)

    @classmethod
    def process_json(self, redfishConfig, url):
        cmd = url.replace('run loop ', '', 1)
        words = cmd.split(' ')
        timings = []

        Trace.log(TraceLevel.DEBUG, '++ words={} - {}'.format(len(words), words))
        if (len(words) == 2):
            count = int(words[0])
            uri = words[1]
            Trace.log(TraceLevel.DEBUG, '++ count={}, uri={}'.format(count, uri))
            
            index = 1
            while index < count+1:
                link = UrlAccess.process_request(redfishConfig, UrlStatus(uri))
                Trace.log(TraceLevel.INFO, '[{0:4}] [{1:18}] GET {2}'.format(index, link.elapsedMicroseconds, uri))
                timings.append(link.elapsedMicroseconds)
                index += 1

            average = sum(timings) / len(timings)
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, 'Average : {:,}'.format(average))
            
        else:
            Trace.log(TraceLevel.ERROR, 'run loop expects: [count] [uri] but has this string ({})'.format(url))


    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
