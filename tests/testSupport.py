# *************************************************************************************
#
# testSupport - Methods supporting Redfish unit test cases
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
import time

from jsonExtract import JsonExtract
from redfishCommand import RedfishCommand
from tests.testSystem import TestSystem
from urlAccess import UrlAccess, UrlStatus

################################################################################
# JsonExtract
################################################################################

class TestSupport:

    #
    # Validate that the link is valid after a URL Access is attempted
    # Validate that JSON data was returned
    #
    @classmethod
    def test_link_status(cls, testObject, link, url):
        testObject.assertTrue(link.valid, 'Link valid for URL ({})'.format(url))
        testObject.assertIsNotNone(link.jsonData, 'JSON data valid for URL ({})'.format(url))


    #
    # tuplePairs is and array of ('key', 'value')
    # For each array entry, validate that the JSON data contains the specified 'key' 
    # If 'value' is not None, validate that 'value' matches the value in the JSON data
    # Example: ("v1", "/redfish/v1/")
    #     key = "v1"
    #     value = "/redfish/v1/"
    #
    @classmethod
    def test_root_tags(cls, testObject, jsonData, tuplePairs):
        for tag in tuplePairs:
            value = JsonExtract.get_value(jsonData, None, tag[0], 1)
            testObject.assertIsNotNone(value, 'JSON Data Required Tag ({}) - ({})'.format(tag[0], value))
            if tag[1] is not None:
                testObject.assertEqual(value, tag[1], 'JSON Data value mismatch: expected ({}) got ({})'.format(tag[1], value))


    #
    # tupleTriplets is and array of ('parent', 'key', 'value')
    # For each array entry, validate that the JSON data contains a 'key' under a specified 'parent' key 
    # If 'value' is not None, validate that 'value' matches the value in the JSON data
    # Example: ("Systems", "@odata.id", "/redfish/v1/ComputerSystem")
    #     parent = "Systems"
    #     key = "@odata.id"
    #     value = "/redfish/v1/ComputerSystem"
    #
    @classmethod
    def test_nested_tags(cls, testObject, jsonData, tupleTriplets):
        for tag in tupleTriplets:
            value = JsonExtract.get_value(jsonData, tag[0], tag[1], 1)
            testObject.assertIsNotNone(value, 'JSON Data Required Tag ({}/{}) - ({})'.format(tag[0], tag[1], value))
            if tag[2] is not None:
                testObject.assertEqual(value, tag[2], 'JSON Data value mismatch: expected ({}) got ({})'.format(tag[2], value))


    @classmethod
    def create_diskgroup_paged(cls, testObject, redfishConfig, desiredName, poolName, driveCount, raidLevel):

        # Create a disk group
        count = driveCount
        command = 'create diskgroup name=' + desiredName + ' disks='
        for x in range(driveCount):
            drive1Url, drive1Number, drive1Serial = TestSystem.get_next_available_drive()
            command = command + drive1Number
            count -= 1
            if count:
                command = command + ','

        command = command + ' pool=' + poolName + ' level=' + raidLevel
        RedfishCommand.execute(redfishConfig, command)

        # Validate that the disk group and Pool exist
        url = config.storagePools
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 2, 'StoragePools Members@odata.count, expected {}, received {}'.format(2, membersCount))

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
        odataIds.remove('/redfish/v1/StorageServices/S1/StoragePools')

        for url in odataIds: 
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
            testObject.assertTrue(link.valid, 'StoragePool link valid for URL ({})'.format(url))

            description = JsonExtract.get_value(link.jsonData, None, 'Description', 1)
            name = JsonExtract.get_value(link.jsonData, None, 'Name', 1)

            if description == 'DiskGroup':
                testObject.assertEqual(name, desiredName, 'StoragePool name error, expected {}, received {}'.format(desiredName, name))
            elif description == 'Pool':
                testObject.assertEqual(name, poolName, 'StoragePool name error, expected {}, received {}'.format(poolName, name))

    @classmethod
    def delete_pool(cls, testObject, redfishConfig, poolName):

        # Remove Pool A and the disk group
        RedfishCommand.execute(redfishConfig, 'delete pools ' + poolName)

        time.sleep(config.sleepTimeAfterDelete)

        url = config.storagePools
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 0, 'StoragePools Members@odata.count, expected {}, received {}'.format(0, membersCount))


    @classmethod
    def create_volume_paged(cls, testObject, redfishConfig, desiredName, poolName, size):

        command = 'create volume name=' + desiredName + ' size=' + str(size) + ' pool=' + poolName
        RedfishCommand.execute(redfishConfig, command)

        # Validate that the volume exists
        url = config.volumes
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 1, 'Volumes Members@odata.count, expected {}, received {}'.format(1, membersCount))

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
        odataIds.remove('/redfish/v1/StorageServices/S1/Volumes')

        # Test name and size
        url = odataIds[0]
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        testObject.assertTrue(link.valid, 'Volume link valid for URL ({})'.format(url))
        name = JsonExtract.get_value(link.jsonData, None, 'Name', 1)
        testObject.assertEqual(name, desiredName, 'Volume name error, expected {}, received {}'.format(desiredName, name))
        capacity = JsonExtract.get_value(link.jsonData, None, 'CapacityBytes', 1)
        testObject.assertLessEqual(capacity, size, 'Volume size error, expected {}, received {}'.format(size, capacity))


    @classmethod
    def delete_volume(cls, testObject, redfishConfig, desiredName):

        # Delete Volume
        RedfishCommand.execute(redfishConfig, 'delete volumes ' + desiredName)

        time.sleep(config.sleepTimeAfterDelete)

        url = config.volumes
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 0, 'Volumes Members@odata.count, expected {}, received {}'.format(0, membersCount))
