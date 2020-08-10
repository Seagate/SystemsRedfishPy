# Redfish Service v1 Tutorial

#### Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates, All Rights Reserved

## Introduction

***Redfish Service*** provides an implementation of the DMTF Redfish and SNIA Swordfish specifications. This is a REST-ful API that is 
accessed over HTTP or Secure HTTP. The interface uses a number of HTTP operations to perform Create, Read, Update, and Delete (CRUD) operations.
This service uses HTTP operations POST to Create, GET to Read, PATCH to Update, and DELETE to Delete. The main features of this service are to
review status of a storage system, provision and expose new storage volumes, and various features for storage system management. This tutorial
covers how these features are accomplished using the Redfish Service. 

Redfish Clients can communicate with this Redfish Service using a variety of different tools including **curl**, DMTF provided validators like
**RedfishServiceValidator**, and Seagate provided python client called **SystemsRedfishPy**. This tutorial uses SystemsRedfishPy to perform the
HTTP operations needed to provision and manage a storage system. How to use SystemsRedfishPy is covered in separate documents where this tutorial
focuses on the Redfish interface and learning Redfish/Swordfish commands.

### Table of Contents
* [(1) Determine Redfish Version](#section1)
* [(2) Determine Redfish Services using Service Root](#section2)
* [(3) Create a Session](#section3)
* [(4) Show Active Sessions](#section4) 
* [(5) Explore Systems](#section5)
* [(6) Explore Chassis](#section6)
* [(7) Explore Managers](#section7)
* [(8) Create A RAID Disk Group using StoragePool](#section8)
* [(9) Create A Volume](#section9)
* [(10) Expose A Volume Using Mapping and StorageGroups](#section10)
* [(11) Update A Volume](#section11)
* [(12) Delete A Volume](#section12)
* [(13) Delete A Pool using StoragePool](#section13)


## <a name="section1">(1) Determine Redfish Version</a>

The root URI for Redfish is `/redfish`. An HTTP GET of this URI returns JSON data that contains the current version of the Redfish specification
supported by the service. 

**Note:** This tool does not require the full URL. When a URI of **/redfish** is entered by the user, the tool creates a full URL using tool configuration 
variables. The protocol is determined by **!http** and that value is used with **!mcip** to form a full URL. For example, the user enters **/redfish**
but the tool performs a HTTP operation on **https://10.235.221.172/redfish**. This tutorial uses this shortened URI syntax.

```
SystemsRedfishPy> python --version
Python 3.7.4

SystemsRedfishPy> python redfishAPI.py -c i100b.json

--------------------------------------------------------------------------------
[1.2.7] Redfish API
--------------------------------------------------------------------------------
[] Run Redfish API commands interactively...

(redfish) !certificatecheck False
(redfish) !http https
(redfish) !mcip 10.235.221.172
(redfish) !password <password>
(redfish) !username <username>

(redfish) !dump
   >> configuration values:
      -- certificatecheck     : False
      -- http                 : https
      -- mcip                 : 10.235.221.172
      -- password             : <password>
      -- username             : <username>

(redfish) http get /redfish
[] http get: url (/redfish)

[] URL        : /redfish
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "v1": "/redfish/v1/"
}
```

You can see by the JSON data returned that the current version supported by this service is v1. So all URIs should use **/redfish/v1** as the base URI.

## <a name="section2">(2) Determine Redfish Services using Service Root</a>

The URI **/redfish/v1** produces a list of all services implemented by this Redfish service.

```
(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)

[] URL        : /redfish/v1
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
    "@odata.id": "/redfish/v1/",
    "@odata.type": "#ServiceRoot.v1_2_0.ServiceRoot",
    "Id": "RootService",
    "Name": "Root Service",
    "RedfishVersion": "1.0.3",
    "UUID": "92384634-2938-2342-8820-489239905423",
    "Systems": {
        "@odata.id": "/redfish/v1/ComputerSystem"
    },
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "StorageServices": {
        "@odata.id": "/redfish/v1/StorageServices"
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Tasks": {
        "@odata.id": "/redfish/v1/TaskService"
    },
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Links": {
        "Oem": {},
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    }
}
```

The key take away from this JSON response is that this service provides a number of models and data for various system information
including: **Systems**, **Chassis**, **StorageServices**, **Managers**, **Tasks**, and **SessionService**.

## <a name="section3">(3) Create a Session</a>

The Redfish specification specifies two supported authentication methods - HTTP basic authentication or session login authentication. This 
service uses the session login authentication. A session is needed in order to access most URIs of the service. Only the following URIs
can be accessed without a session:
* /redfish
* /redfish/v1
* /redfish/odata 
* /redfish/$metadta

To create a session, we POST JSON data containing a username and password to the Sessions object. The tags <username> and <password> must be
replaced with the correct values when executed.

**Note:** An extra command is executed below so that the **X-Auth-Token** is stored for all future HTTP calls. The tool will automatically add the
token to all HTTP headers that require authentication.

```
(redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "<username>", "Password": "<password>" }

[] http post: url (/redfish/v1/SessionService/Sessions)

[] URL          : /redfish/v1/SessionService/Sessions
[] Status       : 201
[] Reason       : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '274'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('X-Auth-Token', 'bfe59eff3b71415853deaceb82612b7e')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Session.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/2",
    "@odata.type": "#Session.v1_1_0.Session",
    "Id": "2",
    "Name": "User Session",
    "Description": "User Session",
    "UserName": "<username>"
}

(redfish) save session 2 bfe59eff3b71415853deaceb82612b7e

[] Redfish session saved (2:bfe59eff3b71415853deaceb82612b7e)
```

Now that we have created a session, and saved the authentication key, we can access all other URIs.


## <a name="section4">(4) Show Active Sessions</a>

Perform an HTTP GET on multiple URIs in other to gather session data and session specifics. You must have an active session in order to do this.

```
(redfish) http get /redfish/v1/SessionService/
[] http get: url (/redfish/v1/SessionService/)

[] URL        : /redfish/v1/SessionService/
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#SessionService.SessionService",
    "@odata.id": "/redfish/v1/SessionService",
    "@odata.type": "#SessionService.v1_1_2.SessionService",
    "Id": "SessionService",
    "Name": "SessionService",
    "Sessions": {
        "@odata.id": "/redfish/v1/SessionService/Sessions"
    },
    "ServiceEnabled": true
}

(redfish) http get /redfish/v1/SessionService/Sessions
[] http get: url (/redfish/v1/SessionService/Sessions)

[] URL        : /redfish/v1/SessionService/Sessions
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#SessionCollection.SessionCollection",
    "@odata.type": "#SessionCollection.SessionCollection",
    "@odata.id": "/redfish/v1/SessionService/Sessions",
    "Name": "Session Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/SessionService/Sessions/2"
        }
    ]
}

(redfish) http get /redfish/v1/SessionService/Sessions/2
[] http get: url (/redfish/v1/SessionService/Sessions/2)

[] URL        : /redfish/v1/SessionService/Sessions/2
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Session.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/2",
    "@odata.type": "#Session.v1_1_0.Session",
    "Id": "2",
    "Name": "User Session",
    "Description": "User Session",
    "UserName": "manage"
}
```

## <a name="section5">(5) Explore Systems</a>


## <a name="section6">(6) Explore Chassis</a>
## <a name="section7">(7) Explore Managers</a>
## <a name="section8">(8) Create A RAID Disk Group using StoragePool</a>
## <a name="section9">(9) Create A Volume</a>
## <a name="section10">(10) Expose A Volume Using Mapping and StorageGroups</a>
## <a name="section11">(11) Update A Volume</a>
## <a name="section12">(12) Delete A Volume</a>
## <a name="section13">(13) Delete A Pool using StoragePool</a>
