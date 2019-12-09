# *************************************************************************************
#
# config - Redfish API global values 
#
# -------------------------------------------------------------------------------------

# Copyright 2019 Seagate Technology LLC or one of its affiliates.
#
# The code contained herein is CONFIDENTIAL to Seagate Technology LLC.
# Portions may also be trade secret. Any use, duplication, derivation, distribution
# or disclosure of this code, for any reason, not expressly authorized in writing by
# Seagate Technology LLC is prohibited. All rights are expressly reserved by
# Seagate Technology LLC.
#
# -------------------------------------------------------------------------------------
#

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
