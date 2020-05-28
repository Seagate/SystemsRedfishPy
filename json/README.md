# SystemsRedfishPy - JSON Folder

## Introduction

This folder is used to store example JSON data files that can be used for various HTTP operations.

* credentials.json - An example JSON file that can be used to create a session. MUST be modified.
* create_diskgroup.json - An example JSON file that can be used to create a disk group. MAY have to be modified.
* create_volume.json - An example JSON file that can be used to create a storage volume. MAY have to be modified.
* create_storagegroup.json - An example JSON file that can be used to create a storage group. MAY have to be modified.
* patch_volume.json - An example JSON file that can be used to modify the name of a volume. MAY have to be modified.

## Examples

* (redfish) http post /redfish/v1/SessionService/Sessions json\credentials.json
* (redfish) save session <id> <key>

* (redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "username", "Password": "password" }
* (redfish) save session <id> <key>

* (redfish) http post /redfish/v1/StorageServices/S1/StoragePools json\create_diskgroup.json
* (redfish) http post /redfish/v1/StorageServices/S1/Volumes json\create_volume.json
* (redfish) http post /redfish/v1/StorageServices/S1/StorageGroups/ json\create_storagegroup.json

* (redfish) http patch /redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000 json\patch_volume.json
* (redfish) http patch /redfish/v1/StorageServices/S1/Volumes/00c0ff5112490000d08ccf5e01000000 { "Name": "NewAVolume01" }
