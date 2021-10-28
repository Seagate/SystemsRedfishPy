# Redfish Service v1 Tutorial

#### Copyright (c) 2020 Seagate Technology LLC and/or its Affiliates, All Rights Reserved

#### Version 1.0

## Introduction

***Redfish Service*** provides an implementation of the DMTF Redfish and SNIA Swordfish specifications. This is a REST-ful API that is 
accessed over HTTP or Secure HTTP. The interface uses a number of HTTP operations to perform Create, Read, Update, and Delete (CRUD) operations.
This service uses HTTP operations POST to Create, GET to Read, PATCH to Update, and DELETE to Delete. The main features of this service are to
review status of a storage system, provision and expose new storage volumes, and various features for storage system management. This tutorial
covers how these features are accomplished using the Redfish Service 1.0. 

Redfish Clients communicate with this Redfish Service using a variety of different tools including **curl**, DMTF provided validators like
**RedfishServiceValidator**, **Postman**, and Seagate provided python client called **SystemsRedfishPy**. This tutorial uses SystemsRedfishPy
to perform the HTTP operations needed to provision and manage a storage system. How to use SystemsRedfishPy is covered in separate documents
where this tutorial focuses on the Redfish interface and learning Redfish/Swordfish commands.

## Table of Contents
* [(1) Determine Redfish Version](#section1)
* [(2) Determine Redfish Services using Service Root](#section2)
* [(3) Create a Session](#section3)
* [(4) Show Active Sessions](#section4) 
* [(5) Explore Systems](#section5)
* [(6) Explore Chassis](#section6)
* [(7) Explore Managers](#section7)
* [(8) Create a RAID Disk Group using StoragePool](#section8)
* [(9) Create a Volume](#section9)
* [(10) Expose a Volume Using Mapping and StorageGroups](#section10)
* [(11) Update a Volume](#section11)
* [(12) Update Volume Mapping](#section12)
* [(13) Delete a StorageGroup or Unmap a Volume](#section13)
* [(14) Delete a Volume](#section14)
* [(15) Delete a Disk Group or Pool using StoragePool](#section15)
* [(16) Summary](#section16)


## <a name="section1">(1) Determine Redfish Version</a>

The root URI for Redfish is `/redfish`. An HTTP GET of this URI returns JSON data that contains the current version of the Redfish specification
supported by the service. 

**Note:** The SystemRedfishPy tool does not require the full URL. When a URI of **/redfish** is entered by the user, the tool uses a full URL
using tool configuration variables: **http** and **mcip**, From the (redfish) prompt enter `!dump` to see current settings . The protocol is determined by **http** and that value is used with **mcip** to form a full URL. For example, the user enters **/redfish**
but the tool performs a HTTP operation on **https://10.230.220.100/redfish**. This tutorial uses this shortened URI syntax.

Quick Start 

Create your own configuration file to store your desired settings. In this example, **myconfig.cfg** was chosen. The recomendation is to use
one config json file per storage array system so that you can quickly connect to multiple desired Redfish Services.

```
cp redfishAPI.cfg myconfig.cfg

SystemsRedfishPy> python --version
Python 3.7.4

SystemsRedfishPy> python redfishAPI.py -c myconfig.cfg

--------------------------------------------------------------------------------
[1.2.7] Redfish API
--------------------------------------------------------------------------------
[] Run Redfish API commands interactively...

(redfish) !certificatecheck False
(redfish) !http https
(redfish) !mcip <ipaddress>
(redfish) !password <password>
(redfish) !username <username>

(redfish) !dump
   >> configuration values:
      -- certificatecheck     : False
      -- http                 : https
      -- mcip                 : <ipaddress>
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

Another key piece of information from the Service Root is the **RedfishVersion** property. This is the version of the Redfish Service, not 
the version of the Redfish Specification. In this case, the Redfish Service is version **1.0.3**.

### Odata

The Redfish service publishes required ODATA 4.0 information through the URI /redfish/v1/odata.
```
(redfish) http get /redfish/v1/odata
[] http get: url (/redfish/v1/odata)

[] URL        : /redfish/v1/odata
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata",
    "value": [
        {
            "name": "Service",
            "kind": "Singleton",
            "url": "/redfish/v1/"
        },
        {
            "name": "Systems",
            "kind": "Singleton",
            "url": "/redfish/v1/ComputerSystem"
        },
        {
            "name": "Chassis",
            "kind": "Singleton",
            "url": "/redfish/v1/Chassis"
        },
        {
            "name": "Managers",
            "kind": "Singleton",
            "url": "/redfish/v1/Managers"
        },
        {
            "name": "TaskService",
            "kind": "Singleton",
            "url": "/redfish/v1/TaskService"
        },
        {
            "name": "SessionService",
            "kind": "Singleton",
            "url": "/redfish/v1/SessionService"
        },
        {
            "name": "Sessions",
            "kind": "Singleton",
            "url": "/redfish/v1/SessionService/Sessions"
        }
    ]
}
```
 
### Metadata

The Redfish service publishes required metadata information through the URI /redfish/v1/$metadata. The Redfish specification states
that XML must be returned for this URI. The data returned indicates which version of each schema is supported by this version of the service.

Schema data is also published online for both Redfish (**http://redfish.dmtf.org/schemas/v1/**) and Swordfish (**http://redfish.dmtf.org/schemas/swordfish/v1/**).
A user can review the JSON data for a schema to learn more about which properties are supported, correct spelling and case, brief description, and links to valid
enumeration values. 

```
(redfish) redfish metadata
Redfish Metadata
---------------------------------------------------------------------------------------------------------
<?xml version="1.0" ?>
<edmx:Edmx Version="4.0" xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx">
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ServiceRoot_v1.xml">
        <edmx:Include Namespace="ServiceRoot"/>
        <edmx:Include Namespace="ServiceRoot.v1_2_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/Capacity_v1.xml">
        <edmx:Include Namespace="Capacity"/>
        <edmx:Include Namespace="Capacity.v1_1_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Chassis_v1.xml">
        <edmx:Include Namespace="Chassis"/>
        <edmx:Include Namespace="Chassis.v1_9_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ChassisCollection_v1.xml">
        <edmx:Include Namespace="ChassisCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ComputerSystem_v1.xml">
        <edmx:Include Namespace="ComputerSystem"/>
        <edmx:Include Namespace="ComputerSystem.v1_6_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ComputerSystemCollection_v1.xml">
        <edmx:Include Namespace="ComputerSystemCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/ClassOfService_v1.xml">
        <edmx:Include Namespace="ClassOfService"/>
        <edmx:Include Namespace="ClassOfService.v1_1_1"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/ClassOfServiceCollection_v1.xml">
        <edmx:Include Namespace="ClassOfServiceCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/DataStorageLineOfService_v1.xml">
        <edmx:Include Namespace="DataStorageLineOfService"/>
        <edmx:Include Namespace="DataStorageLineOfService.v1_1_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/DataStorageLoSCapabilities_v1.xml">
        <edmx:Include Namespace="DataStorageLoSCapabilities"/>
        <edmx:Include Namespace="DataStorageLoSCapabilities.v1_0_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Drive_v1.xml">
        <edmx:Include Namespace="Drive"/>
        <edmx:Include Namespace="Drive.v1_5_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/DriveCollection_v1.xml">
        <edmx:Include Namespace="DriveCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Endpoint_v1.xml">
        <edmx:Include Namespace="Endpoint"/>
        <edmx:Include Namespace="Endpoint.v1_3_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EndpointCollection_v1.xml">
        <edmx:Include Namespace="EndpointCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/EndpointGroup_v1.xml">
        <edmx:Include Namespace="EndpointGroup"/>
        <edmx:Include Namespace="EndpointGroup.v1_1_3"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/EndpointGroupCollection_v1.xml">
        <edmx:Include Namespace="EndpointGroupCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EthernetInterface_v1.xml">
        <edmx:Include Namespace="EthernetInterface"/>
        <edmx:Include Namespace="EthernetInterface.v1_5_1"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EthernetInterfaceCollection_v1.xml">
        <edmx:Include Namespace="EthernetInterfaceCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/IOConnectivityLineOfService_v1.xml">
        <edmx:Include Namespace="IOConnectivityLineOfService"/>
        <edmx:Include Namespace="IOConnectivityLineOfService.v1_0_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/IOConnectivityLoSCapabilities_v1.xml">
        <edmx:Include Namespace="IOConnectivityLoSCapabilities"/>
        <edmx:Include Namespace="IOConnectivityLoSCapabilities.v1_0_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/LineOfService_v1.xml">
        <edmx:Include Namespace="LineOfService"/>
        <edmx:Include Namespace="LineOfService.v1_0_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Manager_v1.xml">
        <edmx:Include Namespace="Manager"/>
        <edmx:Include Namespace="Manager.v1_3_1"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ManagerCollection_v1.xml">
        <edmx:Include Namespace="ManagerCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Power_v1.xml">
        <edmx:Include Namespace="Power"/>
        <edmx:Include Namespace="Power.v1_5_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Redundancy_v1.xml">
        <edmx:Include Namespace="Redundancy"/>
        <edmx:Include Namespace="Redundancy.v1_1_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Session_v1.xml">
        <edmx:Include Namespace="Session"/>
        <edmx:Include Namespace="Session.v1_1_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SessionCollection_v1.xml">
        <edmx:Include Namespace="SessionCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SessionService_v1.xml">
        <edmx:Include Namespace="SessionService"/>
        <edmx:Include Namespace="SessionService.v1_1_2"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Storage_v1.xml">
        <edmx:Include Namespace="Storage"/>
        <edmx:Include Namespace="Storage.v1_6_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/StorageCollection_v1.xml">
        <edmx:Include Namespace="StorageCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageGroup_v1.xml">
        <edmx:Include Namespace="StorageGroup"/>
        <edmx:Include Namespace="StorageGroup.v1_2_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageGroupCollection_v1.xml">
        <edmx:Include Namespace="StorageGroupCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StoragePool_v1.xml">
        <edmx:Include Namespace="StoragePool"/>
        <edmx:Include Namespace="StoragePool.v1_2_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StoragePoolCollection_v1.xml">
        <edmx:Include Namespace="StoragePoolCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageService_v1.xml">
        <edmx:Include Namespace="StorageService"/>
        <edmx:Include Namespace="StorageService.v1_2_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageServiceCollection_v1.xml">
        <edmx:Include Namespace="StorageServiceCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/TaskService_v1.xml">
        <edmx:Include Namespace="TaskService"/>
        <edmx:Include Namespace="TaskService.v1_0_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Thermal_v1.xml">
        <edmx:Include Namespace="Thermal"/>
        <edmx:Include Namespace="Thermal.v1_5_1"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/VLanNetworkInterfaceCollection_v1.xml">
        <edmx:Include Namespace="VLanNetworkInterfaceCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/Volume_v1.xml">
        <edmx:Include Namespace="Volume"/>
        <edmx:Include Namespace="Volume.v1_4_0"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/VolumeCollection_v1.xml">
        <edmx:Include Namespace="VolumeCollection"/>
    </edmx:Reference>
    <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml">
        <edmx:Include Alias="Redfish" Namespace="RedfishExtensions.v1_0_0"/>
    </edmx:Reference>
    <edmx:DataServices>
        <Schema Namespace="Service" xmlns="http://docs.oasis-open.org/odata/ns/edm">
            <EntityContainer Extends="ServiceRoot.v1_2_0.ServiceContainer" Name="Service"/>
        </Schema>
    </edmx:DataServices>
</edmx:Edmx>
```


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

Once a session is created, it remains active for 30 minutes since the last executed command.

**Note:** An extra command is executed below so that the **X-Auth-Token** is stored for all future HTTP calls. The tool will automatically add the
token to all HTTP headers that require authentication. The `<session-hash>` should be replaced with the actual token returned, for example a value such as **bfe59eff3b71415853deaceb82612b7e**.


```
(redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "<username>", "Password": "<password>" }

[] http post: url (/redfish/v1/SessionService/Sessions)

[] URL          : /redfish/v1/SessionService/Sessions
[] Status       : 201
[] Reason       : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '274'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('X-Auth-Token', '<session-hash>')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Session.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/2",
    "@odata.type": "#Session.v1_1_0.Session",
    "Id": "2",
    "Name": "User Session",
    "Description": "User Session",
    "UserName": "<username>"
}

(redfish) save session 2 <session-hash>

[] Redfish session saved (2:<session-hash>)
```

Now that we have created a session, and saved the authentication key, we can access all other URIs.

### Example of HTTP Operation Failure

The following is an example of attempting to perform a Redfish operation before the client created a session.

```
(redfish) http get /redfish/v1/StorageServices/
[] http get: url (/redfish/v1/StorageServices/)

[] URL        : /redfish/v1/StorageServices/
[] Status     : 401
[] Reason     : Unauthorized

(redfish) create session

[] Redfish session established (2:<session-hash>)

(redfish) http get /redfish/v1/StorageServices/
[] http get: url (/redfish/v1/StorageServices/)

[] URL        : /redfish/v1/StorageServices/
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageServiceCollection.StorageServiceCollection",
    "@odata.type": "#StorageServiceCollection.StorageServiceCollection",
    "@odata.id": "/redfish/v1/StorageServices",
    "Name": "StorageService Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1"
        }
    ]
}
```

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

The ComputerSystem schema is used to display physical information about the system. A series of HTTP GET operations are
used to traverse through the system data. Information is provided for Ethernet Interfaces and Storage entities, plus shortcut
links to other physical resources.

* /redfish/v1/ComputerSystem
* /redfish/v1/ComputerSystem/{SystemId}
* /redfish/v1/ComputerSystem/{SystemId}/EthernetInterfaces
* /redfish/v1/ComputerSystem/{SystemId}/Storage
* /redfish/v1/ComputerSystem/{SystemId}/Links

```
(redfish) http get /redfish/v1/ComputerSystem
[] http get: url (/redfish/v1/ComputerSystem)

[] URL        : /redfish/v1/ComputerSystem
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.id": "/redfish/v1/ComputerSystem",
    "Name": "ComputerSystem Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5"
        }
    ]
}

(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5",
    "@odata.type": "#ComputerSystem.v1_6_0.ComputerSystem",
    "Id": "00C0FF437ED5",
    "Name": "Uninitialized Name",
    "Manufacturer": "Unknown",
    "SerialNumber": "00C0FF437ED5",
    "Status": {
        "Health": "OK"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage"
    },
    "Links": {
        "Chassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ],
        "Endpoints": [
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/A0"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/A1"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/B0"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/B1"
            }
        ]
    }
}
```

### Ethernet Interfaces

The EthernetInterfaces schema provides a collection of all Ethernet interfaces supported by this storage system.

```
(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces",
    "Name": "EthernetInterface Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/A"
        },
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/B"
        }
    ]
}

(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/A
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/A)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/A
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EthernetInterface.EthernetInterface",
    "@odata.type": "#EthernetInterface.v1_5_1.EthernetInterface",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/A",
    "Name": "Manager Ethernet Interface",
    "Id": "A",
    "InterfaceEnabled": true,
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PermanentMACAddress": "00:c0:ff:51:12:49",
    "IPv4Addresses": [
        {
            "Address": "10.235.221.171",
            "SubnetMask": "255.255.240.0",
            "Gateway": "10.235.208.1"
        }
    ]
}

(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/B
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/B)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/B
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EthernetInterface.EthernetInterface",
    "@odata.type": "#EthernetInterface.v1_5_1.EthernetInterface",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/EthernetInterfaces/B",
    "Name": "Manager Ethernet Interface",
    "Id": "B",
    "InterfaceEnabled": true,
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PermanentMACAddress": "00:c0:ff:51:12:54",
    "IPv4Addresses": [
        {
            "Address": "10.235.221.172",
            "SubnetMask": "255.255.240.0",
            "Gateway": "10.235.208.1"
        }
    ]
}
```

### Storage

The Storage schema provides information regarding the storage array controllers and redundancy information. It can also be used to view the collection
of storage volumes created on this storage array. The client can also learn which interface protocols are supported, such as SAS, iSCSI, or FC.

```
(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/Storage
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/Storage)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/Storage
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageCollection.StorageCollection",
    "@odata.type": "#StorageCollection.StorageCollection",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage",
    "Name": "Storage Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a"
        },
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b"
        }
    ]
}

