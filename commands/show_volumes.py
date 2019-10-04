#
# @command show volumes
#
# @synopsis Display all configured volumes
#
# @description-start
#
# 'show volumes' displays details about all available volumes, including
# name, serial number, class, size, and health.
#
# Example:
# 
# (redfish) show volumes
# 
#             Name                      SerialNumber   CapacityBytes  Remaining %  Encrypted      State  Health  Pool
#  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#      TestVolume1  00c0ff51124600006358975d01000000      2000000000           99       true    Enabled      OK  /redfish/v1/StorageServices/S1/StoragePools/A
#      TestVolume2  00c0ff51124600007658975d01000000      2000000000           99       true    Enabled      OK  /redfish/v1/StorageServices/S1/StoragePools/A
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, LinkStatus

################################################################################
# VolumeInformation
################################################################################
class VolumeInformation:
    """Volume Information"""

    Name = ''
    SerialNumber = ''
    Manufacturer = ''
    CapacityBytes = ''
    RemainingCapacityPercent = ''
    Encrypted = ''
    State = ''
    Health = ''
    Pools = ''
    
    def init_from_url(self, config, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Volume init from URL {}'.format(url))

        link = UrlAccess.process_link(config, LinkStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Volume: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['CapacityBytes'], link.jsonData['RemainingCapacityPercent'], link.jsonData['Encrypted']))

            self.SerialNumber = link.jsonData['Id']
            self.Name = link.jsonData['Name']
            self.Manufacturer =link.jsonData['Manufacturer']
            self.CapacityBytes = link.jsonData['CapacityBytes']
            self.RemainingCapacityPercent = link.jsonData['RemainingCapacityPercent']
            if (link.jsonData['Encrypted']):
                self.Encrypted = 'true'
            else:
                self.Encrypted = 'false'
            
            healthDict = link.jsonData['Status']
            self.State = healthDict['State']
            self.Health = healthDict['Health']

            sourcesDict = link.jsonData['CapacitySources']
            poolsDict = sourcesDict['ProvidingPools']
            members = poolsDict['Members']
            self.Pools = members[0]['@odata.id']
            

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show volumes"""
    name = 'show volumes'
    link = None
    volumes = []

    @classmethod
    def prepare_url(self, command):
        self.volumes = []
        return ('/redfish/v1/StorageServices/S1/Volumes')

    @classmethod
    def process_json(self, config, url):
        
        # GET Volumes
        self.link = UrlAccess.process_link(config, LinkStatus(url))
        
        # Retrieve a listing of all volumes for this system
        if (self.link.valid):

            totalVolumes = 0 
            createdVolumes = 0
            volumeUrls = []
            
            # Create a list of all the volume URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalVolumes = value
                    Trace.log(TraceLevel.VERBOSE, '... GET volumes total ({})'.format(totalVolumes))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.VERBOSE, '... Members value ({})'.format(value))
                    if (value != None):
                        for volumeLink in value:
                            Trace.log(TraceLevel.VERBOSE, '... ADD volume url ({})'.format(volumeLink['@odata.id']))
                            volumeUrls.append(volumeLink['@odata.id'])
                            createdVolumes += 1
            
            # Create Volume object based on each drive URL
            if (createdVolumes > 0 and createdVolumes == totalVolumes):
                for i in range(len(volumeUrls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET volume data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(volumeUrls), volumeUrls[i]))
                    volume = VolumeInformation()
                    volume.init_from_url(config, volumeUrls[i])
                    self.volumes.append(volume)
            elif (createdVolumes > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Volume information mismatch: Members@odata.count ({}), Memebers {}'.format(totalVolumes, createdVolumes))


    @classmethod
    def display_results(self, config):
        # self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))
        else:
            print('')
            #                0                                 1               2            3          4          5       6  7
            #             Name                      SerialNumber   CapacityBytes  Remaining %  Encrypted      State  Health  Pool
            # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #      TestVolume1  00c0ff51124600006358975d01000000      2000000000           99       true    Enabled      OK  /redfish/v1/StorageServices/S1/StoragePools/A
            #      TestVolume2  00c0ff51124600007658975d01000000      2000000000           99       true    Enabled      OK  /redfish/v1/StorageServices/S1/StoragePools/A
            print('            Name                      SerialNumber   CapacityBytes  Remaining %  Encrypted      State  Health  Pool')
            print(' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            
            if (self.volumes != None):
                for i in range(len(self.volumes)):
                    print('{0: >16}  {1: >31}  {2: >14}  {3: >11}  {4: >9}  {5: >9}  {6: >6}  {7}'.format(
                        self.volumes[i].Name,
                        self.volumes[i].SerialNumber,
                        self.volumes[i].CapacityBytes,
                        self.volumes[i].RemainingCapacityPercent,
                        self.volumes[i].Encrypted,
                        self.volumes[i].State,
                        self.volumes[i].Health,
                        self.volumes[i].Pools))
