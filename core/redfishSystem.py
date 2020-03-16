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

    successfulBaseInit = False
    successfulUrisInit = False
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
    # Store a new URI
    #
    @classmethod
    def store_uri(cls, key, link):
        if (link.valid):
            if (key in link.jsonData):
                cls.systemDict[key] = link.jsonData[key]["@odata.id"]
                if (cls.systemDict[key][-1] != '/'):
                    cls.systemDict[key] = cls.systemDict[key] + '/'

    #
    # Initialize a dictionary of all System Root URIs
    #
    @classmethod
    def initialize_service_root_uris(cls, redfishConfig):

        Trace.log(TraceLevel.DEBUG, '++ initialize_service_root_uris (BaseInit={})'.format(cls.successfulBaseInit))
        
        if (cls.successfulBaseInit == True):
            return

        cls.systemDict = {}
        url = config.redfish
        cls.successfulBaseInit = False

        try:
            # GET Redfish Version
            Trace.log(TraceLevel.DEBUG, '++ GET Redfish Version from ({})'.format(url))
            link = UrlAccess.process_request(redfishConfig, UrlStatus(url), 'GET', False, None)
            if (link.valid):
                cls.systemDict["Root"] = link.jsonData["v1"]
            else:
                Trace.log(TraceLevel.INFO, '-- Invalid URL link for ({})'.format(url))
    
            # GET Redfish Root Services
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["Root"]), 'GET', False, None)
            cls.store_uri("Systems", link)
            cls.store_uri("Chassis", link)
            cls.store_uri("StorageServices", link)
            cls.store_uri("Managers", link)
            cls.store_uri("Tasks", link)
            cls.store_uri("SessionService", link)
    
            cls.systemDict["Sessions"] = cls.systemDict["SessionService"] + 'Sessions/'
            cls.systemDict["metadata"] = cls.systemDict["Root"] + '$metadata/' 
            cls.systemDict["odata"] = cls.systemDict["Root"] + 'odata/'
    
            cls.successfulBaseInit = True

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize Service Root URIs, exception: {}'.format(e))
            cls.successfulBaseInit = False

        Trace.log(TraceLevel.DEBUG, '@@1 systemDict: {}'.format(cls.systemDict))

        Trace.log(TraceLevel.INFO, '++ initialize_service_root_uris: {}'.format(cls.successfulBaseInit))

        return cls.successfulBaseInit

    #
    # Initialize a dictionary of all system URIs
    #
    @classmethod
    def initialize_uris(cls, redfishConfig):

        if (cls.successfulBaseInit == False):
            cls.initialize_service_root_uris(redfishConfig)

        cls.successfulUrisInit = False

        try:
            # GET all Chassis Racks
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["Chassis"]), 'GET', True, None)
            if (link.valid):
                if ('Members' in link.jsonData):
                    racks = []
                    for member in link.jsonData["Members"]:
                        newuri = member["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        racks.append(newuri)
                    cls.systemDict["Racks"] = racks

            # GET all Thermal URIs
            items = []
            for member in cls.systemDict["Racks"]:
                Trace.log(TraceLevel.DEBUG, '>> Racks: {}'.format(member))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(member), 'GET', True, None)
                if (link.valid):
                    if ("Thermal" in link.jsonData):
                        newuri = link.jsonData["Thermal"]["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        items.append(newuri)
            cls.systemDict["Thermals"] = items

            # GET all Power URIs
            items = []
            for member in cls.systemDict["Racks"]:
                Trace.log(TraceLevel.DEBUG, '>> Racks: {}'.format(member))
                link = UrlAccess.process_request(redfishConfig, UrlStatus(member), 'GET', True, None)
                if (link.valid):
                    if ("Power" in link.jsonData):
                        newuri = link.jsonData["Power"]["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        items.append(newuri)
            cls.systemDict["Powers"] = items

            # GET StorageServices Identifier
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServices"]), 'GET', True, None)
            if (link.valid):
                if ('Members' in link.jsonData):
                    for member in link.jsonData["Members"]:
                        newuri = member["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        cls.systemDict["StorageServicesId"] = newuri

            # GET StorageServices Links
            link = UrlAccess.process_request(redfishConfig, UrlStatus(cls.systemDict["StorageServicesId"]), 'GET', True, None)
            cls.store_uri("ClassesOfService", link)
            cls.store_uri("Drives", link)
            cls.store_uri("Endpoints", link)
            cls.store_uri("EndpointGroups", link)
            cls.store_uri("StorageGroups", link)
            cls.store_uri("StoragePools", link)
            cls.store_uri("Volumes", link)

            cls.systemDict["ClassesOfServiceDefault"] = '/redfish/v1/StorageServices(1)/ClassesOfService(Default)'

            if (link.valid):
                if ('Members' in link.jsonData):
                    for member in link.jsonData["Members"]:
                        newuri = member["@odata.id"]
                        if (newuri[-1] != '/'):
                            newuri = newuri + '/'
                        cls.systemDict["StorageServicesId"] = newuri

            cls.successfulUrisInit = True

        except Exception as e:
            Trace.log(TraceLevel.INFO, '-- Unable to initialize system URIs, exception: {}'.format(e))
            cls.successfulUrisInit = False

        Trace.log(TraceLevel.DEBUG, '@@2 systemDict: {}'.format(cls.systemDict))

        Trace.log(TraceLevel.VERBOSE, '++ initialize_uris: {}'.format(cls.successfulUrisInit))

        return cls.successfulUrisInit

    #
    # Get a URI based on a key. These are stored during initialization. For example:
    #     'root'    = '/redfish/v1'
    #     'chassis' = '/redfish/Chassis'
    #
    @classmethod
    def get_uri(cls, redfishConfig, key):
        uri = ''
        if (cls.successfulBaseInit == False):
            cls.initialize_service_root_uris(redfishConfig)

        if (key in cls.systemDict):
            uri = cls.systemDict[key]
            Trace.log(TraceLevel.VERBOSE, '-- System URI for ({}) is ({})'.format(key, uri))
        else:
            if (redfishConfig.sessionValid):
                if (cls.successfulUrisInit == False):
                    cls.initialize_uris(redfishConfig)

                if (key in cls.systemDict):
                    uri = cls.systemDict[key]
                    Trace.log(TraceLevel.VERBOSE, '-- System URI for ({}) is ({})'.format(key, uri))
                else:
                    Trace.log(TraceLevel.INFO, '-- System URI for Key ({}) was not found in system dictionary'.format(key))
            else:
                Trace.log(TraceLevel.INFO, '-- A valid session was not found!')

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

        initialized = False
        if (cls.successfulBaseInit and cls.successfulUrisInit and cls.successfulSystemInit):
            initialized = True

        if (redfishConfig.sessionValid):
            if (cls.successfulUrisInit == False):
                tempstatus = cls.initialize_uris(redfishConfig)
                Trace.log(TraceLevel.INFO, '++ initialize_system: initialize_uris={}'.format(tempstatus))
                if (tempstatus == True):
                    initialized = True
                else:
                    initialized = False

            if (cls.successfulSystemInit == False):
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


