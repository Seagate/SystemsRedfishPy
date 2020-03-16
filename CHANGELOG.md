# Change Log

## [1.1.5] - 2020-03-13
- Added a new configuration variable for the interactive session. The new value is 'entertoexit'. When True,
  the user can press Enter to exit the shell. When False, the user must type exit or quit.
- Added a new 'run loop' command to run and time multiple HTTP GET URI operations. Updated urlAccess.py to
  time and store in UrlStatus a new elapsedMicroseconds value.
- Corrected the storage of the current version in the JSON config file.
- Replaced hard-coded URIs with discovered values from the Root Service and beyond.
- Corrected a typo in the prologue of most files.
- Added testStorageGroup.py
- Added new command 'purge system' and 'show system'

## [1.1.4] - 2020-01-10
- Added new command 'delete sessions $sessionid' so that a script can automatically delete the current
  session and not leave it active after the python redfishAPI exits.
- Added a new simple Label object to encode and decode interal variables, such as $sessionid.
- Added new redfishAPI command line option to pass in a user config file. The user can now call
  python redfishAPI --config myconfig.json or -c myconfig.json and not have to modify the checked in
  version. This also applies to python redfishUnittest --config myconfig.json or -c myconfig.json.
- Added logic to automatically delete the current session before redfishAPI exits.
- Modified urlAccess to handle a byte stream
- Updated the unittest tests to only create a single session, and initialize system data only once.

## [1.1.3] - 2019-12-23
- Corrected the 'show fans' command since the reported JSON data was modified
- Corrected the 'show thermal' command since the reported JSON data was modified

## [1.1.2] - 2019-12-18
- Corrected the drive in use flag for functional testing.

## [1.1.1] - 2019-12-16
- Initial Public Release
- Commands Provided:
    * **create storagegroup** - Create a storage group to map a volume making it visibile to a host or hosts.
    * **create session** - Establish a session with the Redfish Service (using mcip, username, and password)
    * **create volume** - Create a volume
    * **delete diskgroups** - Delete one or more comma-separated disk groups by name or serial number
    * **delete pools** - Delete one or more comma-separated pools by name or serial number
    * **delete sessions** - Delete one or more comma-separated session ids
    * **delete storagegroups** - Delete one or more comma-separated storage groups by serial number
    * **delete volumes** - Delete one or more comma-separated volumes by name or serial number
    * **help [command]** - Display a synopsys of all commands, or details for a command
    * **map volume** - Create or update a storage group to map a volume making it visibile to a host or hosts.
    * **redfish json** - GET and display JSON data for a given URL
    * **create diskgroup** - Create a disk group and add it to a pool
    * **redfish metadata** - GET and display the metadata reported by the Redfish Service
    * **redfish odata** - GET and display the odata reported by the Redfish Service
    * **redfish services** - GET and display the JSON data reported by the Redfish Service root
    * **redfish urls** - Test all URLs reported by this REST API
    * **redfish version** - Display the current version of the Redfish Service.
    * **run script** - Run a script file
    * **show diskgroups** - Display all allocated disk groups and disk group infromation
    * **show disks** - Display all disk drives found in the system
    * **show fans** - Display all fan readings from the system.
    * **show initiators** - Display all initiators found in the system
    * **show pools** - Display all allocated virtual pools and pool information
    * **show ports** - Display all ports found in the system
    * **show sessions** - Display all active sessions, requires an active session
    * **show storagegroups** - Display all created storage groups
    * **show thermal** - Display all temperature data from the system
    * **show volumes** - Display all configured volumes