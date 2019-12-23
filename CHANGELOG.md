# Change Log


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