# *************************************************************************************
#
# testStoragePools - Redfish StoragePools test cases
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
import unittest

from redfishCommand import RedfishCommand
from redfishConfig import RedfishConfig
from tests.testSupport import TestSupport
from tests.testSystem import TestSystem


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
        # Create a RAID1 disk group
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA02', 'A', 4, 'raid5')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    def test_create_diskgroup_paged_raid6(self):
        # Create a RAID1 disk group
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA03', 'A', 6, 'raid6')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')
