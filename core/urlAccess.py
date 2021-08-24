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
from core.jsonBuilder import JsonBuilder, JsonType
import base64
import config
import json
import os
import requests
import socket
import ssl
import sys
import time
import traceback
import urllib.request, urllib.error
import warnings

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
    parent = ''

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

    #
    # process_push
    #     Used to perform an HTTP push of a file and possible JSON data.
    #     Authentication data is automatically added to the HTTP request.
    #     These method uses the python requests package
    #
    @classmethod
    def process_push(self, redfishConfig, link, filename, payload = None):
        Trace.log(TraceLevel.INFO, '++ UrlAccess: process_push - ({}) session ({}:{})'.format(link.url, Label.decode(config.sessionIdVariable), redfishConfig.sessionKey))

        startTime = time.time()

        warnings.filterwarnings('ignore', message='Unverified HTTPS request')

        s = requests.Session()

        fullUrl = redfishConfig.get_value('http') + '://' + redfishConfig.get_mcip() + link.url
        Trace.log(TraceLevel.INFO, '   -- fullUrl: {}'.format(fullUrl))
        Trace.log(TraceLevel.INFO, '   -- filename ({})'.format(filename))

        JsonBuilder.startNew()
        JsonBuilder.newElement('jsonpayload', JsonType.DICT)

        # Add authentication
        if redfishConfig.get_bool('httpbasicauth'):
            encoded = base64.b64encode(str.encode(redfishConfig.get_value('username') + ':' + redfishConfig.get_value('password')))
            Trace.log(TraceLevel.DEBUG, '   -- HTTP Basic Authorization: {}'.format(encoded))
            s.headers.update({'Authorization': 'Basic ' + str(encoded), })
        else:
            Trace.log(TraceLevel.INFO, '   -- X-Auth-Token: {}'.format(redfishConfig.sessionKey))
            s.headers.update({'X-Auth-Token': redfishConfig.sessionKey})

        # Add passed in JSON data
        if payload is not None:
            Trace.log(TraceLevel.INFO, '   -- post w/ JSON')
            if (redfishConfig.get_bool('dumppostdata')):
                Trace.log(TraceLevel.INFO, '[[ PAYLOAD DATA ({}) ]]'.format(link.url))
                print(json.dumps(payload, indent=4))
                Trace.log(TraceLevel.INFO, '[[ PAYLOAD DATA END ]]')
        else:
            payload = {}

        files = {
            'json': (None, json.dumps(payload), 'application/json'),
            'file': (os.path.basename(filename), open(filename, 'rb'), 'application/octet-stream')
        }

        try:
            response = s.request('POST', fullUrl, files=files, verify=False)
            link.urlData = response.text
            link.update_status(response.status_code, response.reason)
            try:
                link.jsonData = json.loads(link.urlData)
            except:
                pass

            # Trace.log(TraceLevel.INFO, '============================== RESPONSE ==============================')
            # print(response.content)
            # print(response.text)
            # print('status_code: {}'.format(response.status_code))
            # print('reason: {}'.format(response.reason))
            # print('request: {}'.format(response.request))
            # Trace.log(TraceLevel.INFO, '============================== END RESPONSE ==============================')

        except Exception as e:
            Trace.log(TraceLevel.ERROR, 'Exception: request(POST) - {}'.format(e))
            link.update_status(418, 'Exception: request(POST) - ' + str(e))
            pass

        link.elapsedMicroseconds = (time.time() - startTime) * 1000000

        return link

    #
    # process_request
    #     Used to perform an HTTP operation of GET, POST, DELETE.
    #     Authentication data is automatically added to the HTTP request.
    #     These method should be updated to use the python requests package
    #
    @classmethod
    def process_request(self, redfishConfig, link, method = 'GET', addAuth = True, data = None, decode = True):

        try:
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request - {} ({}) session ({}:{})'.format(method, link.url, Label.decode(config.sessionIdVariable), redfishConfig.sessionKey))
            fullUrl = redfishConfig.get_value('http') + '://' + redfishConfig.get_mcip() + link.url

            request = urllib.request.Request(fullUrl, method = method)

            if redfishConfig.get_bool('httpbasicauth'):
                Trace.log(TraceLevel.DEBUG, '   -- Using HTTP Basic Auth')
                uername_password = redfishConfig.get_value('username') + ':' + redfishConfig.get_value('password')
                encoded = base64.b64encode(str.encode(uername_password))
                encoded = encoded.decode('utf-8')
                Trace.log(TraceLevel.DEBUG, '   -- uername_password is ({}) encoded is ({})'.format(uername_password, encoded))
                request.add_header('Authorization', 'Basic ' + str(encoded))

            elif (addAuth and redfishConfig.sessionKey is not None):
                Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: X-Auth-Token=({})'.format(redfishConfig.sessionKey))
                request.add_header('X-Auth-Token', redfishConfig.sessionKey)

            startTime = time.time()
            Trace.log(TraceLevel.TRACE, '   >> startTime={}'.format(startTime))

            if (data):
                request.add_header('If-None-Match', '""')
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
            if decode:
                link.urlData = link.response.read().decode('utf-8')
            else:
                link.urlData = link.response.read()

            Trace.log(TraceLevel.TRACE, '[[ urlData DATA ]]')
            Trace.log(TraceLevel.TRACE, '{}'.format(link.urlData))
            Trace.log(TraceLevel.TRACE, '[[ urlData DATA END ]]')

            if (link.urlData):
                try:
                    contentTypeHandled = False                    
                    headers = link.response.getheaders()
                    itemCount = 0
                    for item in headers:
                        Trace.log(TraceLevel.TRACE, '   -- headers[{}]={}'.format(itemCount, item))
                        if len(item) >= 2:
                            if 'json' in item[1]:
                                if isinstance(link.urlData, str):
                                    link.jsonData = json.loads(link.urlData)
                                elif isinstance(link.urlData, bytes):
                                    link.jsonData = json.loads(str(link.urlData.decode("utf-8")))
                                else:
                                    Trace.log(TraceLevel.WARN, '   ++ UrlAccess: unhandled link.urlData type = {}'.format(type(link.urlData)))
                                contentTypeHandled = True
                        itemCount += 1 

                    if not contentTypeHandled:
                        Trace.log(TraceLevel.DEBUG, '   ++ UrlAccess: unhandled content type = {}'.format(headers))

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

        except urllib.error.HTTPError as err:
            link.update_status(err.code, err.reason)
            Trace.log(TraceLevel.TRACE, '   ++ UrlAccess: process_request // ERROR receiving data from ({}): HTTP Error {}: {}'.format(link.url, err.code, err.reason))
            Trace.log(TraceLevel.TRACE, '===== [[ headers DATA ]] =====')
            Trace.log(TraceLevel.TRACE, '{}'.format(err.headers))
            Trace.log(TraceLevel.TRACE, '[[ headers DATA END ]]')

            Trace.log(TraceLevel.INFO, '   -- command-status: {}'.format(err.headers.get('command-status')))
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
                Trace.log(TraceLevel.INFO, '')
                Trace.log(TraceLevel.INFO, '='*120)
                errorMessage = err.read()
                if (redfishConfig.get_bool('dumphttpdata')):
                    Trace.log(TraceLevel.INFO, 'httpData: {}'.format(errorMessage))
                else:
                    Trace.log(TraceLevel.INFO, 'errorMessage = {}'.format(errorMessage))
                Trace.log(TraceLevel.INFO, '='*120)
                pass
        
        return link
