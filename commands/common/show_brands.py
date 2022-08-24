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
# show_brands.py 
#
# ******************************************************************************************
#
# @command show brands
#
# @synopsis Display all available command brands
#
# @description-start
#
# 'show brands' displays a list of all available brand commands, use with the !brand setting.
#
# Example:
#
# (redfish) show brands
# 
#            Brand                  Location     Count
# ----------------------------------------------------
#          systems          commands/systems        36
#           common           commands/common        22
#          example          commands/example         1
#             obmc             commands/obmc         2
# 
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
import os
from core.display import *

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    name = 'show brands'
    link = None
    items = []

    @classmethod
    def prepare_url(self, redfishConfig, command):
        return ('commands')

    @classmethod
    def process_json(self, redfishConfig, url):

        Trace.log(TraceLevel.VERBOSE, '++ show all brands ({}) folder'.format(url))

        data_format = '{brand: >16}  {location: >24}  {count: >8}'
        width=max_width(data_format)
        print('')
        print(data_format.format(brand='Brand', location='Location', count='Count'))
        print('-'*width)

        rootdir = 'commands'
        for folder in os.listdir(rootdir):
            d = os.path.join(rootdir, folder)
            Trace.log(TraceLevel.TRACE, '++ check item ({})'.format(d))
            if os.path.isdir(d) and folder != '__pycache__':
                count = 0
                Trace.log(TraceLevel.TRACE, '>> count files in directory ({})'.format(d))
                for file in os.listdir(d):
                    if os.path.isfile(os.path.join(d, file)) and file != '__init__.py':
                        count += 1
                if os.path.isdir(d):
                    print(data_format.format(
                        brand=folder,
                        location=d,
                        count=count))

    @classmethod
    def display_results(self, redfishConfig):
        return None
