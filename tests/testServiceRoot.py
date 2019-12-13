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
# testServiceRoot.py - Unit test cases for Redfish ServiceRoot capabilities. 
#
# ******************************************************************************************
#

import config
import unittest

from core.jsonExtract import JsonExtract
from core.redfishCommand import RedfishCommand
from core.redfishConfig import RedfishConfig
from core.urlAccess import UrlAccess, UrlStatus
from tests.testSupport import TestSupport

################################################################################
# TestServiceRoot
################################################################################

class TestServiceRoot(unittest.TestCase):

    def setUp(self):
        self.root = '/redfish'
        self.version = 'v1'
        self.versionUrl = '/redfish/v1/'
        self.redfishConfig = RedfishConfig(config.defaultConfigFile)

    def test_version(self):
        # Verify GET /redfish returns JSON data with /redfish/v1/
        url = self.root
        link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', False, None)
        TestSupport.test_link_status(self, link, url)

        expected = [("v1", "/redfish/v1/")]
        TestSupport.test_root_tags(self, link.jsonData, expected)

    def test_serviceroot(self):
        # Verify GET /redfish/v1 returns expected JSON data 
        url = self.versionUrl
        link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', False, None)
        TestSupport.test_link_status(self, link, url)
        
        expected = [
            ("@odata.context", "/redfish/v1/$metadata#ServiceRoot.ServiceRoot"),
            ("@odata.id", "/redfish/v1/"),
            ("@odata.type", "#ServiceRoot.v1_2_0.ServiceRoot"),
            ("Id", "RootService"),
            ("Name", "Root Service"),
            ("RedfishVersion", None),
            ("UUID", None)
        ]
        TestSupport.test_root_tags(self, link.jsonData, expected)

        expected = [
            ("Systems", "@odata.id", "/redfish/v1/ComputerSystem"),
            ("Chassis", "@odata.id", "/redfish/v1/Chassis"),
            ("StorageServices", "@odata.id", "/redfish/v1/StorageServices"),
            ("Managers", "@odata.id", "/redfish/v1/Managers"),
            ("Tasks", "@odata.id", "/redfish/v1/TaskService"),
            ("SessionService", "@odata.id", "/redfish/v1/SessionService"),
        ]
        TestSupport.test_nested_tags(self, link.jsonData, expected)
        
    def test_links(self):
        url = self.versionUrl
        link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', False, None)
        TestSupport.test_link_status(self, link, url)

        RedfishCommand.execute(self.redfishConfig, 'create session')

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
        for url in odataIds: 
            link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', True, None)
            self.assertTrue(link.valid, 'Link valid for URL ({})'.format(url))

