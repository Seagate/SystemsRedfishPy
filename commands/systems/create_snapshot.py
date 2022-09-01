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
# create_snapshot.py 
#
# ******************************************************************************************
#
# @command create snapshot
#
# @synopsis Create a volume snapshot
#
# @description-start
#
# 'create snapshot source=[volumename] name=[snapshotname]
#
# Parameters:
#     The 'source' parameter is required and specifies the volume that will be replicated.
#     The 'name' parameter is required and specifies the name of the new snapshot volume.
#
# Example:
#     create snapshot source=TestVol01 name=snapshot1
#     create snapshot source=TestVol02 name=snapshot2
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# Volume.CreateReplicaTarget
################################################################################

# Example of desired JSON data to POST:
# {
#     "TargetStoragePool": "source volume name",
#     "VolumeName": "snapshot name",
#     "ReplicaType": "Snapshot",
#     "ReplicaUpdateMode": "Asynchronous"
# }

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - create snapshot"""
    name = 'create snapshot'
    command = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        return (RedfishSystem.get_uri(redfishConfig, 'Volumes'))

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '++ Create Snapshot: ({})...'.format(self.command))

        # From the command, build up the required JSON data

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        # TargetStoragePool
        jsonType, source = JsonBuilder.getValue('source', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'TargetStoragePool', source)
        else:
            Trace.log(TraceLevel.ERROR, "'source' is required")
            return

        # VolumeName
        jsonType, name = JsonBuilder.getValue('name', self.command)
        if (jsonType is not JsonType.NONE):
            JsonBuilder.addElement('main', JsonType.STRING, 'VolumeName', name)
        else:
            Trace.log(TraceLevel.ERROR, "'name' is required")
            return

        # ReplicaType, ReplicaUpdateMode
        JsonBuilder.addElement('main', JsonType.STRING, 'ReplicaType', "Snapshot")
        JsonBuilder.addElement('main', JsonType.STRING, 'ReplicaUpdateMode', "Asynchronous")

        fullurl = url + source + '/Actions/Volume.CreateReplicaTarget'
        Trace.log(TraceLevel.VERBOSE, '++ fullurl {}'.format(fullurl))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(fullurl), 'POST', True, JsonBuilder.getElement('main'))

        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, '   -- {0: <14}: {1}'.format('Reason', link.urlReason))

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        pass
