# Redfish Service Tutorial v2.x.x

#### Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates, All Rights Reserved

#### Version 2.x.x

## Introduction

***Redfish Service*** provides an implementation of the DMTF Redfish and SNIA Swordfish specifications. This is a RESTful API that is 
accessed over Secure HTTP. The interface uses a number of HTTP operations to perform Create, Read, Update, and Delete (CRUD) operations.
This service uses HTTP operations POST to Create, GET to Read, PATCH to Update, and DELETE to Delete. The main features of this service are to
review status of a storage system, provision and expose new storage volumes, compose volumes, and various features for storage system
management. This tutorial covers how these features are accomplished using the Redfish Service 2.0. 

Redfish Clients communicate with this Redfish Service using a variety of different tools including **curl**, DMTF provided validators like
**RedfishServiceValidator**, **Postman**, and Seagate provided python client called **SystemsRedfishPy**. This tutorial uses SystemsRedfishPy
to perform the HTTP operations needed to provision and manage a storage system. How to use SystemsRedfishPy is covered in separate documents
where this tutorial focuses on the Redfish interface and learning Redfish/Swordfish commands.


## Table of Contents
* [Redfish Service 1.0 vs 2.0](#section0)
* [(1) Determine Redfish Version](#section1)
* [(2) Determine Redfish Services using Service Root](#section2)
* [(3) Create a Session](#section3)
* [(4) Show Active Sessions](#section4) 
* [(5) Explore Systems and Storage](#section5)
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

* [(16) Toggle Drive Identification LED](#section16)
* [(17) Enable|Disable Background Scrub](#section17)
* [(18) Toggle Write-back/Write-through Capability](#section18)
* [(19) Create Account](#section19)
* [(20) Change Account Password](#section20)
* [(21) Show Fabrics](#section21)
* [(22) Compose Volume](#section22)
* [(23) Update Controller Firmware](#section23)
* [(24) Reboot Controller](#section24)
* [(25) Get Controller Logs](#section25)
* [(26) Get Drive Logs](#section26)
* [(27) Task Service](#section27)
* [(28) Create Volume Snapshot](#section28)
* [(29) Event Service](#section29)
* [(30) Summary](#section30)

[//]: <> (================================================================================================================================================================)
## <a name="section0">Redfish Service 1.0 vs 2.0</a>
[//]: <> (================================================================================================================================================================)

This is a Redfish Service version number, not to be confused with **/redfish/v1** versioning. Redfish Service 1.0.0 was delivered in 2019-2020 and
Redfish Service 2.0.0 will be available in 2021-2022 time frame. A quick way to determine the current version of the Redfish Service running on a
Seagate System Storage Array is to execute the following command `curl -sk https://<ip>/redfish/v1 | grep RedfishServiceVersion` where `<ip>` is
replaced with the 4 byte, dot notation, IPv4 IP address.

```
$ curl -k https://10.230.220.100/redfish/v1 | grep RedfishServiceVersion
            "RedfishServiceVersion": "2.4.20"
```

| Version | URI Notes                                                              |
| :------- | :---------------------------------------------------------------------- |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**AccountService**/ |
| Notes   | New feature for creating, listing, and updating Accounts |
| | |
| 1.0     | /redfish/v1/**ComputerSystems**/ |
| 2.0     | /redfish/v1/**Systems**/ |
| Notes   | Redfish Resource and Schema Guide – DSP2046_2020.3, this URI should be listed as Systems and not ComputerSystems |
| | |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**CompositionService**/ |
| Notes   | New feature for composing volumes, includes ResourceBlocks and ResourceZones |
| | |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**Fabrics**/ |
| Notes   | New feature for exploring Fabrics and Endpoints |
| | |
| 1.0     | /redfish/v1/**StorageServices** |
| 2.0     | (none) |
| Notes   | Removed including ClassesOfService, DataStorageLoSCapabilities, DataStorageLineOfService, IOConnectivityLineOfService, and IOConnectivityLoSCapabilities |
| | |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**Storage** |
| Notes   | New access to **Drives**, **EndpointGroups**, **StorageGroups**, **StoragePools**, and **Volumes** |
| | |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**TaskService** |
| Notes   | New service for monitoring long running tasks and creating Volume snapshots |
| | |
| 1.0     | (none) |
| 2.0     | /redfish/v1/**UpdateService** |
| Notes   | New service for uploading firmware bundles |
| | |
| 1.0     | /redfish/v1/Managers/controller_a/EthernetInterfaces/A |
| 2.0     | /redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated |
| Notes   | New entity |
| | |
| 1.0     | /redfish/v1/Managers/controller_b/EthernetInterfaces/B |
| 2.0     | /redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated |
| Notes   | New entity |

In addition to the new features listed in the previous table, this version also supports a number of other features:
- RedfishServiceVersion
- Toggle Drive Identification LED
- Enable|Disable Background Scrub
- Toggle Write-back/Write-through Capability
- Reboot Controller
- Get Controller Logs
- Get Drive Logs
- Create Volume Snapshot


[//]: <> (================================================================================================================================================================)
## <a name="section1">(1) Determine Redfish Version</a>
[//]: <> (================================================================================================================================================================)

The root URI for Redfish is `/redfish`. An HTTP GET of this URI returns JSON data that contains the current version of the Redfish specification
supported by the service. 

**Note:** The SystemRedfishPy tool does not require the full URL. When a URI of **/redfish** is entered by the user, the tool uses a full URL
using tool configuration variables: **http** and **ipaddress**, From the (redfish) prompt enter `!dump` to see current settings . The protocol (http|https)
is determined by **http** and that value is used with **ipaddress** to form a full URL. For example, the user enters **/redfish**
but the tool performs a HTTP operation on **https://10.230.220.100/redfish**. This tutorial uses this shortened URI syntax.

**Quick Start**

Create your own configuration file to store your desired settings. In this example, **myconfig.cfg** was chosen. The recommendation is to use
one config json file per storage array system so that you can quickly connect to multiple desired Redfish Services.

**Note:** The SystemRedfishPy tool depends on Python 3. and also requires Python packages as listed in [requirements.txt](requirements.txt).


```
cp redfishAPI.cfg myconfig.cfg

SystemsRedfishPy> python3 --version
Python 3.8.10

SystemsRedfishPy> python3 redfishAPI.py -c myconfig.cfg

--------------------------------------------------------------------------------
[2.2.2] Redfish API
--------------------------------------------------------------------------------
-- TraceLevel [4] INFO
-- Reading history (redfishAPI.hist) [1050]
[] Run Redfish API commands interactively...

(redfish) !certificatecheck False
(redfish) !http https
(redfish) !ipaddress <ipaddress>
(redfish) !password <password>
(redfish) !username <username>

(redfish) !dump
   >> configuration values:
   ...
   -- certificatecheck     : False              True|False  When False, the URL will be opened using context=ssl._create_unverified_context. Default is False.
   -- http                 : https              http|https  Switch between use http:// and https://. Default is https.
   -- ipaddress            : 10.230.220.100     <string>    Change all HTTP communications to use this new IP address.
   -- password             : <password>         <string>    Change the password to [password] that is used to log in to the Redfish Service.
   -- username             : <username>         <string>    Change the username to [name] that is used to log in to the Redfish Service.


(redfish) http get /redfish
[] http get: url (/redfish)

[] URL        : /redfish
[] Status     : 200
[] Reason     : OK
[] JSON Data  :
{
    "v1": "/redfish/v1/"
}
```

You can see by the JSON data returned that the current Redfish Specification version supported by this service is v1. So all URIs must use **/redfish/v1** as the base URI.


[//]: <> (================================================================================================================================================================)
## <a name="section2">(2) Determine Redfish Services using Service Root</a>
[//]: <> (================================================================================================================================================================)

The URI **/redfish/v1** produces a list of all services implemented by this Redfish service.

```
(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)


 [] URL        : /redfish/v1
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
    "@odata.id": "/redfish/v1",
    "@odata.type": "#ServiceRoot.v1_9_0.ServiceRoot",
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "CompositionService": {
        "@odata.id": "/redfish/v1/CompositionService"
    },
    "EventService": {
        "@odata.id": "/redfish/v1/EventService"
    },
    "Fabrics": {
        "@odata.id": "/redfish/v1/Fabrics"
    },
    "Id": "RootService",
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Name": "Root Service",
    "Oem": {
        "Seagate": {
            "RedfishServiceVersion": "2.4.20"
        }
    },
    "RedfishVersion": "1.12.0",
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Storage"
    },
    "Systems": {
        "@odata.id": "/redfish/v1/Systems"
    },
    "Tasks": {
        "@odata.id": "/redfish/v1/TaskService"
    },
    "UUID": "92384634-2938-2342-8820-489239905423",
    "UpdateService": {
        "@odata.id": "/redfish/v1/UpdateService"
    }
}
```

The key take away from this JSON response is that this service provides a number of models and data for various system information
including: **AccountService**, **Chassis**, **CompositionService**, **Fabrics**, **SessionService**, **Managers**, **Storage**,
**Systems**, **TaskService**, and **UpdateService**.

Another key piece of information from the Service Root is the **RedfishVersion** property. This is the version of the Redfish
Specification supported by this Service, the version of Redfish Service is specified by **"Oem": { "Seagate": { "RedfishServiceVersion": "2.4.20" } }**.
In this case, the Redfish Service is version **2.4.20**.

### Odata

The Redfish service publishes required ODATA 4.0 information through the URI /redfish/v1/odata.
```
(redfish) http get /redfish/v1/odata
[] http get: url (/redfish/v1/odata)

 [] URL        : /redfish/v1/odata
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/odata",
    "value": [
        {
            "name": "Service",
            "kind": "Singleton",
            "url": "/redfish/v1/"
        },
        {
            "name": "AccountService",
            "kind": "Singleton",
            "url": "/redfish/v1/AccountService"
        },
        {
            "name": "Chassis",
            "kind": "Singleton",
            "url": "/redfish/v1/Chassis"
        },
        {
            "name": "CompositionService",
            "kind": "Singleton",
            "url": "/redfish/v1/CompositionService"
        },
        {
            "name": "EventService",
            "kind": "Singleton",
            "url": "/redfish/v1/EventService"
        },
        {
            "name": "Fabrics",
            "kind": "Singleton",
            "url": "/redfish/v1/Fabrics"
        },
        {
            "name": "Managers",
            "kind": "Singleton",
            "url": "/redfish/v1/Managers"
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
        },
        {
            "name": "Storage",
            "kind": "Singleton",
            "url": "/redfish/v1/Storage"
        },
        {
            "name": "Systems",
            "kind": "Singleton",
            "url": "/redfish/v1/Systems"
        },
        {
            "name": "Tasks",
            "kind": "Singleton",
            "url": "/redfish/v1/TaskService"
        },
        {
            "name": "UpdateService",
            "kind": "Singleton",
            "url": "/redfish/v1/UpdateService"
        }
    ]
}
```
 
### Metadata

The Redfish service publishes required metadata information through the URI /redfish/v1/$metadata. The Redfish specification states
that **XML** must be returned for this URI. The data returned indicates which version of each schema is supported by this version of the service.

Schema data is also published online for both Redfish (**http://redfish.dmtf.org/schemas/v1/**) and Swordfish (**http://redfish.dmtf.org/schemas/swordfish/v1/**).
A user can review the JSON data for a schema to learn more about which properties are supported, correct spelling and case, brief description, and links to valid
enumeration values. 

```
(redfish) http get /redfish/v1/$metadata
[] http get: url (/redfish/v1/$metadata)

 [] URL        : /redfish/v1/$metadata
 [] Status     : 200
 [] Reason     : OK
 [] XML Data   :
<?xml version="1.0" encoding="UTF-8"?>
<edmx:Edmx xmlns:edmx="http://docs.oasis-open.org/odata/ns/edmx" Version="4.0">
   <edmx:DataServices>
      <Schema xmlns="http://docs.oasis-open.org/odata/ns/edm" Namespace="Service">
         <EntityContainer Name="Service" Extends="ServiceRoot.v1_2_0.ServiceContainer" />
      </Schema>
   </edmx:DataServices>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/Capacity_v1.xml">
      <edmx:Include Namespace="Capacity" />
      <edmx:Include Namespace="Capacity.v1_2_0" />
   </edmx:Reference>
   <edmx:Reference Uri="https://redfish.dmtf.org/schemas/v1/AccountService_v1.xml">
      <edmx:Include Namespace="AccountService" />
      <edmx:Include Namespace="AccountService.v1_9_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Chassis_v1.xml">
      <edmx:Include Namespace="Chassis" />
      <edmx:Include Namespace="Chassis.v1_15_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ChassisCollection_v1.xml">
      <edmx:Include Namespace="ChassisCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="https://redfish.dmtf.org/schemas/v1/CollectionCapabilities_v1.xml">
      <edmx:Include Namespace="CollectionCapabilities" />
      <edmx:Include Namespace="CollectionCapabilities.v1_2_2" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/CompositionService_v1.xml">
      <edmx:Include Namespace="CompositionService" />
      <edmx:Include Namespace="CompositionService.v1_1_2" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ComputerSystem_v1.xml">
      <edmx:Include Namespace="ComputerSystem" />
      <edmx:Include Namespace="ComputerSystem.v1_14_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ComputerSystemCollection_v1.xml">
      <edmx:Include Namespace="ComputerSystemCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Drive_v1.xml">
      <edmx:Include Namespace="Drive" />
      <edmx:Include Namespace="Drive.v1_12_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/DriveCollection_v1.xml">
      <edmx:Include Namespace="DriveCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Endpoint_v1.xml">
      <edmx:Include Namespace="Endpoint" />
      <edmx:Include Namespace="Endpoint.v1_5_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EndpointCollection_v1.xml">
      <edmx:Include Namespace="EndpointCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="https://redfish.dmtf.org/schemas/v1/EndpointGroup_v1.xml">
      <edmx:Include Namespace="EndpointGroup" />
      <edmx:Include Namespace="EndpointGroup.v1_3_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EndpointGroupCollection_v1.xml">
      <edmx:Include Namespace="EndpointGroupCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EthernetInterface_v1.xml">
      <edmx:Include Namespace="EthernetInterface" />
      <edmx:Include Namespace="EthernetInterface.v1_6_3" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EthernetInterfaceCollection_v1.xml">
      <edmx:Include Namespace="EthernetInterfaceCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Event_v1.xml">
      <edmx:Include Namespace="Event" />
      <edmx:Include Namespace="Event.v1_6_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EventDestination_v1.xml">
      <edmx:Include Namespace="EventDestination" />
      <edmx:Include Namespace="EventDestination.v1_10_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EventDestinationCollection_v1.xml">
      <edmx:Include Namespace="EventDestinationCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/EventService_v1.xml">
      <edmx:Include Namespace="EventService" />
      <edmx:Include Namespace="EventService.v1_7_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Fabric_v1.xml">
      <edmx:Include Namespace="Fabric" />
      <edmx:Include Namespace="Fabric.v1_2_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/FabricCollection_v1.xml">
      <edmx:Include Namespace="FabricCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="https://redfish.dmtf.org/schemas/v1/Fan_v1.xml">
      <edmx:Include Namespace="Fan" />
      <edmx:Include Namespace="Fan.v1_0_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/IOStatistics_v1.xml">
      <edmx:Include Namespace="IOStatistics" />
      <edmx:Include Namespace="IOStatistics.v1_0_3" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/IPAddresses_v1.xml">
      <edmx:Include Namespace="IPAddresses" />
      <edmx:Include Namespace="IPAddresses.v1_0_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/LogService_v1.xml">
      <edmx:Include Namespace="LogService" />
      <edmx:Include Namespace="LogService.v1_2_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/LogServiceCollection_v1.xml">
      <edmx:Include Namespace="LogServiceCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Manager_v1.xml">
      <edmx:Include Namespace="Manager" />
      <edmx:Include Namespace="Manager.v1_11_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ManagerCollection_v1.xml">
      <edmx:Include Namespace="ManagerCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ManagerAccount_v1.xml">
      <edmx:Include Namespace="ManagerAccount" />
      <edmx:Include Namespace="ManagerAccount.v1_8_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ManagerAccountCollection_v1.xml">
      <edmx:Include Namespace="ManagerAccountCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Power_v1.xml">
      <edmx:Include Namespace="Power" />
      <edmx:Include Namespace="Power.v1_7_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Redundancy_v1.xml">
      <edmx:Include Namespace="Redundancy" />
      <edmx:Include Namespace="Redundancy.v1_4_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Resource_v1.xml">
      <edmx:Include Namespace="Resource" />
      <edmx:Include Namespace="Resource.v1_0_0" />
      <edmx:Include Namespace="Resource.v1_11_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ResourceBlock_v1.xml">
      <edmx:Include Namespace="ResourceBlock" />
      <edmx:Include Namespace="ResourceBlock.v1_3_4" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ResourceBlockCollection_v1.xml">
      <edmx:Include Namespace="ResourceBlockCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/RedfishExtensions_v1.xml">
      <edmx:Include Namespace="RedfishExtensions.v1_0_0" Alias="Redfish" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ServiceRoot_v1.xml">
      <edmx:Include Namespace="ServiceRoot" />
      <edmx:Include Namespace="ServiceRoot.v1_9_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Session_v1.xml">
      <edmx:Include Namespace="Session" />
      <edmx:Include Namespace="Session.v1_3_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SessionCollection_v1.xml">
      <edmx:Include Namespace="SessionCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SessionService_v1.xml">
      <edmx:Include Namespace="SessionService" />
      <edmx:Include Namespace="SessionService.v1_1_8" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SoftwareInventory_v1.xml">
      <edmx:Include Namespace="SoftwareInventory" />
      <edmx:Include Namespace="SoftwareInventory.v1_4_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/SoftwareInventoryCollection_v1.xml">
      <edmx:Include Namespace="SoftwareInventoryCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Storage_v1.xml">
      <edmx:Include Namespace="Storage" />
      <edmx:Include Namespace="Storage.v1_10_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/StorageCollection_v1.xml">
      <edmx:Include Namespace="StorageCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageGroup_v1.xml">
      <edmx:Include Namespace="StorageGroup" />
      <edmx:Include Namespace="StorageGroup.v1_5_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageGroupCollection_v1.xml">
      <edmx:Include Namespace="StorageGroupCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StoragePool_v1.xml">
      <edmx:Include Namespace="StoragePool" />
      <edmx:Include Namespace="StoragePool.v1_5_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StoragePoolCollection_v1.xml">
      <edmx:Include Namespace="StoragePoolCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/StorageReplicaInfo_v1.xml">
      <edmx:Include Namespace="StorageReplicaInfo" />
      <edmx:Include Namespace="StorageReplicaInfo.v1_3_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Task_v1.xml">
      <edmx:Include Namespace="Task" />
      <edmx:Include Namespace="Task.v1_5_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/TaskCollection_v1.xml">
      <edmx:Include Namespace="TaskCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/TaskService_v1.xml">
      <edmx:Include Namespace="TaskService" />
      <edmx:Include Namespace="TaskService.v1_1_6" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Thermal_v1.xml">
      <edmx:Include Namespace="Thermal" />
      <edmx:Include Namespace="Thermal.v1_7_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/UpdateService_v1.xml">
      <edmx:Include Namespace="UpdateService" />
      <edmx:Include Namespace="UpdateService.v1_8_3" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/Volume_v1.xml">
      <edmx:Include Namespace="Volume" />
      <edmx:Include Namespace="Volume.v1_6_1" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/swordfish/v1/VolumeCollection_v1.xml">
      <edmx:Include Namespace="VolumeCollection" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/Zone_v1.xml">
      <edmx:Include Namespace="Zone" />
      <edmx:Include Namespace="Zone.v1_6_0" />
   </edmx:Reference>
   <edmx:Reference Uri="http://redfish.dmtf.org/schemas/v1/ZoneCollection_v1.xml">
      <edmx:Include Namespace="ZoneCollection" />
   </edmx:Reference>
</edmx:Edmx>
```


[//]: <> (================================================================================================================================================================)
## <a name="section3">(3) Create a Session</a>
[//]: <> (================================================================================================================================================================)

The Redfish specification specifies two supported authentication methods - HTTP basic authentication or session login authentication. This 
service uses the session login authentication. A session is needed in order to access most URIs of the service. Only the following URIs
can be accessed without a session:
* /redfish
* /redfish/v1
* /redfish/odata 
* /redfish/$metadta
* /redfish/v1/SessionService/Sessions (for HTTP POST)

To create a session, we POST JSON data containing a username and password to the Sessions object. The tags `<username>` and `<password>` must be
replaced with the correct values when executed.

Once a session is created, it remains active for 30 minutes since the last executed command.

**Note:** This section demonstrates using HTTP POST to create a session, so the reader understands the Redfish aspects of creating a session. This tool also
allows a single step short-cut, just run ```(redfish) create session``` to accomplish the same as the below steps.

**Note:** An extra command is executed below so that the **X-Auth-Token** is stored for all future HTTP calls. The tool will automatically add the
token to all HTTP headers that require authentication. The `<session-hash>` should be replaced with the actual token returned, for example a value such as **03c30f8620682d75bf8076d22880f940**.


```
(redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "<username>", "Password": "<password>" }

[] http post: url (/redfish/v1/SessionService/Sessions)
[[ POST DATA (/redfish/v1/SessionService/Sessions) ]]
{
    "UserName": "<username>",
    "Password": "<password>"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/SessionService/Sessions
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '273'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('X-Auth-Token', '03c30f8620682d75bf8076d22880f940')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Session.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/3",
    "@odata.type": "#Session.v1_3_0.Session",
    "Description": "User Session",
    "Id": "3",
    "Name": "User Session",
    "UserName": "manage"
}

(redfish) save session 2 <session-hash>

[] Redfish session saved (2:<session-hash>)
```

Now that we have created a session, and saved the authentication key, we can access all other URIs.

### Example of HTTP Operation Failure

The following is an example of attempting to perform a Redfish operation before the client created a session.

```
(redfish) http get /redfish/v1/Storage/
[] http get: url (/redfish/v1/Storage/)

 [] URL        : /redfish/v1/Storage/
 [] Status     : 401
 [] Reason     : Unauthorized
 [] Context    : 2 Invalid session key

(redfish) create session
   -- ServiceVersion: 2
   -- IP Address    : https://10.230.220.100
   -- Discovered: Root                      >> /redfish/v1
   -- Discovered: AccountService            >> /redfish/v1/AccountService/
   -- Discovered: Chassis                   >> /redfish/v1/Chassis/
   -- Discovered: CompositionService        >> /redfish/v1/CompositionService/
   -- Discovered: EventService              >> /redfish/v1/EventService/
   -- Discovered: Fabrics                   >> /redfish/v1/Fabrics/
   -- Discovered: Managers                  >> /redfish/v1/Managers/
   -- Discovered: SessionService            >> /redfish/v1/SessionService/
   -- Discovered: Systems                   >> /redfish/v1/Systems/
   -- Discovered: Tasks                     >> /redfish/v1/TaskService/
   -- Discovered: UpdateService             >> /redfish/v1/UpdateService/
   -- Discovered: Accounts                  >> /redfish/v1/AccountService/Accounts/
   -- Discovered: Sessions                  >> /redfish/v1/SessionService/Sessions/
   -- Discovered: metadata                  >> /redfish/v1/$metadata/
   -- Discovered: odata                     >> /redfish/v1/odata/

[[ POST DATA (/redfish/v1/SessionService/Sessions/) ]]
{
    "UserName": "<username>",
    "Password": "<password>"
}
[[ POST DATA END ]]
[] Redfish session established (4:02a363c116a11639e2f488ee23fbad7b)

(redfish) http get /redfish/v1/Storage/
[] http get: url (/redfish/v1/Storage/)

 [] URL        : /redfish/v1/Storage/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageCollection.StorageCollection",
    "@odata.id": "/redfish/v1/Storage",
    "@odata.type": "#StorageCollection.StorageCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_b"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Storage Collection"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section4">(4) Show Active Sessions</a>
[//]: <> (================================================================================================================================================================)

Perform an HTTP GET on multiple URIs in other to gather session data and session specifics. You must have an active session in order to do this.

```
(redfish) http get /redfish/v1/SessionService/
[] http get: url (/redfish/v1/SessionService/)

 [] URL        : /redfish/v1/SessionService/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#SessionService.SessionService",
    "@odata.id": "/redfish/v1/SessionService",
    "@odata.type": "#SessionService.v1_1_8.SessionService",
    "Id": "SessionService",
    "Name": "SessionService",
    "ServiceEnabled": true,
    "Sessions": {
        "@odata.id": "/redfish/v1/SessionService/Sessions"
    }
}

(redfish) http get /redfish/v1/SessionService/Sessions
[] http get: url (/redfish/v1/SessionService/Sessions)

 [] URL        : /redfish/v1/SessionService/Sessions
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#SessionCollection.SessionCollection",
    "@odata.id": "/redfish/v1/SessionService/Sessions",
    "@odata.type": "#SessionCollection.SessionCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/SessionService/Sessions/4"
        },
        {
            "@odata.id": "/redfish/v1/SessionService/Sessions/3"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Session Collection"
}


(redfish) http get /redfish/v1/SessionService/Sessions/4
[] http get: url (/redfish/v1/SessionService/Sessions/4)

 [] URL        : /redfish/v1/SessionService/Sessions/4
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Session.Session",
    "@odata.id": "/redfish/v1/SessionService/Sessions/4",
    "@odata.type": "#Session.v1_3_0.Session",
    "Description": "User Session",
    "Id": "4",
    "Name": "User Session",
    "UserName": "manage"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section5">(5) Explore Systems and Storage</a>
[//]: <> (================================================================================================================================================================)

The ComputerSystem schema is used to display physical information about the system. A series of HTTP GET operations are
used to traverse through the system data. Information is provided for Ethernet Interfaces and Storage entities, plus shortcut
links to other physical resources.

* /redfish/v1/Systems
* /redfish/v1/Systems/{SystemId}
* /redfish/v1/Systems/{SystemId}/LogServices
* /redfish/v1/Systems/{SystemId}/Storage
* /redfish/v1/Systems/{SystemId}/Actions/ComputerSystem.Reset"

LogServices are described in [(24) Get Controller Logs](#section24). The ComputerSystem.Reset action is described in[(23) Reboot Controller](#section23).


```
(redfish) http get /redfish/v1/Systems
[] http get: url (/redfish/v1/Systems)

 [] URL        : /redfish/v1/Systems
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.id": "/redfish/v1/Systems",
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531"
        }
    ],
    "Members@odata.count": 1,
    "Name": "ComputerSystem Collection"
}

(redfish) http get /redfish/v1/Systems/SGFTJ2032520531
[] http get: url (/redfish/v1/Systems/SGFTJ2032520531)

 [] URL        : /redfish/v1/Systems/SGFTJ2032520531
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
    "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531",
    "@odata.type": "#ComputerSystem.v1_14_0.ComputerSystem",
    "Actions": {
        "#ComputerSystem.Reset": {
            "ResetType@Redfish.AllowableValues": [
                "GracefulRestart"
            ],
            "target": "/redfish/v1/Systems/SGFTJ2032520531/Actions/ComputerSystem.Reset"
        }
    },
    "Id": "SGFTJ2032520531",
    "Links": {
        "Chassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/LogServices"
    },
    "Manufacturer": "SEAGATE",
    "Name": "Uninitialized Test1",
    "SerialNumber": "SGFTJ2032520531",
    "Status": {
        "Health": "OK"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage"
    }
}
```


### Storage

The Storage schema provides information regarding the storage array controllers and redundancy information. It is used to view the collection
of StorageGroups, StoragePools, and Volumes created on this storage array. It is used to view available disk drives. The client can
also display EndpointGroups for ports and initiators and review supported controller protocols (SAS, FC, iSCSI, etc.).

The **"Oem": { "Seagate": { "DiskAdvancedSettings": {} } }** section describes OEM specific advanced settings that can be controller through this
Redfish service, such as: BackgroundDiskGroupScrub and BackgroundDiskScrub.

**Note:** The same information is accessible under `/redfish/v1/Storage`. This shorter URI can be used without having to use `/redfish/v1/Systems/{SystemsId}`.

```
(redfish) http get /redfish/v1/Systems/SGFTJ2032520531/Storage
[] http get: url (/redfish/v1/Systems/SGFTJ2032520531/Storage)

 [] URL        : /redfish/v1/Systems/SGFTJ2032520531/Storage
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageCollection.StorageCollection",
    "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage",
    "@odata.type": "#StorageCollection.StorageCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_b"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Storage Collection"
}

(redfish) http get /redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a
[] http get: url (/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a)

 [] URL        : /redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
    "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a",
    "@odata.type": "#Storage.v1_10_0.Storage",
    "Drives": [
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.0"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.1"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.8"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.9"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.10"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.11"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.12"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.13"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.14"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.15"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.16"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.17"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.18"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.19"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.20"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.21"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.22"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.23"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.2"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.3"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.4"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.5"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.6"
        },
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Drives/0.7"
        }
    ],
    "EndpointGroups": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/EndpointGroups"
    },
    "Id": "A",
    "Name": "controller_a",
    "Oem": {
        "Seagate": {
            "DiskAdvancedSettings": {
                "BackgroundDiskGroupScrub": "Disabled",
                "BackgroundDiskScrub": "Disabled",
                "ValidScrubSettings": [
                    "Enabled",
                    "Disabled",
                    "On",
                    "Off"
                ]
            }
        }
    },
    "Redundancy": [
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a#/Redundancy/0",
            "MaxNumSupported": 2,
            "MemberId": "A",
            "MinNumNeeded": 1,
            "Mode": "Sharing",
            "Name": "Controller Redundancy Group 1",
            "RedundancySet": [
                {
                    "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a"
                },
                {
                    "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_b"
                }
            ],
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Status": {
        "Health": "OK"
    },
    "StorageControllers": [
        {
            "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a#/StorageControllers/0",
            "Manufacturer": "SEAGATE",
            "MemberId": "A",
            "Name": "controller_a",
            "SerialNumber": "00C0FF546059",
            "Status": {
                "Health": "OK"
            },
            "SupportedControllerProtocols": [
                "iSCSI"
            ]
        }
    ],
    "StorageGroups": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/StorageGroups"
    },
    "StoragePools": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/StoragePools"
    },
    "Volumes": {
        "@odata.id": "/redfish/v1/Systems/SGFTJ2032520531/Storage/controller_a/Volumes"
    }
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section6">(6) Explore Chassis</a>
[//]: <> (================================================================================================================================================================)

The Chassis schema is used to display enclosure information about the physical system. A series of HTTP GET operations are
used to traverse through the physical data. Information is provided for Enclosures, Location, Thermal, Power, Drive links, and
other properties. 

* /redfish/v1/Chassis
* /redfish/v1/Chassis/{ChassisId}
* /redfish/v1/Chassis/{ChassisId}/Power
* /redfish/v1/Chassis/{ChassisId}/Thermal

```
(redfish) http get /redfish/v1/Chassis
[] http get: url (/redfish/v1/Chassis)

 [] URL        : /redfish/v1/Chassis
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ChassisCollection.ChassisCollection",
    "@odata.id": "/redfish/v1/Chassis",
    "@odata.type": "#ChassisCollection.ChassisCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Chassis Collection"
}

(redfish) http get /redfish/v1/Chassis/enclosure_0
[] http get: url (/redfish/v1/Chassis/enclosure_0)

 [] URL        : /redfish/v1/Chassis/enclosure_0
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Chassis.Chassis",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0",
    "@odata.type": "#Chassis.v1_15_0.Chassis",
    "ChassisType": "StorageEnclosure",
    "Id": "enclosure_0",
    "Location": {
        "Placement": {
            "Rack": "0",
            "RackOffset": 0
        }
    },
    "LocationIndicatorActive": false,
    "Manufacturer": "SEAGATE",
    "Name": "enclosure_0",
    "Power": {
        "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power"
    },
    "PowerState": "On",
    "SerialNumber": "500C0FF05205313C",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Thermal": {
        "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal"
    }
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
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Power.Power",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power",
    "@odata.type": "#Power.v1_7_0.Power",
    "Id": "Power",
    "Name": "Power",
    "PowerSupplies": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/PowerSupplies/0",
            "MemberId": "psu_0.0",
            "Name": "PSU 0, Left",
            "PartNumber": "FRUKE16-01",
            "SerialNumber": "DHSIFTJ-20326G4B0T",
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/PowerSupplies/1",
            "MemberId": "psu_0.1",
            "Name": "PSU 1, Right",
            "PartNumber": "FRUKE16-01",
            "SerialNumber": "DHSIFTJ-20326G4B2L",
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Voltages": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/0",
            "MemberId": "sensor_volt_ctrl_B.0",
            "Name": "Capacitor Pack Voltage-Ctlr B",
            "ReadingVolts": 10.890000343322754,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/1",
            "MemberId": "sensor_volt_ctrl_B.1",
            "Name": "Capacitor Cell 1 Voltage-Ctlr B",
            "ReadingVolts": 2.700000047683716,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/2",
            "MemberId": "sensor_volt_ctrl_B.2",
            "Name": "Capacitor Cell 2 Voltage-Ctlr B",
            "ReadingVolts": 2.7100000381469727,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/3",
            "MemberId": "sensor_volt_ctrl_B.3",
            "Name": "Capacitor Cell 3 Voltage-Ctlr B",
            "ReadingVolts": 2.7100000381469727,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/4",
            "MemberId": "sensor_volt_ctrl_B.4",
            "Name": "Capacitor Cell 4 Voltage-Ctlr B",
            "ReadingVolts": 2.7100000381469727,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/5",
            "MemberId": "sensor_volt_ctrl_A.0",
            "Name": "Capacitor Pack Voltage-Ctlr A",
            "ReadingVolts": 10.819999694824219,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/6",
            "MemberId": "sensor_volt_ctrl_A.1",
            "Name": "Capacitor Cell 1 Voltage-Ctlr A",
            "ReadingVolts": 2.690000057220459,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/7",
            "MemberId": "sensor_volt_ctrl_A.2",
            "Name": "Capacitor Cell 2 Voltage-Ctlr A",
            "ReadingVolts": 2.690000057220459,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/8",
            "MemberId": "sensor_volt_ctrl_A.3",
            "Name": "Capacitor Cell 3 Voltage-Ctlr A",
            "ReadingVolts": 2.690000057220459,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/9",
            "MemberId": "sensor_volt_ctrl_A.4",
            "Name": "Capacitor Cell 4 Voltage-Ctlr A",
            "ReadingVolts": 2.700000047683716,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/10",
            "MemberId": "sensor_volt_psu_0.1.0",
            "Name": "Voltage 12V Rail Loc: right-PSU",
            "ReadingVolts": 12.180000305175781,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/11",
            "MemberId": "sensor_volt_psu_0.1.1",
            "Name": "Voltage 5V Rail Loc: right-PSU",
            "ReadingVolts": 5.0,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/12",
            "MemberId": "sensor_volt_psu_0.0.0",
            "Name": "Voltage 12V Rail Loc: left-PSU",
            "ReadingVolts": 12.220000267028809,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Power#/Voltages/13",
            "MemberId": "sensor_volt_psu_0.0.1",
            "Name": "Voltage 5V Rail Loc: left-PSU",
            "ReadingVolts": 4.960000038146973,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ]
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
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Thermal.Thermal",
    "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal",
    "@odata.type": "#Thermal.v1_7_0.Thermal",
    "Fans": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/0",
            "MemberId": "fan_0.0",
            "Name": "Fan 0",
            "Reading": 4500,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/1",
            "MemberId": "fan_0.1",
            "Name": "Fan 1",
            "Reading": 4500,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/2",
            "MemberId": "fan_0.2",
            "Name": "Fan 2",
            "Reading": 4800,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Fans/3",
            "MemberId": "fan_0.3",
            "Name": "Fan 3",
            "Reading": 4560,
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Id": "Thermal",
    "Name": "Thermal",
    "Temperatures": [
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/0",
            "MemberId": "sensor_temp_ctrl_B.1",
            "Name": "sensor_temp_ctrl_B.1",
            "ReadingCelsius": 51,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/1",
            "MemberId": "sensor_temp_ctrl_B.2",
            "Name": "sensor_temp_ctrl_B.2",
            "ReadingCelsius": 49,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/2",
            "MemberId": "sensor_temp_ctrl_B.3",
            "Name": "sensor_temp_ctrl_B.3",
            "ReadingCelsius": 46,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/3",
            "MemberId": "sensor_temp_ctrl_B.4",
            "Name": "sensor_temp_ctrl_B.4",
            "ReadingCelsius": 64,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/4",
            "MemberId": "sensor_temp_ctrl_B.5",
            "Name": "sensor_temp_ctrl_B.5",
            "ReadingCelsius": 66,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/5",
            "MemberId": "sensor_temp_ctrl_B.6",
            "Name": "sensor_temp_ctrl_B.6",
            "ReadingCelsius": 49,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/6",
            "MemberId": "sensor_temp_ctrl_A.1",
            "Name": "sensor_temp_ctrl_A.1",
            "ReadingCelsius": 59,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/7",
            "MemberId": "sensor_temp_ctrl_A.2",
            "Name": "sensor_temp_ctrl_A.2",
            "ReadingCelsius": 52,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/8",
            "MemberId": "sensor_temp_ctrl_A.3",
            "Name": "sensor_temp_ctrl_A.3",
            "ReadingCelsius": 38,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/9",
            "MemberId": "sensor_temp_ctrl_A.4",
            "Name": "sensor_temp_ctrl_A.4",
            "ReadingCelsius": 45,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/10",
            "MemberId": "sensor_temp_ctrl_A.5",
            "Name": "sensor_temp_ctrl_A.5",
            "ReadingCelsius": 59,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/11",
            "MemberId": "sensor_temp_ctrl_A.6",
            "Name": "sensor_temp_ctrl_A.6",
            "ReadingCelsius": 53,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/12",
            "MemberId": "sensor_temp_encl_0.0",
            "Name": "sensor_temp_encl_0.0",
            "ReadingCelsius": 21,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/13",
            "MemberId": "sensor_temp_encl_0.1",
            "Name": "sensor_temp_encl_0.1",
            "ReadingCelsius": 17,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/14",
            "MemberId": "sensor_temp_iom_0.B.0",
            "Name": "sensor_temp_iom_0.B.0",
            "ReadingCelsius": 34,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/15",
            "MemberId": "sensor_temp_iom_0.A.0",
            "Name": "sensor_temp_iom_0.A.0",
            "ReadingCelsius": 26,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/16",
            "MemberId": "sensor_temp_psu_0.1.0",
            "Name": "sensor_temp_psu_0.1.0",
            "ReadingCelsius": 16,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/17",
            "MemberId": "sensor_temp_psu_0.1.1",
            "Name": "sensor_temp_psu_0.1.1",
            "ReadingCelsius": 25,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/18",
            "MemberId": "sensor_temp_psu_0.0.0",
            "Name": "sensor_temp_psu_0.0.0",
            "ReadingCelsius": 18,
            "Status": {
                "State": "Enabled"
            }
        },
        {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0/Thermal#/Temperatures/19",
            "MemberId": "sensor_temp_psu_0.0.1",
            "Name": "sensor_temp_psu_0.0.1",
            "ReadingCelsius": 27,
            "Status": {
                "State": "Enabled"
            }
        }
    ]
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section7">(7) Explore Managers</a>
[//]: <> (================================================================================================================================================================)

The Managers schema is used to display storage controller information for the system. A series of HTTP GET operations are
used to traverse through the data. Information is provided for Controllers, Firmware Version, Status, Ethernet Interfaces, and
other properties. 

* /redfish/v1/Managers
* /redfish/v1/Managers/{ManagerId}
* /redfish/v1/Managers/{ManagerId}/EthernetInterfaces

```
(redfish) http get /redfish/v1/Managers
[] http get: url (/redfish/v1/Managers)

 [] URL        : /redfish/v1/Managers
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ManagerCollection.ManagerCollection",
    "@odata.id": "/redfish/v1/Managers",
    "@odata.type": "#ManagerCollection.ManagerCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/controller_a"
        },
        {
            "@odata.id": "/redfish/v1/Managers/controller_b"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Manager Collection"
}

(redfish) http get /redfish/v1/Managers/controller_a
[] http get: url (/redfish/v1/Managers/controller_a)

 [] URL        : /redfish/v1/Managers/controller_a
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
    "@odata.id": "/redfish/v1/Managers/controller_a",
    "@odata.type": "#Manager.v1_11_0.Manager",
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces"
    },
    "FirmwareVersion": "I200B009",
    "Id": "controller_a",
    "ManagerType": "ManagementController",
    "Name": "/redfish/v1/Managers/management_controller_a",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/Managers/controller_b
[] http get: url (/redfish/v1/Managers/controller_b)

 [] URL        : /redfish/v1/Managers/controller_b
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Manager.Manager",
    "@odata.id": "/redfish/v1/Managers/controller_b",
    "@odata.type": "#Manager.v1_11_0.Manager",
    "EthernetInterfaces": {
        "@odata.id": "/redfish/v1/Managers/controller_b/EthernetInterfaces"
    },
    "FirmwareVersion": "I200B009",
    "Id": "controller_b",
    "ManagerType": "ManagementController",
    "Name": "/redfish/v1/Managers/management_controller_b",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}
```

### Ethernet Interfaces

The EthernetInterfaces schema provides a collection of all Ethernet interfaces supported by this storage system. Review Ethernet interface details
like the MAC address, IPv4 and IPv6 addresses.

```
(redfish) http get /redfish/v1/Managers/controller_a/EthernetInterfaces
[] http get: url (/redfish/v1/Managers/controller_a/EthernetInterfaces)

 [] URL        : /redfish/v1/Managers/controller_a/EthernetInterfaces
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces",
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Ethernet Interface Collection"
}

(redfish) http get /redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated
[] http get: url (/redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated)

 [] URL        : /redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EthernetInterface.EthernetInterface",
    "@odata.id": "/redfish/v1/Managers/controller_a/EthernetInterfaces/Dedicated",
    "@odata.type": "#EthernetInterface.v1_6_3.EthernetInterface",
    "AutoNeg": true,
    "FullDuplex": true,
    "IPv4Addresses": [
        {
            "Address": "10.235.208.138",
            "Gateway": "10.235.208.1",
            "SubnetMask": "255.255.240.0"
        }
    ],
    "IPv6Addresses": [
        {
            "Address": "fe80::2c0:ffff:fe54:6059"
        }
    ],
    "Id": "A",
    "InterfaceEnabled": true,
    "Name": "Dedicated Ethernet Interface",
    "PermanentMACAddress": "00:C0:FF:54:60:59",
    "SpeedMbps": 1000,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}


(redfish) http get /redfish/v1/Managers/controller_b/EthernetInterfaces
[] http get: url (/redfish/v1/Managers/controller_b/EthernetInterfaces)

 [] URL        : /redfish/v1/Managers/controller_b/EthernetInterfaces
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "@odata.id": "/redfish/v1/Managers/controller_b/EthernetInterfaces",
    "@odata.type": "#EthernetInterfaceCollection.EthernetInterfaceCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Ethernet Interface Collection"
}

(redfish) http get /redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated
[] http get: url (/redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated)

 [] URL        : /redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EthernetInterface.EthernetInterface",
    "@odata.id": "/redfish/v1/Managers/controller_b/EthernetInterfaces/Dedicated",
    "@odata.type": "#EthernetInterface.v1_6_3.EthernetInterface",
    "AutoNeg": true,
    "FullDuplex": true,
    "IPv4Addresses": [
        {
            "Address": "10.235.208.139",
            "Gateway": "10.235.208.1",
            "SubnetMask": "255.255.240.0"
        }
    ],
    "IPv6Addresses": [
        {
            "Address": "fe80::2c0:ffff:fe54:6058"
        }
    ],
    "Id": "B",
    "InterfaceEnabled": true,
    "Name": "Dedicated Ethernet Interface",
    "PermanentMACAddress": "00:C0:FF:54:60:58",
    "SpeedMbps": 1000,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section8">(8) Create a RAID Disk Group using StoragePool</a>
[//]: <> (================================================================================================================================================================)

A new RAID disk group is created using the Swordfish StoragePool entity and a HTTP POST operation. The operation must include a 
number of properties used to create the disk group. Follow these steps to obtain required information first.

1. Determine the URIs of all Drives to be included in the disk group.
2. Decide on the RAID level for the storage group.
3. Decide whether this is for Pool A or Pool B.
4. Decide on a Name for the disk group.


### Step 1. Show Drives

```
(redfish) http get /redfish/v1/Storage/controller_a/Drives
[] http get: url (/redfish/v1/Storage/controller_a/Drives)

 [] URL        : /redfish/v1/Storage/controller_a/Drives
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Drives",
    "@odata.type": "#DriveCollection.DriveCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.8"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.9"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.10"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.11"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.12"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.13"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.14"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.15"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.16"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.17"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.18"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.19"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.20"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.21"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.22"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.23"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.4"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.5"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.6"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.7"
        }
    ],
    "Members@odata.count": 24,
    "Name": "Drive Collection"
}
```

### Step 2. Create JSON Data used for POST Operation

Here are the properties that are used to create a new disk group. **Note** that when you create the first disk group, a pool will be automatically created if
one does not already exist.

| Property           | Mandatory | Description |
| ------------------ | --------- | ----------- |
| Name               | No        | The name that will be assigned to this storage group. |
| CapacitySources    | Yes       | This is a data structure containing the property **ProvidingDrives** and then a list of drives that will be used to create the resource. |
| AllocatedPools     | No        | This is a data structure containing the property **Members** and a list of StoragePools. The new disk group will be added to the indicated storage pool |
| SupportedRAIDTypes | Yes       | This provides the RAID level, raid0, raid1, raid5, raid6, raid10, or adapt - used to create the new storage group. |

For this operation, the JSON data needed for the operation is stored in a text file called **v2_create_diskgroup.json**. This **MUST** be modified for each storage system. See below.

```
{
    "Name": "dgA01",
    "CapacitySources": {
        "ProvidingDrives": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
            }
        ]
    },
    "AllocatedPools": {
        "Members": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
            }
        ]
    },
    "SupportedRAIDTypes": [
        "RAID5"
    ]
}
```

Now create a disk group named **dgA01**. These steps can be repeated to create as many disk groups as desired. After creating a disk group,
use the HTTP GET operation on the StoragePool collection to view all existing disk groups and storage pools. We will also perform an HTTP GET on
the new disk group and pool to see the details of each.

**Note:** The **Description** property is used to differentiate between a **DiskGroup** and a **Pool**. See below in the JSON data returned.

**Note:** This command was executed on a linux system so a slash `/` was used for `json/v2_create_diskgroup.json`. Other operating systems may require a backslash `\`.

```
(redfish) http post /redfish/v1/Storage/controller_a/StoragePools json/v2_create_diskgroup.json
[] http post: url (/redfish/v1/Storage/controller_a/StoragePools)
[[ POST DATA (/redfish/v1/Storage/controller_a/StoragePools) ]]
{
    "Name": "dgA01",
    "CapacitySources": {
        "ProvidingDrives": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
            }
        ]
    },
    "AllocatedPools": {
        "Members": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
            }
        ]
    },
    "SupportedRAIDTypes": [
        "RAID5"
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '2179'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StoragePool.StoragePool",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01",
    "@odata.type": "#StoragePool.v1_5_0.StoragePool",
    "AllocatedVolumes": {
        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a"
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 5378095972352,
            "ConsumedBytes": 0
        }
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/dgA01#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900000e80f16100000000",
            "Name": "dgA01",
            "ProvidingDrives": {
                "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
                "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a",
                "@odata.type": "#DriveCollection.DriveCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/0.0"
                    },
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/0.1"
                    },
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/0.2"
                    },
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/0.3"
                    }
                ],
                "Members@odata.count": 4,
                "Name": "Drives"
            }
        }
    ],
    "Description": "DiskGroup",
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "ReadIORequestTime": "44506",
        "WriteHitIORequests": 30,
        "WriteIOKiBytes": 92374016,
        "WriteIORequestTime": "44506"
    },
    "Id": "00c0ff54605900000e80f16100000000",
    "MaxBlockSizeBytes": 512,
    "Name": "dgA01",
    "RemainingCapacityPercent": 100,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "SupportedRAIDTypes": [
        "RAID5"
    ]
}


(redfish) http get /redfish/v1/Storage/controller_a/StoragePools
[] http get: url (/redfish/v1/Storage/controller_a/StoragePools)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01"
        }
    ],
    "Members@odata.count": 2,
    "Name": "StoragePool Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/StoragePools/A
[] http get: url (/redfish/v1/Storage/controller_a/StoragePools/A)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools/A
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StoragePool.StoragePool",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A",
    "@odata.type": "#StoragePool.v1_5_0.StoragePool",
    "AllocatedPools": {
        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools"
    },
    "AllocatedVolumes": {
        "@odata.id": "/redfish/v1/Storage/controller_a/Volumes"
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 5378095972352,
            "ConsumedBytes": 16384
        }
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900001080f16101000000",
            "Name": "A",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Description": "Pool",
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "ReadIORequestTime": "0",
        "WriteHitIORequests": 155,
        "WriteIOKiBytes": 181867008,
        "WriteIORequestTime": "0"
    },
    "Id": "00c0ff54605900001080f16101000000",
    "MaxBlockSizeBytes": 512,
    "Name": "A",
    "RemainingCapacityPercent": 99,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}


(redfish) http get /redfish/v1/Storage/controller_a/StoragePools/dgA01
[] http get: url (/redfish/v1/Storage/controller_a/StoragePools/dgA01)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools/dgA01
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StoragePool.StoragePool",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01",
    "@odata.type": "#StoragePool.v1_5_0.StoragePool",
    "AllocatedVolumes": {
        "@odata.id": "/redfish/v1/Storage/controller_a/Volumes"
    },
    "Capacity": {
        "Data": {
            "AllocatedBytes": 5378095972352,
            "ConsumedBytes": 16384
        }
    },
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900000e80f16100000000",
            "Name": "dgA01",
            "ProvidingDrives": {
                "@odata.context": "/redfish/v1/$metadata#DriveCollection.DriveCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/Drives",
                "@odata.type": "#DriveCollection.DriveCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
                    },
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
                    },
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
                    },
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
                    }
                ],
                "Members@odata.count": 4,
                "Name": "Drives"
            }
        }
    ],
    "Description": "DiskGroup",
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "ReadIORequestTime": "0",
        "WriteHitIORequests": 155,
        "WriteIOKiBytes": 181867008,
        "WriteIORequestTime": "0"
    },
    "Id": "00c0ff54605900000e80f16100000000",
    "MaxBlockSizeBytes": 512,
    "Name": "dgA01",
    "RemainingCapacityPercent": 99,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "SupportedRAIDTypes": [
        "RAID5"
    ]
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section9">(9) Create a Volume</a>
[//]: <> (================================================================================================================================================================)

A Volume is created using the Redfish/Swordfish Volume entity and a HTTP POST operation. The operation must include a 
number of properties used to create the volume. Here are the properties that are used to create a volume.

| Property         | Mandatory | Description |
| ---------------- | --------- | ----------- |
| Name             | No        | The name that will be assigned to the volume. |
| CapacityBytes    | No        | The size in bytes of the desired volume. |
| CapacitySources  | Yes       | This is a data structure with an **@odata.id** value pointing to the desired **StoragePool**. |

For this example operation, the JSON data needed for the operation is stored in a text file called **create_volume.json**. This data **MAY** change for each storage system. See below.

```
{
    "Name": "AVolume01",
    "CapacityBytes": 100000000000,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
        }
    ]
}
```

Now create a volume named **AVolume01**. These steps can be repeated to create as many volumes as desired. After creating a volume,
use the HTTP GET operation on the Volume collection to view all existing volumes. We will also perform an HTTP GET on the new volume
to see the details. The StoragePool A or B can be used based on what you have already created.

For this operation, the Redfish service returns an HTTP status of **201/Created** and a JSON representation of the new volume.

**Note:** The volume is not visible to a host until a StorageGroup is created to map the volume to EndpointGroups. See the next step.

```
(redfish) http post /redfish/v1/Storage/controller_a/Volumes json/create_volume.json
[] http post: url (/redfish/v1/Storage/controller_a/Volumes)
[[ POST DATA (/redfish/v1/Storage/controller_a/Volumes) ]]
{
    "Name": "AVolume01",
    "CapacityBytes": 100000000000,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
        }
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1711'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/AVolume01",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/AVolume01#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900003d83f16101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/Storage/controller_a/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff54605900003d83f16101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}


(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Volume Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
[] http get: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900003d83f16101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff54605900003d83f16101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section10">(10) Expose a Volume Using Mapping and StorageGroups</a>
[//]: <> (================================================================================================================================================================)

A StorageGroup is a Swordfish entity used to link a Volume to ServerEndpoints (ports) and a ClientEndpoints (initiators). A LogicalUnitNumber (LUN) 
can also be tied to a StorageGroup where applicable. Create and manage StorageGroups as a way to expose a Volume to one or more host systems.

**Note:** This service restricts a StorageGroup to map a single volume to a single initiator. Multiple storage groups can be created to create additional mappings.
 
 Here are the properties that are used to create a StorageGroup.

| Property              | Mandatory | Description |
| --------------------- | --------- | ----------- |
| AccessCapability      | No        | This is a string. Valid choices are **Read** or **ReadWrite**. This property is part of the **MappedVolumes** JSON array. Default is ReadWrite. |
| LogicalUnitNumber     | Yes       | Specify the LUN used for mapping the volume. This property is part of the **MappedVolumes** JSON array. **Note:** This value must be a string. |
| Volume                | Yes       | This specifies the Volume URI to be used for the mapping. This property is part of the **MappedVolumes** JSON array. |
| ClientEndpointGroups  | Yes       | A host initiator must be specified. Provide a list of one initiator group to use in the volume mapping. |
| ServerEndpointGroups  | No        | Provide a list of one or more storage port groups to use in the volume mapping. If no port is provided, the volume will be mapped to all available ports. |

For this example operation, the JSON data needed for the operation is stored in a text file called **v2_create_storagegroup.json**. This file **MUST** change for each storage system. See below.

```
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Endpoints/iqn.1994-05.com.redhat:csi-lab-51"
        }
    ],
    "MappedVolumes": [
        {
            "AccessCapability": "ReadWrite",
            "LogicalUnitNumber": "1",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/AVolume01"
            }
        }
    ]
}
```

### Step 1. Show EndpointGroups

Use HTTP GET operations to determine which EndpointGroups you want to use to create your StorageGroup.

```
(redfish) http get /redfish/v1/Storage/controller_a/EndpointGroups
[] http get: url (/redfish/v1/Storage/controller_a/EndpointGroups)

 [] URL        : /redfish/v1/Storage/controller_a/EndpointGroups
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EndpointGroupCollection.EndpointGroupCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups",
    "@odata.type": "#EndpointGroupCollection.EndpointGroupCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/iqn.1994-05.com.redhat:csi-lab-51"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/iqn.1993-08.org.debian:01:112233abcde"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/iqn.1993-08.org.debian:01:f09ec67ce4f5"
        }
    ],
    "Members@odata.count": 11,
    "Name": "EndpointGroup Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/EndpointGroups/A0
