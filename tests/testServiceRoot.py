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
# testServiceRoot.py - Unit test cases for Redfish ServiceRoot capabilities. 
#
# ******************************************************************************************
#

from core.jsonExtract import JsonExtract
from core.redfishCommand import RedfishCommand
from core.redfishConfig import RedfishConfig
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus
from tests.testSupport import TestSupport
from core.label import Label
import config
import unittest
import sys

################################################################################
# TestServiceRoot
################################################################################

class TestServiceRoot(unittest.TestCase):

    redfishConfig = None

    @classmethod
    def setUpClass(cls):
        cls.root = '/redfish'
        cls.version = 'v1'
        cls.versionUrl = '/redfish/v1/'
        cls.redfishConfig = RedfishConfig(Label.decode(config.sessionConfig))

    def test_version(self):
        # Verify GET /redfish returns JSON data with /redfish/v1/
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        url = self.root
        link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', False, None)
        TestSupport.test_link_status(self, link, url)

        expected = [("v1", "/redfish/v1/")]
        TestSupport.test_root_tags(self, link.jsonData, expected)

    def test_serviceroot(self):
        # Verify GET /redfish/v1 returns expected JSON data 
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
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
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        url = self.versionUrl
        link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', False, None)
        TestSupport.test_link_status(self, link, url)

        RedfishCommand.execute(self.redfishConfig, 'create session')

        odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
        for url in odataIds: 
            link = UrlAccess.process_request(self.redfishConfig, UrlStatus(url), 'GET', True, None)
            self.assertTrue(link.valid, 'Link valid for URL ({})'.format(url))

        # Delete any current active session
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is not None:
            RedfishCommand.execute(self.redfishConfig, f'delete sessions {sessionId}')
