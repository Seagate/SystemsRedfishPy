# *************************************************************************************
#
# testSystem - Routines to discover and retrieve available system resources. 
#
# -------------------------------------------------------------------------------------

# Copyright 2019 Seagate Technology LLC or one of its affiliates.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology LLC.
# Portions may also be trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized in writing by
# Seagate Technology LLC is prohibited. All rights are expressly reserved by
# Seagate Technology LLC.
#
# -------------------------------------------------------------------------------------
#

import config

from jsonExtract import JsonExtract
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus


################################################################################
# JsonExtract
################################################################################

class TestSystem:

    # An array of tuples storing disk information.
    #   disks[0] = [inUse, 'id', 'serial-number', 'speed', 'capacity', 'block-size', 'state', 'health']
    #   disks[N] = [inUse, 'id', 'serial-number', 'speed', 'capacity', 'block-size', 'state', 'health']
    drives = []

    #
    # Initialize an array of disks.
    #
    @classmethod
    def initialize_disks(cls, testObject, redfishConfig):

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

            driveInfo = [False, drive_number, serial_number, speed, capacity, block_size, state, health]
            cls.drives.append(driveInfo)

        cls.drives.sort(key=lambda tup: tup[1], reverse=False)

        Trace.log(TraceLevel.DEBUG, '++ initialize_disks: {} drives added'.format(len(cls.drives)))
        Trace.log(TraceLevel.DEBUG, '@@ drives: {}'.format(cls.drives))

    #
    # Initialize all needed system information. This must be called once at
    # before testing begins.
    #
    @classmethod
    def initialize_system(cls, testObject, redfishConfig):
        cls.initialize_disks(testObject, redfishConfig)

    @classmethod
    def get_next_available_drive(cls):
        url = None
        drive_number = ''
        serial_number = ''

        for drive in cls.drives:
            if drive[0] == False:
                drive_number = drive[1]
                serial_number = drive[2]
                url = config.drives + drive_number
                drive[0] = True
                Trace.log(TraceLevel.DEBUG, '++ get_next_available_drive: return drive {}, in use {}'.format(drive[1], drive[0]))
                break

        return url, drive_number, serial_number

