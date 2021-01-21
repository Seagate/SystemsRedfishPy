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
# http_patch.py 
#
# ******************************************************************************************
#
# @command http patch <url> <json | file>
#
# @synopsis Execute an HTTP PATCH operation on a URL passing JSON data as provided
#
# @description-start
#
# This command will perform an HTTP PATCH operation on the specified URL. Either the JSON
# data provided as a parameter will be included with the HTTP operation, or the JSON data 
# provided in a file. The third parameter is the '<url>'. If the fourth parameter contains
# a left curly bracket ('{') this function will expect well-formed JSON data; otherwise,
# this function will attempt to open and read the contents of a file. 
#
# Example:
#
# Example 1:
# (redfish) http patch /redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000 json\patch_volume.json

# Example 2:
# (redfish) http patch /redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000 { "Name": "NewAVolume01" }
#
# Example output:
# 
# [] URL          : /redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000
# [] Status       : 200
# [] Reason       : OK
# 
# [] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1754'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]
# 
# [] HTTP Data    : {'@odata.context': '/redfish/v1/$metadata#Volume.Volume', '@odata.id': '/redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000', '@odata.type': '#Volume.v1_4_0.Volume', 'AccessCapabilities': ['Read', 'Write'], 'BlockSizeBytes': 512, 'Capacity': {'Data': {'AllocatedBytes': 0, 'ConsumedBytes': 0}}, 'CapacityBytes': 99996401664, 'CapacitySources': [{'@odata.id': '/redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000#/CapacitySources/0', '@odata.type': '#Capacity.v1_1_2.CapacitySource', 'Id': '00c0ff5112490000d08ccf5e01000000', 'Name': 'NewAVolumeYYY', 'ProvidingPools': {'@odata.context': '/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection', '@odata.id': '/redfish/v1/StorageServices/S1/StoragePools', '@odata.type': '#StoragePoolCollection.StoragePoolCollection', 'Members': [{'@odata.id': '/redfish/v1/StorageServices/S1/StoragePools/A'}], 'Members@odata.count': 1, 'Name': 'StoragePools'}}], 'Encrypted': False, 'EncryptionTypes': ['NativeDriveEncryption'], 'IOStatistics': {'ReadHitIORequests': 0, 'ReadIOKiBytes': 0, 'WriteHitIORequests': 0, 'WriteIOKiBytes': 0}, 'Id': '00c0ff5112490000d08ccf5e01000000', 'Name': 'NewAVolumeYYY', 'RemainingCapacityPercent': 100, 'Status': {'Health': 'OK', 'State': 'Enabled'}}
# 
# [] JSON Data    : {
#     "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
#     "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000",
#     "@odata.type": "#Volume.v1_4_0.Volume",
#     "Id": "00c0ff5112490000d08ccf5e01000000",
#     (...snipped...)
#     "Name": "NewAVolume01",
#     "RemainingCapacityPercent": 100,
#     "Status": {
#         "Health": "OK",
#         "State": "Enabled"
#     }
# }
# 
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.argExtract import ArgExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - http patch """
    name = 'http patch'
    link = None
    command = ''
    startingurl = ''

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        _, self.startingurl = ArgExtract.get_value(command, 2)
        Trace.log(TraceLevel.VERBOSE, 'http patch: url ({})'.format(self.startingurl))
        return (self.startingurl)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, '[] http patch: url ({})'.format(url))
        _, jsonData = ArgExtract.get_json(self.command, 3)
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'PATCH', True, json.dumps(jsonData, indent=4))
        self.link = link

    @classmethod
    def display_results(self, redfishConfig):
        Trace.log(TraceLevel.INFO, '')
        Trace.log(TraceLevel.INFO, '[] URL          : {}'.format(self.startingurl))
        Trace.log(TraceLevel.INFO, '[] Status       : {}'.format(self.link.urlStatus))
        Trace.log(TraceLevel.INFO, '[] Reason       : {}'.format(self.link.urlReason))

        if (self.link != None and self.link.response != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] HTTP Headers : {}'.format(self.link.response.getheaders()))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.VERBOSE, '')
            Trace.log(TraceLevel.VERBOSE, '[] HTTP Data    : {}'.format(self.link.jsonData))

        if (self.link != None and self.link.jsonData != None):
            Trace.log(TraceLevel.INFO, '')
            Trace.log(TraceLevel.INFO, '[] JSON Data    : {}'.format(json.dumps(self.link.jsonData, indent=4)))
