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
# show_fans.py 
#
# ******************************************************************************************
#
# @command show fans
#
# @synopsis Display all fan readings from the system.
#
# @description-start
#
# 'show fans' displays details about all fan readings.
#
# Example:
#
# (redfish) show fans
#
#          Chassis    SensorName       Reading    Health
#   ----------------------------------------------------
#      enclosure_0         Fan 0          7680        OK
#      enclosure_0         Fan 1          7380        OK
#      enclosure_0         Fan 2          7620        OK
#      enclosure_0         Fan 3          7500        OK 
#
# @description-end
#
from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# DiskInformation
################################################################################
class FanInformation:
    """Fan Information"""

    Enclosure = ''
    MemberId = ''
    Reading = 0
    Name = ''
    StatusState = ''
    StatusHealth = ''

    def __init__(self, Enclosure, MemberId, Reading, Name, StatusState, StatusHealth):
        self.Enclosure = Enclosure
        self.MemberId = MemberId
        self.Reading = Reading
        self.Name = Name
        self.StatusState = StatusState
        self.StatusHealth = StatusHealth

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show fans"""
    name = 'show fans'
    link = None
    readings = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.readings = []
        return (RedfishSystem.get_uri(redfishConfig, 'Thermals'))
        
    @classmethod
    def process_json(self, redfishConfig, url):

        # GET Thermal Collection
        for thermalUrl in url:
            Trace.log(TraceLevel.DEBUG, '++ GET collection from ({})'.format(thermalUrl))
            self.link = UrlAccess.process_request(redfishConfig, UrlStatus(thermalUrl))
        
            # Retrieve a listing of all fans for this system
            if (self.link.valid):
                
                # Create a list of all the URLs
                for (key, value) in self.link.jsonData.items():
                    Trace.log(TraceLevel.TRACE, '   ++ Fans collection: key={} value={}'.format(key, value))
                    if (key == 'Fans'):
                        for link in value:
                            Trace.log(TraceLevel.DEBUG, '   ++ process item {}'.format(link['@odata.id']))

                            words = link['@odata.id'].split('/')
                            if (len(words) >= 4):
                                enclosure = words[4]
                            else:
                                enclosure = 'unknown'
    
                            MemberId = link['MemberId']
                            Reading = str(link['Reading'])
                            Name = link['Name']
                            statusDict = link['Status']
                            StatusState = statusDict['State']
                            StatusHealth = statusDict['Health']
                            
                            item = FanInformation(enclosure, MemberId, Reading, Name, StatusState, StatusHealth)
                            self.readings.append(item)

    @classmethod
    def display_results(self, redfishConfig):
        if (self.link != None):
            if (self.link.valid == False):
                print('')
                print(' [] URL        : {}'.format(self.link.url))
                print(' [] Status     : {}'.format(self.link.urlStatus))
                print(' [] Reason     : {}'.format(self.link.urlReason))
    
            else:
                print('')
                print('         Chassis    SensorName       Reading    Health')
                print('  ----------------------------------------------------')
                #           enclosure_0         Fan 0      7440 RPM        OK
                for i in range(len(self.readings)):
    
                    print('  {0: >14}  {1: >12}  {2: >12}  {3: >8}'.format(
                        self.readings[i].Enclosure,
                        self.readings[i].Name,
                        self.readings[i].Reading,
                        self.readings[i].StatusHealth))
