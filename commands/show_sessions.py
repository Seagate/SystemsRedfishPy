#
# @command show sessions
#
# @synopsis Display all active sessions, requires an active session
#
# @description-start
#
# 'show sessions' displays details about all authenticated sessions.
#
# Example:
#
# (redfish) show sessions
# 
#    Id          UserName              Name       Description
#  ---------------------------------------------------------
#     7            manage      User Session      User Session
#     8            manage      User Session      User Session
#     9            manage      User Session      User Session
#    10            manage      User Session      User Session
#    11            manage      User Session      User Session
#    12            manage      User Session      User Session
#    13            manage      User Session      User Session
#    14            manage      User Session      User Session
#    15            manage      User Session      User Session
#    16            manage      User Session      User Session
#    17            manage      User Session      User Session
#    18            manage      User Session      User Session#
#
# @description-end
#

from commands.commandHandlerBase import CommandHandlerBase
from trace import TraceLevel, Trace
from urlAccess import UrlAccess, UrlStatus

################################################################################
# SessionInformation
################################################################################
class SessionInformation:
    """Session Information"""

    Id = None
    Name = ''
    Description = ''
    UserName = ''
    
    def init_from_url(self, config, url):
        Trace.log(TraceLevel.DEBUG, '   ++ Init from URL {}'.format(url))

        link = UrlAccess.process_request(config, UrlStatus(url))

        if (link.valid):        
            Trace.log(TraceLevel.DEBUG, '   ++ Session: ({}, {}, {}, {})'.format(
                link.jsonData['Id'], link.jsonData['Name'], link.jsonData['Description'], link.jsonData['UserName']))
    
            self.Id = int(link.jsonData['Id'])
            self.Name = link.jsonData['Name']
            self.Description =link.jsonData['Description']
            self.UserName = link.jsonData['UserName']

################################################################################
# CommandHandler
################################################################################
class CommandHandler(CommandHandlerBase):
    """Command - show sessions"""
    name = 'show sessions'
    link = None
    sessions = []

    @classmethod
    def prepare_url(self, command):
        self.sessions = []
        return ('/redfish/v1/SessionService/Sessions')
        
    @classmethod
    def process_json(self, config, url):

        # GET DriveCollection
        Trace.log(TraceLevel.VERBOSE, '++ GET Session collection from ({})'.format(url))
        self.link = UrlAccess.process_request(config, UrlStatus(url))

        # Retrieve a listing of all sessions
        if (self.link.valid):
            
            total = 0 
            created = 0
            urls = []

            Trace.log(TraceLevel.TRACE, '   -- <<< RESPONSE >>>>')
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('x-auth-token', self.link.response.getheader('x-auth-token', '')))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('version', self.link.response.version))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('status', self.link.response.status))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('reason', self.link.response.reason))

            # Create a list of all the URLs
            for (key, value) in self.link.jsonData.items():
                if (key == 'Members@odata.count'):
                    total = value
                elif (key == 'Members'):
                    for link in value:
                        urls.append(link['@odata.id'])
                        created += 1
            
            # Create object based on each URL
            if (created > 0 and created == total):
                for i in range(len(urls)):
                    Trace.log(TraceLevel.VERBOSE, '   -- GET data ({0: >3}) of ({1: >3}) url ({2})'.format(i, len(urls), urls[i]))
                    session = SessionInformation()
                    session.init_from_url(config, urls[i])
                    self.sessions.append(session)
            else:
                Trace.log(TraceLevel.ERROR, '   ++ CommandHandler: Information mismatch: Members@odata.count ({}), Memebers {}'.format(total, created))


    @classmethod
    def display_results(self, config):
        # self.print_banner(self)
        if (self.link.valid == False):
            print('')
            print(' [] URL        : {}'.format(self.link.url))
            print(' [] Status     : {}'.format(self.link.urlStatus))
            print(' [] Reason     : {}'.format(self.link.urlReason))

        else:
            # Sort the list b
            self.sessions.sort(key=lambda x: x.Id, reverse=False)

            print('')
            print('   Id          UserName              Name       Description')
            print(' ---------------------------------------------------------')
            for i in range(len(self.sessions)):
                print(' {0: >4}  {1: >16}  {2: >16}  {3: >16}'.format(
                    self.sessions[i].Id,
                    self.sessions[i].UserName,
                    self.sessions[i].Name,
                    self.sessions[i].Description))
