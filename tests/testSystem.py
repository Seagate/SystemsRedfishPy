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

    #
    # Initialize an array of disks by using the Redfish API.
    #
    @classmethod
    def initialize_drives(cls, testObject, redfishConfig):

        cls.drives = []
        url = config.drives

        # GET DriveCollection
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        testObject.assertTrue(link.valid, 'Link valid for URL ({})'.format(url))
        testObject.assertIsNotNone(link.jsonData, 'JSON data valid for URL ({})'.format(url))

        # Retrieve a listing of all drives for this system
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        totalDrives = int(membersCount)
        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
        
        Trace.log(TraceLevel.INFO, '++ initialize_disks: membersCount={}, totalDrives={}'.format(membersCount, totalDrives))

        # Don't include the main @odata.id for the Drive Collection, all others are Drives/#.#
        odataIds.remove('/redfish/v1/StorageServices/S1/Drives')

        testObject.assertGreater(totalDrives, 0, 'Drives Members@odata.count ({})'.format(membersCount))
        testObject.assertGreater(len(odataIds), 0, 'Drives @odata.id length error ({})'.format(len(odataIds)))
        testObject.assertEqual(totalDrives, len(odataIds), 'Drives Members vs @odata.id error ({}, {})'.format(totalDrives, len(odataIds)))

        for driveUrl in odataIds: 
            link = UrlAccess.process_request(redfishConfig, UrlStatus(driveUrl), 'GET', True, None)
            testObject.assertTrue(link.valid, 'Drive link valid for URL ({})'.format(driveUrl))

            drive_number = JsonExtract.get_value(link.jsonData, None, 'Id', 1)
            serial_number = JsonExtract.get_value(link.jsonData, None, 'SerialNumber', 1)
            speed = JsonExtract.get_value(link.jsonData, None, 'NegotiatedSpeedGbs', 1)
            capacity = JsonExtract.get_value(link.jsonData, None, 'CapacityBytes', 1)
            block_size = JsonExtract.get_value(link.jsonData, None, 'BlockSizeBytes', 1)
            state = JsonExtract.get_value(link.jsonData, 'Status', 'State', 1)
            health = JsonExtract.get_value(link.jsonData, 'Status', 'Health', 1)

            driveInfo = {'inUse': False, 'number': drive_number, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health}

            cls.drives.append(driveInfo)

        cls.drives.sort(key=lambda k: k['number'], reverse=False)

        Trace.log(TraceLevel.DEBUG, '++ initialize_disks: {} drives added'.format(len(cls.drives)))
        Trace.log(TraceLevel.TRACE, '@@ drives: {}'.format(cls.drives))

    #
    # Initialize all needed system information. This must be called once at
    # before testing begins.
    #
    @classmethod
    def initialize_system(cls, testObject, redfishConfig):
        cls.initialize_drives(testObject, redfishConfig)

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


