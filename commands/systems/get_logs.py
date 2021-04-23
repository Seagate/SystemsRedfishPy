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
# get_logs.py 
#
# ******************************************************************************************
#
# @command get logs
#
# @synopsis Retrieve controller or disk drive logs and store in logs.zip.
#
# @description-start
#
# 'get logs component=[controller|drive] logtype=[disk|diskfarm|etc] drivenumber=[enclosure.slot]
#
# Note:
#     This command is only valid for Redfish Service Version 2.
#
# Parameters:
#     'component' - Required
#         options: controller, drive
#
#     'logtype' - Required for 'drive', not used for 'controller'
#         options: disk, diskfarm, diskibt, disksm2, diskidd, diskfarmlct, diskfarmfield,
#                 diskfarmts1, diskfarmts2, diskfarmsf1, diskfarmsf2, diskfarmsf3,
#                 diskfarmsf4, diskfarmfactory
#
#     'drivenumber' - Required for 'drive', not used for 'controller'
#         options: enclosure.slot, for example 0.24
#
#     Note: Not all drive log types are available for all drives. If a drive log type is
#           supplied that is not supported by the drive, the command will fail.
#
# Examples:
#     get logs component=controller
#     get logs component=drive logtype=diskfarm drivenumber=0.1
#
# @description-end
#

import json
from commands.commandHandlerBase import CommandHandlerBase
from core.jsonBuilder import JsonBuilder, JsonType
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus
import time
import zipfile

# Display the results of a get logs call
def display_log_results(link, log_filename, display_contents):
    error_filename = 'ErrorMessage.txt'
    error_exists = False

    Trace.log(TraceLevel.INFO, "   -- {0: <14}: {1}".format('Status', link.urlStatus))
    Trace.log(TraceLevel.INFO, "   -- {0: <14}: {1}".format('Reason', link.urlReason))

    if link.urlStatus == 200 and link.urlData != None:
        outF = open(log_filename, 'wb')
        outF.write(link.urlData)
        outF.close()
        Trace.log(TraceLevel.INFO, "   -- Download complete to '{}'".format(log_filename))

        if display_contents:
            Trace.log(TraceLevel.INFO, "")
            Trace.log(TraceLevel.INFO, "   -- Contents of zip file '{}':".format(log_filename))

        # Display contents of zip file and check for error file
        zip_file = zipfile.ZipFile(log_filename, 'r')
        for name in zip_file.namelist():
            if name == error_filename:
                error_exists = True
            if display_contents:
                Trace.log(TraceLevel.INFO, "      ** {}".format(name))

        # Extract and display error file if it exists
        if error_exists:
            zip_file.extractall()
            Trace.log(TraceLevel.INFO, "")
            Trace.log(TraceLevel.INFO, "   -- Contents of file '{}':".format(error_filename))
            with open(error_filename) as f:
                lines = f.read().splitlines()
                for line in lines:
                    if len(line.strip()) > 0:
                        Trace.log(TraceLevel.INFO, "      || {}".format(line))
        zip_file.close()
    else:
        Trace.log(TraceLevel.INFO, "ERROR: get logs POST returned no URL data")


# The get logs call returns a task id which needs to be monitored until
# until the TaskState is 'Completed', once completed, execute another POST
# to retrieve the log file.
def process_task_status(redfishConfig, link, log_filename):

    if link.urlStatus != 201:
        # First POST failed, don't proceed further
        Trace.log(TraceLevel.INFO, "   -- {0: <14}: {1}".format('Status', link.urlStatus))
        Trace.log(TraceLevel.INFO, "   -- {0: <14}: {1}".format('Reason', link.urlReason))
        return

    taskid = ''
    if (link.valid and link.jsonData is not None and 'Id' in link.jsonData):
        taskid = link.jsonData['Id']

    Trace.log(TraceLevel.INFO, "")
    Trace.log(TraceLevel.INFO, "   >> Monitor task '{}' for Completed".format(taskid))

    # Poll the task status until it is Completed
    completed = 0
    delay = 30
    counter = 1
    uri = RedfishSystem.get_uri(redfishConfig, 'Tasks') + 'Tasks/' + taskid
    while completed == 0:
        link2 = UrlAccess.process_request(redfishConfig, UrlStatus(uri), 'GET', True, None)
        if link2.urlStatus == 200:
            if (link2.valid and link2.jsonData is not None and 'TaskState' in link2.jsonData):
                if link2.jsonData['TaskState'] == 'Completed':
                    Trace.log(TraceLevel.INFO, "      == TaskState: '{}'".format(link2.jsonData['TaskState']))
                    completed = 1
                else:
                    Trace.log(TraceLevel.INFO, "      == TaskState: '{}' (sleep {})".format(link2.jsonData['TaskState'], delay))
                    time.sleep(delay)
                    # Reduce the sleep delay after 2m 30s
                    if counter == 5:
                        delay = int(delay / 10)
                    counter += 1
            else:
                Trace.log(TraceLevel.INFO, "      == ERROR: Failed to obtain task status")
                completed = 2
        else:
            Trace.log(TraceLevel.INFO, "      == {0: <14}: {1}".format('Status', link2.urlStatus))
            Trace.log(TraceLevel.INFO, "      == {0: <14}: {1}".format('Reason', link2.urlReason))
            completed = 3

    # Retrieve and store the log file
    if completed == 1:
        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)
        JsonBuilder.addElement('main', JsonType.STRING, 'DiagnosticDataType', 'OEM')
        JsonBuilder.addElement('main', JsonType.STRING, 'OEMDiagnosticDataType', 'DownloadLogData')

        Trace.log(TraceLevel.INFO, "")
        Trace.log(TraceLevel.INFO, "++ POST get logs (controller, DownloadLogData)")
        link3 = UrlAccess.process_request(redfishConfig, UrlStatus(link.url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4), decode=False)
        display_log_results(link3, log_filename, display_contents=False)


