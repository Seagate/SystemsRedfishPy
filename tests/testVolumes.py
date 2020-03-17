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
# testVolumes.py - Unit test cases for Redfish/Swordfish Volume capabilities. 
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
# TestSupport
################################################################################

class TestVolumes(unittest.TestCase):

    redfishConfig = None
    systemInitialized = False

    @classmethod
    def setUpClass(cls):
        cls.redfishConfig = RedfishConfig(Label.decode(config.sessionConfig))
        RedfishCommand.execute(cls.redfishConfig, 'create session')
        cls.systemInitialized = RedfishSystem.initialize_system(cls.redfishConfig)

    def test_create_volume_1(self):
        Trace.log(TraceLevel.VERBOSE, '>> Run {}.{}:{}'.format(type(self).__name__, sys._getframe(  ).f_code.co_name, sys._getframe(  ).f_lineno))
        self.assertTrue(self.systemInitialized, 'System could not be initialized ({})'.format(self.systemInitialized))
        TestSupport.create_diskgroup_paged(self, self.redfishConfig, 'dgA01', 'A', 4, 'raid5')
        TestSupport.create_volume_paged(self, self.redfishConfig, 'TestVolume01', 'A', 10000000)
        TestSupport.delete_volume(self, self.redfishConfig, 'TestVolume01')
        TestSupport.delete_pool(self, self.redfishConfig, 'A')

    @classmethod
    def tearDownClass(cls):
        # Delete any current active session
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is not None:
            RedfishCommand.execute(cls.redfishConfig, f'delete sessions {sessionId}')
