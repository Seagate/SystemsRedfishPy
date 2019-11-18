#
# @command show fans
#
# @synopsis Display all fan readings from the system.
#
# @description-start
#
# 'show fans' displays details about all fan readings.
#
# Example:
#
# (redfish) show fans
# 
#     SensorName       Reading    Health  Enclosure
#   -----------------------------------------------
#          Fan 0      7440 RPM        OK          0
#          Fan 1      7380 RPM        OK          0
#          Fan 2      7380 RPM        OK          0
#          Fan 3      7140 RPM        OK          0
#
# @description-end
#
import config

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# DiskInformation
################################################################################
class FanInformation:
    """Fan Information"""

    Enclosure = 0
    MemberId = ''
    ReadingRPM = 0
    Name = ''
    StatusState = ''
    StatusHealth = ''

    def __init__(self, Enclosure, MemberId, ReadingRPM, Name, StatusState, StatusHealth):
        self.Enclosure = Enclosure
        self.MemberId = MemberId
        self.ReadingRPM =ReadingRPM
        self.Name = Name
        self.StatusState = StatusState
        self.StatusHealth = StatusHealth

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show fans"""
    name = 'show fans'
    link = None
    readings = []

    @classmethod
    def prepare_url(self, command):
        self.readings = []
        return (config.thermal)
        
    @classmethod
    def process_json(self, redfishConfig, url):

        # GET DriveCollection
        Trace.log(TraceLevel.VERBOSE, '++ GET collection from ({})'.format(url))
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))
        
        # Retrieve a listing of all fans for this system
        if (self.link.valid):
            
            # Create a list of all the URLs
            for (key, value) in self.link.jsonData.items():
                Trace.log(TraceLevel.TRACE, '   ++ Fans collection: key={} value={}'.format(key, value))
                if (key == 'Fans'):
                    for link in value:
                        Trace.log(TraceLevel.TRACE, '   ++ process item {}'.format(link['@odata.id']))

                        MemberId = link['MemberId']
                        ReadingRPM = str(link['ReadingRPM']) + ' RPM'
                        Name = link['Name']
                        statusDict = link['Status']
                        StatusState = statusDict['State']
                        StatusHealth = statusDict['Health']
                        
                        item = FanInformation(0, MemberId, ReadingRPM, Name, StatusState, StatusHealth)
                        self.readings.append(item)

    @classmethod
    def display_results(self, redfishConfig):
        # self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            print('    SensorName       Reading    Health  Enclosure')
            print('  -----------------------------------------------')
            #               Fan 0     7440 RPM        OK           0
            for i in range(len(self.readings)):

                print('  {0: >12}  {1: >12}  {2: >8}  {3: >9}'.format(
                    self.readings[i].Name,
                    self.readings[i].ReadingRPM,
                    self.readings[i].StatusHealth,
                    self.readings[i].Enclosure))
