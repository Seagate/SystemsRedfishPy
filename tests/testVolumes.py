# *************************************************************************************
#
# testVolumes - Redfish Volumes test cases
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


class TestVolumes(unittest.TestCase):

    def setUp(self):
        self.redfishConfig = RedfishConfig(config.defaultConfigFile)
        RedfishCommand.execute(self.redfishConfig, 'create session')
        TestSystem.initialize_system(self, self.redfishConfig)

    def test_create_volume_1(self):
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA02', 'A', 4, 'raid5')
        TestSupport.create_volume_paged(self, self.redfishConfig, 'TestVolume01', 'A', 10000000)
        TestSupport.delete_volume(self, self.redfishConfig, 'TestVolume01')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')
