#
# @command show thermal
#
# @synopsis Display all temperature data from the system.
#
# @description-start
#
# 'show thermal' displays details about all temperature readings.
#
# Example:
#
# (redfish) show thermal
# 
#                                     SensorName  Reading    Health  Enclosure
#   --------------------------------------------------------------------------
#                         CPU Temperature-Ctlr A     46 C        OK          0
#              Capacitor Pack Temperature-Ctlr A     14 C   Warning          0
#                    Expander Temperature-Ctlr A     38 C        OK          0
#             Disk Controller Temperature-Ctlr A     69 C        OK          0
#             Host Controller Temperature-Ctlr A     60 C        OK          0
#     SBB IOM Inlet Temperature Loc: upper-IOM A     30 C        OK          0
#                         CPU Temperature-Ctlr B     47 C        OK          0
#              Capacitor Pack Temperature-Ctlr B     16 C   Warning          0
#                    Expander Temperature-Ctlr B     55 C        OK          0
#             Disk Controller Temperature-Ctlr B     82 C        OK          0
#             Host Controller Temperature-Ctlr B     61 C        OK          0
#     SBB IOM Inlet Temperature Loc: lower-IOM B     34 C        OK          0
#                Temperature Inlet Loc: left-PSU     26 C        OK          0
#              Temperature Hotspot Loc: left-PSU     29 C        OK          0
#               Temperature Inlet Loc: right-PSU     27 C        OK          0
#             Temperature Hotspot Loc: right-PSU     29 C        OK          0
#                  Ops Panel Ambient Temperature     33 C        OK          0
#                           Midplane Temperature     25 C        OK          0
#                                       Disk 0.0     26 C        OK          0
#                                       Disk 0.1     26 C        OK          0
#                                       Disk 0.2     25 C        OK          0
#                                       Disk 0.3     26 C        OK          0
#                                       Disk 0.4     26 C        OK          0
#                                       Disk 0.5     25 C        OK          0
#                                       Disk 0.6     25 C        OK          0
#                                       Disk 0.9     25 C        OK          0
#                                      Disk 0.10     25 C        OK          0
#                                      Disk 0.11     26 C        OK          0
#                                      Disk 0.12     25 C        OK          0
#                                      Disk 0.13     26 C        OK          0
#                                      Disk 0.14     29 C        OK          0
#                                      Disk 0.15     28 C        OK          0
#                                      Disk 0.16     25 C        OK          0
#                                      Disk 0.17     25 C        OK          0
#                                      Disk 0.18     26 C        OK          0
#                                      Disk 0.19     26 C        OK          0
#                                      Disk 0.20     26 C        OK          0
#                                      Disk 0.21     27 C        OK          0
#                                      Disk 0.22     27 C        OK          0
#                                      Disk 0.23     30 C        OK          0
#                                       Disk 0.7     26 C        OK          0
#                                       Disk 0.8     24 C        OK          0
# 
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# DiskInformation
################################################################################
class ThermalInformation:
    """Thermal Information"""

    Enclosure = 0
    MemberId = ''
    Name = ''
    ReadingCelcius = ''
    SensorName = ''
    StatusState = ''
    StatusHealth = ''

    def __init__(self, MemberId, Name, ReadingCelcius, SensorName, StatusState, StatusHealth):
        self.MemberId = MemberId
        self.Name = Name
        self.ReadingCelcius =ReadingCelcius
        self.SensorName = SensorName
        self.StatusState = StatusState
        self.StatusHealth = StatusHealth

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show thermal"""
    name = 'show thermal'
    link = None
    readings = []

    @classmethod
    def prepare_url(self, command):
        self.readings = []
        return ('/redfish/v1/Chassis/enclosure_0/Thermal')
        
    @classmethod
    def process_json(self, config, url):

        # GET DriveCollection
        Trace.log(TraceLevel.VERBOSE, '++ GET Thermal collection from ({})'.format(url))
        self.link = UrlAccess.process_request(config, UrlStatus(url))
        
        # Retrieve a listing of all temperatures for this system
        if (self.link.valid):
            
            # Create a list of all the URLs
            for (key, value) in self.link.jsonData.items():
                Trace.log(TraceLevel.TRACE, '   ++ Thermal collection: key={} value={}'.format(key, value))
                if (key == 'Temperatures'):
                    for link in value:
                        Trace.log(TraceLevel.TRACE, '   ++ process item {}'.format(link['@odata.id']))

                        MemberId = link['MemberId']
                        Name = link['Name']
                        ReadingCelcius = str(link['ReadingCelcius'])
                        test = link['test']
                        statusDict = link['Status']
                        StatusState = statusDict['State']
                        StatusHealth = statusDict['Health']
                        
                        # Adjust certain strings
                        ReadingCelcius = ReadingCelcius.replace('.0', ' C')
                        SensorName = test
                        if (SensorName == 'Temperature Loc: Disk'):
                            SensorName = 'Disk ' + Name.replace('sensor_temp_disk_', '')
                        
                        item = ThermalInformation(MemberId, Name, ReadingCelcius, SensorName, StatusState, StatusHealth)
                        self.readings.append(item)

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
            print('                                    SensorName  Reading    Health  Enclosure')
            print('  --------------------------------------------------------------------------')
            #        SBB IOM Inlet Temperature Loc: lower-IOM BL     100 C        OK           0
            for i in range(len(self.readings)):

                print('  {0: >44}  {1: >7}  {2: >8}  {3: >9}'.format(
                    self.readings[i].SensorName,
                    self.readings[i].ReadingCelcius,
                    self.readings[i].StatusHealth,
                    self.readings[i].Enclosure))
