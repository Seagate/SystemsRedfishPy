#
# urlAccess (command handler)
#
# This module provides a comman access point for all URL accesses.
#

import json
import socket
import urllib.request, urllib.error

from trace import TraceLevel, Trace

################################################################################
# LinkStatus
################################################################################
class LinkStatus():
    url = ''
    urlStatus = 0
    urlReason = ''
    urlData = None
    jsonData = None
    sessionKey = ''
    checked = False
    valid = False

    def __init__(self, url):
        self.url = url

    def do_check(self):
        return (self.checked == False)

    def add_url(self, url):
        self.url = url
        Trace.log(TraceLevel.TRACE, '   ++ LinkStatus(add): url=({})'.format(url))

    def update_status(self, status, reason, data = None):
        self.urlStatus = status
        self.urlReason = reason
        self.urlData = data
        self.checked = True
        if (status == 200 or status == 201):
            self.valid = True

        try:
            if (data != None):
                self.jsonData = json.loads(data)
                
        except:
            pass
            
        Trace.log(TraceLevel.DEBUG, '   ++ LinkStatus(update_status): status={} reason={} valid={}'.format(status, reason, self.valid))

################################################################################
# UrlAccess
################################################################################
class UrlAccess():

    @classmethod
    def process_link(self, config, link, addAuth = True, authenticationData = None):
        
        try:
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_link ({}) session ({})'.format(link.url, config.sessionKey))
            fullUrl = 'http://' + config.get_value('mcip') + link.url

            req = urllib.request.Request(fullUrl)

            if (authenticationData):
                req.add_header('Content-Type', 'application/json; charset=utf-8')
                jsondata = json.dumps(authenticationData)
                jsondataasbytes = jsondata.encode('utf-8')
                req.add_header('Content-Length', len(jsondataasbytes))
                response = urllib.request.urlopen(req, jsondataasbytes, timeout=config.get_urltimeout())

                if (response.status == 201):
                    link.sessionKey = response.getheader('x-auth-token', '')

            else:
                if (addAuth):
                    req.add_header('x-auth-token', config.sessionKey)
                response = urllib.request.urlopen(req, timeout=config.get_urltimeout())

            Trace.log(TraceLevel.TRACE, '   -- <<< RESPONSE >>>>')
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('x-auth-token', response.getheader('x-auth-token', '')))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('version', response.version))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('status', response.status))
            Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('reason', response.reason))

            data = response.read()

            if (authenticationData):
                details = json.loads(data)
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Id', details['Id']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Name', details['Name']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Description', details['Description']))
                Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('UserName', details['UserName']))
                
            link.update_status(response.status, response.reason, data)

            if (config.get_int_value('dumpjsondata') == 1):
                if (link.jsonData != None):
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA ({}) ]]'.format(link.url))
                    print(json.dumps(link.jsonData, indent=4))
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')

            response.close()
                
        except socket.timeout:
            link.update_status(598, 'socket.timeout')
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_link // ERROR receiving data from ({}): Socket Error {}: {}'.format(link.url, 598, 'socket.timeout'))
            pass

        except urllib.error.URLError as err:
            link.update_status(501, err.reason)
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_link // ERROR receiving data from ({}): URL Error {}'.format(link.url, err.reason))
            pass

        except urllib.error.HTTPError as err:
            link.update_status(err.code, err.reason)
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_link // ERROR receiving data from ({}): HTTP Error {}: {}'.format(link.url, err.code, err.reason))
            pass
        
        return link