(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a",
    "@odata.type": "#Storage.v1_6_0.Storage",
    "Name": "controller_a",
    "Id": "controller_a",
    "Status": {
        "Health": "OK"
    },
    "Volumes": {
        "@odata.id": "/redfish/v1/StorageServices/S1/Volumes"
    },
    "StorageControllers": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a#/StorageControllers/0",
            "Name": "controller_a",
            "Manufacturer": "Unknown",
            "SerialNumber": "00C0FF511249",
            "SupportedControllerProtocols": [
                "SAS"
            ],
            "Status": {
                "Health": "OK"
            },
            "MemberId": "0"
        }
    ],
    "Redundancy": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a#/Redundancy/0",
            "Name": "Controller Redundancy Group 1",
            "Mode": "Failover",
            "MaxNumSupported": 2,
            "MinNumNeeded": 1,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            "MemberId": "0",
            "RedundancySet": [
                {
                    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a"
                },
                {
                    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b"
                }
            ]
        }
    ],
    "Links": {
        "Enclosures": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    }
}

(redfish) http get /redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b
[] http get: url (/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b)

[] URL        : /redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b",
    "@odata.type": "#Storage.v1_6_0.Storage",
    "Name": "controller_b",
    "Id": "controller_b",
    "Status": {
        "Health": "OK"
    },
    "Volumes": {
        "@odata.id": "/redfish/v1/StorageServices/S1/Volumes"
    },
    "StorageControllers": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b#/StorageControllers/0",
            "Name": "controller_b",
            "Manufacturer": "Unknown",
            "SerialNumber": "00C0FF511254",
            "SupportedControllerProtocols": [
                "SAS"
            ],
            "Status": {
                "Health": "OK"
            },
            "MemberId": "1"
        }
    ],
    "Redundancy": [
        {
            "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b#/Redundancy/0",
            "Name": "Controller Redundancy Group 1",
            "Mode": "Failover",
            "MaxNumSupported": 2,
            "MinNumNeeded": 1,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            },
            "MemberId": "1",
            "RedundancySet": [
                {
                    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_a"
                },
                {
                    "@odata.id": "/redfish/v1/ComputerSystem/00C0FF437ED5/Storage/controller_b"
                }
            ]
        }
    ],
    "Links": {
        "Enclosures": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    }
}
```


## <a name="section6">(6) Explore Chassis</a>

The Chassis schema is used to display enclosure information about the system. A series of HTTP GET operations are
used to traverse through the physical data. Information is provided for Enclosures, Location, Thermal, Power, Drive links, and
other properties. 

* /redfish/v1/Chassis
* /redfish/v1/Chassis/{ChassisId}
* /redfish/v1/Chassis/{ChassisId}/Thermal
* /redfish/v1/Chassis/{ChassisId}/Power
* /redfish/v1/Chassis/{ChassisId}/Links/Drives

```
(redfish) http get /redfish/v1/Chassis
[] http get: url (/redfish/v1/Chassis)

