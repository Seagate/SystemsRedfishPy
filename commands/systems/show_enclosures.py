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
# show_enclosures.py 
#
# ******************************************************************************************
#
# @command show enclosures
#
# @synopsis Display all enclosures in the system
#
# @description-start
#
# 'show enclosures' displays details about all available enclosures along with midplane serial numbers.
#
# Example:
#
# (redfish) show enclosures
#
#  Enc      SerialNumber      Vendor  Rack  Pos        State        Health
#  -----------------------------------------------------------------------
#    1  500c0ff0cde3873c     Seagate     0    0      Enabled      Critical
#    2  500c0ff0cde3843c     Seagate     0    0      Enabled            OK
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# EnclosureInformation
################################################################################
class EnclosureInformation:
    """Enclosure Information"""

    Id = ''
    Name = ''
    ChassisType = ''
    IndicatorLED = ''
    PowerState = ''

    EnclosureNumber = ''
    SerialNumber = ''
    Manufacturer = ''
    Rack = ''
    RackOffset = ''
    State = ''
    Health = ''

    def init_from_url(self, redfishConfig, url):

        Trace.log(TraceLevel.DEBUG, '   ++ Enclosure init from URL {}'.format(url))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):

            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('ChassisType' in link.jsonData):
                self.ChassisType = link.jsonData['ChassisType']

            if ('IndicatorLED' in link.jsonData):
                self.IndicatorLED = link.jsonData['IndicatorLED']

            if ('PowerState' in link.jsonData):
                self.PowerState = link.jsonData['PowerState']

            words = self.Id.split('_')
            if (len(words) > 0):
                self.EnclosureNumber = words[1]

            if ('SerialNumber' in link.jsonData):
                self.SerialNumber = link.jsonData['SerialNumber']

            if ('Manufacturer' in link.jsonData):
                self.Manufacturer = link.jsonData['Manufacturer']

            if ('Location' in link.jsonData):
                location = link.jsonData['Location']
                if ('Placement' in location):
                    placement = location['Placement']
                    if ('Rack' in placement):
                        self.Rack = placement['Rack']
                    if ('RackOffset' in placement):
                        self.RackOffset = placement['RackOffset']

            if ('Status' in link.jsonData):
                status = link.jsonData['Status']
                if ('State' in status):
                    self.State = status['State']
                if ('Health' in status):
                    self.Health = status['Health']
                
        return (True)

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show enclosures"""
    name = 'show enclosures'
    enclosures = []
    link = None

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.enclosures = []
        return (RedfishSystem.get_uri(redfishConfig, 'Chassis'))

    @classmethod
    def process_json(self, redfishConfig, url):

        if (not url):
            return

        # GET list of enclosures
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a listing of all enclosures for this system

        if (self.link.valid and self.link.jsonData != None):

            total = 0 
            created = 0
            urls = []
            
            # Create a list of all the pool URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                    Trace.log(TraceLevel.VERBOSE, '... GET total ({})'.format(total))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '... Members value ({})'.format(value))
                    if (value != None):
                        for groupLink in value:
                            url = groupLink['@odata.id']
                            Trace.log(TraceLevel.VERBOSE, '... ADD url ({})'.format(url))
                            urls.append(url)
                            created += 1

            # Create object based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    enc = EnclosureInformation()
                    if (enc.init_from_url(redfishConfig, urls[i])):
                        self.enclosures.append(enc)
            elif (created > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Members {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):

        if (self.link == None):
            return 

        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            #         0                 1           2     3    4            5             6
            print(' Enc      SerialNumber      Vendor  Rack  Pos        State        Health')
            print(' -----------------------------------------------------------------------')
            #        1   500C0FF0CDE3873C     Seagate     0    0      Enabled      Critical
            if (self.enclosures != None):
                for i in range(len(self.enclosures)):
                    print(' {0: >3}  {1: >16}  {2: >10}  {3: >4}  {4: >3}  {5: >11}  {6: >12}'.format(
                        self.enclosures[i].EnclosureNumber,
                        self.enclosures[i].SerialNumber,
                        self.enclosures[i].Manufacturer,
                        self.enclosures[i].Rack,
                        self.enclosures[i].RackOffset,
                        self.enclosures[i].State,
                        self.enclosures[i].Health
                        ))
