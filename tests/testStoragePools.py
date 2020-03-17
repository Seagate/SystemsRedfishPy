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
# testStoragePools.py - Unit test cases for Redfish/Swordfish StoragePools capabilities. 
#
# ******************************************************************************************
#

from core.label import Label
from core.redfishCommand import RedfishCommand
from core.redfishConfig import RedfishConfig
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from tests.testSupport import TestSupport
import config
import unittest
import sys

################################################################################
# TestStoragePools
################################################################################

class TestStoragePools(unittest.TestCase):

    redfishConfig = None
    systemInitialized = False

    @classmethod
    def setUpClass(cls):
        cls.redfishConfig = RedfishConfig(Label.decode(config.sessionConfig))
        RedfishCommand.execute(cls.redfishConfig, 'create session')
        cls.systemInitialized = RedfishSystem.initialize_system(cls.redfishConfig)

    def test_create_diskgroup_paged_raid1(self):
        # Create a RAID1 disk group
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        self.assertTrue(self.systemInitialized, 'System could not be initialized ({})'.format(self.systemInitialized))
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA01', 'A', 2, 'raid1')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    def test_create_diskgroup_paged_raid5(self):
        # Create a RAID5 disk group
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        self.assertTrue(self.systemInitialized, 'System could not be initialized ({})'.format(self.systemInitialized))
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA02', 'A', 4, 'raid5')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    def test_create_diskgroup_paged_raid6(self):
        # Create a RAID6 disk group
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        self.assertTrue(self.systemInitialized, 'System could not be initialized ({})'.format(self.systemInitialized))
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA03', 'A', 6, 'raid6')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    @classmethod
    def tearDownClass(cls):
        # Delete any current active session
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is not None:
            RedfishCommand.execute(cls.redfishConfig, f'delete sessions {sessionId}')