[] URL        : /redfish/v1/Chassis
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ChassisCollection.ChassisCollection",
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "@odata.id": "/redfish/v1/Chassis",
    "Name": "Chassis Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0"
        }
    ]
}

(redfish) http get /redfish/v1/Chassis/enclosure_0
[] http get: url (/redfish/v1/Chassis/enclosure_0)

[] URL        : /redfish/v1/Chassis/enclosure_0
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0",
    "@odata.type": "#Chassis.v1_9_0.Chassis",
    "Id": "enclosure_0",
    "Name": "enclosure_0",
    "ChassisType": "StorageEnclosure",
    "Manufacturer": "Unknown",
    "SerialNumber": "500c0ff0437ed53c",
    "IndicatorLED": "Off",
    "PowerState": "On",
    "Location": {
        "Placement": {
            "Rack": "0",
            "RackOffset": 0
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal"
    },
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power"
    },
    "Links": {
        "Drives": [
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.0"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.1"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.2"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.3"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.4"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.5"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.6"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.7"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.8"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.9"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.10"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.11"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.12"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.13"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.14"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.15"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.16"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.17"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.18"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.19"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.20"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.21"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.22"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.23"
            }
        ]
    }
}
```

### Thermal

Review temperature and fan data for all sensors provided in the system.

```
(redfish) http get /redfish/v1/Chassis/enclosure_0/Thermal
[] http get: url (/redfish/v1/Chassis/enclosure_0/Thermal)

