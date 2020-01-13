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
# testSystem.py - Routines to discover and retrieve available system resources. 
#
# ******************************************************************************************
#

import config
from core.jsonExtract import JsonExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# TestSystem
################################################################################

class TestSystem:

    # An array of dictionary items storing disk information.
    #   drives[0] = { 'inUse': inUse, 'number': id, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health]
    #   drives[N] = { 'inUse': inUse, 'number': id, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health]
    drives = []
    successfulInitialization = False

    #
    # Initialize an array of disks by using the Redfish API.
    #
    @classmethod
    def initialize_drives(cls, redfishConfig):

        cls.drives = []
        url = config.drives
        cls.successfulInitialization = False

        try:
            # GET DriveCollection
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
    
            # Retrieve a listing of all drives for this system
            membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
            totalDrives = int(membersCount)
            odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
            
            Trace.log(TraceLevel.INFO, '++ initialize_drives: membersCount={}, totalDrives={}'.format(membersCount, totalDrives))

            # Don't include the main @odata.id for the Drive Collection, all others are Drives/#.#
            odataIds.remove('/redfish/v1/StorageServices/S1/Drives')

            for driveUrl in odataIds: 
                link = UrlAccess.process_request(redfishConfig, UrlStatus(driveUrl), 'GET', True, None)
    
                drive_number = JsonExtract.get_value(link.jsonData, None, 'Id', 1)
                serial_number = JsonExtract.get_value(link.jsonData, None, 'SerialNumber', 1)
                speed = JsonExtract.get_value(link.jsonData, None, 'NegotiatedSpeedGbs', 1)
                capacity = JsonExtract.get_value(link.jsonData, None, 'CapacityBytes', 1)
                block_size = JsonExtract.get_value(link.jsonData, None, 'BlockSizeBytes', 1)
                state = JsonExtract.get_value(link.jsonData, 'Status', 'State', 1)
                health = JsonExtract.get_value(link.jsonData, 'Status', 'Health', 1)
    
                # If the drive is linked to one or more volumes, it is already in use.
                volumes = JsonExtract.get_value(link.jsonData, 'Volumes', '@odata.id', 1)
                inUse = False
                if volumes is not None:
                    inUse = True
    
                driveInfo = {'inUse': inUse, 'number': drive_number, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health}
                Trace.log(TraceLevel.VERBOSE, '++ initialize_drives: {0: >6} / {1} - {2: >24}'.format(drive_number, inUse, serial_number))
                cls.drives.append(driveInfo)

                cls.drives.sort(key=lambda k: k['number'], reverse=False)

                cls.successfulInitialization = True

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize drives, exception: {}'.format(e))
            cls.successfulInitialization = False

        Trace.log(TraceLevel.DEBUG, '++ initialize_disks: {} drives added'.format(len(cls.drives)))
        Trace.log(TraceLevel.TRACE, '@@ drives: {}'.format(cls.drives))

        return cls.successfulInitialization

    #
    # Initialize all needed system information. This must be called once at
    # before testing begins.
    #
    @classmethod
    def initialize_system(cls, redfishConfig):
        return cls.initialize_drives(redfishConfig)

    #
    # Returns the next available drive from the system information table.
    #
    # Returns a dictionary with url, drive number, and serial number.
    #
    @classmethod
    def get_next_available_drive(cls):
        url = None
        drive_number = ''
        serial_number = ''

        for drive in cls.drives:
            if drive['inUse'] == False:
                drive_number = drive['number']
                serial_number = drive['serial']
                url = config.drives + drive_number
                drive['inUse'] = True
                Trace.log(TraceLevel.DEBUG, '++ get_next_available_drive: return drive {}, in use {}'.format(drive_number, drive['inUse']))
                break

        return {'url': url, 'number': drive_number ,'serial': serial_number}


