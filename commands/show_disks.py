#
# @command show disks
#
# @synopsis Display all disk drives found in the system
#
# @description-start
#
# 'show disks' displays details about all disk drives, including
# id, serial number, manufacturer, revision, speed, size, and health.
#
# Example:
#
# (redfish) show disks
# 
#     Id            SerialNumber  Manufacturer  Revision   PartNumber  NegotiatedSpeedGbs    CapacityBytes  BlockSizeBytes  Health
#   ------------------------------------------------------------------------------------------------------------------------------
#    0.0    S0M1VV4Q0000B429BKCC            HP      HPD5  EG0600FCVBK                 6.0     600127266816             512      OK
#    0.1    WFJ00F3E0000J743S390       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.2    WFJ0EBDH0000E837J6ZD       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.3    WFJ0EBJE0000E837J6YU       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.4    WFJ02R3W0000E8141NWF       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.5    WFJ02QTG0000E81478QH       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.6    WFJ011960000E807FH1M       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.7    WFJ02HXW0000E8141NHS       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.8    WFJ002FG0000J732US78       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#    0.9    WFJ002DZ0000J732USC9       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.10    WFJ0EBBM0000E837J7DU       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.11    WFJ02QTN0000E81478WX       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.12    WFJ00F540000J743S2YB       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.13    WFJ0EBB20000E8380S97       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.14    WAF0PLKX0000E8399LZJ       SEAGATE      CT03  ST600MP0146                12.0     600127266816             512      OK
#   0.15    WAF0PKMN0000E8399MFG       SEAGATE      CT03  ST600MP0146                12.0     600127266816             512      OK
#   0.16    WFJ0ELES0000E837J6U1       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.17    WFJ0EBEY0000E837J70E       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.18    WFJ0EBJZ0000E837J6YN       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.19    WFJ0ELEM0000E837J6V6       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.20    WFJ002X70000J730L5XV       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.21    WFJ001XT0000J732UR0N       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.22    WFJ001410000J730L5VG       SEAGATE      N003  ST600MM0009                12.0     600127266816             512      OK
#   0.23    WFJ01GG40000E810BE2L       SEAGATE      C003  ST600MM0099                12.0     600127266816             512      OK
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# DiskInformation
################################################################################
class DiskInformation:
    """Disk Information"""

    Id = ''
    SerialNumber = ''
    Manufacturer = ''
    Revision = ''
    PartNumber = ''
    NegotiatedSpeedGbs = ''
    CapacityBytes = ''
    BlockSizeBytes = ''
    Health = ''
    
    def init_from_url(self, config, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Disk init from URL {}'.format(url))

        link = UrlAccess.process_request(config, UrlStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Disk: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['CapacityBytes'], link.jsonData['SerialNumber'], link.jsonData['Manufacturer'], link.jsonData['Protocol']))
    
            self.Id = link.jsonData['Id']
            self.SerialNumber = link.jsonData['SerialNumber']
            self.Manufacturer =link.jsonData['Manufacturer']
            self.Revision = link.jsonData['Revision']
            self.PartNumber = link.jsonData['PartNumber']
            self.NegotiatedSpeedGbs = link.jsonData['NegotiatedSpeedGbs']
            self.CapacityBytes = link.jsonData['CapacityBytes']
            self.BlockSizeBytes = link.jsonData['BlockSizeBytes']
            healthDict = link.jsonData['Status']
            self.Health = healthDict['Health']

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show disks"""
    name = 'show disks'
    link = None
    disks = []

    @classmethod
    def prepare_url(self, command):
        self.disks = []
        return ('/redfish/v1/StorageServices/S1/Drives')
        
    @classmethod
    def process_json(self, config, url):

        # GET DriveCollection
        Trace.log(TraceLevel.VERBOSE, '++ GET Drive collection from ({})'.format(url))
        self.link = UrlAccess.process_request(config, UrlStatus(url))
        
        # Retrieve a listing of all drives for this system
        if (self.link.valid):
            totalDrives = 0 
            createdDrives = 0
            driveUrls = []
            
            # Create a list of all the drive URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalDrives = value
                elif (key == 'Members'):
                    for driveLink in value:
                        driveUrls.append(driveLink['@odata.id'])
                        createdDrives += 1
            
            # Create Drive object based on each drive URL
            if (createdDrives > 0 and createdDrives == totalDrives):
                for i in range(len(driveUrls)):
                    Trace.log(TraceLevel.VERBOSE, '   -- GET Drive data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(driveUrls), driveUrls[i]))
                    disk = DiskInformation()
                    disk.init_from_url(config, driveUrls[i])
                    self.disks.append(disk)
            else:
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Drive information mismatch: Members@odata.count ({}), Memebers {}'.format(totalDrives, createdDrives))


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
            print('    Id            SerialNumber  Manufacturer  Revision   PartNumber  NegotiatedSpeedGbs    CapacityBytes  BlockSizeBytes  Health')
            print('  ------------------------------------------------------------------------------------------------------------------------------')
            #         0.23    WFJ01GG40000E810BE2L       SEAGATE      C003  ST600MM0099                12.0     600127266816             512      OK
            for i in range(len(self.disks)):
                print('{0: >6}  {1: >22}  {2: >12}  {3: >8}  {4: >10}  {5: >18}  {6: >15}  {7: >14}  {8: >6}'.format(
                    self.disks[i].Id,
                    self.disks[i].SerialNumber,
                    self.disks[i].Manufacturer,
                    self.disks[i].Revision,
                    self.disks[i].PartNumber,
                    self.disks[i].NegotiatedSpeedGbs,
                    self.disks[i].CapacityBytes,
                    self.disks[i].BlockSizeBytes,
                    self.disks[i].Health))