[] URL        : /redfish/v1/Chassis/enclosure_0/Thermal
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal",
    "@odata.type": "#Thermal.v1_5_1.Thermal",
    "Name": "Thermal",
    "Id": "Thermal",
    "Temperatures": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/0",
            "MemberId": "0",
            "Name": "sensor_temp_ctrl_A.1",
            "ReadingCelsius": 48.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/1",
            "MemberId": "1",
            "Name": "sensor_temp_ctrl_A.2",
            "ReadingCelsius": 46.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/2",
            "MemberId": "2",
            "Name": "sensor_temp_ctrl_A.3",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/3",
            "MemberId": "3",
            "Name": "sensor_temp_ctrl_A.4",
            "ReadingCelsius": 41.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/4",
            "MemberId": "4",
            "Name": "sensor_temp_ctrl_A.5",
            "ReadingCelsius": 71.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/5",
            "MemberId": "5",
            "Name": "sensor_temp_ctrl_A.6",
            "ReadingCelsius": 63.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/6",
            "MemberId": "6",
            "Name": "sensor_temp_iom_0.A.0",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/7",
            "MemberId": "7",
            "Name": "sensor_temp_ctrl_B.1",
            "ReadingCelsius": 48.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/8",
            "MemberId": "8",
            "Name": "sensor_temp_ctrl_B.2",
            "ReadingCelsius": 44.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/9",
            "MemberId": "9",
            "Name": "sensor_temp_ctrl_B.3",
            "ReadingCelsius": 36.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/10",
            "MemberId": "10",
            "Name": "sensor_temp_ctrl_B.4",
            "ReadingCelsius": 56.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/11",
            "MemberId": "11",
            "Name": "sensor_temp_ctrl_B.5",
            "ReadingCelsius": 82.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/12",
            "MemberId": "12",
            "Name": "sensor_temp_ctrl_B.6",
            "ReadingCelsius": 66.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/13",
            "MemberId": "13",
            "Name": "sensor_temp_iom_0.B.0",
            "ReadingCelsius": 38.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/14",
            "MemberId": "14",
            "Name": "sensor_temp_psu_0.0.0",
            "ReadingCelsius": 33.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/15",
            "MemberId": "15",
            "Name": "sensor_temp_psu_0.0.1",
            "ReadingCelsius": 35.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/16",
            "MemberId": "16",
            "Name": "sensor_temp_psu_0.1.0",
            "ReadingCelsius": 26.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/17",
            "MemberId": "17",
            "Name": "sensor_temp_psu_0.1.1",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/18",
            "MemberId": "18",
            "Name": "sensor_temp_encl_0.0",
            "ReadingCelsius": 36.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/19",
            "MemberId": "19",
            "Name": "sensor_temp_encl_0.1",
            "ReadingCelsius": 26.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/20",
            "MemberId": "20",
            "Name": "sensor_temp_disk_0.0",
            "ReadingCelsius": 29.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/21",
            "MemberId": "21",
            "Name": "sensor_temp_disk_0.1",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/22",
            "MemberId": "22",
            "Name": "sensor_temp_disk_0.2",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/23",
            "MemberId": "23",
            "Name": "sensor_temp_disk_0.3",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/24",
            "MemberId": "24",
            "Name": "sensor_temp_disk_0.4",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/25",
            "MemberId": "25",
            "Name": "sensor_temp_disk_0.5",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/26",
            "MemberId": "26",
            "Name": "sensor_temp_disk_0.6",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/27",
            "MemberId": "27",
            "Name": "sensor_temp_disk_0.7",
            "ReadingCelsius": 28.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/28",
            "MemberId": "28",
            "Name": "sensor_temp_disk_0.8",
            "ReadingCelsius": 29.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/29",
            "MemberId": "29",
            "Name": "sensor_temp_disk_0.9",
            "ReadingCelsius": 29.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/30",
            "MemberId": "30",
            "Name": "sensor_temp_disk_0.10",
            "ReadingCelsius": 29.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/31",
            "MemberId": "31",
            "Name": "sensor_temp_disk_0.11",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/32",
            "MemberId": "32",
            "Name": "sensor_temp_disk_0.12",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/33",
            "MemberId": "33",
            "Name": "sensor_temp_disk_0.13",
            "ReadingCelsius": 31.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/34",
            "MemberId": "34",
            "Name": "sensor_temp_disk_0.14",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/35",
            "MemberId": "35",
            "Name": "sensor_temp_disk_0.15",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/36",
            "MemberId": "36",
            "Name": "sensor_temp_disk_0.16",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/37",
            "MemberId": "37",
            "Name": "sensor_temp_disk_0.17",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/38",
            "MemberId": "38",
            "Name": "sensor_temp_disk_0.18",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/39",
            "MemberId": "39",
            "Name": "sensor_temp_disk_0.19",
            "ReadingCelsius": 30.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/40",
            "MemberId": "40",
            "Name": "sensor_temp_disk_0.20",
            "ReadingCelsius": 31.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/41",
            "MemberId": "41",
            "Name": "sensor_temp_disk_0.21",
            "ReadingCelsius": 32.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/42",
            "MemberId": "42",
            "Name": "sensor_temp_disk_0.22",
            "ReadingCelsius": 34.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/43",
            "MemberId": "43",
            "Name": "sensor_temp_disk_0.23",
            "ReadingCelsius": 36.0,
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        }
    ],
    "Fans": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/0",
            "MemberId": "0",
            "Reading": 7500,
            "Name": "Fan 0",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/1",
            "MemberId": "1",
            "Reading": 7320,
            "Name": "Fan 1",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/2",
            "MemberId": "2",
            "Reading": 7560,
            "Name": "Fan 2",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/3",
            "MemberId": "3",
            "Reading": 7440,
            "Name": "Fan 3",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        }
    ]
}
```

### Power

Review power supply and voltage data for the system.

```
(redfish) http get /redfish/v1/Chassis/enclosure_0/Power
[] http get: url (/redfish/v1/Chassis/enclosure_0/Power)

[] URL        : /redfish/v1/Chassis/enclosure_0/Power
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Power.Power",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power",
    "@odata.type": "#Power.v1_5_2.Power",
    "Id": "Power",
    "Name": "Power",
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/PowerSupplies/0",
            "MemberId": "0",
            "SerialNumber": "DHSIFTJ-18526G2X30",
            "PartNumber": "FRUKE16-01",
            "Name": "PSU 0, Left",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/PowerSupplies/1",
            "MemberId": "1",
            "SerialNumber": "DHSIFTJ-18526G2X4C",
            "PartNumber": "FRUKE16-01",
            "Name": "PSU 1, Right",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        }
    ],
    "Voltages": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/0",
            "MemberId": "0",
            "ReadingVolts": 10.74,
            "Name": "Capacitor Pack Voltage-Ctlr A",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/1",
            "MemberId": "1",
            "ReadingVolts": 2.69,
            "Name": "Capacitor Cell 1 Voltage-Ctlr A",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/2",
            "MemberId": "2",
            "ReadingVolts": 2.69,
            "Name": "Capacitor Cell 2 Voltage-Ctlr A",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/3",
            "MemberId": "3",
            "ReadingVolts": 2.69,
            "Name": "Capacitor Cell 3 Voltage-Ctlr A",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/4",
            "MemberId": "4",
            "ReadingVolts": 2.68,
            "Name": "Capacitor Cell 4 Voltage-Ctlr A",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/5",
            "MemberId": "5",
            "ReadingVolts": 10.79,
            "Name": "Capacitor Pack Voltage-Ctlr B",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/6",
            "MemberId": "6",
            "ReadingVolts": 2.7,
            "Name": "Capacitor Cell 1 Voltage-Ctlr B",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/7",
            "MemberId": "7",
            "ReadingVolts": 2.7,
            "Name": "Capacitor Cell 2 Voltage-Ctlr B",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/8",
            "MemberId": "8",
            "ReadingVolts": 2.7,
            "Name": "Capacitor Cell 3 Voltage-Ctlr B",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/9",
            "MemberId": "9",
            "ReadingVolts": 2.69,
            "Name": "Capacitor Cell 4 Voltage-Ctlr B",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/10",
            "MemberId": "10",
            "ReadingVolts": 12.22,
            "Name": "Voltage 12V Rail Loc: left-PSU",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/11",
            "MemberId": "11",
            "ReadingVolts": 4.96,
            "Name": "Voltage 5V Rail Loc: left-PSU",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/12",
            "MemberId": "12",
            "ReadingVolts": 12.18,
            "Name": "Voltage 12V Rail Loc: right-PSU",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/13",
            "MemberId": "13",
            "ReadingVolts": 4.96,
            "Name": "Voltage 5V Rail Loc: right-PSU",
            "Status": {
                "State": "Enabled",
                "Health": "OK"
            }
        }
    ]
}
```


## <a name="section7">(7) Explore Managers</a>

The Managers schema is used to display storage controller information for the system. A series of HTTP GET operations are
used to traverse through the data. Information is provided for Controllers, Firmware Version, Status, Ethernet Interfaces, and
other properties. 

* /redfish/v1/Managers
* /redfish/v1/Managers/{ManagerId}
* /redfish/v1/Managers/{ManagerId}/EthernetInterfaces
* /redfish/v1/Managers/{ManagerId}/Links/ManagerForChassis

```
(redfish) http get /redfish/v1/Managers
[] http get: url (/redfish/v1/Managers)

