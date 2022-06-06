[![License: The MIT License](https://img.shields.io/badge/license-MIT-green?longCache=true)](https://opensource.org/licenses/MIT)  [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)  [![GitHub release](https://img.shields.io/github/release/Naereen/StrapDown.js.svg)](https://GitHub.com/Naereen/StrapDown.js/releases/)

# SystemsRedfishPy

## Cross platform Python tool for provisioning and managing storage systems using the RESTful Redfish/Swordfish API.

#### Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved

## Introduction

***SystemsRedfishPy*** is a command line tool that implements the client side of the Redfish RESTful API for Storage System Management.

Source code files of the SystemsRedfishPy open source project are available to you under [The MIT License](https://opensource.org/licenses/MIT).  The
SystemsRedfishPy project repository is maintained at https://github.com/Seagate.

**Redfish** is the new RESTful API for hardware management defined by the DMTF Scalable Platform Management Forum (SPMF).  It provides a 
modern, secure, multi-node, extendable interface for hardware management. **Swordfish** authored by SNIA provides extensions for handling
storage specific provisioning and management. 

**SystemsRedfishPy** goes beyond common HTTP tools such as curl to provide quick and easy storage management and storage volume creation. This
tool provides simple one-step commands handling multiple Redfish URI requests in order to carry out storage management. The main features of
this package are:
 
* Command line or script file execution
* Set up is a breeze and configuration settings are modified with a **bang** (`!setting [value]`)
* Add new configuration variables via a single line with easy access routines
* Handles multiple command sets for various product brands - `!brand [product]` to switch between command sets 
* Drop in new commands to increase desired functionality - with no modifications to the infrastructure 
* Help text built in to each command file
* Built in unittest for quick regression testing of a Redfish service
* Debug logging and tracing built in for command line usage or unit test cases 
* Class modules to simplify working with URIs and JSON data 

## Background

Seagate Systems (Enterprise Data Solutions (EDS)) provides a Redfish/Swordfish Service that was first released in 2019. This
new service was first featured on the Seagate Indium product line. This package provides a reference client that can be used on
any computer with Python installed. This reference client enables you to perform configuration and maintenance operations on a
storage controller using the Redfish/Swordfish API.

The Redfish API is a standard REST API maintained by [DMTF Redfish](https://www.dmtf.org/standards/redfish). The Swordfish API
is an extension to the Redfish API maintained by [SNIA Swordfish](https://www.snia.org/forums/smi/swordfish).


## Why SystemsRedfishPy?

1. **SystemsRedfishPy** was originally written during the development of the Redfish storage service, helpful for validating
storage service operations and to quickly and easily display JSON data from various URIs.
2. **SystemsRedfishPy** was extended to provide test cases to quickly validate and report on the status of the current
Redfish service version. 
3. **SystemsRedfishPy** provides an example implementation for how a client can execute common storage management functions
like create a RAID disk group, create a storage pool, create a storage volume, and map that volume to a host computer.
4. **SystemsRedfishPy** can also be called from other scripts, used as a command line tool, or execute scripts to quickly provision
storage or check on the health of a storage system. 


## Installation

This project is maintained under [GitHub SystemsRedfishPy](https://github.com/Seagate).

The process to use this client is to clone a copy of the project to your local hard drive.

Clone the project
```
cd base_directory
git clone SystemsRedfishPy.git
cd SystemsRedfishPy
python3 redfishAPI.py
```

## Requirements

Your client computer must have Python3.6 (or later) installed. You will also need network access to the desired controller,
and know the IP Address of the target controller running the Redfish Service. User credentials are required in order to
create a Redfish sessions and provision storage.

Using **SystemsRedfishPy** relies on the packages specified in requirements.txt. But HTML and XML packages are used if you
desire to run unit test cases and produce HTML or XML reports and these are not automatically installed. See the [test document](UNITTEST.md) for more information.

- `pip install -r requirements.txt`

**Note:** You may have to use `pip install --user -r requirements.txt` in some Windows environment.

## Quick Tutorial

This client can run in either an interactive mode, or by parsing a script file. This quick tutorial demonstrates the
interactive mode. All commands entered at the prompt can also be pasted into a text file and run as a script.

Open a terminal window and change directories to the SystemsRedfishPy folder. Run the command 'python redfishAPI.py'
and you will be presented with a '(redfish)' prompt.

As a best practice, it is suggested that you copy redfishAPI.cfg to myconfig.cfg or any name of your choice. Then edit the following properties in that file:
* "dumphttpdata": "True",
* "ipaddress": "[your-service-ip]",
* "password": "[service-password]",
* "username": "[service-username]",
* "http": "http or https",

Additional Properties Note:
* Set `!serviceversion 1` - to work with the earlier version of the Redfish Service that supported ClassesOfService
* Set `!serviceversion 2` - to work with the latest version of the Redfish Service that supports fabrics, composition, etc.
* This can be done at the (redfish) prompt using !serviceversion [1|2]

Then, use python redfishAPI.py -c myconfig.json to run interactive commands using your system configuration settings.

```bash
> python3 redfishAPI.py -c myconfig.json

--------------------------------------------------------------------------------
[2.1.4] Redfish API
--------------------------------------------------------------------------------
[] Run Redfish API commands interactively...

(redfish)
```

There are five main categories of commands that can be entered.
 
### Help

help - provides a list of available commands
help [command name] - provides details on a command

### Configuration Commands

There are several configuration commands useful to set up communications and tracing.

| Command            | Description |
| ------------------ | ----------- |
| !dump              | Print out all configuration options. This is useful to learn what settings are available. |
| ![setting] [value] | Change the value for that setting. |

To configure which controller to talk to:

| Command              | Description |
| -------------------- | ----------- |
| !ipaddress 10.235.221.120 | Change all HTTP communications to use this new ip address. |
| !username [name]     | Change the username to `[name]` that is used to log in to the Redfish Service. |
| !password [password] | Change the password to `[password]` that is used to log in to the Redfish Service. |

When running commands, you have several options to help debug issues, and to configure the system. Here is a complete list:

| Command                         | Description |
| ------------------------------- | ----------- |
| !annotate [True,False]          | Provides a banner for every line of script file processed. Default is `True`. |
| !brand [product]                | Specifies the subfolder of commands to use. Default is `systems`, but `example` is provided. |
| !certificatecheck [True,False]  | When False, the URL will be opened using context=ssl._create_unverified_context. Default is `False`. |
| !dump                           | Print out all configuration options. This is useful to learn what settings are available. |
| !dumphttpdata [True,False]      | Display all HTTP data read from the Redfish Service. Useful for additional info. Default is `False`. |
| !dumpjsondata [True,False]      | Display all JSON data read from the Redfish Service. Default is `False`. |
| !dumppostdata [True,False]      | Display all data that is sent via an HTTP POST operation. Default is `False`. |
| !entertoexit [True,False]       | When True, pressing Enter in interactive mode will exit the tool. Default is `False`. |
| !http [https,https]             | Switch between use http:// and https://. Default is `https`. |
| !linktestdelay [seconds]        | How long to delay between URLs when running the 'redfish urls' command. Default is `0`. |
| !ipaddress [ip]                 | Change all HTTP communications to use this new ip address. |
| !port [port]                    | Change all HTTP communications to use this new port value, default is 80. |
| !password [password]            | Change the password to `[password]` that is used to log in to the Redfish Service. |
| !serviceversion [1,2]           | Specify the Redfish Service version. This changes command behavior based on supported schemas. Default is `2`. |
| !showelapsed [True,False]       | Display how long each command took. Default is `False`. |
| !trace [4-7]                    | Turn on additional tracing. 4=DEFAULT, 5=VERBOSE, 6=DEBUG, 7=TRACE. Default is `4`. |
| !urltimeout [seconds]           | How long to wait for a URL request before timing out. Default is `30`. |
| !usefinalslash [True,False]     | When True, all Redfish URIs will have a slash as the final character in the URL. Default is `True`. |
| !username [name]                | Change the username to `[name]` that is used to log in to the Redfish Service. |


### Redfish Commands

Most commands require that you establish a session with the target Redfish Service. To do so, use 'create session'.
This command will use the configuration settings, listed above, such as ipaddress, username, and password and attempt to
establish a session.

```bash
--------------------------------------------------------------------------------
[2.1.4] Redfish API
--------------------------------------------------------------------------------
[] Run Redfish API commands interactively...

(redfish) create session
   -- ServiceVersion: 2
   -- IP Address    : https://<ip>
   -- Discovered: Root                      >> /redfish/v1
   -- Discovered: Chassis                   >> /redfish/v1/Chassis/
   -- Discovered: CompositionService        >> /redfish/v1/CompositionService/
   -- Discovered: Fabrics                   >> /redfish/v1/Fabrics/
   -- Discovered: Managers                  >> /redfish/v1/Managers/
   -- Discovered: SessionService            >> /redfish/v1/SessionService/
   -- Discovered: Systems                   >> /redfish/v1/Systems/
   -- Discovered: Tasks                     >> /redfish/v1/TaskService/
   -- Discovered: UpdateService             >> /redfish/v1/UpdateService/
   -- Discovered: Sessions                  >> /redfish/v1/SessionService/Sessions/
   -- Discovered: metadata                  >> /redfish/v1/$metadata/
   -- Discovered: odata                     >> /redfish/v1/odata/

[] Redfish session established (4:<sessionkey>)

[] Elapsed time: 0m 2s to execute command
```

The main redfish commands are used for debugging or learning more about the data returned by the Redfish Service.

For example:

| Command                     | Description |
| --------------------------- | ----------- |
| redfish json [url]          | Display the JSON data returned from a GET to [url]. Errors are also reported. |
| redfish urls [optional url] | Traverse every URL reported by the service, validate them, and produce a report. If no optional url is specified, then traversing starts with '/redfish/v1'. |


### Systems Commands

The system commands use the Redfish Service API to create volumes, display disks, and other configuration and
maintenance items. Use 'help [command]' to display additional examples. 

For example:

```bash
(redfish) show disks - will display all disk drives in the system
(redfish) show pools - will display all configured virtual pools
(redfish) show volumes - will display all configured volumes
(redfish) create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1 - to create a new RAID1 disk group
(redfish) create volume name=TestVol01 size=100000000000 pool=A - to create a new volume
```

### HTTP Commands

The HTTP commands allow you to do native HTTP GET, DELETE, POST, and PATCH commands.

As a note, most Redfish commands require that you establish a session with the target Redfish Service. If you use
the 'http post' command to create a session, you should also call 'save session [id] [key]' so that all following
http commands can use the session credentials.
 
| Command                                       | Description |
| --------------------------------------------- | ----------- |
| http get [url]                                | Perform an HTTP GET operation on a URI |
| http post [url] [json or filename]            | Perform an HTTP POST operation on a URI, sending the specified JSON data |
| http patch [url] [json or filename]           | Perform an HTTP PATCH operation on a URI, sending the specified JSON data |
| http delete [url]                             | Perform an HTTP DELETE operation on a URI |
| http push [url] [imagefile] [<]json or file]  | Perform an HTTP POST operation to transfer a file to a URI |

Examples:

```bash
(redfish) http get /redfish
(redfish) http get /redfish/v1
(redfish) http post /redfish/v1/SessionService/Sessions { "UserName": "[username]", "Password": "[password]" }
(redfish) save session [id] [key]
(redfish) http get /redfish/v1/Chassis
(redfish) http get /redfish/v1/Managers
(redfish) http post /redfish/v1/SessionService/Sessions credentials.json
```
### Get Log Commands

The get logs commands allow you retrieve controller or drive logs. Here are examples of executing each.

```bash
(redfish) get logs component=controller

++ get logs: /redfish/v1/Systems/00C0FF437ED5/LogServices/controller_a/Actions/LogService.CollectDiagnosticData...
++ POST get logs (controller, CollectControllerLog)

   >> Monitor task 'getlogs-task' for Completed
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 30)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Running' (sleep 3)
      == TaskState: 'Completed'

++ POST get logs (controller, DownloadLogData)
   -- Status        : 200
   -- Reason        : OK
   -- Download complete to 'logfile.zip'
```

An example of retrieving disk drive logs.

```bash
(redfish) get logs component=drive

```

## Redfish Tutorials

| Tutorial                       | Description |
| ------------------------------ | ----------- |
| [tutorial-redfish-service-v1.md](tutorial-redfish-service-v1.md) | Explore Redfish API operations using the Seagate Systems Redfish Service v1. |


## Design

If you want to make changes to this reference client, there is a [design document](design.md) that provides an overview
of how to make changes and add new commands. The main system design allows you to add commands, and help for
commands, without having to change any of the underlying core files. The only step needed is to add your new
command to the 'commands' folder using the prescribed template.


## Unit Testing

If you want to run unit testing, the [unit test document](unittest.md) provides an overview of how to install
the reporting packages, run unit tests, and also add new unit tests.
