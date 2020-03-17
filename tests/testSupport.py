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
# testSupport.py - Methods supporting Redfish unit test cases. 
#
# ******************************************************************************************
#

import config
import time
from core.jsonExtract import JsonExtract
from core.redfishCommand import RedfishCommand
from core.redfishSystem import RedfishSystem
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# TestSupport
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
        command = 'create diskgroup name=' + desiredName + ' disks='
        while driveCount > 0:
            drive = RedfishSystem.get_next_available_drive(redfishConfig)
            command = command + drive['number']
            driveCount -= 1
            if driveCount:
                command = command + ','

        command = command + ' pool=' + poolName + ' level=' + raidLevel
        RedfishCommand.execute(redfishConfig, command)

        # Validate that the disk group and Pool exist
        url = RedfishSystem.get_uri(redfishConfig, 'StoragePools')
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 2, 'StoragePools Members@odata.count, expected {}, received {}'.format(2, membersCount))

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")

        # Don't include the main @odata.id for the Collection
        if (url[-1] == '/'):
            url = url[:-1]

        if (len(odataIds) > 0):
            odataIds.remove(url)        

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

        url = RedfishSystem.get_uri(redfishConfig, 'StoragePools')
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 0, 'StoragePools Members@odata.count, expected {}, received {}'.format(0, membersCount))


    @classmethod
    def create_volume_paged(cls, testObject, redfishConfig, desiredName, poolName, size):

        command = 'create volume name=' + desiredName + ' size=' + str(size) + ' pool=' + poolName
        RedfishCommand.execute(redfishConfig, command)

        # Validate that the volume exists
        url = RedfishSystem.get_uri(redfishConfig, 'Volumes')
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 1, 'Volumes Members@odata.count, expected {}, received {}'.format(1, membersCount))

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")

        # Don't include the main @odata.id for the Collection
        if (url[-1] == '/'):
            url = url[:-1]

        if (len(odataIds) > 0):
            odataIds.remove(url)        

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

        url = RedfishSystem.get_uri(redfishConfig, 'Volumes')
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 0, 'Volumes Members@odata.count, expected {}, received {}'.format(0, membersCount))


    @classmethod
    def create_storage_group(cls, testObject, redfishConfig, lun, volume, access, ports, initiators):

        command = 'create storagegroup lun=\"' + lun + '\"' + ' volume=' + volume + ' access=' + access + ' ports=' + ports + ' initiators=' + initiators
        RedfishCommand.execute(redfishConfig, command)

        # Validate that the StorageGroup exists
        url = RedfishSystem.get_uri(redfishConfig, 'StorageGroups')
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        cls.test_link_status(testObject, link, url)
        membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
        testObject.assertEqual(membersCount, 1, 'StorageGroups Members@odata.count, expected {}, received {}'.format(1, membersCount))

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")

        # Don't include the main @odata.id for the Collection
        if (url[-1] == '/'):
            url = url[:-1]

        if (len(odataIds) > 0):
            odataIds.remove(url)        

        # Test name
        url = odataIds[0]
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
        testObject.assertTrue(link.valid, 'StorageGroup link valid for URL ({})'.format(url))

        name = JsonExtract.get_value(link.jsonData, None, 'Name', 1)
        words = name.split('_')
        testObject.assertEqual(2, len(words), 'StorageGroup Name error, expected {}, received {}'.format(2, len(words)))
        volumeId = words[0]
        testObject.assertEqual(volume, volumeId, 'StorageGroup Volume Name error, expected {}, received {}'.format(volume, volumeId))