[] URL        : /redfish/v1/Managers
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'@odata.context': '/redfish/v1/$metadata#ManagerCollection.ManagerCollection', '@odata.type': '#ManagerCollection.ManagerCollection', '@odata.id': '/redfish/v1/Managers', 'Name': 'Manager Collection', 'Members@odata.count': 2, 'Members': [{'@odata.id': '/redfish/v1/Managers/controller_a'}, {'@odata.id': '/redfish/v1/Managers/controller_b'}]}
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ManagerCollection.ManagerCollection",
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "@odata.id": "/redfish/v1/Managers",
    "Name": "Manager Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/controller_a"
        },
        {
            "@odata.id": "/redfish/v1/Managers/controller_b"
        }
    ]
}

(redfish) http get /redfish/v1/Managers/controller_a
[] http get: url (/redfish/v1/Managers/controller_a)

[] URL        : /redfish/v1/Managers/controller_a
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'@odata.context': '/redfish/v1/$metadata#Manager.Manager', '@odata.id': '/redfish/v1/Managers/controller_a', '@odata.type': '#Manager.v1_3_1.Manager', 'Id': 'controller_a', 'Name': 'management_controller_a', 'ManagerType': 'ManagementController', 'FirmwareVersion': 'IN100B050e', 'Status': {'State': 'Enabled', 'Health': 'OK'}, 'EthernetInterfaces': {'@odata.id': '/redfish/v1/Managers/controller_a/EthernetInterfaces'}, 'Links': {'ManagerForChassis': [{'@odata.id': '/redfish/v1/Chassis/enclosure_0'}]}}
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
    "@odata.id": "/redfish/v1/Managers/controller_a",
    "@odata.type": "#Manager.v1_3_1.Manager",
    "Id": "controller_a",
    "Name": "management_controller_a",
    "ManagerType": "ManagementController",
    "FirmwareVersion": "IN100B050e",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces"
    },
    "Links": {
        "ManagerForChassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    }
}

(redfish) http get /redfish/v1/Managers/controller_b
[] http get: url (/redfish/v1/Managers/controller_b)

[] URL        : /redfish/v1/Managers/controller_b
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'@odata.context': '/redfish/v1/$metadata#Manager.Manager', '@odata.id': '/redfish/v1/Managers/controller_b', '@odata.type': '#Manager.v1_3_1.Manager', 'Id': 'controller_b', 'Name': 'management_controller_b', 'ManagerType': 'ManagementController', 'FirmwareVersion': 'IN100B050e', 'Status': {'State': 'Enabled', 'Health': 'OK'}, 'EthernetInterfaces': {'@odata.id': '/redfish/v1/Managers/controller_b/EthernetInterfaces'}, 'Links': {'ManagerForChassis': [{'@odata.id': '/redfish/v1/Chassis/enclosure_0'}]}}
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
    "@odata.id": "/redfish/v1/Managers/controller_b",
    "@odata.type": "#Manager.v1_3_1.Manager",
    "Id": "controller_b",
    "Name": "management_controller_b",
    "ManagerType": "ManagementController",
    "FirmwareVersion": "IN100B050e",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/controller_b/EthernetInterfaces"
    },
    "Links": {
        "ManagerForChassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    }
}
```

### Ethernet Interfaces

Review Ethernet intrface details like the MAC address and IPv4 addresses.

```
(redfish) http get /redfish/v1/Managers/controller_a/EthernetInterfaces
[] http get: url (/redfish/v1/Managers/controller_a/EthernetInterfaces)

[] URL        : /redfish/v1/Managers/controller_a/EthernetInterfaces
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces",
    "Name": "EthernetInterface Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces/A"
        }
    ]
}

(redfish) http get /redfish/v1/Managers/controller_a/EthernetInterfaces/A
[] http get: url (/redfish/v1/Managers/controller_a/EthernetInterfaces/A)

[] URL        : /redfish/v1/Managers/controller_a/EthernetInterfaces/A
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EthernetInterface.EthernetInterface",
    "@odata.type": "#EthernetInterface.v1_5_1.EthernetInterface",
    "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces/A",
    "Name": "Manager Ethernet Interface",
    "Id": "A",
    "InterfaceEnabled": true,
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "PermanentMACAddress": "00:c0:ff:51:12:49",
    "IPv4Addresses": [
        {
            "Address": "10.235.221.171",
            "SubnetMask": "255.255.240.0",
            "Gateway": "10.235.208.1"
        }
    ]
}
```


## <a name="section8">(8) Create a RAID Disk Group using StoragePool</a>

A new RAID disk group is created using the Swordfish StoragePool entity and a HTTP POST operation. The operation must include a 
number of properties used to create the disk group. Follow these steps to obtain required information first.

1. Determine the URI of the RAID level for the disk group.
2. Determine the URIs of all Drives to be included in the disk group.
3. Decide whether this is for Pool A or Pool B.
4. Decide on a Name for the disk group.

### Step 1. Show RAID Levels

```
(redfish) http get /redfish/v1/StorageServices/S1/ClassesOfService
[] http get: url (/redfish/v1/StorageServices/S1/ClassesOfService)

[] URL        : /redfish/v1/StorageServices/S1/ClassesOfService
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#ClassOfServiceCollection.ClassOfServiceCollection",
    "@odata.type": "#ClassOfServiceCollection.ClassOfServiceCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService",
    "Name": "ClassOfService Collection",
    "Members@odata.count": 7,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/NRAID"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID5"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID6"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID10"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/ADAPT"
        }
    ]
}
```

### Step 2. Show Drives

```
(redfish) http get /redfish/v1/StorageServices/S1/Drives
[] http get: url (/redfish/v1/StorageServices/S1/Drives)