[] http get: url (/redfish/v1/Storage/controller_a/EndpointGroups/A0)

 [] URL        : /redfish/v1/Storage/controller_a/EndpointGroups/A0
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EndpointGroup.EndpointGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0",
    "@odata.type": "#EndpointGroup.v1_3_1.EndpointGroup",
    "Description": "Collection of Endpoints",
    "Endpoints": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Endpoints/A0"
        }
    ],
    "GroupType": "Server",
    "Id": "hostport_A0",
    "Name": "A0"
}


(redfish) http get /redfish/v1/Storage/controller_a/EndpointGroups/iqn.1994-05.com.redhat:csi-lab-51
[] http get: url (/redfish/v1/Storage/controller_a/EndpointGroups/iqn.1994-05.com.redhat:csi-lab-51)

 [] URL        : /redfish/v1/Storage/controller_a/EndpointGroups/iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EndpointGroup.EndpointGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/iqn.1994-05.com.redhat:csi-lab-51",
    "@odata.type": "#EndpointGroup.v1_3_1.EndpointGroup",
    "Description": "Collection of Endpoints",
    "Endpoints": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Endpoints/iqn.1994-05.com.redhat:csi-lab-51"
        }
    ],
    "GroupType": "Client",
    "Id": "iqn.1994-05.com.redhat:csi-lab-51",
    "Name": "I0"
}
```

### Step 2. Show Volumes

Use HTTP GET operations to determine which Volume you want to use to create your StorageGroup.

```
(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Volume Collection"
}
```

### Step 3. Create a StorageGroup

Now create the StorageGroup. These steps can be repeated to create multiple StorageGroups to map multiple volumes. After creating a StorageGroup,
use the HTTP GET operation on the collection to view all existing groups. We will also perform an HTTP GET on the new StorageGroup
to see the details.

```
(redfish) http post /redfish/v1/Storage/controller_a/StorageGroups json/v2_create_storagegroup.json
[] http post: url (/redfish/v1/Storage/controller_a/StorageGroups)
[[ POST DATA (/redfish/v1/Storage/controller_a/StorageGroups) ]]
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        }
    ],
    "ClientEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Endpoints/iqn.1994-05.com.redhat:csi-lab-51"
        }
    ],
    "MappedVolumes": [
        {
            "AccessCapability": "ReadWrite",
            "LogicalUnitNumber": "1",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/AVolume01"
            }
        }
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups
 [] Status     : 201
 [] Reason     : Created


