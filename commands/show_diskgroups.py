#
# @command show diskgroups
#
# @synopsis Display all allocated disk groups and disk group infromation
#
# @description-start
#
# 'show diskgroups' displays details about all available disk groups.
#
# Example:
#
# (redfish) show diskgroups
# 
#      Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes  ConsumedBytes  Health  ClasOfService
#  ---------------------------------------------------------------------------------------------------------------------
#     dgA01  00c0ff5112460000f55a925d00000000        512         0      1283457024     1283457024      OK          RAID1
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# PoolInformation
################################################################################
class StorageGroupInformation:
    """Storage Group Information"""

    SerialNumber = ''
    Name = ''
    Manufacturer = ''
    MaxBlockSizeBytes = 0
    AllocatedVolumes = []
    RemainingCapacityPercent = 0
    AllocatedBytes = ''
    ConsumedBytes = ''
    State = ''
    Health = ''
    ClassofService = ''
    
    def init_from_url(self, config, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Storage Group init from URL {}'.format(url))

        link = UrlAccess.process_request(config, UrlStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Storage Group: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['Manufacturer'], link.jsonData['MaxBlockSizeBytes'], link.jsonData['RemainingCapacityPercent']))

            self.SerialNumber = link.jsonData['Id']
            self.Name = link.jsonData['Name']
            self.Manufacturer = link.jsonData['Manufacturer']
            self.MaxBlockSizeBytes = link.jsonData['MaxBlockSizeBytes']

            try:
                self.AllocatedVolumes = []
                avs = link.jsonData['AllocatedVolumes']
                for i in range(len(avs)):
                    # Example: '/redfish/v1/StorageServices/S1/StoragePools/00c0ff5112460000f55a925d00000000/Volumes/00c0ff5112460000f75a925d02000000'
                    words = avs[i].split('/')
                    if (len(words) >= 7):
                        Trace.log(TraceLevel.TRACE, '   ++ Adding allocated volume ({}) from ({})'.format(words[7], avs[i]))
                        self.AllocatedVolumes.append(words[7])
            except:
                self.AllocatedVolumes = []
                pass

            self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']

            capacity = link.jsonData['Capacity']
            data = capacity['Data']
            self.AllocatedBytes = data['AllocatedBytes']
            self.ConsumedBytes = data['ConsumedBytes']
            
            status = link.jsonData['Status']
            self.State = status['State']
            self.Health = status['Health']
            
            dcos = link.jsonData['DefaultClassOfService']
            self.ClassofService = dcos['@odata.id'].replace('/redfish/v1/StorageServices/S1/ClassesOfService/', '')
            

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show diskgroups"""
    name = 'show diskgroups'
    pools = []
    link = None

    @classmethod
    def prepare_url(self, command):
        self.groups = []
        return ('/redfish/v1/StorageServices/S1/StoragePools')

    @classmethod
    def process_json(self, config, url):
        
        # GET Pools
        self.link = UrlAccess.process_request(config, UrlStatus(url))
        
        # Retrieve a listing of all disk groups for this system
        # Note: Version 1.1 returns storage groups and pools, only take StoragePools that start with 00c0ff

        if (self.link.valid):

            totalGroups = 0 
            createdGroups = 0
            groupUrls = []
            
            # Create a list of all the pool URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalGroups = value
                    Trace.log(TraceLevel.VERBOSE, '... GET groups total ({})'.format(totalGroups))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '... Members value ({})'.format(value))
                    if (value != None):
                        for groupLink in value:
                            url = groupLink['@odata.id']
                            words = url.split('/')
                            idnumber = words[len(words)-1]
                            if (idnumber.startswith('00c0ff')):
                                Trace.log(TraceLevel.VERBOSE, '... ADD storage group url ({})'.format(url))
                                groupUrls.append(url)
                                createdGroups += 1
                            else:
                                Trace.log(TraceLevel.TRACE, '... SKIP storage group url ({})'.format(url))
                                totalGroups -= 1

            # Create Pool object based on each drive URL
            if (createdGroups > 0 and createdGroups == totalGroups):
                for i in range(len(groupUrls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET Storage Group data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(groupUrls), groupUrls[i]))
                    group = StorageGroupInformation()
                    group.init_from_url(config, groupUrls[i])
                    self.groups.append(group)
            elif (createdGroups > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Storage Group information mismatch: Members@odata.count ({}), Memebers {}'.format(totalGroups, createdGroups))


    @classmethod
    def display_results(self, config):
        #self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            print('         Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes  ConsumedBytes  Health  ClasOfService')
            print(' -------------------------------------------------------------------------------------------------------------------------')
    
            if (self.groups != None):
                for i in range(len(self.groups)):
                    print(' {0: >12}  {1: >32}  {2: >9}  {3: >8}  {4: >14}  {5: >13}  {6: >6}  {7: >13}'.format(
                        self.groups[i].Name,
                        self.groups[i].SerialNumber,
                        self.groups[i].MaxBlockSizeBytes,
                        self.groups[i].RemainingCapacityPercent,
                        self.groups[i].AllocatedBytes,
                        self.groups[i].ConsumedBytes,
                        self.groups[i].Health,
                        self.groups[i].ClassofService
                        ))
                    
                    for volume in range(len(self.groups[i].AllocatedVolumes)):
                        print(' -- Allocated Volume: {}'.format(self.groups.AllocatedVolumes[volume]))