[] URL        : /redfish/v1/StorageServices/S1/Drives
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
    "@odata.type": "#DriveCollection.DriveCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Drives",
    "Name": "Drive Collection",
    "Members@odata.count": 24,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.2"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.3"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.4"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.5"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.6"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.7"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.8"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.9"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.10"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.11"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.12"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.13"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.14"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.15"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.16"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.17"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.18"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.19"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.20"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.21"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.22"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.23"
        }
    ]
}
```

### Step 3. Create JSON Data used for POST Operation

Here are the properties that are used to create a new disk group. **Note** that when you create the first disk group, a pool will be automatically created if
one does not already exist.

| Property         | Mandatory | Description |
| ---------------- | --------- | ----------- |
| Name             | No        | The name that will be assigned to this storage group. |
| CapacitySources  | Yes       | This is a data structure containing the property **Providing Drives** and then a list of drives that will be used to create the resource. |
| AllocatedPools   | No        | This is a data structure containing the property **Members** and a list of StoragePools. The new disk group will be added to the indicated storage pool |
| ClassesOfService | Yes       | This provides the class of service, such as RAID1, RAID6, etc. that will be used to create the new storage group. |

For this operation, the JSON data needed for the operation is stored in a text file called **create_diskgroup.json**. See below.

```
{
    "Name": "dgA01",
    "CapacitySources": {
        "ProvidingDrives": [
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.0"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.1"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.2"
            },
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.3"
            }
        ]
    },
    "AllocatedPools": {
        "Members": [
            {
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
            }
        ]
    },
    "ClassesOfService": {
        "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID5"
    }
}
```

Now create a disk group named **dgA01**. These steps can be repeated to create as many disk groups as desired. After creating a disk group,
use the HTTP GET operation on the StoragePool collection to view all existing disk groups and storage pools. We will also perform an HTTP GET on
the new disk group and pool to see the details of each.

**Note:** The **Description** property is used to differentiate between a **DiskGroup** and a **Pool**. See below in the JSON data returned.

```
(redfish) http post /redfish/v1/StorageServices/S1/StoragePools json\create_diskgroup.json
[] http post: url (/redfish/v1/StorageServices/S1/StoragePools)

[] URL          : /redfish/v1/StorageServices/S1/StoragePools
[] Status       : 204
[] Reason       : No Content


(redfish) http get /redfish/v1/StorageServices/S1/StoragePools
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
    "Name": "StoragePool Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePool.StoragePool",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000",
    "@odata.type": "#StoragePool.v1_2_0.StoragePool",
    "Id": "00c0ff51124900007d88315f00000000",
    "Name": "dgA01",
    "Description": "DiskGroup",
    "MaxBlockSizeBytes": 512,
    "AllocatedVolumes": {
        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000/Volumes"
    },
    "RemainingCapacityPercent": 0,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 1798177816576,
            "ConsumedBytes": 1798177816576
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "DefaultClassOfService": {
        "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService/RAID5"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900007d88315f00000000",
            "Name": "dgA01",
            "ProvidingDrives": {
                "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/Drives",
                "@odata.type": "#DriveCollection.DriveCollection",
                "Name": "Drives",
                "Members@odata.count": 4,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.0"
                    },
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.1"
                    },
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.2"
                    },
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/Drives/0.3"
                    }
                ]
            }
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/StoragePools/A
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools/A)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools/A
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePool.StoragePool",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A",
    "@odata.type": "#StoragePool.v1_2_0.StoragePool",
    "Id": "00c0ff51124900007f88315f01000000",
    "Name": "A",
    "Description": "Pool",
    "MaxBlockSizeBytes": 512,
    "AllocatedVolumes": {
        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A/Volumes"
    },
    "AllocatedPools": {
        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools"
    },
    "RemainingCapacityPercent": 99,
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "ReadIORequestTime": "0",
        "WriteHitIORequests": 154,
        "WriteIOKiBytes": 351889,
        "WriteIORequestTime": "0"
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 1780997947392,
            "ConsumedBytes": 8388608
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900007f88315f01000000",
            "Name": "A",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Name": "StoragePools",
                "Members@odata.count": 1,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900007d88315f00000000"
                    }
                ]
            }
        }
    ]
}
```


## <a name="section9">(9) Create a Volume</a>

A Volume is created using the Redfish/Swordfish Volume entity and a HTTP POST operation. The operation must include a 
number of properties used to create the volume. Here are the properties that are used to create a volume.

| Property         | Mandatory | Description |
| ---------------- | --------- | ----------- |
| Name             | No        | The name that will be assigned to the volume. |
| CapacityBytes    | No        | The size in bytes of the desired volume. |
| CapacitySources  | Yes       | This is a data structure with an **@odata.id** value pointing to the desired **StoragePool**. |
| Links            | No        | This is a data structure containing the property **ClassOfService** with an @odata.id value pointing to the desired class of service. |

For this operation, the JSON data needed for the operation is stored in a text file called **create_volume.json**. See below.

```
{
    "Name": "AVolume01",
    "CapacityBytes": 100000000000,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
        }
    ],
    "Links": {
        "ClassOfService": {
            "@odata.id": "/redfish/v1/StorageServices/S1/ClassesOfService(Default)"
        }
    }
}
```

Now create a volume named **AVolume01**. These steps can be repeated to create as many volumes as desired. After creating a volume,
use the HTTP GET operation on the Volume collection to view all existing volumes. We will also perform an HTTP GET on the new volume
to see the details.

For this operation, the Redfish service returns an HTTP status of **201/Created** and a JSON representation of the new volume.

**Note:** The volume is not visible to a host until a StorageGroup is created to map the volume to EndpointGroups. See the next step.

```
(redfish) http post /redfish/v1/StorageServices/S1/Volumes json\create_volume.json
[] http post: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL          : /redfish/v1/StorageServices/S1/Volumes
[] Status       : 201
[] Reason       : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1705'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/AVolume01",
    "@odata.type": "#Volume.v1_4_0.Volume",
    "Id": "00c0ff51124900006189325f01000000",
    "Name": "AVolume01",
    "BlockSizeBytes": 512,
    "CapacityBytes": 99996401664,
    "RemainingCapacityPercent": 99,
    "Encrypted": true,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 99996401664,
            "ConsumedBytes": 0
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/AVolume01#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900006189325f01000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Name": "StoragePools",
                "Members@odata.count": 1,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
                    }
                ]
            }
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/Volumes
[] http get: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL        : /redfish/v1/StorageServices/S1/Volumes
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes",
    "Name": "Volume Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000
[] http get: url (/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000)

