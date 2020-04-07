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
# redfishSystem.py - Routines to discover, store, and retrieve system information. 
#
# ******************************************************************************************
#

import config
from core.jsonExtract import JsonExtract
from core.trace import TraceLevel, Trace
from core.urlAccess import UrlAccess, UrlStatus


################################################################################
# RedfishSystem
################################################################################

class RedfishSystem:

    successfulRootInit = False
    systemDict = {} 

    # An array of dictionary items storing disk information.
    #   drives[0] = { 'inUse': inUse, 'number': id, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health]
    #   drives[N] = { 'inUse': inUse, 'number': id, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health]
    # An array of ports and array of initiators
    successfulSystemInit = False
    drives = []
    ports = []
    initiators = []

    #
    # Display discovered URI for the user
    #
    @classmethod
    def discovered_uri(cls, key, value):
        Trace.log(TraceLevel.INFO, '   -- Discovered: {0:18} >> {1}'.format(key, value))

    #
    # Store a new URI
    #
    @classmethod
    def store_uri(cls, key, link):
        if (link.valid):
            if (key in link.jsonData):
                newValue = link.jsonData[key]["@odata.id"]
                if (newValue[-1] != '/'):
                    newValue = newValue + '/'
                cls.systemDict[key] = newValue
                cls.discovered_uri(key, newValue)

    #
    # Store a new URI
    #
    @classmethod
    def store_uri_value(cls, key, uri):
        cls.systemDict[key] = uri
        cls.discovered_uri(key, uri)

    #
    # Initialize a dictionary of all System Root URIs. These URIs do not require a session.
    #
    @classmethod
    def initialize_service_root_uris(cls, redfishConfig):

        Trace.log(TraceLevel.DEBUG, '++ initialize_service_root_uris (BaseInit={})'.format(cls.successfulRootInit))
        
        if (cls.successfulRootInit == True):
            return

        cls.systemDict = {}
        url = config.redfish
        cls.successfulRootInit = True

        try:
            # GET Redfish Version
            Trace.log(TraceLevel.TRACE, '++ GET Redfish Version from ({})'.format(url))
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False, None)
            if (link.valid and "v1" in link.jsonData):
                newValue = link.jsonData["v1"]
                cls.systemDict["Root"] = newValue
                cls.discovered_uri("Root", newValue)
            else:
                Trace.log(TraceLevel.ERROR, '-- System Init: Invalid URL link for ({})'.format(url))
                cls.successfulRootInit = False
    
            # GET Redfish Root Services
            if (cls.successfulRootInit):
                link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["Root"]), 'GET', False, None)
                cls.store_uri("Systems", link)
                cls.store_uri("Chassis", link)
                cls.store_uri("StorageServices", link)
                cls.store_uri("Managers", link)
                cls.store_uri("Tasks", link)
                cls.store_uri("SessionService", link)
        
                cls.store_uri_value("Sessions", cls.systemDict["SessionService"] + 'Sessions/')
                cls.store_uri_value("metadata", cls.systemDict["Root"] + '$metadata/' )
                cls.store_uri_value("odata", cls.systemDict["Root"] + 'odata/')
    
        except Exception as e:
            Trace.log(TraceLevel.ERROR, '-- Unable to initialize Service Root URIs, exception: {}'.format(e))
            cls.successfulRootInit = False

        Trace.log(TraceLevel.DEBUG, '@@1 systemDict: {}'.format(cls.systemDict))

        return cls.successfulRootInit

    #
    # Update the system URI dictionary for the specificed key
    #
    @classmethod
    def fill_storage_services_id(cls, redfishConfig, key):

        if (key not in cls.systemDict):
            if ('StorageServicesId' not in cls.systemDict ):
                # GET StorageServices Identifier
                link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServices"]), 'GET', True, None)
                if (link.valid and link.jsonData is not None and 'Members' in link.jsonData):
                    for member in link.jsonData["Members"]:
                        newuri = member["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        cls.store_uri_value("StorageServicesId", newuri)

    #
    # Update the system URI dictionary for the specificed key
    #
    @classmethod
    def get_uri_specific(cls, redfishConfig, key):

        uri = ''

        Trace.log(TraceLevel.DEBUG, '++ get_uri_specific({}) ...'.format(key))

        if (key == "Racks" or key == "Thermals" or key == "Powers"):
            # GET all Chassis Racks
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["Chassis"]), 'GET', True, None)
            if (link.valid and link.jsonData is not None and 'Members' in link.jsonData):
                racks = []
                for member in link.jsonData["Members"]:
                    newuri = member["@odata.id"]
                    if (newuri[-1] != '/'):
                        newuri = newuri + '/'
                    racks.append(newuri)
                cls.store_uri_value("Racks", racks)
                uri = racks

        if (key == "Thermals"):
            # GET all Thermal URIs
            items = []
            for member in cls.systemDict["Racks"]:
                Trace.log(TraceLevel.DEBUG, '>> Racks: {}'.format(member))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(member), 'GET', True, None)
                if (link.valid and link.jsonData is not None and 'Thermal' in link.jsonData):
                    newuri = link.jsonData["Thermal"]["@odata.id"]
                    if (newuri[-1] != '/'):
                        newuri = newuri + '/'
                    items.append(newuri)
            cls.store_uri_value("Thermals", items)
            uri = items

        if (key == "Powers"):
            # GET all Power URIs
            items = []
            for member in cls.systemDict["Racks"]:
                Trace.log(TraceLevel.DEBUG, '>> Racks: {}'.format(member))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(member), 'GET', True, None)
                if (link.valid and link.jsonData is not None and 'Power' in link.jsonData):
                    newuri = link.jsonData["Power"]["@odata.id"]
                    if (newuri[-1] != '/'):
                        newuri = newuri + '/'
                    items.append(newuri)
            cls.store_uri_value("Powers", items)
            uri = items

        if (key == "StorageServicesId"):
            # GET StorageServices Identifier
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServices"]), 'GET', True, None)
            if (link.valid and link.jsonData is not None and 'Members' in link.jsonData):
                for member in link.jsonData["Members"]:
                    newuri = member["@odata.id"]
                    if (newuri[-1] != '/'):
                        newuri = newuri + '/'
                    cls.store_uri_value("StorageServicesId", newuri)
                    uri = newuri

        if (key == "ClassesOfService"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("ClassesOfService", link)
            uri = cls.systemDict["ClassesOfService"]

        if (key == "Drives"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("Drives", link)
            uri = cls.systemDict["Drives"]

        if (key == "Endpoints"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("Endpoints", link)
            uri = cls.systemDict["Endpoints"]

        if (key == "EndpointGroups"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("EndpointGroups", link)
            uri = cls.systemDict["EndpointGroups"]

        if (key == "StorageGroups"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("StorageGroups", link)
            uri = cls.systemDict["StorageGroups"]

        if (key == "StoragePools"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("StoragePools", link)
            uri = cls.systemDict["StoragePools"]

        if (key == "Volumes"):
            cls.fill_storage_services_id(redfishConfig, key)
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("Volumes", link)
            uri = cls.systemDict["Volumes"]

        if (key == "ClassesOfServiceDefault"):
            cls.store_uri_value("ClassesOfServiceDefault", '/redfish/v1/StorageServices(1)/ClassesOfService(Default)')
            uri = cls.systemDict["ClassesOfServiceDefault"]

        Trace.log(TraceLevel.TRACE, '@@2 systemDict: {}'.format(cls.systemDict))

        return uri

    #
    # Get a URI based on a key. These are stored during initialization. For example:
    #     'root'    = '/redfish/v1'
    #     'chassis' = '/redfish/Chassis'
    #
    @classmethod
    def get_uri(cls, redfishConfig, key):

        uri = ''

        Trace.log(TraceLevel.DEBUG, '++ get_uri({}) ...'.format(key))

        if (cls.successfulRootInit == False):
            cls.initialize_service_root_uris(redfishConfig)

        if (key in cls.systemDict):
            uri = cls.systemDict[key]
            Trace.log(TraceLevel.VERBOSE, '-- URI for ({}) is ({})'.format(key, uri))
        else:
            if (redfishConfig.sessionValid):
                uri = cls.get_uri_specific(redfishConfig, key)
            else:
                Trace.log(TraceLevel.ERROR, '-- A valid session is required!')

        Trace.log(TraceLevel.DEBUG, '++ get_uri({}) returning ({})'.format(key, uri))

        return uri

    #
    # Initialize an array of disks by using the Redfish API.
    #
    @classmethod
    def initialize_drives(cls, redfishConfig):

        inited = False
        cls.drives = []
        url = cls.get_uri(redfishConfig, 'Drives')
        Trace.log(TraceLevel.INFO, '++ initialize_drives: url={}'.format(url))

        try:
            # GET DriveCollection
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
    
            # Retrieve a listing of all drives for this system
            membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
            totalDrives = int(membersCount)
            odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
            
            Trace.log(TraceLevel.INFO, '++ initialize_drives: membersCount={}, totalDrives={}'.format(membersCount, totalDrives))

            # Don't include the main @odata.id for the Drive Collection, all others are Drives/#.#
            if (url[-1] == '/'):
                url = url[:-1]

            if (len(odataIds) > 0):
                odataIds.remove(url)

            for driveUrl in odataIds: 
                Trace.log(TraceLevel.TRACE, '++ extracting data for driveUrl={}'.format(driveUrl))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(driveUrl), 'GET', True, None)
    
                drive_number = JsonExtract.get_value(link.jsonData, None, 'Id', 1)
                serial_number = JsonExtract.get_value(link.jsonData, None, 'SerialNumber', 1)
                speed = JsonExtract.get_value(link.jsonData, None, 'NegotiatedSpeedGbs', 1)
                capacity = JsonExtract.get_value(link.jsonData, None, 'CapacityBytes', 1)
                block_size = JsonExtract.get_value(link.jsonData, None, 'BlockSizeBytes', 1)
                state = JsonExtract.get_value(link.jsonData, 'Status', 'State', 1)
                health = JsonExtract.get_value(link.jsonData, 'Status', 'Health', 1)
    
                # If the drive is linked to one or more volumes, it is already in use.
                volumes = JsonExtract.get_value(link.jsonData, 'Volumes', '@odata.id', 1)
                inUse = False
                if volumes is not None:
                    inUse = True
    
                driveInfo = {'inUse': inUse, 'number': drive_number, 'serial': serial_number, 'speed': speed, 'capacity': capacity, 'size': block_size, 'state': state, 'health': health}
                Trace.log(TraceLevel.VERBOSE, '++ initialize_drives: {0: >6} / {1} - {2: >24}'.format(drive_number, inUse, serial_number))
                cls.drives.append(driveInfo)

                cls.drives.sort(key=lambda k: k['number'], reverse=False)

            inited = True
            Trace.log(TraceLevel.VERBOSE, '++ initialize_drives: inited={}'.format(inited))

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize drives, exception: {}'.format(e))
            inited = False

        Trace.log(TraceLevel.DEBUG, '++ initialize_disks: {} drives added'.format(len(cls.drives)))
        Trace.log(TraceLevel.TRACE, '@@ drives: {}'.format(cls.drives))

        return inited


    #
    # Initialize an array of ports using the Redfish API.
    #
    @classmethod
    def initialize_ports(cls, redfishConfig):

        inited = False
        cls.ports = []

        url = RedfishSystem.get_uri(redfishConfig, 'EndpointGroups')
        Trace.log(TraceLevel.INFO, '++ initialize_ports: url={}'.format(url))

        try:
            # GET DriveCollection
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
    
            # Retrieve a listing of all drives for this system
            membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
            totalItems = int(membersCount)
            odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
            Trace.log(TraceLevel.INFO, '++ odataIds: {}'.format(odataIds))

            Trace.log(TraceLevel.INFO, '++ initialize_ports: membersCount={}, totalDrives={}'.format(membersCount, totalItems))

            # Don't include the main @odata.id for the Drive Collection, all others are Drives/#.#
            if (url[-1] == '/'):
                url = url[:-1]

            if (len(odataIds) > 0):
                odataIds.remove(url)

            for itemUrl in odataIds: 
                Trace.log(TraceLevel.TRACE, '++ extracting data for Url={}'.format(itemUrl))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(itemUrl), 'GET', True, None)

                if ('GroupType' in link.jsonData):
                    groupType = link.jsonData['GroupType']
    
                    if ((groupType == "Server") and ('All' not in link.jsonData['Id'])):
                        endpoints = link.jsonData['Endpoints']
                        for i in range(len(endpoints)):
                            # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                            endpointUri = endpoints[i]['@odata.id']
                            Trace.log(TraceLevel.DEBUG, '   ++ Adding endpoint: ({})'.format(endpointUri))
                            link2 = UrlAccess.process_request(redfishConfig, UrlStatus(endpointUri))

                            if (link2.valid):
                                newItem = link2.jsonData['Id']
                                if (newItem not in cls.ports):
                                    Trace.log(TraceLevel.DEBUG, '   ++ Port: {}'.format(newItem))
                                    cls.ports.append(newItem)

            inited = True

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize ports, exception: {}'.format(e))
            inited = False

        Trace.log(TraceLevel.VERBOSE, '++ initialize_ports: inited={}, count={}'.format(inited, len(cls.ports)))
        Trace.log(TraceLevel.DEBUG, '@@ ports: {}'.format(cls.ports))

        return inited

    #
    # Initialize an array of initiators using the Redfish API.
    #
    @classmethod
    def initialize_initiators(cls, redfishConfig):

        inited = False
        cls.initiators = []

        url = RedfishSystem.get_uri(redfishConfig, 'EndpointGroups')
        Trace.log(TraceLevel.INFO, '++ initialize_initiators: url={}'.format(url))

        try:
            # GET DriveCollection
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', True, None)
    
            # Retrieve a listing of all drives for this system
            membersCount = JsonExtract.get_value(link.jsonData, None, 'Members@odata.count', 1)
            totalItems = int(membersCount)
            odataIds = JsonExtract.get_values(link.jsonData, "@odata.id")
            Trace.log(TraceLevel.INFO, '++ odataIds: {}'.format(odataIds))

            Trace.log(TraceLevel.INFO, '++ initialize_initiators: membersCount={}, totalDrives={}'.format(membersCount, totalItems))

            # Don't include the main @odata.id for the Drive Collection, all others are Drives/#.#
            if (url[-1] == '/'):
                url = url[:-1]

            if (len(odataIds) > 0):
                odataIds.remove(url)

            for itemUrl in odataIds: 
                Trace.log(TraceLevel.DEBUG, '++ extracting data for Url={}'.format(itemUrl))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(itemUrl), 'GET', True, None)

                if ('GroupType' in link.jsonData):
                    groupType = link.jsonData['GroupType']
    
                    if ((groupType == "Client") and ('All' not in link.jsonData['Id'])):
                        endpoints = link.jsonData['Endpoints']
                        for i in range(len(endpoints)):
                            # Example: "@odata.id": "/redfish/v1/StorageServices/S1/EndpointGroups/500605b00ab61310"
                            endpointUri = endpoints[i]['@odata.id']
                            Trace.log(TraceLevel.DEBUG, '   ++ Adding initiator: ({})'.format(endpointUri))
                            link2 = UrlAccess.process_request(redfishConfig, UrlStatus(endpointUri))
                            
                            if (link2.valid):
                                newItem = link2.jsonData['Id']
                                if (newItem not in cls.initiators):
                                    Trace.log(TraceLevel.DEBUG, '   ++ Initiator: {}'.format(newItem))
                                    cls.initiators.append(newItem)

            inited = True

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize initiators, exception: {}'.format(e))
            inited = False

        Trace.log(TraceLevel.VERBOSE, '++ initialize_initiators: inited={}, count={}'.format(inited, len(cls.initiators)))
        Trace.log(TraceLevel.DEBUG, '@@ initiators: {}'.format(cls.initiators))

        return inited

    #
    # Initialize all needed system information. This must be called once at
    # before testing begins.
    #
    @classmethod
    def initialize_system(cls, redfishConfig):

        initialized = cls.successfulSystemInit

        if (initialized is False and redfishConfig.sessionValid):

            tempstatus = cls.initialize_drives(redfishConfig)
            Trace.log(TraceLevel.INFO, '++ initialize_system: initialize_drives={}'.format(tempstatus))
            if (tempstatus == True):
                initialized = True
            else:
                initialized = False

            tempstatus = cls.initialize_ports(redfishConfig)
            Trace.log(TraceLevel.INFO, '++ initialize_system: initialize_ports={}'.format(tempstatus))
            if (tempstatus == True):
                initialized = True
            else:
                initialized = False

            tempstatus = cls.initialize_initiators(redfishConfig)
            Trace.log(TraceLevel.INFO, '++ initialize_system: initialize_initiators={}'.format(tempstatus))
            if (tempstatus == True):
                initialized = True
            else:
                initialized = False

            cls.successfulSystemInit = initialized

        Trace.log(TraceLevel.INFO, '++ initialize_system: {}'.format(initialized))

        return (initialized)

    #
    # Returns the next available drive from the system information table.
    #
    # Returns a dictionary with url, drive number, and serial number.
    #
    @classmethod
    def get_next_available_drive(cls, redfishConfig):
        url = None
        drive_number = ''
        serial_number = ''

        if (cls.successfulSystemInit == False):
            RedfishSystem.initialize_system(redfishConfig)

        for drive in cls.drives:
            if drive['inUse'] == False:
                drive_number = drive['number']
                serial_number = drive['serial']
                url = cls.get_uri(redfishConfig, 'Drives') + drive_number
                drive['inUse'] = True
                Trace.log(TraceLevel.DEBUG, '++ get_next_available_drive: return drive {}, in use {}'.format(drive_number, drive['inUse']))
                break

        return {'url': url, 'number': drive_number ,'serial': serial_number}

    #
    # Returns an array of ports
    #
    @classmethod
    def get_ports(cls, redfishConfig):

        if (cls.successfulSystemInit == False):
            RedfishSystem.initialize_system(redfishConfig)

        ports = ','.join(cls.ports)
        Trace.log(TraceLevel.VERBOSE, '++ get_ports: {}'.format(ports))

        return ports

    #
    # Returns an array of initiators
    #
    @classmethod
    def get_initiators(cls, redfishConfig):

        if (cls.successfulSystemInit == False):
            RedfishSystem.initialize_system(redfishConfig)

        initiators = ','.join(cls.initiators)
        Trace.log(TraceLevel.VERBOSE, '++ get_initiators: {}'.format(initiators))

        return initiators


