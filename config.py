#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of thThe MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# config.py - Redfish API global values 
#
# ******************************************************************************************
#

################################################################################
# Internal 
################################################################################
sessionConfig = '$config'
sessionIdVariable = '$sessionid'

################################################################################
# Redfish 
################################################################################
defaultConfigFile = 'redfishAPI.json'

################################################################################
# Storage Services URIs
################################################################################
classesOfService = '/redfish/v1/StorageServices/S1/ClassesOfService/'
classesOfServiceDefault = '/redfish/v1/StorageServices(1)/ClassesOfService(Default)'
drives = '/redfish/v1/StorageServices/S1/Drives/'
endpoints = '/redfish/v1/StorageServices/S1/Endpoints/'
endpointGroups = '/redfish/v1/StorageServices/S1/EndpointGroups/'
metadata = '/redfish/v1/$metadata'
odata = '/redfish/v1/odata'
redfish = '/redfish/'
redfishV1 = '/redfish/v1/'
sessions = '/redfish/v1/SessionService/Sessions/'
storageGroups = '/redfish/v1/StorageServices/S1/StorageGroups/'
storagePools = '/redfish/v1/StorageServices/S1/StoragePools/'
thermal = '/redfish/v1/Chassis/enclosure_0/Thermal/'
volumes = '/redfish/v1/StorageServices/S1/Volumes/'

################################################################################
# Testing
################################################################################
reportFolder = 'reports'
sleepTimeAfterDelete = 2
testFolder = 'tests'
