#
# @command show pools
#
# @synopsis Display all allocated virtual pools and pool information
#
# @description-start
#
# 'show pools' displays details about all available pools, including
# name, serial number, class, size, and health.
#
# Example:
#
# Name Serial Number                    Class    Blocksize Total Size Avail  Snap Size OverCommit  Disk Groups Volumes  Low Thresh  Mid Thresh  High Thresh  Sec Fmt   Health
# -----------------------------------------------------------------------------
# A    00c0ff5112460000f75a925d01000000 Virtual  512       2341.6GB   2341.5GB  0B        Enabled     2           1        50.00 %     75.00 %  90.82 %      512n      OK
# B    00c0ff51124800008863925d01000000 Virtual  512       576.8GB    576.8GB   0B        Enabled     1           0        50.00 %     75.00 %  76.00 %      512n      OK
# -----------------------------------------------------------------------------
# Success: Command completed successfully. (2019-10-01 14:18:01)
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, LinkStatus

################################################################################
# PoolInformation
################################################################################
class PoolInformation:
    """Pool Information"""

    Name = ''
    Id = ''
    Manufacturer = ''
    BlockSizeBytes = ''
    AllocatedVolumes = ''
    RemainingCapacityPercent = ''
    ReadHitIORequests = ''
    ReadIOKiBytes = ''
    ReadIORequestTime = ''
    WriteHitIORequests = ''
    WriteIOKiBytes = ''
    WriteIORequestTime = ''
    AllocatedBytes = ''
    ConsumedBytes = ''
    State = ''
    Health = ''
    
    def init_from_url(self, config, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Pool init from URL {}'.format(url))

        link = UrlAccess.process_link(config, LinkStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Pool: ({}, {}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['Manufacturer'], link.jsonData['BlockSizeBytes'], link.jsonData['remainingCapacityPercent']))

            self.Name = link.jsonData['Name']
            self.Id = link.jsonData['Id']
            self.Manufacturer = link.jsonData['Manufacturer']
            self.BlockSizeBytes = link.jsonData['BlockSizeBytes']

            try:
                avs = link.jsonData['AllocatedVolumes']
                self.AllocatedVolumes = len(avs)
            except:
                self.AllocatedVolumes = 0
                pass

            self.RemainingCapacityPercent = link.jsonData['remainingCapacityPercent']

            iostats = link.jsonData['IOStatistics']
            self.ReadHitIORequests = iostats['ReadHitIORequests']
            self.ReadIOKiBytes = iostats['ReadIOKiBytes']
            self.ReadIORequestTime = iostats['ReadIORequestTime']
            self.WriteHitIORequests = iostats['WriteHitIORequests']
            self.WriteIOKiBytes = iostats['WriteIOKiBytes']
            self.WriteIORequestTime = iostats['WriteIORequestTime']

            capacity = link.jsonData['Capacity']
            data = capacity['Data']
            self.AllocatedBytes = data['AllocatedBytes']
            self.ConsumedBytes = data['ConsumedBytes']
            
            status = link.jsonData['Status']
            self.State = status['State']
            self.Health = status['Health']
            

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show pools"""
    name = 'show pools'
    pools = []
    link = None

    @classmethod
    def prepare_url(self, command):
        self.pools = []
        return ('/redfish/v1/StorageServices/S1/StoragePools')

    @classmethod
    def process_json(self, config, url):
        
        # GET Pools
        self.link = UrlAccess.process_link(config, LinkStatus(url))
        
        # Retrieve a listing of all pools for this system
        # Note: Version 1.1 returns storage groups and pools, don't take StoragePools that start with 00c0ff

        if (self.link.valid):

            totalPools = 0 
            createdPools = 0
            poolUrls = []
            
            # Create a list of all the pool URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    totalPools = value
                    Trace.log(TraceLevel.VERBOSE, '... GET pools total ({})'.format(totalPools))
                elif (key == 'Members'):
                    Trace.log(TraceLevel.TRACE, '... Members value ({})'.format(value))
                    if (value != None):
                        for poolLink in value:
                            url = poolLink['@odata.id']
                            words = url.split('/')
                            idnumber = words[len(words)-1]
                            if (idnumber.startswith('00c0ff')):
                                Trace.log(TraceLevel.TRACE, '... SKIP pool url ({})'.format(url))
                                totalPools -= 1
                            else:
                                Trace.log(TraceLevel.VERBOSE, '... ADD pool url ({})'.format(url))
                                poolUrls.append(url)
                                createdPools += 1

            # Create Pool object based on each drive URL
            if (createdPools > 0 and createdPools == totalPools):
                for i in range(len(poolUrls)):
                    Trace.log(TraceLevel.VERBOSE, '... GET pool data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(poolUrls), poolUrls[i]))
                    pool = PoolInformation()
                    pool.init_from_url(config, poolUrls[i])
                    self.pools.append(pool)
            elif (createdPools > 0):
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Pool information mismatch: Members@odata.count ({}), Memebers {}'.format(totalPools, createdPools))


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
            # Name Serial Number                    Class    Blocksize Total Size Avail  Snap Size OverCommit  Disk Groups Volumes  Low Thresh  Mid Thresh  High Thresh  Sec Fmt   Health
            # -----------------------------------------------------------------------------
            # A    00c0ff5112460000f75a925d01000000 Virtual  512       2341.6GB   2341.5GB  0B        Enabled     2           1        50.00 %     75.00 %  90.82 %      512n      OK
    
            #          0                                 1          2        3         4             5          6         7              8           9         10              11             12      13
            print(' Name                      SerialNumber  BlockSize  Volumes  Capacity  ReadRequests  ReadBytes  ReadTime  WriteRequests  WriteBytes  WriteTime  AllocatedBytes  ConsumedBytes  Health')
            print(' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
    
            if (self.pools != None):
                for i in range(len(self.pools)):
                    print(' {0: >4}  {1: >32}  {2: >9}  {3: >7}  {4: >8}  {5: >12}  {6: >9}  {7: >8}  {8: >13}  {9: >10}  {10: >9}  {11: >14}  {12: >13}  {13: >6}'.format(
                        self.pools[i].Name,
                        self.pools[i].Id,
                        self.pools[i].BlockSizeBytes,
                        self.pools[i].AllocatedVolumes,
                        self.pools[i].RemainingCapacityPercent,
                        self.pools[i].ReadHitIORequests,
                        self.pools[i].ReadIOKiBytes,
                        self.pools[i].ReadIORequestTime,
                        self.pools[i].WriteHitIORequests,
                        self.pools[i].WriteIOKiBytes,
                        self.pools[i].WriteIORequestTime,
                        self.pools[i].AllocatedBytes,
                        self.pools[i].ConsumedBytes,
                        self.pools[i].Health))