(redfish) http get /redfish/v1/Storage/controller_a/StorageGroups
[] http get: url (/redfish/v1/Storage/controller_a/StorageGroups)

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51"
        }
    ],
    "Members@odata.count": 1,
    "Name": "StorageGroup Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
[] http get: url (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51)

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "@odata.type": "#StorageGroup.v1_5_0.StorageGroup",
    "AccessState": "Optimized",
    "Description": "Volume Mapping Information",
    "Id": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "MappedVolumes": [
        {
            "AccessCapability": "ReadWrite",
            "LogicalUnitNumber": "1",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
            }
        }
    ],
    "Name": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        }
    ],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "VolumesAreExposed": true
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section11">(11) Update a Volume</a>
[//]: <> (================================================================================================================================================================)

You can update a Volume using an HTTP PATCH operation. In the JSON data passed to the Redfish Service, include a new name
such as: **{ "Name": "NewAVolume01" }**. The new name will be visible in the returned JSON data.

```
(redfish) http get /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
[] http get: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900003d83f16101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff54605900003d83f16101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}


(redfish) http patch /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000 { "Name": "NewAVolume01" }
(redfish) http patch /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000 { "Name": "NewAVolume01" }
[] http patch: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000)
[[ POST DATA (/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000) ]]
{
    "Name": "NewAVolume01"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1834'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "AccessCapabilities": [
        "Read",
        "Write"
    ],
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff54605900003d83f16101000000",
            "Name": "NewAVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff54605900003d83f16101000000",
    "Name": "NewAVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section12">(12) Update Volume Mapping</a>
[//]: <> (================================================================================================================================================================)

There are a number of actions that can be performed on a StorageGroup to update the mapping of a volume.

### Change Logical Unit Number (LUN)

Perform a HTTP PATCH on a StorageGroup URI passing a new LogicalUnitNumber to update the LUN of the StorageGroup. The JSON response
data will contain the same data as a GET /redfish/v1/Storage/{StorageId}/StorageGroups/{StorageGroupId}. In this example, the LUN is changed
from **1** to **111** as is seen in the JSON data below.

**Note:** This revision requires that LogicalUnitNumber be a string.

For this operation, the JSON data needed for the operation is stored in a text file called **patch_sg_lun_1a.json**. See below.

```
{
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111"
        }
    ]
}
```

Now perform the PATCH operation.

```
(redfish) http patch /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51 json/patch_sg_lun_1a.json
[] http patch: url (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51)
[[ POST DATA (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51) ]]
{
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111"
        }
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1719'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "@odata.type": "#StorageGroup.v1_5_0.StorageGroup",
    "AccessState": "Optimized",
    "Description": "Volume Mapping Information",
    "Id": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "MappedVolumes": [
        {
            "AccessCapability": "ReadWrite",
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
            }
        }
    ],
    "Name": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B3"
        }
    ],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "VolumesAreExposed": true
}
```

### Change Ports

Perform a PATCH on a StorageGroup URI passing an array of ServerEndpointGroups to update the ports of the StorageGroup. For this operation, 
the JSON data needed for the operation is stored in a text file called **patch_sg_ports_A0-B0.json**. See below.

```
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        }
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111"
        }
    ]
}
```

Now perform the PATCH operation after getting the current details of the StorageGroup. Notice how the property **ServerEndpointGroups** has
been updated to contain only two ports.

```
(redfish) http patch /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51 json/patch_sg_ports_A0-B0.json
[] http patch: url (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51)
[[ POST DATA (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51) ]]
{
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        }
    ],
    "MappedVolumes": [
        {
            "LogicalUnitNumber": "111"
        }
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1125'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "@odata.type": "#StorageGroup.v1_5_0.StorageGroup",
    "AccessState": "Optimized",
    "Description": "Volume Mapping Information",
    "Id": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "MappedVolumes": [
        {
            "AccessCapability": "ReadWrite",
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
            }
        }
    ],
    "Name": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        }
    ],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "VolumesAreExposed": true
}
```

### Change Access

Perform a PATCH on a StorageGroup URI passing a new AccessCapabilities to update the access capabilities of the StorageGroup. 
The JSON response data will contain the same data as a GET /redfish/v1/Storage/{StorageId}/StorageGroups/{StorageGroupId}.

For this operation, the JSON data needed for the operation is stored in a text file called **patch_sg_access_readonly_1.json**. See below.

```
{
    "MappedVolumes": [
        {
            "AccessCapability": "Read",
            "LogicalUnitNumber": "111"
        }
    ]
}
```

Now perform the PATCH operation after getting the current details of the StorageGroup. Notice how the property **AccessCapabilities** has
been updated to be read-only.

```
(redfish) http patch /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51 json/patch_sg_access_readonly_1.json
[] http patch: url (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51)
[[ POST DATA (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51) ]]
{
    "MappedVolumes": [
        {
            "AccessCapability": "Read",
            "LogicalUnitNumber": "111"
        }
    ]
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1714'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#StorageGroup.StorageGroup",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "@odata.type": "#StorageGroup.v1_5_0.StorageGroup",
    "AccessState": "Optimized",
    "Description": "Volume Mapping Information",
    "Id": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "MappedVolumes": [
        {
            "AccessCapability": "Read",
            "LogicalUnitNumber": "111",
            "Volume": {
                "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
            }
        }
    ],
    "Name": "00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51",
    "ServerEndpointGroups": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B3"
        }
    ],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "VolumesAreExposed": true
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section13">(13) Delete a StorageGroup or Unmap a Volume</a>
[//]: <> (================================================================================================================================================================)

The HTTP DELETE request is used to delete a StorageGroup. You delete a StorageGroup by using its identifier. No request properties
are specified in the request body, simply use the correct URI. Use HTTP GET **/redfish/v1/Storage/{StorageId}/StorageGroups** to view the
identifiers and URIs of all existing StorageGroups.

**Note:** After deleting a StorageGroup, that volume will no longer be visible to the host system.

```
(redfish) http get /redfish/v1/Storage/controller_a/StorageGroups
[] http get: url (/redfish/v1/Storage/controller_a/StorageGroups)

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51"
        }
    ],
    "Members@odata.count": 1,
    "Name": "StorageGroup Collection"
}


(redfish) http delete /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
[] http delete: url (/redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51)

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups/00c0ff54605900003d83f16101000000_iqn.1994-05.com.redhat:csi-lab-51
 [] Status     : 200
 [] Reason     : OK


(redfish) http get /redfish/v1/Storage/controller_a/StorageGroups
[] http get: url (/redfish/v1/Storage/controller_a/StorageGroups)

 [] URL        : /redfish/v1/Storage/controller_a/StorageGroups
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StorageGroupCollection.StorageGroupCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups",
    "@odata.type": "#StorageGroupCollection.StorageGroupCollection",
    "Members": [],
    "Members@odata.count": 0,
    "Name": "StorageGroup Collection"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section14">(14) Delete a Volume</a>
[//]: <> (================================================================================================================================================================)

Use the Volume entity and HTTP DELETE operation to delete a volume. A list of current volumes should be used to obtain the full URI to the volume
that you want to delete. After you delete the volume, use HTTP GET on Volumes to verify that the volume is no longer reported.

```
(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Volume Collection"
}


(redfish) http delete /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
[] http delete: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff54605900003d83f16101000000
 [] Status     : 200
 [] Reason     : OK



(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [],
    "Members@odata.count": 0,
    "Name": "Volume Collection"
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section15">(15) Delete a Disk Group or Pool using StoragePool</a>
[//]: <> (================================================================================================================================================================)

Use the StoragePool entity and HTTP DELETE operation to delete a disk group or pool. A list of current StoragePools should be used to obtain the 
full URI to the disk group or pool that you want to delete. After you delete the entity, use HTTP GET on StoragePools to verify that the entity
is no longer reported.

**Note:*** When you delete a pool, all disk groups will be automatically deleted.

```
(redfish) http get /redfish/v1/Storage/controller_a/StoragePools
[] http get: url (/redfish/v1/Storage/controller_a/StoragePools)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/dgA01"
        }
    ],
    "Members@odata.count": 2,
    "Name": "StoragePool Collection"
}


(redfish) http delete /redfish/v1/Storage/controller_a/StoragePools/A
[] http delete: url (/redfish/v1/Storage/controller_a/StoragePools/A)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools/A
 [] Status     : 200
 [] Reason     : OK


(redfish) http get /redfish/v1/Storage/controller_a/StoragePools
[] http get: url (/redfish/v1/Storage/controller_a/StoragePools)

 [] URL        : /redfish/v1/Storage/controller_a/StoragePools
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
    "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
    "Members": [],
    "Members@odata.count": 0,
    "Name": "StoragePool Collection"
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section16">(16) Toggle Drive Identification LED</a>
[//]: <> (================================================================================================================================================================)

The Drive resource and an HTTP PATCH operation is used to update the **LocationIndicatorActive** parameter, turning a disk drive's LED on or off using a boolean value.

Use HTTP GET operations to see a list of drives and then retrieve details on a single drive. Then use HTTP PATCH to turn the LED on and then off.

Here is the JSON data for these operation, please note that LocationIndicatorActive value is a boolean, not a string:
- `{ "LocationIndicatorActive": true }`
- `{ "LocationIndicatorActive": false }`

```
(redfish) http get /redfish/v1/Storage/controller_a/Drives
[output omitted]


(redfish) http patch /redfish/v1/Storage/controller_a/Drives/0.0 { "LocationIndicatorActive": true }
[] http patch: url (/redfish/v1/Storage/controller_a/Drives/0.0)
[[ POST DATA (/redfish/v1/Storage/controller_a/Drives/0.0) ]]
{
    "LocationIndicatorActive": true
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Drives/0.0
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1210'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Drive.Drive",
    "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0",
    "@odata.type": "#Drive.v1_12_0.Drive",
    "BlockSizeBytes": 512,
    "CapacityBytes": 1800360124416,
    "EncryptionAbility": "None",
    "EncryptionStatus": "Unecrypted",
    "FailurePredicted": false,
    "Id": "WBN01JLC0000E813EPRP",
    "Identifiers": [
        {
            "DurableName": "disk_00.00",
            "DurableNameFormat": "NAA"
        }
    ],
    "Links": {
        "Chassis": {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0"
        }
    },
    "LocationIndicatorActive": true,
    "Manufacturer": "SEAGATE",
    "MediaType": "HDD",
    "Name": "0.0",
    "NegotiatedSpeedGbs": 12.0,
    "PartNumber": "ST1800MM0129",
    "PhysicalLocation": {
        "PartLocation": {
            "LocationOrdinalValue": 0,
            "LocationType": "Slot"
        },
        "Placement": {
            "Rack": "0",
            "RackOffset": 0
        }
    },
    "Protocol": "SAS",
    "Revision": "C003",
    "RotationSpeedRPM": 10000,
    "SerialNumber": "WBN01JLC0000E813EPRP",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}


(redfish) http patch /redfish/v1/Storage/controller_a/Drives/0.0 { "LocationIndicatorActive": false }
[] http patch: url (/redfish/v1/Storage/controller_a/Drives/0.0)
[[ POST DATA (/redfish/v1/Storage/controller_a/Drives/0.0) ]]
{
    "LocationIndicatorActive": false
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Drives/0.0
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1211'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Drive.Drive",
    "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0",
    "@odata.type": "#Drive.v1_12_0.Drive",
    "BlockSizeBytes": 512,
    "CapacityBytes": 1800360124416,
    "EncryptionAbility": "None",
    "EncryptionStatus": "Unecrypted",
    "FailurePredicted": false,
    "Id": "WBN01JLC0000E813EPRP",
    "Identifiers": [
        {
            "DurableName": "disk_00.00",
            "DurableNameFormat": "NAA"
        }
    ],
    "Links": {
        "Chassis": {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0"
        }
    },
    "LocationIndicatorActive": false,
    "Manufacturer": "SEAGATE",
    "MediaType": "HDD",
    "Name": "0.0",
    "NegotiatedSpeedGbs": 12.0,
    "PartNumber": "ST1800MM0129",
    "PhysicalLocation": {
        "PartLocation": {
            "LocationOrdinalValue": 0,
            "LocationType": "Slot"
        },
        "Placement": {
            "Rack": "0",
            "RackOffset": 0
        }
    },
    "Protocol": "SAS",
    "Revision": "C003",
    "RotationSpeedRPM": 10000,
    "SerialNumber": "WBN01JLC0000E813EPRP",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}


(redfish) http get /redfish/v1/Storage/controller_a/Drives/0.0
[] http get: url (/redfish/v1/Storage/controller_a/Drives/0.0)

 [] URL        : /redfish/v1/Storage/controller_a/Drives/0.0
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Drive.Drive",
    "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0",
    "@odata.type": "#Drive.v1_12_0.Drive",
    "BlockSizeBytes": 512,
    "CapacityBytes": 1800360124416,
    "EncryptionAbility": "None",
    "EncryptionStatus": "Unecrypted",
    "FailurePredicted": false,
    "Id": "WBN01JLC0000E813EPRP",
    "Identifiers": [
        {
            "DurableName": "disk_00.00",
            "DurableNameFormat": "NAA"
        }
    ],
    "Links": {
        "Chassis": {
            "@odata.id": "/redfish/v1/Chassis/enclosure_0"
        }
    },
    "LocationIndicatorActive": false,
    "Manufacturer": "SEAGATE",
    "MediaType": "HDD",
    "Name": "0.0",
    "NegotiatedSpeedGbs": 12.0,
    "PartNumber": "ST1800MM0129",
    "PhysicalLocation": {
        "PartLocation": {
            "LocationOrdinalValue": 0,
            "LocationType": "Slot"
        },
        "Placement": {
            "Rack": "0",
            "RackOffset": 0
        }
    },
    "Protocol": "SAS",
    "Revision": "C003",
    "RotationSpeedRPM": 10000,
    "SerialNumber": "WBN01JLC0000E813EPRP",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section17">(17) Enable|Disable Background Scrub</a>
[//]: <> (================================================================================================================================================================)

The **Storage** resource and an HTTP PATCH operation is used to update the **DiskAdvancedSettings** settings for background disk scrub and background disk group scrub.
This operation can update two parameters:
- BackgroundDiskGroupScrub can be "Enabled" or "Disabled"
- BackgroundDiskScrub can be "Enabled" or "Disabled"

Here is the JSON data for these operation:
- `{ "Oem": { "Seagate": { "DiskAdvancedSettings": { "BackgroundDiskGroupScrub": "Enabled", "BackgroundDiskScrub": "Enabled" } } } }`
- `{ "Oem": { "Seagate": {"DiskAdvancedSettings": { "BackgroundDiskGroupScrub": "Disabled", "BackgroundDiskScrub": "Disabled" } } } }`

The following example turns on these services and then turns them off.

```
(redfish) http patch /redfish/v1/Storage/controller_a { "Oem": { "Seagate": { "DiskAdvancedSettings": { "BackgroundDiskGroupScrub": "Enabled", "BackgroundDiskScrub": "Enabled" } } } }
[] http patch: url (/redfish/v1/Storage/controller_a)
[[ POST DATA (/redfish/v1/Storage/controller_a) ]]
{
    "Oem": {
        "Seagate": {
            "DiskAdvancedSettings": {
                "BackgroundDiskGroupScrub": "Enabled",
                "BackgroundDiskScrub": "Enabled"
            }
        }
    }
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '4367'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
    "@odata.id": "/redfish/v1/Storage/controller_a",
    "@odata.type": "#Storage.v1_10_0.Storage",
    "Drives": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.4"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.5"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.6"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.7"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.8"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.9"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.10"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.11"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.12"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.13"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.14"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.15"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.16"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.17"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.18"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.19"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.20"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.21"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.22"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.23"
        }
    ],
    "EndpointGroups": {
        "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups"
    },
    "Id": "A",
    "Name": "controller_a",
    "Oem": {
        "Seagate": {
            "DiskAdvancedSettings": {
                "BackgroundDiskGroupScrub": "Enabled",
                "BackgroundDiskScrub": "Enabled",
                "ValidScrubSettings": [
                    "Enabled",
                    "Disabled",
                    "On",
                    "Off"
                ]
            }
        }
    },
    "Redundancy": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a#/Redundancy/0",
            "MaxNumSupported": 2,
            "MemberId": "A",
            "MinNumNeeded": 1,
            "Mode": "Sharing",
            "Name": "Controller Redundancy Group 1",
            "RedundancySet": [
                {
                    "@odata.id": "/redfish/v1/Storage/controller_a"
                },
                {
                    "@odata.id": "/redfish/v1/Storage/controller_b"
                }
            ],
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Status": {
        "Health": "OK"
    },
    "StorageControllers": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a#/StorageControllers/0",
            "Manufacturer": "SEAGATE",
            "MemberId": "A",
            "Name": "controller_a",
            "SerialNumber": "00C0FF546059",
            "Status": {
                "Health": "OK"
            },
            "SupportedControllerProtocols": [
                "iSCSI"
            ]
        }
    ],
    "StorageGroups": {
        "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups"
    },
    "StoragePools": {
        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools"
    },
    "Volumes": {
        "@odata.id": "/redfish/v1/Storage/controller_a/Volumes"
    }
}


(redfish) http patch /redfish/v1/Storage/controller_a { "Oem": { "Seagate": { "DiskAdvancedSettings": { "BackgroundDiskGroupScrub": "Disabled", "BackgroundDiskScrub": "Disabled" } } } }
[] http patch: url (/redfish/v1/Storage/controller_a)
[[ POST DATA (/redfish/v1/Storage/controller_a) ]]
{
    "Oem": {
        "Seagate": {
            "DiskAdvancedSettings": {
                "BackgroundDiskGroupScrub": "Disabled",
                "BackgroundDiskScrub": "Disabled"
            }
        }
    }
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '4369'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Storage.Storage",
    "@odata.id": "/redfish/v1/Storage/controller_a",
    "@odata.type": "#Storage.v1_10_0.Storage",
    "Drives": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.0"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.1"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.2"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.3"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.4"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.5"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.6"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.7"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.8"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.9"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.10"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.11"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.12"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.13"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.14"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.15"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.16"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.17"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.18"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.19"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.20"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.21"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.22"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Drives/0.23"
        }
    ],
    "EndpointGroups": {
        "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups"
    },
    "Id": "A",
    "Name": "controller_a",
    "Oem": {
        "Seagate": {
            "DiskAdvancedSettings": {
                "BackgroundDiskGroupScrub": "Disabled",
                "BackgroundDiskScrub": "Disabled",
                "ValidScrubSettings": [
                    "Enabled",
                    "Disabled",
                    "On",
                    "Off"
                ]
            }
        }
    },
    "Redundancy": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a#/Redundancy/0",
            "MaxNumSupported": 2,
            "MemberId": "A",
            "MinNumNeeded": 1,
            "Mode": "Sharing",
            "Name": "Controller Redundancy Group 1",
            "RedundancySet": [
                {
                    "@odata.id": "/redfish/v1/Storage/controller_a"
                },
                {
                    "@odata.id": "/redfish/v1/Storage/controller_b"
                }
            ],
            "Status": {
                "Health": "OK",
                "State": "Enabled"
            }
        }
    ],
    "Status": {
        "Health": "OK"
    },
    "StorageControllers": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a#/StorageControllers/0",
            "Manufacturer": "SEAGATE",
            "MemberId": "A",
            "Name": "controller_a",
            "SerialNumber": "00C0FF546059",
            "Status": {
                "Health": "OK"
            },
            "SupportedControllerProtocols": [
                "iSCSI"
            ]
        }
    ],
    "StorageGroups": {
        "@odata.id": "/redfish/v1/Storage/controller_a/StorageGroups"
    },
    "StoragePools": {
        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools"
    },
    "Volumes": {
        "@odata.id": "/redfish/v1/Storage/controller_a/Volumes"
    }
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section18">(18) Toggle Write-back/Write-through Capability</a>
[//]: <> (================================================================================================================================================================)

Use the Volume entity and the HTTP PATCH operation to update a volume's write-back vs write-through caching policy. A list of current volumes should be used to obtain
the full URI to the volume that you want to update. After you update the volume, use HTTP GET on the Volume to verify the updated parameter. The `Name` parameter is used
to retrieve the Volume information after the update.

Here is the JSON data for these operation, where `<name>` is replaced with the correct volume name>:
- `{ "Name": "<name>", "WriteCachePolicy": "UnprotectedWriteBack" }`
- `{ "Name": "<name>", "WriteCachePolicy": "WriteThrough" }`

```
(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Volume Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000
[] http get: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff5460590000f2a9f76101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff5460590000f2a9f76101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}

(redfish) http patch /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000 { "Name": "AVolume01", "WriteCachePolicy": "WriteThrough" }
[] http patch: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000)
[[ POST DATA (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000) ]]
{
    "Name": "AVolume01",
    "WriteCachePolicy": "WriteThrough"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1753'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff5460590000f2a9f76101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff5460590000f2a9f76101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "WriteThrough"
}


(redfish) http patch /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000 { "Name": "AVolume01", "WriteCachePolicy": "UnprotectedWriteBack" }
[] http patch: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000)
[[ POST DATA (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000) ]]
{
    "Name": "AVolume01",
    "WriteCachePolicy": "UnprotectedWriteBack"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1761'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff5460590000f2a9f76101000000",
            "Name": "AVolume01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff5460590000f2a9f76101000000",
    "Name": "AVolume01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section19">(19) Create Account</a>
[//]: <> (================================================================================================================================================================)

The AccountService resources is used to list current Accounts and also create new accounts. The first step is to list existing Accounts, then use HTTP POST to
/redfish/v1/AccountService/Accounts to create a new account, then list the details of the newly created account. When creating a new account, the password must follow
the requirements listed for the MC API.

HTTP commands and URIs used:
- http get /redfish/v1/AccountService/Accounts
- http post /redfish/v1/AccountService/Accounts { "UserName": "`<username>`", "Password": "`<password>`" }
- http get /redfish/v1/AccountService/Accounts/{NewAccountId}

```
(redfish) http get /redfish/v1/AccountService/Accounts
[] http get: url (/redfish/v1/AccountService/Accounts)

 [] URL        : /redfish/v1/AccountService/Accounts
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ManagerAccountCollection.ManagerAccountCollection",
    "@odata.id": "/redfish/v1/AccountService/Accounts",
    "@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/AccountService/Accounts/manage"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Account Collection"
}


(redfish) http post /redfish/v1/AccountService/Accounts { "UserName": "manage2", "Password": "Manager2!" }
[] http post: url (/redfish/v1/AccountService/Accounts)
[[ POST DATA (/redfish/v1/AccountService/Accounts) ]]
{
    "UserName": "manage2",
    "Password": "Manager2!"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/AccountService/Accounts
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '456'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
    "@odata.id": "/redfish/v1/AccountService/Accounts",
    "@odata.type": "#ManagerAccount.v1_8_0.ManagerAccount",
    "AccountTypes": [
        "ManagerConsole"
    ],
    "Description": "User Account",
    "Enabled": true,
    "Id": "manage2",
    "Locked": false,
    "Name": "User Account",
    "Password": "Manager2!",
    "RoleId": "monitor",
    "UserName": "manage2"
}


(redfish) http get /redfish/v1/AccountService/Accounts/manager2
[] http get: url (/redfish/v1/AccountService/Accounts/manager2)

 [] URL        : /redfish/v1/AccountService/Accounts/manager2
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ManagerAccount.ManagerAccount",
    "@odata.id": "/redfish/v1/AccountService/Accounts/manager2",
    "@odata.type": "#ManagerAccount.v1_8_0.ManagerAccount"
}


(redfish) http get /redfish/v1/AccountService/Accounts/
[] http get: url (/redfish/v1/AccountService/Accounts/)

 [] URL        : /redfish/v1/AccountService/Accounts/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ManagerAccountCollection.ManagerAccountCollection",
    "@odata.id": "/redfish/v1/AccountService/Accounts",
    "@odata.type": "#ManagerAccountCollection.ManagerAccountCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/AccountService/Accounts/manage"
        },
        {
            "@odata.id": "/redfish/v1/AccountService/Accounts/manage2"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Account Collection"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section20">(20) Change Account Password</a>
[//]: <> (================================================================================================================================================================)

The AccountService resources is also used to update the password for an account. Use HTTP PATCH to /redfish/v1/AccountService/Accounts/{AccountId} to change the password
for that Account.

HTTP commands and URIs used:
- http patch /redfish/v1/AccountService/Accounts/{AccountId} { "Password": "`<new-password>`" }

```
(redfish) http patch /redfish/v1/AccountService/Accounts/manage2 { "Password": "Manager2New!" }
[] http patch: url (/redfish/v1/AccountService/Accounts/manage2)
[[ POST DATA (/redfish/v1/AccountService/Accounts/manage2) ]]
{
    "Password": "Manager2New!"
}
[[ POST DATA END ]]

 [] URL        : /redfish/v1/AccountService/Accounts/manage2
 [] Status     : 200
 [] Reason     : OK

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '912'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]
```

[//]: <> (================================================================================================================================================================)
## <a name="section21">(21) Show Fabrics</a>
[//]: <> (================================================================================================================================================================)

The Fabrics resource is used to explore the various fabric connections supported by the controller running the Redfish Service. Use HTTP GET operations to traverse the
resource and discover Fabric elements.

The following commands were executed on a system to give a sense for Fabric resources.
- http get /redfish/v1/Fabrics
- http get /redfish/v1/Fabrics/{FabricId}
- http get /redfish/v1/Fabrics/{FabricId}/Endpoints

```
(redfish) http get /redfish/v1/Fabrics
[] http get: url (/redfish/v1/Fabrics)

 [] URL        : /redfish/v1/Fabrics
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#FabricCollection.FabricCollection",
    "@odata.id": "/redfish/v1/Fabrics",
    "@odata.type": "#FabricCollection.FabricCollection",
    "Description": "List of fabrics presented to host",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI"
        }
    ],
    "Members@odata.count": 1,
    "Name": "Fabric Collection"
}


