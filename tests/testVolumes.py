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
# testVolumes.py - Unit test cases for Redfish/Swordfish Volume capabilities. 
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
# TestSupport
################################################################################

class TestVolumes(unittest.TestCase):

    def setUp(self):
        self.redfishConfig = RedfishConfig(config.defaultConfigFile)
        RedfishCommand.execute(self.redfishConfig, 'create session')
        TestSystem.initialize_system(self, self.redfishConfig)

    def test_create_volume_1(self):
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA01', 'A', 4, 'raid5')
        TestSupport.create_volume_paged(self, self.redfishConfig, 'TestVolume01', 'A', 10000000)
        TestSupport.delete_volume(self, self.redfishConfig, 'TestVolume01')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')