################################################################################
# POST Request Body Examples
################################################################################
#
# Example JSON POST request data for CollectControllerLog
# {
#     "DiagnosticDataType": "OEM",
#     "OEMDiagnosticDataType": "CollectControllerLog"
# }
#
# Example JSON POST request data for GetDriveLog
# {
#     "DiagnosticDataType": "OEM",
#     "OEMDiagnosticDataType": "GetDriveLog"
#     "DriveLogType": "diskfarm"
#     "DriveNumber": "0.1"
# }
#

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - get logs"""
    name = "get logs"
    command = ""

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.command = command
        # Example: /redfish/v1/Systems/00C0FF472054/LogServices/controller_a/Actions/LogService.CollectDiagnosticData
        uri = RedfishSystem.get_uri(redfishConfig, 'SystemsLogServices') + 'Actions/LogService.CollectDiagnosticData'
        return (uri)

    @classmethod
    def process_json(self, redfishConfig, url):
        Trace.log(TraceLevel.INFO, "")
        Trace.log(TraceLevel.INFO, "++ get logs: {}...".format(url))

        if (redfishConfig.get_version() < 2):
            Trace.log(TraceLevel.INFO, "ERROR: get logs is only supported in service version 2: (ServiceVersion={})".format(redfishConfig.get_version()))
            return

        jsonType, component = JsonBuilder.getValue('component', self.command)
        if (jsonType is JsonType.NONE):
            Trace.log(TraceLevel.INFO, "ERROR: get logs requires that you provide a 'component' (controller, drive)")
            return

        # From the command, build up the required JSON data

        logtype = ''
        drivenumber = ''

        JsonBuilder.startNew()
        JsonBuilder.newElement('main', JsonType.DICT)

        if component == 'controller':
            JsonBuilder.addElement('main', JsonType.STRING, 'DiagnosticDataType', 'OEM')
            JsonBuilder.addElement('main', JsonType.STRING, 'OEMDiagnosticDataType', 'CollectControllerLog')

        elif component == 'drive':
            JsonBuilder.addElement('main', JsonType.STRING, 'DiagnosticDataType', 'OEM')
            JsonBuilder.addElement('main', JsonType.STRING, 'OEMDiagnosticDataType', 'GetDriveLog')
            # DriveLogType
            jsonType, logtype = JsonBuilder.getValue('logtype', self.command)
            if (jsonType is not JsonType.NONE):
                JsonBuilder.addElement('main', JsonType.STRING, 'DriveLogType', logtype)
            # DriveNumber
            jsonType, drivenumber = JsonBuilder.getValue('drivenumber', self.command)
            if (jsonType is not JsonType.NONE):
                JsonBuilder.addElement('main', JsonType.STRING, 'DriveNumber', drivenumber)

        else:
            Trace.log(TraceLevel.INFO, "ERROR: get logs unsupported 'component' type ({})".format(component))
            return

        # Execute the required HTTP operations to perform the log pull

        log_filename = 'logfile.zip'

        if component == 'controller':
            Trace.log(TraceLevel.INFO, "++ POST get logs (controller, CollectControllerLog)")
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4), decode=False)
            process_task_status(redfishConfig, link, log_filename)

        else:
            Trace.log(TraceLevel.INFO, "++ POST get logs (drive, {}, {})".format(logtype, drivenumber))
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'POST', True, json.dumps(JsonBuilder.getElement('main'), indent=4), decode=False)
            display_log_results(link, log_filename, display_contents=True)

    @classmethod
    def display_results(self, redfishConfig):
        # Nothing to do in this case
        Trace.log(TraceLevel.INFO, " ")
