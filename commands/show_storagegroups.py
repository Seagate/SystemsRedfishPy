#
# @command show storagegroups
#
# @synopsis Display all created storage groups
#
# @description-start
#
# 'show storagegroups' displays details about all created storage groups.
#
# Example:
#
# (redfish) show storagegroups
# 
#      Name                      SerialNumber  BlockSize  Capacity  AllocatedBytes  ConsumedBytes  Health  ClasOfService
#  ---------------------------------------------------------------------------------------------------------------------
#     dgA01  00c0ff5112460000f55a925d00000000        512         0      1283457024     1283457024      OK          RAID1
#
# @description-end
#

import config
from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# PoolInformation
################################################################################
class StorageGroupInformation:
    """Storage Group Information"""

    Description = ''
    SerialNumber = ''
    MembersAreConsistent = ''
    VolumesAreExposed = ''
    Name = ''
    AccessState = ''

    # MappedVolumes
    LogicalUnitNumber = ''
    Volume = ''
    
    ClientEndpointGroups = []   # Initiators
    ServerEndpointGroups = []   # Ports
    
    # Status
    State = ''
    Health = ''
    HealthRollup = ''

    def init_from_url(self, redfishConfig, url):

        Trace.log(TraceLevel.DEBUG, '   ++ Storage Group init from URL {}'.format(url))
        link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        if (link.valid):
            Trace.log(TraceLevel.VERBOSE, '   ++ Storage Group: ({}, {})'.format(link.jsonData['Id'], link.jsonData['Name']))

            try:
                self.Description = link.jsonData['Description']
                self.SerialNumber = link.jsonData['Id']
                self.MembersAreConsistent = link.jsonData['MembersAreConsistent']
                self.VolumesAreExposed = link.jsonData['VolumesAreExposed']
                self.Name = link.jsonData['Name']
                self.AccessState = link.jsonData['AccessState']

                self.ClientEndpointGroups = []
                ceg = link.jsonData['ClientEndpointGroups']
                for i in range(len(ceg)):
                    # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                    url = ceg[i]['@odata.id'].replace(config.endpointGroups, '')
                    self.ClientEndpointGroups.append(url)

                self.ServerEndpointGroups = []
                seg = link.jsonData['ServerEndpointGroups']
                for i in range(len(seg)):
                    # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                    url = seg[i]['@odata.id'].replace(config.endpointGroups, '')
                    self.ServerEndpointGroups.append(url)

                mv = link.jsonData['MappedVolumes']
                for i in range(len(mv)):
                    # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                    self.LogicalUnitNumber = mv[i]['LogicalUnitNumber']
                    self.Volume = mv[i]['Volume']['@odata.id'].replace(config.volumes, '')

                status = link.jsonData['Status']
                self.State = status['State']
                self.Health = status['Health']
                self.HealthRollup = status['HealthRollup']

            except:
                self.Description = 'Unknown'
#                pass

        return True

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show storagegroups"""
    name = 'show storagegroups'
    pools = []
    link = None

    @classmethod
    def prepare_url(self, command):
        self.groups = []
        return (config.storageGroups)

    @classmethod
    def process_json(self, redfishConfig, url):

        # GET list of pools and disk groups
        self.link = UrlAccess.process_request(redfishConfig, UrlStatus(url))

        # Retrieve a listing of all storage groups for this system

        if (self.link.valid):

            total = 0 
            created = 0
            urls = []
            
            # Create a list of URIs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                    Trace.log(TraceLevel.VERBOSE, '.. GET total ({})'.format(total))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '.. Members value ({})'.format(value))
                    if (value != None):
                        for groupLink in value:
                            url = groupLink['@odata.id']
                            Trace.log(TraceLevel.VERBOSE, '.. ADD storage group url ({})'.format(url))
                            urls.append(url)
                            created += 1

            # Create object based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '.. GET Storage Group data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls)-1, urls[i]))
                    group = StorageGroupInformation()
                    if (group.init_from_url(redfishConfig, urls[i])):
                        self.groups.append(group)
            elif (created > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Memebers {}'.format(total, created))


    @classmethod
    def display_results(self, redfishConfig):
        #self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            print('')
            print('         Name                                       SerialNumber    State  Health  VolumesAreExposed  LUN                            Volume                          Initiators        Ports')
            print(' -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            #                     00c0ff511246000026fdc35d01000000_500605b00ab61310  Enabled      OK              false   12  00c0ff511246000026fdc35d01000000   500605b00ab61310,500605b00ab61311        A0,B0
            if (self.groups != None):
                for i in range(len(self.groups)):
                    print(' {0: >12}  {1: >49}  {2: >7}  {3: >6}  {4: >17}  {5: >3}  {6: >31}  {7: >34}  {8: >11}'.format(
                        self.groups[i].Name,
                        self.groups[i].SerialNumber,
                        self.groups[i].State,
                        self.groups[i].Health,
                        self.groups[i].VolumesAreExposed,
                        self.groups[i].LogicalUnitNumber,
                        self.groups[i].Volume,
                        ",".join(self.groups[i].ClientEndpointGroups),
                        ",".join(self.groups[i].ServerEndpointGroups),
                        ))
