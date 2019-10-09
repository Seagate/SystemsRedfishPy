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
# UrlStatus
################################################################################
class UrlStatus():
    url = ''
    urlStatus = 0
    urlReason = ''
    response = None
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
        Trace.log(TraceLevel.TRACE, '   ++ UrlStatus(add): url=({})'.format(url))

    def update_status(self, status, reason):
        self.urlStatus = status
        self.urlReason = reason
        self.checked = True
        if (status == 200 or status == 201):
            self.valid = True

        Trace.log(TraceLevel.DEBUG, '   ++ UrlStatus(update_status): status={} reason={} valid={}'.format(status, reason, self.valid))

################################################################################
# UrlAccess
################################################################################
class UrlAccess():

    @classmethod
    def process_request(self, config, link, method = 'GET', addAuth = True, data = None):

        try:
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request - {} ({}) session ({})'.format(method, link.url, config.sessionKey))
            fullUrl = 'http://' + config.get_value('mcip') + link.url

            request = urllib.request.Request(fullUrl, method = method)

            if (data):
                request.add_header('Content-Type', 'application/json; charset=utf-8')
                jsondata = json.dumps(data)
                jsondataasbytes = jsondata.encode('utf-8')
                request.add_header('Content-Length', len(jsondataasbytes))

            if (addAuth):
                request.add_header('x-auth-token', config.sessionKey)

            if (data):
                link.response = urllib.request.urlopen(request, jsondataasbytes, timeout=config.get_urltimeout())
            else:
                link.response = urllib.request.urlopen(request, timeout=config.get_urltimeout())
                
            link.urlData = link.response.read()

            if (link.urlData):
                try:
                    link.jsonData = json.loads(link.urlData)
                except:
                    pass

            link.update_status(link.response.status, link.response.reason)

            if (config.get_int_value('dumpjsondata') == 1):
                if (link.jsonData != None):
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA ({}) ]]'.format(link.url))
                    print(json.dumps(link.jsonData, indent=4))
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')

            link.response.close()
                
        except socket.timeout:
            link.update_status(598, 'socket.timeout')
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): Socket Error {}: {}'.format(link.url, 598, 'socket.timeout'))
            pass

        except urllib.error.URLError as err:
            link.update_status(501, err.reason)
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): URL Error {}'.format(link.url, err.reason))
            pass

        except urllib.error.HTTPError as err:
            link.update_status(err.code, err.reason)
            Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): HTTP Error {}: {}'.format(link.url, err.code, err.reason))
            pass
        
        return link
