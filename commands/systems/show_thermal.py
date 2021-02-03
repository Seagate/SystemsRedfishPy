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
# show_thermal.py 
#
# ******************************************************************************************
#
# @command show thermal
#
# @synopsis Display all temperature data from the system
#
# @description-start
#
# 'show thermal' displays details about all temperature readings.
#
# Example:
#
# (redfish) show thermal
# 
#          Chassis    SensorName       Reading    Health
#   ----------------------------------------------------
#      enclosure_0      ctrl_A.1          46.0        OK
#      enclosure_0      ctrl_A.2          45.0        OK
#      enclosure_0      ctrl_A.3          30.0        OK
#      enclosure_0      ctrl_A.4          38.0        OK
#      enclosure_0      ctrl_A.5          70.0        OK
#      enclosure_0      ctrl_A.6          63.0        OK
#      enclosure_0     iom_0.A.0          30.0        OK
#      enclosure_0      ctrl_B.1          46.0        OK
#      enclosure_0      ctrl_B.2          42.0        OK
#      enclosure_0      ctrl_B.3          34.0        OK
#      enclosure_0      ctrl_B.4          55.0        OK
#      enclosure_0      ctrl_B.5          82.0        OK
#      enclosure_0      ctrl_B.6          62.0        OK
#      enclosure_0     iom_0.B.0          35.0        OK
#      enclosure_0     psu_0.0.0          28.0        OK
#      enclosure_0     psu_0.0.1          30.0        OK
#      enclosure_0     psu_0.1.0          27.0        OK
#      enclosure_0     psu_0.1.1          30.0        OK
#      enclosure_0      encl_0.0          33.0        OK
#      enclosure_0      encl_0.1          25.0        OK
#      enclosure_0      disk_0.0          29.0        OK
#      enclosure_0      disk_0.1          29.0        OK
#      enclosure_0      disk_0.2          28.0        OK
#      enclosure_0      disk_0.3          29.0        OK
#      enclosure_0      disk_0.4          28.0        OK
#      enclosure_0      disk_0.5          29.0        OK
#      enclosure_0      disk_0.6          29.0        OK
#      enclosure_0      disk_0.7          28.0        OK
#      enclosure_0      disk_0.8          28.0        OK
#      enclosure_0      disk_0.9          28.0        OK
#      enclosure_0     disk_0.20          27.0        OK
#      enclosure_0     disk_0.21          28.0        OK
#      enclosure_0     disk_0.22          29.0        OK
#      enclosure_0     disk_0.23          30.0        OK
#      enclosure_0     disk_0.10          28.0        OK
#      enclosure_0     disk_0.11          29.0        OK
#      enclosure_0     disk_0.12          29.0        OK
#      enclosure_0     disk_0.13          28.0        OK
#      enclosure_0     disk_0.14          32.0        OK
#      enclosure_0     disk_0.15          31.0        OK
#      enclosure_0     disk_0.16          28.0        OK
#      enclosure_0     disk_0.17          28.0        OK
#      enclosure_0     disk_0.18          28.0        OK
#      enclosure_0     disk_0.19          28.0        OK

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
class ThermalInformation:
    """Thermal Information"""

    Enclosure = 0
    MemberId = ''
    Name = ''
    ReadingCelsius = ''
    SensorName = ''
    StatusState = ''
    StatusHealth = ''

    def __init__(self, MemberId, Name, ReadingCelsius, SensorName, StatusState, StatusHealth, Enclosure):
        self.MemberId = MemberId
        self.Name = Name
        self.ReadingCelsius =ReadingCelsius
        self.SensorName = SensorName
        self.StatusState = StatusState
        self.StatusHealth = StatusHealth
        self.Enclosure = Enclosure

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show thermal"""
    name = 'show thermal'
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
            Trace.log(TraceLevel.VERBOSE, '++ GET Thermal collection from ({})'.format(thermalUrl))
            self.link = UrlAccess.process_request(redfishConfig, UrlStatus(thermalUrl))

            # Retrieve a listing of all temperatures for this system
            if (self.link.valid):
                
                # Create a list of all the URLs
                for (key, value) in self.link.jsonData.items():
                    Trace.log(TraceLevel.TRACE, '   ++ Thermal collection: key={} value={}'.format(key, value))
                    if (key == 'Temperatures'):
                        for link in value:
                            Trace.log(TraceLevel.TRACE, '   ++ process item {}'.format(link['@odata.id']))

                            words = link['@odata.id'].split('/')
                            if (len(words) >= 4):
                                Enclosure = words[4]
                            else:
                                Enclosure = 'unknown'

                            value = 'Test' if 1 == 1 else 'NoTest'

                            MemberId = link['MemberId'] if 'MemberId' in link else 'N/A'
                            Name = link['Name'] if 'Name' in link else 'N/A'
                            ReadingCelsius = link['ReadingCelsius'] if 'ReadingCelsius' in link else 'N/A'

                            if ('Status' in link):
                                statusDict = link['Status']
                                StatusState = statusDict['State'] if 'State' in statusDict else 'N/A'
                                StatusHealth = statusDict['Health'] if 'Health' in statusDict else 'N/A'
                            else:
                                StatusState = 'N/A'
                                StatusHealth = 'N/A'
    
                            # Adjust certain strings
                            SensorName = Name.replace('sensor_temp_', '')
    
                            item = ThermalInformation(MemberId, Name, ReadingCelsius, SensorName, StatusState, StatusHealth, Enclosure)
                            self.readings.append(item)

    @classmethod
    def display_results(self, redfishConfig):
        # self.print_banner(self)
        if (self.link != None):
            if (self.link == None or self.link.valid == False):
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
                        self.readings[i].SensorName,
                        self.readings[i].ReadingCelsius,
                        self.readings[i].StatusHealth))