(redfish) http get /redfish/v1/Fabrics/iSCSI
[] http get: url (/redfish/v1/Fabrics/iSCSI)

 [] URL        : /redfish/v1/Fabrics/iSCSI
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Fabric.Fabric",
    "@odata.id": "/redfish/v1/Fabrics/iSCSI",
    "@odata.type": "#Fabric.v1_2_1.Fabric",
    "Description": "An iSCSI fabric with ports",
    "Endpoints": {
        "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints"
    },
    "FabricType": "iSCSI",
    "Id": "iSCSI",
    "Name": "iSCSI Fabric",
    "Status": {
        "HealthRollup": "OK",
        "State": "Enabled"
    }
}


(redfish) http get /redfish/v1/Fabrics/iSCSI/Endpoints
[] http get: url (/redfish/v1/Fabrics/iSCSI/Endpoints)

 [] URL        : /redfish/v1/Fabrics/iSCSI/Endpoints
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EndpointCollection.EndpointCollection",
    "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints",
    "@odata.type": "#EndpointCollection.EndpointCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/A0"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/A1"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/A2"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/A3"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/B0"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/B1"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/B2"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/B3"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/iqn.1994-05.com.redhat:csi-lab-51"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/iqn.1993-08.org.debian:01:112233abcde"
        },
        {
            "@odata.id": "/redfish/v1/Fabrics/iSCSI/Endpoints/iqn.1993-08.org.debian:01:f09ec67ce4f5"
        }
    ],
    "Members@odata.count": 11,
    "Name": "Endpoint Collection"
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section22">(22) Compose Volume</a>
[//]: <> (================================================================================================================================================================)

The CompositionService is used to compose a volume in a single step. The process of composing a volume requires a number of parameters in order to create a storage
pool, create a volume, and map that volume. The CompositionService is also used to discover available ResourceBlocks and ResourceZones.

Use HTTP GET operations to discover ResourceBlocks, ResourceZones and Capabilities, then use an HTP POST operation to compose a volume. The Capabilities resource defines
the parameters required for volume composition.

HTTP Commands:
- Step 1: Discovery
  - http get /redfish/v1/CompositionService
  - http get /redfish/v1/CompositionService/ResourceZones
  - http get /redfish/v1/CompositionService/ResourceZones/{ZoneId}
  - http get /redfish/v1/CompositionService/ResourceBlocks
  - http get /redfish/v1/CompositionService/ResourceBlocks/{ResourceBlockId}
  - http get /redfish/v1/Systems/Capabilities
- Step 2: Composition
  - http post /redfish/v1/Systems `{JSON DATA}`
  - http get /redfish/v1/CompositionService/ResourceBlocks/
- Step 3: Delete Composed Volume
  - http delete /redfish/v1/CompositionService/ResourceBlocks/{VolumeId}

Here is the `compose_volume4.json` contents used for this example. The actual values used will vary from system to system. Also note that the resources must be available before a volume can be composed.

```
{
    "Name": "ComposedVolumeA01",
    "Description": "Composed Volume A01",
    "RAIDType": "RAID6",
    "CapacityBytes": 2000000000,
    "LogicalUnitNumber": 0,

    "AccessCapabilities": [
        "Read",
        "Write"
    ],

    "Links": {
        "ClientEndpointGroups": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/500605b00db9a070"
            }
        ],
        "ResourceBlocks": [
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.1"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.2"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.3"
            }
        ],
        "ServerEndpointGroups": [
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A0"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/A1"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B0"
            },
            {
                "@odata.id": "/redfish/v1/Storage/controller_a/EndpointGroups/B1"
            }
        ]
    }
}
```

### Step 1: Discovery

Example commands and output:

```
(redfish) http get /redfish/v1/CompositionService
[] http get: url (/redfish/v1/CompositionService)

 [] URL        : /redfish/v1/CompositionService
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#CompositionService.CompositionService",
    "@odata.id": "/redfish/v1/CompositionService",
    "@odata.type": "#CompositionService.v1_1_2.CompositionService",
    "AllowOverprovisioning": true,
    "AllowZoneAffinity": false,
    "Id": "CompositionService",
    "Name": "Composition Service",
    "ResourceBlocks": {
        "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks"
    },
    "ResourceZones": {
        "@odata.id": "/redfish/v1/CompositionService/ResourceZones"
    },
    "ServiceEnabled": true,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/CompositionService/ResourceZones
[] http get: url (/redfish/v1/CompositionService/ResourceZones)

 [] URL        : /redfish/v1/CompositionService/ResourceZones
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ZoneCollection.ZoneCollection",
    "@odata.id": "/redfish/v1/CompositionService/ResourceZones",
    "@odata.type": "#ZoneCollection.ZoneCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceZones/HDD"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceZones/SSD"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Zone Collection"
}

(redfish) http get /redfish/v1/CompositionService/ResourceZones/SSD
[] http get: url (/redfish/v1/CompositionService/ResourceZones/SSD)

 [] URL        : /redfish/v1/CompositionService/ResourceZones/SSD
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@Redfish.CollectionCapabilities": {
        "@odata.type": "#CollectionCapabilities.v1_2_2.CollectionCapabilities",
        "Capabilities": [
            {
                "CapabilitiesObject": {
                    "@odata.id": "/redfish/v1/Systems/Capabilities"
                },
                "Links": {
                    "TargetCollection": {
                        "@odata.id": "/redfish/v1/Systems"
                    }
                },
                "UseCase": "VolumeCreation"
            }
        ]
    },
    "@odata.context": "/redfish/v1/$metadata#Zone.Zone",
    "@odata.id": "/redfish/v1/CompositionService/ResourceZones/SSD",
    "@odata.type": "#Zone.v1_6_0.Zone",
    "Id": "SSD",
    "Links": {
        "ResourceBlocks": []
    },
    "Name": "Resource Zone SSD",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/CompositionService/ResourceZones/HDD
[] http get: url (/redfish/v1/CompositionService/ResourceZones/HDD)

 [] URL        : /redfish/v1/CompositionService/ResourceZones/HDD
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@Redfish.CollectionCapabilities": {
        "@odata.type": "#CollectionCapabilities.v1_2_2.CollectionCapabilities",
        "Capabilities": [
            {
                "CapabilitiesObject": {
                    "@odata.id": "/redfish/v1/Systems/Capabilities"
                },
                "Links": {
                    "TargetCollection": {
                        "@odata.id": "/redfish/v1/Systems"
                    }
                },
                "UseCase": "VolumeCreation"
            }
        ]
    },
    "@odata.context": "/redfish/v1/$metadata#Zone.Zone",
    "@odata.id": "/redfish/v1/CompositionService/ResourceZones/HDD",
    "@odata.type": "#Zone.v1_6_0.Zone",
    "Id": "HDD",
    "Links": {
        "ResourceBlocks": [
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.1"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.2"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.3"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.4"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.5"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.6"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.7"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.8"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.9"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.10"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.11"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.12"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.13"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.14"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.15"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.16"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.17"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.18"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.19"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.20"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.21"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.22"
            },
            {
                "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.23"
            }
        ]
    },
    "Name": "Resource Zone HDD",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/CompositionService/ResourceBlocks
[] http get: url (/redfish/v1/CompositionService/ResourceBlocks)

 [] URL        : /redfish/v1/CompositionService/ResourceBlocks
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ResourceBlockCollection.ResourceBlockCollection",
    "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks",
    "@odata.type": "#ResourceBlockCollection.ResourceBlockCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.1"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.2"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.3"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.4"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.5"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.6"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.7"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.8"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.9"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.10"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.11"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.12"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.13"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.14"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.15"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.16"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.17"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.18"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.19"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.20"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.21"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.22"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.23"
        }
    ],
    "Members@odata.count": 24,
    "Name": "ResourceBlock Collection"
}

(redfish) http get /redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0
[] http get: url (/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0)

 [] URL        : /redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ResourceBlock.ResourceBlock",
    "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0",
    "@odata.type": "#ResourceBlock.v1_3_4.ResourceBlock",
    "CompositionStatus": {
        "CompositionState": "Unused"
    },
    "Drives": [
        {
            "@odata.id": "/redfish/v1/Systems/DHSIFTJ-1852437ED5/Storage/controller_a/Drives/0.0"
        }
    ],
    "Id": "WAF0PKT90000E8399LVL",
    "Name": "0.0",
    "ResourceBlockType": [
        "Storage"
    ],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/Systems/Capabilities
[] http get: url (/redfish/v1/Systems/Capabilities)

 [] URL        : /redfish/v1/Systems/Capabilities
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Systems/Capabilities",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "AccessCapabilities@Redfish.RequiredOnCreate": false,
    "AccessCapabilities@Redfish.SetOnlyOnCreate": true,
    "AllocatedPools@Redfish.RequiredOnCreate": false,
    "AllocatedPools@Redfish.SetOnlyOnCreate": true,
    "CapacityBytes@Redfish.RequiredOnCreate": false,
    "CapacityBytes@Redfish.SetOnlyOnCreate": true,
    "Description@Redfish.RequiredOnCreate": false,
    "Description@Redfish.SetOnlyOnCreate": true,
    "Id": "VolumeCapabilities",
    "Links": {
        "ClientEndpoints@Redfish.RequiredOnCreate": true,
        "ClientEndpoints@Redfish.SetOnlyOnCreate": true,
        "ServerEndpoints@Redfish.RequiredOnCreate": false,
        "ServerEndpoints@Redfish.SetOnlyOnCreate": true
    },
    "LogicalUnitNumber@Redfish.RequiredOnCreate": true,
    "LogicalUnitNumber@Redfish.SetOnlyOnCreate": true,
    "Name": "POST requirements for Composing a Volume",
    "Name@Redfish.RequiredOnCreate": true,
    "Name@Redfish.SetOnlyOnCreate": true,
    "RAIDType@Redfish.RequiredOnCreate": true,
    "RAIDType@Redfish.SetOnlyOnCreate": true,
    "ResourceBlocks@Redfish.RequiredOnCreate": true,
    "ResourceBlocks@Redfish.SetOnlyOnCreate": true
}
```

### Step 2: Composition
```
(redfish) http post /redfish/v1/Systems json/compose_volume4.json
[] http post: url (/redfish/v1/Systems)

 [] URL        : /redfish/v1/Systems
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '1764'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_b/Volumes/ComposedVolumeA01",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 1996488704,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_b/Volumes/ComposedVolumeA01#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff5112540000d8edf76101000000",
            "Name": "ComposedVolumeA01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/redfish/v1/redfish/v1/Storage/controller_b",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/redfish/v1/redfish/v1/Storage/controller_b/B"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff5112540000d8edf76101000000",
    "Name": "ComposedVolumeA01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}


(redfish) http get /redfish/v1/CompositionService/ResourceBlocks/
[] http get: url (/redfish/v1/CompositionService/ResourceBlocks/)

 [] URL        : /redfish/v1/CompositionService/ResourceBlocks/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ResourceBlockCollection.ResourceBlockCollection",
    "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks",
    "@odata.type": "#ResourceBlockCollection.ResourceBlockCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.0"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.1"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.2"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.3"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.4"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.5"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.6"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.7"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.8"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.9"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.10"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.11"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.12"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.13"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.14"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.15"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.16"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.17"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.18"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.19"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.20"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.21"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.22"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/DriveBlock-0.23"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/StoragePoolBlock-B"
        },
        {
            "@odata.id": "/redfish/v1/CompositionService/ResourceBlocks/VolumeBlock-00c0ff5112540000d8edf76101000000"
        }
    ],
    "Members@odata.count": 26,
    "Name": "ResourceBlock Collection"
}
```

### Step 3: Delete Composed Volume

```
(redfish) http delete /redfish/v1/CompositionService/ResourceBlocks/VolumeBlock-00c0ff5112540000d8edf76101000000
[] http delete: url (/redfish/v1/CompositionService/ResourceBlocks/VolumeBlock-00c0ff5112540000d8edf76101000000)

 [] URL        : /redfish/v1/CompositionService/ResourceBlocks/VolumeBlock-00c0ff5112540000d8edf76101000000
 [] Status     : 200
 [] Reason     : OK
```


[//]: <> (================================================================================================================================================================)
## <a name="section23">(23) Update Controller Firmware</a>
[//]: <> (================================================================================================================================================================)

Redfish clients can use the Redfish service to update controller firmware using the **UpdateService** resource. The Update Services allows a client to upload a new
firmware bundle to the storage controller and retrieve current firmware bundle information.

The HTTP POST command requires HTTP multipart form-data which is more complicated to do via a command line, so this example relies on the SystemsRedfishPy `http push`
command along with JSON data to create the multipart form data. This command can take several minutes to transfer a large image bundle.

The `http get /redfish/v1` command is used to determine the **RedfishServiceVersion** to validate the firmware image update, before and after the firmware update.

**Note:** Any active HTTP session will be reset by the controller reboot and you must re-establish a session with the Redfish Service. The actual reboot time, when
the Redfish Service continues to allow sessions, will vary but may take 2-3 minutes.

HTTP Commands:
- Step 1: Discovery
  - http get /redfish/v1
  - http get /redfish/v1/UpdateService
  - http get /redfish/v1/UpdateService/FirmwareInventory
  - http get /redfish/v1/UpdateService/FirmwareInventory/{BundleId}
- Step 2: Firmware Upload
  - http push `<sfw file>` /redfish/v1/UpdateService/FWUpdate `{ "Targets": [], "@Redfish.OperationApplyTime": "Immediate" }`


JSON Data options:
- **Targets** is not used but must be included as an empty array []
- **@Redfish.OperationApplyTime** has two options: **Immediate** or **OnReset**


HTTP multipart/form-data example:
```
multipart/form-data; boundary=---------------------------d74496d66958873e
Content-Length: <computed-length>
Connection: keep-alive
X-Auth-Token: <session-auth-token>
-----------------------------d74496d66958873e
Content-Disposition: form-data; name="UpdateParameters"
Content-Type: application/json
{
"Targets": [],
"@Redfish.OperationApplyTime": "Immediate|OnReset"
}
-----------------------------d74496d66958873e
Content-Disposition: form-data; name="UpdateFile"; filename="<software-bundle.sfw>"
Content-Type: application/octet-stream
<software image binary>
```

### Step 1: Discovery

```
(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)

 [] URL        : /redfish/v1
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
    "@odata.id": "/redfish/v1",
    "@odata.type": "#ServiceRoot.v1_9_0.ServiceRoot",
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "CompositionService": {
        "@odata.id": "/redfish/v1/CompositionService"
    },
    "EventService": {
        "@odata.id": "/redfish/v1/EventService"
    },
    "Fabrics": {
        "@odata.id": "/redfish/v1/Fabrics"
    },
    "Id": "RootService",
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Name": "Root Service",
    "Oem": {
        "Seagate": {
            "RedfishServiceVersion": "2.4.20"
        }
    },
    "RedfishVersion": "1.12.0",
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Storage"
    },
    "Systems": {
        "@odata.id": "/redfish/v1/Systems"
    },
    "Tasks": {
        "@odata.id": "/redfish/v1/TaskService"
    },
    "UUID": "92384634-2938-2342-8820-489239905423",
    "UpdateService": {
        "@odata.id": "/redfish/v1/UpdateService"
    }
}

(redfish) http get /redfish/v1/UpdateService
[] http get: url (/redfish/v1/UpdateService)

 [] URL        : /redfish/v1/UpdateService
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#UpdateService.UpdateService",
    "@odata.id": "/redfish/v1/UpdateService",
    "@odata.type": "#UpdateService.v1_8_3.UpdateService",
    "Actions": {
        "#UpdateService.StartUpdate": {
            "Targets@Redfish.AllowableValues": "[]",
            "target": "/redfish/v1/UpdateService/Actions/UpdateService.StartUpdate",
            "title": "StartUpdate"
        }
    },
    "FirmwareInventory": {
        "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory"
    },
    "Id": "UpdateService",
    "MultipartHttpPushUri": "/redfish/v1/UpdateService/FWUpdate",
    "Name": "Update Service",
    "ServiceEnabled": true,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    }
}

(redfish) http get /redfish/v1/UpdateService/FirmwareInventory
[] http get: url (/redfish/v1/UpdateService/FirmwareInventory)

 [] URL        : /redfish/v1/UpdateService/FirmwareInventory
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventoryCollection.SoftwareInventoryCollection",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory",
    "@odata.type": "#SoftwareInventoryCollection.SoftwareInventoryCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_0"
        },
        {
            "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_1"
        }
    ],
    "Members@odata.count": 2,
    "Name": "FirmwareInventory Collection"
}

(redfish) http get /redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_0
[] http get: url (/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_0)

 [] URL        : /redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_0
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_0",
    "@odata.type": "#SoftwareInventory.v1_4_0.SoftwareInventory",
    "Id": "firmware-bundle_0",
    "Measurement": {
        "MeasurementSize": 32,
        "MeasurementSpecification": 1
    },
    "Name": "firmware-bundle",
    "ReleaseDate": "2022-01-25T19:19:03Z",
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Updateable": true,
    "Version": "I210A009e"
}

(redfish) http get /redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_1
[] http get: url (/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_1)

 [] URL        : /redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_1
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#SoftwareInventory.SoftwareInventory",
    "@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/firmware-bundle_1",
    "@odata.type": "#SoftwareInventory.v1_4_0.SoftwareInventory",
    "Id": "firmware-bundle_1",
    "Measurement": {
        "MeasurementSize": 32,
        "MeasurementSpecification": 1
    },
    "Name": "firmware-bundle",
    "ReleaseDate": "2022-01-25T19:19:03Z",
    "Status": {
        "Health": "OK",
        "State": "StandbyOffline"
    },
    "Updateable": true,
    "Version": "I210A009e"
}
```

### Step 2: Firmware Upload
```
(redfish) http push mc_bundle.sfw /redfish/v1/UpdateService/FWUpdate { "Targets": [], "@Redfish.OperationApplyTime": "Immediate" }
[] http push: url (/redfish/v1/UpdateService/FWUpdate)
++ UrlAccess: process_push - (/redfish/v1/UpdateService/FWUpdate) session (6:ecd14c3e99858affbd4618a3f54d90ce)
   -- fullUrl: https://10.235.221.172/redfish/v1/UpdateService/FWUpdate
   -- filename (mc_bundle.sfw)
   -- X-Auth-Token: ecd14c3e99858affbd4618a3f54d90ce
   -- post w/ JSON

[] URL          : /redfish/v1/UpdateService/FWUpdate
[] Status       : 202
[] Reason       : Accepted


(redfish) create session
   -- ServiceVersion: 2
   -- IP Address    : https://<ip>

[] Redfish session established (2:7fa905e6d31567e5b38fbc0d558f358e)

(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)

 [] URL        : /redfish/v1
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ServiceRoot.ServiceRoot",
    "@odata.id": "/redfish/v1",
    "@odata.type": "#ServiceRoot.v1_9_0.ServiceRoot",
    "AccountService": {
        "@odata.id": "/redfish/v1/AccountService"
    },
    "Chassis": {
        "@odata.id": "/redfish/v1/Chassis"
    },
    "CompositionService": {
        "@odata.id": "/redfish/v1/CompositionService"
    },
    "EventService": {
        "@odata.id": "/redfish/v1/EventService"
    },
    "Fabrics": {
        "@odata.id": "/redfish/v1/Fabrics"
    },
    "Id": "RootService",
    "Links": {
        "Sessions": {
            "@odata.id": "/redfish/v1/SessionService/Sessions"
        }
    },
    "Managers": {
        "@odata.id": "/redfish/v1/Managers"
    },
    "Name": "Root Service",
    "Oem": {
        "Seagate": {
            "RedfishServiceVersion": "2.4.21"
        }
    },
    "RedfishVersion": "1.12.0",
    "SessionService": {
        "@odata.id": "/redfish/v1/SessionService"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Storage"
    },
    "Systems": {
        "@odata.id": "/redfish/v1/Systems"
    },
    "Tasks": {
        "@odata.id": "/redfish/v1/TaskService"
    },
    "UUID": "92384634-2938-2342-8820-489239905423",
    "UpdateService": {
        "@odata.id": "/redfish/v1/UpdateService"
    }
}

```


[//]: <> (================================================================================================================================================================)
## <a name="section24">(24) Reboot Controller</a>
[//]: <> (================================================================================================================================================================)

The Systems resource and associated **ComputerSystem.Reset** action is used to reboot a controller. Use HTTP GET to discover the SystemId and then use the http command
listed below to reboot the controller.

JSON Data options:
- **ResetType** has only one option at this time: **GracefulRestart**

HTTP Commands:
- http get /redfish/v1/Systems/
- http get /redfish/v1/Systems/{SystemId}
- http post /redfish/v1/Systems/{SystemId}/Actions/ComputerSystem.Reset { "ResetType": "GracefulRestart" }

**Note:** Any active HTTP session will be reset by the controller reboot and you must re-establish a session with the Redfish Service. The actual reboot time, when
the Redfish Service continues to allow sessions, will vary but may take 2-3 minutes.

```
(redfish) http get /redfish/v1/Systems/
[] http get: url (/redfish/v1/Systems/)

 [] URL        : /redfish/v1/Systems/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ComputerSystemCollection.ComputerSystemCollection",
    "@odata.id": "/redfish/v1/Systems",
    "@odata.type": "#ComputerSystemCollection.ComputerSystemCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Systems/DHSIFTJ-1852437ED5"
        }
    ],
    "Members@odata.count": 1,
    "Name": "ComputerSystem Collection"
}

(redfish) http get /redfish/v1/Systems/DHSIFTJ-1852437ED5
[] http get: url (/redfish/v1/Systems/DHSIFTJ-1852437ED5)

 [] URL        : /redfish/v1/Systems/DHSIFTJ-1852437ED5
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#ComputerSystem.ComputerSystem",
    "@odata.id": "/redfish/v1/Systems/DHSIFTJ-1852437ED5",
    "@odata.type": "#ComputerSystem.v1_14_0.ComputerSystem",
    "Actions": {
        "#ComputerSystem.Reset": {
            "ResetType@Redfish.AllowableValues": [
                "GracefulRestart"
            ],
            "target": "/redfish/v1/Systems/DHSIFTJ-1852437ED5/Actions/ComputerSystem.Reset"
        }
    },
    "Id": "DHSIFTJ-1852437ED5",
    "Links": {
        "Chassis": [
            {
                "@odata.id": "/redfish/v1/Chassis/enclosure_0"
            }
        ]
    },
    "LogServices": {
        "@odata.id": "/redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices"
    },
    "Name": "Uninitialized Name",
    "SerialNumber": "DHSIFTJ-1852437ED5",
    "Status": {
        "Health": "OK"
    },
    "Storage": {
        "@odata.id": "/redfish/v1/Systems/DHSIFTJ-1852437ED5/Storage"
    }
}


(redfish) http post /redfish/v1/Systems/DHSIFTJ-1852437ED5/Actions/ComputerSystem.Reset { "ResetType": "GracefulRestart" }
[] http post: url (/redfish/v1/Systems/DHSIFTJ-1852437ED5/Actions/ComputerSystem.Reset)

 [] URL        : /redfish/v1/Systems/DHSIFTJ-1852437ED5/Actions/ComputerSystem.Reset
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '546'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "status": [
        {
            "component-id": "",
            "meta": "/meta/status",
            "object-name": "status",
            "response": "Command completed successfully. - The command to restart SC B completed successfully. The controller will restart in approximately 30 seconds. (2022-01-31 16:11:45)",
            "response-type": "Success",
            "response-type-numeric": 0,
            "return-code": 0,
            "time-stamp": "2022-01-31 16:11:45",
            "time-stamp-numeric": 1643645505
        }
    ]
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section25">(25) Get Controller Logs</a>
[//]: <> (================================================================================================================================================================)

The LogServices resource along with the TaskService is used to retrieve controller logs and monitor the log collection process. Since the controller log file hundreds
of megabytes, the process can take several minutes. The two main JSON parameters used are described below, followed by the series of HTTP commands used to extract the
controller log file. Example Task data is presented also for reference. For this example, the `(redfish) get logs` command is used which performs all required steps.
To fully understand the client requirements, like the requirement to write the received binary data to a zip file, please see `commands/systems/get_logs.py`.

LogService POST JSON Data:
- **DiagnosticDataType**: only valid value is **OEM**
- **OEMDiagnosticDataType** relevant options are: **CollectControllerLog**, **DownloadLogData**

HTTP Commands:
- Step 1: Prepare Controller Logs
  - http get /redfish/v1/Systems
  - http get /redfish/v1/Systems/{SystemId}/LogServices/{Id}
  - http post /redfish/v1/Systems/{SystemId}/LogServices/{Id}/Actions/LogService.CollectDiagnosticData `{ "DiagnosticDataType": "OEM", "OEMDiagnosticDataType": "CollectControllerLog" }`
- Step 2: Monitor the Preparation Task
  - http get /redfish/v1/TaskService/getlogs-task
  - http get /redfish/v1/TaskService/getlogs-task
- Step 3: Retrieve the binary Log file and store it to a file
  - http post /redfish/v1/Systems/{SystemId}/LogServices/{Id}/Actions/LogService.CollectDiagnosticData `{ "DiagnosticDataType": "OEM", "OEMDiagnosticDataType": "DownloadLogData" }`

### Example Task Data
```
(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task

JSON Response Data:
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Running",
    "TaskStatus": "OK"
}

(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task
JSON Response Data:
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Running",
    "TaskStatus": "OK"
}

(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task
JSON Response Data:
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
```

### help get logs

```
(redfish) help get logs

 ==========================================================================================================================================================================

 Command: get logs

 Description:
 
 get logs component=[controller|drive] logtype=[disk|diskfarm|etc] drivenumber=[enclosure.slot] file=[filename]
 
 Note:
     This command is only valid for Redfish Service Version 2.
 
 Parameters:
     'component' - Required
         options: controller, drive
 
     'logtype' - Required for 'drive', not used for 'controller'
         options: disk, diskfarm, diskibt, disksm2, diskiddcap, diskiddoff, diskfarmlct,
                 diskfarmfield, diskfarmts1, diskfarmts2, diskfarmsf1, diskfarmsf2,
                 diskfarmsf3, diskfarmsf4, diskfarmfactory
 
     'drivenumber' - Required for 'drive', not used for 'controller'
         options: enclosure.slot, for example 0.24
 
     'file' - Optional
         options: default is to store the data to 'logfile.zip'
                  user can also specify a filename
 
     Note: Not all drive log types are available for all drives. If a drive log type is
           supplied that is not supported by the drive, the command will fail.
 
 Examples:
     get logs component=controller file=controller_logs.zip
     get logs component=drive logtype=diskfarm drivenumber=0.1 file=diskfarm.zip
```

### get controller logs
```
(redfish) get logs component=controller file=controller_logs.zip
   -- Discovered: SystemId                  >> /redfish/v1/Systems/DHSIFTJ-1852437ED5/
   -- Discovered: Storage                   >> /redfish/v1/Systems/DHSIFTJ-1852437ED5/Storage/
   -- Discovered: ControllerId0             >> controller_a
   -- Discovered: ControllerId1             >> controller_b
   -- Discovered: ActiveControllerId        >> controller_b
   -- Discovered: StorageActiveController   >> /redfish/v1/Systems/DHSIFTJ-1852437ED5/Storage/controller_b/
   -- Discovered: SystemsLogServices        >> /redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices/controller_b

++ POST get logs (controller, CollectControllerLog)
[[ POST DATA (/redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices/controller_b/Actions/LogService.CollectDiagnosticData) ]]
{
    "DiagnosticDataType": "OEM",
    "OEMDiagnosticDataType": "CollectControllerLog"
}
[[ POST DATA END ]]

   >> Monitor task 'getlogs-task' for Completed
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Completed'

++ POST get logs (controller, DownloadLogData)
[[ POST DATA (/redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices/controller_b/Actions/LogService.CollectDiagnosticData) ]]
{
    "DiagnosticDataType": "OEM",
    "OEMDiagnosticDataType": "DownloadLogData"
}
[[ POST DATA END ]]
WARNING:    ++ UrlAccess: unhandled content type = [('Connection', 'close'), ('Content-Type', 'IntentionallyUnknownMimeType; charset="utf-8"'), ('Content-Length', '17444959'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('content-disposition', 'attachment; filename="logs.zip"')]
   -- Status        : 200
   -- Reason        : OK
   -- Download complete to 'controller_logs.zip' (17,444,959)
```


[//]: <> (================================================================================================================================================================)
## <a name="section26">(26) Get Drive Logs</a>
[//]: <> (================================================================================================================================================================)

The LogServices resource is used to retrieve disk drive logs. The two main JSON parameters used are described below. To retrieve a disk drive log file, the client
performs one POST operation and the log file is returned as an array of bytes to the client’s HTTP request. For this example, the `(redfish) get logs` command is used
which performs all required steps. To fully understand the client requirements, like the requirement to write the received binary data to a zip file,
please see `commands/systems/get_logs.py`.

Since not all drives support all log types, two example are shown below - one that succeeds and one that fails.

LogService POST JSON Data:
- **DiagnosticDataType**: only valid value is **OEM**
- **OEMDiagnosticDataType** relvant options are: **GetDriveLog**
- **DriveLogType**: disk, diskfarm, diskibt, disksm2, diskiddcap, diskiddoff, diskfarmlct, diskfarmfield, diskfarmts1, diskfarmts2, diskfarmsf1, diskfarmsf2, diskfarmsf3, diskfarmsf4, diskfarmfactory
- **DriveNumber**: single number such as '0.1', other examples: 0.0, 1.0, 0.23, etc.

HTTP Commands:
- Step 1: Prepare Controller Logs
  - http get /redfish/v1/Systems
  - http get /redfish/v1/Systems/{SystemId}/LogServices/{Id}
  - http post /redfish/v1/Systems/{SystemId}/LogServices/{Id}/Actions/LogService.CollectDiagnosticData `{ "DiagnosticDataType": "OEM", "OEMDiagnosticDataType": "GetDriveLog", "DriveLogType": "diskfarm", "DriveNumber": "0.1" }`

### help get logs

```
(redfish) help get logs

 ==========================================================================================================================================================================

 Command: get logs

 Description:
 
 get logs component=[controller|drive] logtype=[disk|diskfarm|etc] drivenumber=[enclosure.slot] file=[filename]
 
 Note:
     This command is only valid for Redfish Service Version 2.
 
 Parameters:
     'component' - Required
         options: controller, drive
 
     'logtype' - Required for 'drive', not used for 'controller'
         options: disk, diskfarm, diskibt, disksm2, diskiddcap, diskiddoff, diskfarmlct,
                 diskfarmfield, diskfarmts1, diskfarmts2, diskfarmsf1, diskfarmsf2,
                 diskfarmsf3, diskfarmsf4, diskfarmfactory
 
     'drivenumber' - Required for 'drive', not used for 'controller'
         options: enclosure.slot, for example 0.24
 
     'file' - Optional
         options: default is to store the data to 'logfile.zip'
                  user can also specify a filename
 
     Note: Not all drive log types are available for all drives. If a drive log type is
           supplied that is not supported by the drive, the command will fail.
 
 Examples:
     get logs component=controller file=controller_logs.zip
     get logs component=drive logtype=diskfarm drivenumber=0.1 file=diskfarm.zip
```

### get drive logs

```
(redfish) get logs component=drive logtype=disk drivenumber=0.1 file=disk.zip

++ POST get logs (drive, disk, 0.1)
[[ POST DATA (/redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices/controller_b/Actions/LogService.CollectDiagnosticData) ]]
{
    "DiagnosticDataType": "OEM",
    "OEMDiagnosticDataType": "GetDriveLog",
    "DriveLogType": "disk",
    "DriveNumber": "0.1"
}
[[ POST DATA END ]]
WARNING:    ++ UrlAccess: unhandled content type = [('Connection', 'close'), ('Content-Type', 'IntentionallyUnknownMimeType; charset="utf-8"'), ('Content-Length', '1526639'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('content-disposition', 'attachment; filename="logs.zip"')]
   -- Status        : 200
   -- Reason        : OK
   -- Download complete to 'disk.zip' (1,526,639)

   -- Contents of zip file 'disk.zip':
      ** DriveDebugDump.uds
 

(redfish) get logs component=drive logtype=diskfarm drivenumber=0.1 file=diskfarm.zip

++ POST get logs (drive, diskfarm, 0.1)
[[ POST DATA (/redfish/v1/Systems/DHSIFTJ-1852437ED5/LogServices/controller_b/Actions/LogService.CollectDiagnosticData) ]]
{
    "DiagnosticDataType": "OEM",
    "OEMDiagnosticDataType": "GetDriveLog",
    "DriveLogType": "diskfarm",
    "DriveNumber": "0.1"
}
[[ POST DATA END ]]
WARNING:    ++ UrlAccess: unhandled content type = [('Connection', 'close'), ('Content-Type', 'IntentionallyUnknownMimeType; charset="utf-8"'), ('Content-Length', '319'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate'), ('content-disposition', 'attachment; filename="logs.zip"')]
   -- Status        : 200
   -- Reason        : OK
   -- Download complete to 'diskfarm.zip' (319)

   -- Contents of zip file 'diskfarm.zip':
      ** ErrorMessage.txt

   -- Contents of file 'ErrorMessage.txt':
      || Error retrieving drive debug dump (likely cause: Non-Seagate drive or operation not supported on this model).
      || Prerequisites: Drive must be a spinning/ready native-SAS Seagate drive.
```


[//]: <> (================================================================================================================================================================)
## <a name="section27">(27) Task Service</a>
[//]: <> (================================================================================================================================================================)

The TaskService resouce is used to monitor long running tasks. Use HTTP GET commands to discover a Task Id and then use additional HTTP GET commands to retrieve task
specific information. In this example, watch the **TaskState** change from **Running** to **Completed** once the task completes. Once a task does complete, and status
is retrieved, that task will no longer be presented under `http get /redfish/v1/TaskService/Tasks`.

HTTP Commands:
- http get /redfish/v1/TaskService
- http get /redfish/v1/TaskService/Tasks
- http get /redfish/v1/TaskService/Tasks/{TaskId}

### Example Task Information:

```
(redfish) http get /redfish/v1/TaskService/
[] http get: url (/redfish/v1/TaskService/)

 [] URL        : /redfish/v1/TaskService/
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#TaskService.TaskService",
    "@odata.id": "/redfish/v1/TaskService",
    "@odata.type": "#TaskService.v1_1_6.TaskService",
    "CompletedTaskOverWritePolicy": "Manual",
    "Id": "TaskService",
    "LifeCycleEventOnTaskStateChange": false,
    "Name": "Task Service",
    "ServiceEnabled": true,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Tasks": {
        "@odata.id": "/redfish/v1/TaskService/Tasks"
    }
}


(redfish) http get /redfish/v1/TaskService/Tasks
[] http get: url (/redfish/v1/TaskService/Tasks)

 [] URL        : /redfish/v1/TaskService/Tasks
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#TaskCollection.TaskCollection",
    "@odata.id": "/redfish/v1/TaskService/Tasks",
    "@odata.type": "#TaskCollection.TaskCollection",
    "Members": [],
    "Members@odata.count": 0,
    "Name": "Task Collection"
}

(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task
[] http get: url (/redfish/v1/TaskService/Tasks)

 [] URL        : /redfish/v1/TaskService/Tasks
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Running",
    "TaskStatus": "OK"
}

(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task
[] http get: url (/redfish/v1/TaskService/Tasks)

 [] URL        : /redfish/v1/TaskService/Tasks
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Running",
    "TaskStatus": "OK"
}

(redfish) http get /redfish/v1/TaskService/Tasks/getlogs-task
[] http get: url (/redfish/v1/TaskService/Tasks)

 [] URL        : /redfish/v1/TaskService/Tasks
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Task.Task",
    "@odata.id": "/redfish/v1/TaskService/Tasks/getlogs-task",
    "@odata.type": "#Task.v1_5_1.Task",
    "Id": "getlogs-task",
    "Name": "Task getlogs-task",
    "StartTime": "2021-04-20T09:46:26+00:00",
    "TaskState": "Completed",
    "TaskStatus": "OK"
}
```

[//]: <> (================================================================================================================================================================)
## <a name="section28">(28) Create Volume Snapshot</a>
[//]: <> (================================================================================================================================================================)

A Redfish client can create a volume snapshot using an HTTP POST to the Volume. Use HTTP GET to retrieve the desired Volume URI, then executed an HTTP POST to create a
new snapshot. The action requires four parameters:
- `"ReplicaType": "Snapshot"`
- `"ReplicaUpdateMode": "Asynchronous"`
- `"TargetStoragePool": "{SourceVolumeName}"`
- `"VolumeName": "{SnapshotVolumeName}"`

HTTP operations:
- http post /redfish/v1/Storage/controller_a/Volumes/{VolumeId}/Actions/Volume.CreateReplicaTarget json/create_snapshot.json
- http get /redfish/v1/Storage/controller_a/Volumes
- http get /redfish/v1/Storage/controller_a/Volumes/{SnapshotId}

json/create_snapshot.json contents:
```
{
    "ReplicaType": "Snapshot",
    "ReplicaUpdateMode": "Asynchronous",
    "TargetStoragePool": "AVolume01",
    "VolumeName": "Snapshot01"
}
```

Here is the execution of creating a new snapshot volume:

```
(redfish) http post /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000/Actions/Volume.CreateReplicaTarget json/create_snapshot.json
[] http post: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000/Actions/Volume.CreateReplicaTarget)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff5460590000f2a9f76101000000/Actions/Volume.CreateReplicaTarget
 [] Status     : 201
 [] Reason     : Created

[] HTTP Headers : [('Connection', 'close'), ('Content-Type', 'application/json; charset="utf-8"'), ('Content-Length', '486'), ('X-Frame-Options', 'SAMEORIGIN'), ('Content-Security-Policy', "script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src * 'self' data:; base-uri 'self'; object-src 'self'"), ('X-Content-Type-Options', 'nosniff'), ('X-XSS-Protection', '1'), ('Strict-Transport-Security', 'max-age=31536000; '), ('Cache-Control', 'no-cache, no-store, must-revalidate')]

[] JSON Data    : {
    "status": [
        {
            "component-id": "Snapshot01",
            "meta": "/meta/status",
            "object-name": "status",
            "response": "Command completed successfully. (Snapshot01) - Snapshot(s) were created. (2022-01-31 10:41:08)",
            "response-type": "Success",
            "response-type-numeric": 0,
            "return-code": 0,
            "time-stamp": "2022-01-31 10:41:08",
            "time-stamp-numeric": 1643625668
        }
    ]
}


(redfish) http get /redfish/v1/Storage/controller_a/Volumes
[] http get: url (/redfish/v1/Storage/controller_a/Volumes)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#VolumeCollection.VolumeCollection",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes",
    "@odata.type": "#VolumeCollection.VolumeCollection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000aebcf76101000000"
        },
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000"
        }
    ],
    "Members@odata.count": 2,
    "Name": "Volume Collection"
}


(redfish) http get /redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000
[] http get: url (/redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000)

 [] URL        : /redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#Volume.Volume",
    "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000",
    "@odata.type": "#Volume.v1_6_1.Volume",
    "BlockSizeBytes": 512,
    "Capacity": {
        "Data": {
            "AllocatedBytes": 0,
            "ConsumedBytes": 0
        }
    },
    "CapacityBytes": 99996401664,
    "CapacitySources": [
        {
            "@odata.id": "/redfish/v1/Storage/controller_a/Volumes/00c0ff5112490000c3bcf76101000000#/CapacitySources/0",
            "@odata.type": "#Capacity.v1_2_0.CapacitySource",
            "Id": "00c0ff5112490000c3bcf76101000000",
            "Name": "Snapshot01",
            "ProvidingPools": {
                "@odata.context": "/redfish/v1/$metadata#StoragePoolCollection.StoragePoolCollection",
                "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools",
                "@odata.type": "#StoragePoolCollection.StoragePoolCollection",
                "Members": [
                    {
                        "@odata.id": "/redfish/v1/Storage/controller_a/StoragePools/A"
                    }
                ],
                "Members@odata.count": 1,
                "Name": "StoragePools"
            }
        }
    ],
    "Encrypted": false,
    "EncryptionTypes": [
        "NativeDriveEncryption"
    ],
    "IOStatistics": {
        "ReadHitIORequests": 0,
        "ReadIOKiBytes": 0,
        "WriteHitIORequests": 0,
        "WriteIOKiBytes": 0
    },
    "Id": "00c0ff5112490000c3bcf76101000000",
    "Name": "Snapshot01",
    "RemainingCapacityPercent": 100,
    "ReplicaTargets": [],
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "WriteCachePolicy": "UnprotectedWriteBack"
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section29">(29) Event Service</a>
[//]: <> (================================================================================================================================================================)

The EventService resource is not fully implemented in this release. Some commands are available, but the Redfish Service does not sent Events asynchronously at this time.
This resource is a place holder until the full feature is released.

```
(redfish) http get /redfish/v1/EventService
[] http get: url (/redfish/v1/EventService)

 [] URL        : /redfish/v1/EventService
 [] Status     : 200
 [] Reason     : OK
 [] JSON Data  :
{
    "@odata.context": "/redfish/v1/$metadata#EventService.EventService",
    "@odata.id": "/redfish/v1/EventService",
    "@odata.type": "#EventService.v1_7_1.EventService",
    "Actions": {
        "#EventService.SubmitTestEvent": {
            "target": "/redfish/v1/EventService/Actions/EventService.SubmitTestEvent"
        }
    },
    "DeliveryRetryAttempts": 3,
    "DeliveryRetryIntervalSeconds": 60,
    "Id": "EventService",
    "Name": "Event Service",
    "ServiceEnabled": true,
    "Status": {
        "Health": "OK",
        "State": "Enabled"
    },
    "Subscriptions": {
        "@odata.id": "/redfish/v1/EventService/Subscriptions"
    }
}
```


[//]: <> (================================================================================================================================================================)
## <a name="section30">(30) Summary</a>
[//]: <> (================================================================================================================================================================)

Hopefully this tutorial increased your understanding of how to use the Redfish Service to manage a storage system.