[] URL        : /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000",
    "@odata.type": "#Volume.v1_4_0.Volume",
    "Id": "00c0ff51124900006189325f01000000",
    "Name": "AVolume01",
    "BlockSizeBytes": 512,
    "CapacityBytes": 99996401664,
    "RemainingCapacityPercent": 99,
    "Encrypted": true,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 99996401664,
            "ConsumedBytes": 0
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900006189325f01000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Name": "StoragePools",
                "Members@odata.count": 1,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
                    }
                ]
            }
        }
    ]
}
```


## <a name="section10">(10) Expose a Volume Using Mapping and StorageGroups</a>

A StorageGroup is a Swordfish entity used to link a Volume to ServerEndpoints (ports) and a ClientEndpoints (initiators). A LogicalUnitNumber (LUN) 
can also be tied to a StorageGroup where applicable. Create and manage StorageGroups as a way to expose a Volume to one or more host systems.

**Note:** This service restricts a StorageGroup to map a single volume to a single initiator. Multiple storage groups can be created to create additional mappings.
 
 Here are the properties that are used to create a StorageGroup.

| Property              | Mandatory | Description |
| --------------------- | --------- | ----------- |
| LogicalUnitNumber     | Yes       | Specify the LUN to be used for mapping the volume. This property is part of the **MappedVolumes** JSON array. **Note:** This revision requires that this value be a string. |
| Volume                | Yes       | This specifies the Volume URI to be used for the mapping. This property is part of the **MappedVolumes** JSON array. |
| ClientEndpointGroups  | Yes       | A host initiator must be specified. Provide a list of one initiator group to use in the volume mapping. |
| ServerEndpointGroups  | No        | Provide a list of one or more storage port groups to use in the volume mapping. If no port is provided, the volume will be mapped to all available ports. |
| AccessCapabilities    | No        | This is a JSON array of strings to specify read only or read-write access to the volume. Valid choices are **Read** and **Write**. If this parameter is omitted, the volume will default to Read,Write accessibility. |

For this operation, the JSON data needed for the operation is stored in a text file called **create_storagegroup.json**. See below.

```
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B1"
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070"
        }
    ],
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "1",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/AVolume01"
            }
        }
    ]
}
```

### Step 1. Show EndpointGroups

Use HTTP GET operations to determine which EndpointGroups you want to use to create your StorageGroup.

```
(redfish) http get /redfish/v1/StorageServices/S1/EndpointGroups/
[] http get: url (/redfish/v1/StorageServices/S1/EndpointGroups/)

[] URL        : /redfish/v1/StorageServices/S1/EndpointGroups/
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EndpointGroupCollection.EndpointGroupCollection",
    "@odata.type": "#EndpointGroupCollection.EndpointGroupCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups",
    "Name": "EndpointGroup Collection",
    "Members@odata.count": 10,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a070"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/0000111122223333"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/4444555566667777"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a071"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/HG1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/hg1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B1"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/EndpointGroups/A0
[] http get: url (/redfish/v1/StorageServices/S1/EndpointGroups/A0)

[] URL        : /redfish/v1/StorageServices/S1/EndpointGroups/A0
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EndpointGroup.EndpointGroup",
    "@odata.type": "#EndpointGroup.v1_1_3.EndpointGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0",
    "Name": "SEG_A0",
    "Id": "A0",
    "GroupType": "Server",
    "Description": "Collection of server endpoints for A0",
    "Members@odata.count": 1,
    "Endpoints": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/A0"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/Endpoints/A0
[] http get: url (/redfish/v1/StorageServices/S1/Endpoints/A0)

[] URL        : /redfish/v1/StorageServices/S1/Endpoints/A0
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Endpoint.Endpoint",
    "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/A0",
    "@odata.type": "#Endpoint.v1_3_0.Endpoint",
    "Name": "A0",
    "Description": "This instance represents a port",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Identifiers": [
        {
            "DurableName": "A0",
            "DurableNameFormat": "NAA"
        }
    ],
    "Id": "A0"
}

(redfish) http get /redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a070
[] http get: url (/redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a070)

[] URL        : /redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a070
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#EndpointGroup.EndpointGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00db9a070",
    "@odata.type": "#EndpointGroup.v1_1_3.EndpointGroup",
    "Name": "CEG_500605b00db9a070",
    "Id": "500605b00db9a070",
    "GroupType": "Client",
    "Description": "Collection of client endpoints for 500605b00db9a070",
    "Endpoints": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070
[] http get: url (/redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070)

[] URL        : /redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Endpoint.Endpoint",
    "@odata.id": "/redfish/v1/StorageServices/S1/Endpoints/500605b00db9a070",
    "@odata.type": "#Endpoint.v1_3_0.Endpoint",
    "Name": "SAS-port1",
    "Description": "This instance represents an initiator",
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "Identifiers": [
        {
            "DurableName": "500605b00db9a070",
            "DurableNameFormat": "NAA"
        }
    ],
    "Id": "500605b00db9a070"
}
```

### Step 2. Show Volumes

Use HTTP GET operations to determine which Volume you want to use to create your StorageGroup.

```
(redfish) http get /redfish/v1/StorageServices/S1/Volumes
[] http get: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL        : /redfish/v1/StorageServices/S1/Volumes
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes",
    "Name": "Volume Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
        }
    ]
}
```

### Step 3. Create a StorageGroup

Now create the StorageGroup. These steps can be repeated to create multiple StorageGroups to map multiple volumes. After creating a StorageGroup,
use the HTTP GET operation on the collection to view all existing groups. We will also perform an HTTP GET on the new StorageGroup
to see the details.

```
(redfish) http post /redfish/v1/StorageServices/S1/StorageGroups json\create_storagegroup.json
[] http post: url (/redfish/v1/StorageServices/S1/StorageGroups)

[] URL          : /redfish/v1/StorageServices/S1/StorageGroups
[] Status       : 201
[] Reason       : Created

(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups",
    "Name": "StorageGroup Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000"
        }
    ]
}

(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "AVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "1",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B1"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}
```


## <a name="section11">(11) Update a Volume</a>

You can update a Volume using an HTTP PATCH operation. In the JSON data passed to the Redfish Service, include a new name
such as: **{ "Name": "NewAVolume01" }**. The new name will be visible in the returned JSOIN data.

```
(redfish) http get /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000
[] http get: url (/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000)

[] URL        : /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000",
    "@odata.type": "#Volume.v1_4_0.Volume",
    "Id": "00c0ff51124900006189325f01000000",
    "Name": "AVolume01",
    "BlockSizeBytes": 512,
    "CapacityBytes": 99996401664,
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "RemainingCapacityPercent": 99,
    "Encrypted": true,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 99996401664,
            "ConsumedBytes": 0
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900006189325f01000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Name": "StoragePools",
                "Members@odata.count": 1,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
                    }
                ]
            }
        }
    ]
}

(redfish) http patch /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000 { "Name": "NewAVolume01" }
[] http patch: url (/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000)

[] URL          : /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000
[] Status       : 200
[] Reason       : OK
[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000",
    "@odata.type": "#Volume.v1_4_0.Volume",
    "Id": "00c0ff51124900006189325f01000000",
    "Name": "NewAVolume01",
    "BlockSizeBytes": 512,
    "CapacityBytes": 99996401664,
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "RemainingCapacityPercent": 99,
    "Encrypted": true,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 99996401664,
            "ConsumedBytes": 0
        }
    },
    "Status": {
        "State": "Enabled",
        "Health": "OK"
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_1_2.CapacitySource",
            "Id": "00c0ff51124900006189325f01000000",
            "Name": "NewAVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Name": "StoragePools",
                "Members@odata.count": 1,
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
                    }
                ]
            }
        }
    ]
}
```

## <a name="section12">(12) Update Volume Mapping</a>

There are a number of actions that can be performed on a StorageGroup to update the mapping of a volume.

### Change Logical Unit Number (LUN)

Perform a HTTP PATCH on a StorageGroup URI passing a new LogicalUnitNumber to update the LUN of the StorageGroup. The JSON response
data will contain the same data as a GET /redfish/v1/StorageServices/S1/StorageGroups/{StorageGroupId}. In this example, the LUN is changed
from **1** to *111* as is seen in the JSON data below.

**Note:** This revision requires that LogicalUnitNumber be a string.

For this operation, the JSON data needed for the operation is stored in a text file called **patch_storagegroup_lun.json**. See below.

```
{
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111"
        }
    ]
}
```

Now perform the PATCH operaiton.

```
(redfish) http patch /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000 json\patch_storagegroup_lun.json
[] http patch: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL          : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status       : 200
[] Reason       : OK
[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "AVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B1"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}
```

### Change Ports

Perform a PATCH on a StorageGroup URI passing an array of ServerEndpointGroups to update the ports of the StorageGroup. For this operation, 
the JSON data needed for the operation is stored in a text file called **patch_storagegroup_ports.json**. See below.

```
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        }
    ]
}
```

Now perform the PATCH operaiton after getting the current details of the StorageGroup. Notice how the property **ServerEndpointGroups** has
been updated to contain only two ports.

```
(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "NewAVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B1"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}

