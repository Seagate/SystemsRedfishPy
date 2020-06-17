#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# urlAccess.py - This module provides a comman access point for all URL accesses. 
#
# ******************************************************************************************
#

from core.label import Label
from core.trace import TraceLevel, Trace
import config
import json
import socket
import ssl
import sys
import time
import traceback
import urllib.request, urllib.error

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
    elapsedMicroseconds = 0

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

        Trace.log(TraceLevel.TRACE, '   ++ UrlStatus(update_status): status={} reason={} valid={}'.format(status, reason, self.valid))

################################################################################
# UrlAccess
################################################################################
class UrlAccess():

    @classmethod
    def process_request(self, redfishConfig, link, method = 'GET', addAuth = True, data = None):

        try:
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request - {} ({}) session ({}:{})'.format(method, link.url, Label.decode(config.sessionIdVariable), redfishConfig.sessionKey))
            fullUrl = redfishConfig.get_value('http') + '://' + redfishConfig.get_value('mcip') + link.url

            request = urllib.request.Request(fullUrl, method = method)

            if (addAuth and redfishConfig.sessionKey is not None):
                Trace.log(TraceLevel.VERBOSE, '   ++ UrlAccess: X-Auth-Token=({})'.format(redfishConfig.sessionKey))
                request.add_header('X-Auth-Token', redfishConfig.sessionKey)

            startTime = time.time()
            Trace.log(TraceLevel.TRACE, '   >> startTime={}'.format(startTime))

            if (data):
                request.add_header('Content-Type', 'application/json; charset=utf-8')
                jsondataasbytes = data.encode('utf-8')                
                request.add_header('Content-Length', len(jsondataasbytes))
                Trace.log(TraceLevel.TRACE, '   ++ Content-Length={}'.format(len(jsondataasbytes)))
                if (redfishConfig.get_bool('dumppostdata')):
                    Trace.log(TraceLevel.INFO, '[[ POST DATA ({}) ]]'.format(link.url))
                    print(data)
                    Trace.log(TraceLevel.INFO, '[[ POST DATA END ]]')
                if (redfishConfig.get_bool('certificatecheck') == False):
                    link.response = urllib.request.urlopen(request, jsondataasbytes, timeout=redfishConfig.get_urltimeout(), context=ssl._create_unverified_context())
                else:
                    link.response = urllib.request.urlopen(request, jsondataasbytes, timeout=redfishConfig.get_urltimeout())
            else:
                if (redfishConfig.get_bool('certificatecheck') == False):
                    link.response = urllib.request.urlopen(request, timeout=redfishConfig.get_urltimeout(), context=ssl._create_unverified_context())
                else:
                    link.response = urllib.request.urlopen(request, timeout=redfishConfig.get_urltimeout())

            endTime = time.time()
            elapsed = (endTime - startTime) * 1000000
            Trace.log(TraceLevel.TRACE, '   >> endTime={}'.format(endTime))
            Trace.log(TraceLevel.TRACE, '   >> elapsed={}'.format(elapsed))

            link.elapsedMicroseconds = elapsed
            link.urlData = link.response.read().decode('utf-8')
            
            Trace.log(TraceLevel.TRACE, '[[ urlData DATA ]]')
            Trace.log(TraceLevel.TRACE, '{}'.format(link.urlData))
            Trace.log(TraceLevel.TRACE, '[[ urlData DATA END ]]')

            if (link.urlData):
                try:
                    headers = link.response.getheaders()
                    # Trace.log(TraceLevel.TRACE, '@@ headers={}'.format(json.dumps(headers, indent=4)))
                    contentType = headers[1][1]
                    Trace.log(TraceLevel.TRACE, '   -- contentType: {}'.format(contentType))
                    if ('json' in contentType or 'nosniff' in contentType):
                        link.jsonData = json.loads(link.urlData)
                    else:
                        Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: unhandled content type = {}'.format(contentType))

                except Exception as inst:
                    Trace.log(TraceLevel.INFO, '   -- Exception: Trying to convert to JSON data, url={}'.format(fullUrl))
                    Trace.log(TraceLevel.INFO, '   -- jsonData={} -- {}'.format(link.jsonData, sys.exc_info()[0], inst))
                    Trace.log(TraceLevel.INFO, '-'*100)
                    Trace.log(TraceLevel.INFO, '   -- urlData={}'.format(link.urlData))
                    Trace.log(TraceLevel.INFO, '-'*100)
                    traceback.print_exc(file=sys.stdout)
                    Trace.log(TraceLevel.INFO, '-'*100)
                    pass
            else:
                Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request // No urlData')

            link.update_status(link.response.status, link.response.reason)

            if (redfishConfig.get_bool('dumpjsondata')):
                if (link.jsonData != None):
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA ({}) ]]'.format(link.url))
                    print(json.dumps(link.jsonData, indent=4))
                    Trace.log(TraceLevel.INFO, '[[ JSON DATA END ]]')

            link.response.close()

        except socket.timeout:
            link.update_status(598, 'socket.timeout')
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): Socket Error {}: {}'.format(link.url, 598, 'socket.timeout'))
            pass

        except urllib.error.URLError as err:
            errorCode = 0
            if hasattr(err,'code'):
                errorCode = err.code
            errorReason = 'Unknown'
            if hasattr(err,'reason'):
                errorReason = err.reason
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): URL Error code={} reason={}'.format(link.url, errorCode, errorReason))
            link.update_status(errorCode, errorReason)

            # Print the contents of the HTTP message response
            read_op = getattr(err, "read", None)
            if (callable(read_op)):
                Trace.log(TraceLevel.VERBOSE, '   ' + '='*60 + '  HTTP Error START  ' + '='*60)
                errorMessage = err.read()
                if (redfishConfig.get_bool('dumphttpdata')):
                    Trace.log(TraceLevel.INFO, '   -- httpData {}'.format(errorMessage))
                else:
                    Trace.log(TraceLevel.VERBOSE, '  errorMessage = {}'.format(errorMessage))
                Trace.log(TraceLevel.VERBOSE, '   ' + '='*60 + '  HTTP Error END  ' + '='*60)
                pass

        except urllib.error.HTTPError as err:
            link.update_status(err.code, err.reason)
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): HTTP Error {}: {}'.format(link.url, err.code, err.reason))
            pass
        
        return link
