#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# load_config.py 
#
# ******************************************************************************************
#
# @command load config
#
# @synopsis Load a new configuration file and reset discovered items.
#
# @description-start
#
# 'load config <filename>' Read and use configuration settings from a new file.
#
# Example:
#
# (redfish) load config myconfig.cfg
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
from core.label import Label
from core.redfishCommand import RedfishCommand
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
import config

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - load config"""
    name = 'load config'

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.commandFull = command
        filename = command.strip().replace('load config ', '')
        Trace.log(TraceLevel.DEBUG, '-- load settings from ({})'.format(filename))
        return (filename)

    @classmethod
    def process_json(self, redfishConfig, url):
        sessionId = Label.decode(config.sessionIdVariable)
        if sessionId is not None:
            RedfishCommand.execute(redfishConfig, 'delete sessions ' + sessionId)
        RedfishSystem.reset_discovered(redfishConfig, False)
        redfishConfig.load_config(url)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do
        print('')