(redfish) http patch /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000 json\patch_storagegroup_ports.json
[] http patch: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL          : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status       : 200
[] Reason       : OK
[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "NewAVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}
```

### Change Access

Perform a PATCH on a StorageGroup URI passing a new AccessCapabilities to update the access capabilities of the StorageGroup. 
The JSON response data will contain the same data as a GET /redfish/v1/StorageServices/S1/StorageGroups/{StorageGroupId}.

For this operation, the JSON data needed for the operation is stored in a text file called **patch_storagegroup_access.json**. See below.

```
{
    "AccessCapabilities": [
        "Read"
    ]
}
```

Now perform the PATCH operaiton after getting the current details of the StorageGroup. Notice how the property **AccessCapabilities** has
been updated to be read-only.

```
(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "NewAVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}

(redfish) http patch /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000 json\patch_storagegroup_access.json
[] http patch: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL          : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status       : 200
[] Reason       : OK
[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "@odata.type": "#StorageGroup.v1_2_0.StorageGroup",
    "Description": "Mapping Information",
    "Id": "00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000",
    "Name": "NewAVolume01_00c0ff51124900007db6945e01010000",
    "AccessCapabilities": [
        "Read"
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900006189325f01000000"
            }
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/00c0ff51124900007db6945e01010000"
        }
    ],
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/B0"
        }
    ],
    "AccessState": "Optimized",
    "Status": {
        "State": "Enabled",
        "Health": "OK",
        "HealthRollup": "OK"
    },
    "MembersAreConsistent": true,
    "VolumesAreExposed": true
}
```


## <a name="section13">(13) Delete a StorageGroup or Unmap a Volume</a>

The HTTP DELETE request is used to delete a StorageGroup. You delete a StorageGroup by using its identifier. No request properties
are specified in the request body, simply use the correct URI. Use GET **/redfish/v1/StorageServices/S1/StorageGroups** to view the
identifiers and URIs of all existing StorageGroups.

Note: After deleting a StorageGroup, that volume will no longer be visible to any host system.

```
(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups/
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups/)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups",
    "Name": "StorageGroup Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000"
        }
    ]
}

(redfish) http delete /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] http delete: url (/redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/00c0ff51124900006189325f01000000_00c0ff51124900007db6945e01010000
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully.'}}

(redfish) http get /redfish/v1/StorageServices/S1/StorageGroups/
[] http get: url (/redfish/v1/StorageServices/S1/StorageGroups/)

[] URL        : /redfish/v1/StorageServices/S1/StorageGroups/
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StorageGroups",
    "Name": "StorageGroup Collection",
    "Members@odata.count": 0,
    "Members": []
}
```


## <a name="section14">(14) Delete a Volume</a>

Use the Volume entity and HTTP DELETE operation to delete a volume. A list of current volumes should be used to obtain the full URI to the volume
that you want to delete. After you delete the volume, use HTTP GET on Volumes to verify that the volume is no longer reported.

```
(redfish) http get /redfish/v1/StorageServices/S1/Volumes
[] http get: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL        : /redfish/v1/StorageServices/S1/Volumes
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes",
    "Name": "Volume Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900000f68195f01000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900001568195f01000000"
        }
    ]
}

(redfish) http delete /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900001568195f01000000
[] http delete: url (/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900001568195f01000000)

[] URL        : /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900001568195f01000000
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully.'}}

(redfish) http get /redfish/v1/StorageServices/S1/Volumes
[] http get: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL        : /redfish/v1/StorageServices/S1/Volumes
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes",
    "Name": "Volume Collection",
    "Members@odata.count": 1,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900000f68195f01000000"
        }
    ]
}

(redfish) http delete /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900000f68195f01000000
[] http delete: url (/redfish/v1/StorageServices/S1/Volumes/00c0ff51124900000f68195f01000000)

[] URL        : /redfish/v1/StorageServices/S1/Volumes/00c0ff51124900000f68195f01000000
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully.'}}

(redfish) http get /redfish/v1/StorageServices/S1/Volumes
[] http get: url (/redfish/v1/StorageServices/S1/Volumes)

[] URL        : /redfish/v1/StorageServices/S1/Volumes
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/Volumes",
    "Name": "Volume Collection",
    "Members@odata.count": 0,
    "Members": []
}
```

## <a name="section15">(15) Delete a Disk Group or Pool using StoragePool</a>

Use the StoragePool entity and HTTP DELETE operation to delete a disk group or pool. A list of current StoragePools should be used to obtain the 
full URI to the disk group or pool that you want to delete. After you delete the entity, use HTTP GET on StoragePools to verify that the entity
is no longer reported.

**Note:*** When you delete a pool, all disk groups will be automatically deleted.

```
(redfish) http get /redfish/v1/StorageServices/S1/StoragePools
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
    "Name": "StoragePool Collection",
    "Members@odata.count": 4,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff5112490000d767195f00000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff5112490000f067195f00000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900000768195f00000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
        }
    ]
}

(redfish) http delete /redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900000768195f00000000
[] http delete: url (/redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900000768195f00000000)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools/00c0ff51124900000768195f00000000
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully.'}}

(redfish) http get /redfish/v1/StorageServices/S1/StoragePools
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
    "Name": "StoragePool Collection",
    "Members@odata.count": 2,
    "Members": [
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/00c0ff5112490000f067195f00000000"
        },
        {
            "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools/A"
        }
    ]
}

(redfish) http delete /redfish/v1/StorageServices/S1/StoragePools/A
[] http delete: url (/redfish/v1/StorageServices/S1/StoragePools/A)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools/A
[] Status     : 200
[] Reason     : OK
[] HTTP Data  : {'error': {'code': 'Base.1.0.GeneralError', 'message': '0: Command completed successfully.'}}

(redfish) http get /redfish/v1/StorageServices/S1/StoragePools
[] http get: url (/redfish/v1/StorageServices/S1/StoragePools)

[] URL        : /redfish/v1/StorageServices/S1/StoragePools
[] Status     : 200
[] Reason     : OK
[] JSON Data  : {
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/StorageServices/S1/StoragePools",
    "Name": "StoragePool Collection",
    "Members@odata.count": 0,
    "Members": []
}
```


## <a name="section16">(16) Summary</a>

Hopefully this tutorial increased your understanding of how to use the Redfish Service to manage a storage system.
