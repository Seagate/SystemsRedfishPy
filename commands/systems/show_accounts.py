#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# show_accounts.py 
#
# ******************************************************************************************
#
# @command show accounts
#
# @synopsis Display all user accounts
#
# @description-start
#
# 'show accounts' displays all user accounts and brief information about each account
#
# Example:
#
# (redfish) show accounts
#
#         UserName                                 Roles  Enabled   Locked             Types  Description
# ----------------------------------------------------------------------------------------------------------------
#           manage    diagnostic,manage,standard,monitor        1        0    ManagerConsole  User Account
#          user101               manage,standard,monitor        1        0    ManagerConsole  User Account
#          user200                               monitor        1        0    ManagerConsole  User Account
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from core.redfishSystem import RedfishSystem
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus

################################################################################
# PoolInformation
################################################################################
class AccountInformation:
    """Account Information"""

    AccountTypes = []
    Description = ''
    Enabled = ''
    Id = ''
    Locked = ''
    Name = ''
    RoleId = ''
    UserName = ''

    def init_from_url(self, redfishConfig, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Account init from URL {}'.format(url))

        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid and link.jsonData is not None):

            # AccountTypes
            if ('AccountTypes' in link.jsonData):
                try:
                    self.AccountTypes = ','.join(link.jsonData['AccountTypes'])
                except:
                    self.AccountTypes = 'Unknown'

            # Description
            if ('Description' in link.jsonData):
                self.Description = link.jsonData['Description']

            # Enabled
            if ('Enabled' in link.jsonData):
                self.Enabled = link.jsonData['Enabled']

            # Id
            if ('Id' in link.jsonData):
                self.Id = link.jsonData['Id']

            # Locked
            if ('Locked' in link.jsonData):
                self.Locked = link.jsonData['Locked']

            # Name
            if ('Name' in link.jsonData):
                self.Name = link.jsonData['Name']

            # RoleId
            if ('RoleId' in link.jsonData):
                self.RoleId = link.jsonData['RoleId']

            # UserName
            if ('UserName' in link.jsonData):
                self.UserName = link.jsonData['UserName']

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show accounts"""
    name = 'show accounts'
    accounts = []
    link = None

    @classmethod
    def prepare_url(self, redfishConfig, command):
        self.groups = []
        return (RedfishSystem.get_uri(redfishConfig, 'AccountService'))

    @classmethod
    def process_json(self, redfishConfig, url):

        if (not url):
            return

        # GET Account Service information
        self.accounts = []
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a link to Accounts
        accountsurl = ''
        if (self.link.valid and self.link.jsonData != None):
            if ('Accounts' in self.link.jsonData):
                accountsdata = self.link.jsonData['Accounts']
                if ('@odata.id' in accountsdata):
                    accountsurl = accountsdata['@odata.id']

        if accountsurl != '':
            self.link = UrlAccess.process_request(redfishConfig, UrlStatus(accountsurl))

            # Retrieve a listing of all accounts for this system
            if (self.link.valid and self.link.jsonData != None):
                total = 0 
                created = 0
                urls = []
            
                # Create a list of all the account URLs
                for (key, value) in self.link.jsonData.items():
                    if (key == 'Members@odata.count'):
                        total = value
                        Trace.log(TraceLevel.VERBOSE, '... GET total ({})'.format(total))
                    elif (key == 'Members'):
                        Trace.log(TraceLevel.TRACE, '... Members value ({})'.format(value))
                        if (value != None):
                            for groupLink in value:
                                url = groupLink['@odata.id']
                                Trace.log(TraceLevel.VERBOSE, '... ADD accounts url ({})'.format(url))
                                urls.append(url)
                                created += 1

                # Create object based on each drive URL
                if (created > 0 and created == total):
                    for i in range(len(urls)):
                        Trace.log(TraceLevel.VERBOSE, '... GET Account data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                        account = AccountInformation()
                        account.init_from_url(redfishConfig, urls[i])
                        self.accounts.append(account)
                elif (created > 0):
                    Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Members {}'.format(total, created))

    @classmethod
    def display_results(self, redfishConfig):

        if (self.link == None):
            return 

        if (self.link.valid == False):
            self.link.print_status()

        else:
            data_format = '{username: >16}  {roles: >36}  {enabled: >7}  {locked: >7}  {types: >16}  {description}'
            width=16+2+36+2+7+2+7+2+16+2+20
            print('')
            print(data_format.format(username='UserName', roles='Roles', enabled='Enabled', locked='Locked', types='Types', description='Description'))
            print('-'*(width))

            for i in range(len(self.accounts)):
                print(data_format.format(
                    username=self.accounts[i].UserName,
                    roles=self.accounts[i].RoleId,
                    enabled=self.accounts[i].Enabled,
                    locked=self.accounts[i].Locked,
                    types=self.accounts[i].AccountTypes,
                    description=self.accounts[i].Description))
