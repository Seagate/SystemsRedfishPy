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
# testStoragePools.py - Unit test cases for Redfish/Swordfish StoragePools capabilities. 
#
# ******************************************************************************************
#

import config
import unittest

from core.redfishCommand import RedfishCommand
from core.redfishConfig import RedfishConfig
from tests.testSupport import TestSupport
from tests.testSystem import TestSystem

################################################################################
# TestStoragePools
################################################################################

class TestStoragePools(unittest.TestCase):

    def setUp(self):
        self.redfishConfig = RedfishConfig(config.defaultConfigFile)
        RedfishCommand.execute(self.redfishConfig, 'create session')
        TestSystem.initialize_system(self, self.redfishConfig)

    def test_create_diskgroup_paged_raid1(self):
        # Create a RAID1 disk group
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA01', 'A', 2, 'raid1')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    def test_create_diskgroup_paged_raid5(self):
        # Create a RAID5 disk group
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA02', 'A', 4, 'raid5')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    def test_create_diskgroup_paged_raid6(self):
        # Create a RAID6 disk group
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA03', 'A', 6, 'raid6')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')
