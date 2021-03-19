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
# show_tasks.py 
#
# ******************************************************************************************
#
# @command show tasks
#
# @synopsis Display all tasks and status for each task
#
# @description-start
#
# 'show tasks' displays details about all available tasks
#
# Example:
# 
# (redfish) show tasks
# 
#                          Id                           Name         State        Status
# --------------------------------------------------------------------------------------
#         firmware-update-task     Task firmware-update-task           New            OK
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# TaskInformation
################################################################################
class TaskInformation:
    """Task Information"""

    Id: ''
    Name = ''
    TaskState = ''
    TaskStatus = ''

    # JSON Response Data:
    # {
    #     "@odata.context": "/redfish/v1/$metadata#Task.Task",
    #     "@odata.id": "/redfish/v1/TaskService/Tasks/firmware-update-task",
    #     "@odata.type": "#Task.v1_5_1.Task",
    #     "Id": "firmware-update-task",
    #     "Name": "Task firmware-update-task",
    #     "TaskState": "New",
    #     "TaskStatus": "OK"
    # }

    def init_from_url(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Task init from URL {}'.format(url))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET')

        if (link.valid and link.jsonData is not None):
            if ('Id' in link.jsonData and 'Name' in link.jsonData):
                Trace.log(TraceLevel.DEBUG, '   ++ Task: ({}, {})'.format(link.jsonData['Id'], link.jsonData['Name']))

            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']

            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            if ('TaskState' in link.jsonData):
                self.TaskState = link.jsonData['TaskState']

            if ('TaskStatus' in link.jsonData):
                self.TaskStatus = link.jsonData['TaskStatus']


################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show tasks"""
    name = 'show tasks'
    link = None
    tasks = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.tasks = []
        return (RedfishSystem.get_uri(redfishConfig, 'Tasks') + 'Tasks')

    @classmethod
    def process_json(self, redfishConfig, url):
        
        # GET Volumes
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET')
        
        # Retrieve a listing of all volumes for this system
        if (self.link.valid and self.link.jsonData is not None):

            totalTasks = 0 
            createdTasks = 0
            tasksUrls = []
            
            # Create a list of all the volume URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalTasks = value
                    Trace.log(TraceLevel.VERBOSE, '... GET tasks total ({})'.format(totalTasks))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.VERBOSE, '... Members value ({})'.format(value))
                    if (value != None):
                        for taskLink in value:
                            Trace.log(TraceLevel.VERBOSE, '... ADD task url ({})'.format(taskLink['@odata.id']))
                            tasksUrls.append(taskLink['@odata.id'])
                            createdTasks += 1
            
            # Create Volume object based on each drive URL
            if (createdTasks > 0 and createdTasks == totalTasks):
                for i in range(len(tasksUrls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET task data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(tasksUrls), tasksUrls[i]))
                    task = TaskInformation()
                    task.init_from_url(redfishConfig, tasksUrls[i])
                    self.tasks.append(task)
            elif (createdTasks > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Task information mismatch: Members@odata.count ({}), Memebers {}'.format(totalTasks, createdTasks))


    @classmethod
    def display_results(self, redfishConfig):

        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))
        else:

            # Id: ''
            # Name = ''
            # TaskState = ''
            # TaskStatus = ''

            data_format = '{id: >28}  {name: >28}  {state: >12}  {status: >12}'
            print(data_format.format(id='Id', name='Name', state='State', status='Status'))
            print('-'*(88))

            for i in range(len(self.tasks)):
                print(data_format.format(
                    id=self.tasks[i].Id,
                    name=self.tasks[i].Name,
                    state=self.tasks[i].TaskState,
                    status=self.tasks[i].TaskStatus))

            print('')
