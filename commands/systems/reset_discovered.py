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
# reset_discovered.py 
#
# ******************************************************************************************
#
# @command reset discovered
#
# @synopsis Clear and rediscover URLs presented by the Redfish Service
#
# @description-start
#
# 'reset discovered' Clear all discovered URLs and then rescan URLs presented by the service
#
# Example:
#
# (redfish) reset discovered
# -- Reseting discovered URLs...
#    -- Discovered: Root               >> /redfish/v1
#    -- Discovered: Chassis            >> /redfish/v1/Chassis/
#    -- Discovered: CompositionService >> /redfish/v1/CompositionService/
#    -- Discovered: Fabrics            >> /redfish/v1/Fabrics/
#    -- Discovered: Managers           >> /redfish/v1/Managers/
#    -- Discovered: SessionService     >> /redfish/v1/SessionService/
#    -- Discovered: Systems            >> /redfish/v1/Systems/
#    -- Discovered: Tasks              >> /redfish/v1/TaskService/
#    -- Discovered: UpdateService      >> /redfish/v1/UpdateService/
#    -- Discovered: Sessions           >> /redfish/v1/SessionService/Sessions/
#    -- Discovered: metadata           >> /redfish/v1/$metadata/
#    -- Discovered: odata              >> /redfish/v1/odata/#
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - reset discovered"""
    name = 'reset discovered'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        return None

    @classmethod
    def process_json(self, redfishConfig, url):
        RedfishSystem.reset_discovered(redfishConfig)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do
        print('')
