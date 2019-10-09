
# Seagate Systems Redfish Python Reference Client


## Introduction

The Seagate Systems (aka EDS) provides a Redfish/Swordfish Service that was first released in 2019. This new service was first
featured on the Seagate Indium product line, and then the PODs product line. This package provides a reference client that can
be used on any computer with Python installed. This reference client enables you to perform configuration and maintenance
operations on a Indium controller using the Redfish/Swordfish API.

The Redfish API is a standard REST API maintained by [DMTF Redfish](https://www.dmtf.org/standards/redfish). The Swordfish API
is an extension to the Redfish API maintained by [SNIA Swordfish](https://www.snia.org/forums/smi/swordfish).


## Installation

This project is maintained under the [EDS ADT seagit repository](https://seagit.okla.seagate.com/eds-adt/SystemsRedfishPy).

The process to use this client is to create a copy of the project on your local hard drive. Once you have the project run:

```
$ cd <working-folder>
$ git clone https://seagit.okla.seagate.com/eds-adt/SystemsRedfishPy.git
$ cd SystemsRedfishPy
$ python redfishAPI.py -h
```

In order to use SSH, you will need to [add an SSH key](https://seagit.okla.seagate.com/profile/keys).



## Requirements

Your client computer must have Python3 installed. You will also need network access to the desired controller, and know the 
IP Address of the target controller running the Redfish Service.


## Quick Tutorial

This client can run in either an interactive mode, or by parsing a script files. This quick tutorial demonstrates the
interactive mode. All commands entered at the prompt can also be pasted into a text file and run as a script.

Open a terminal window and change directories to the SystemsRedfishPy folder. Run the command 'python redfishAPI.py'
and you will be presented with a '(redfish)' prompt. 

```bash
>python redfishAPI.py

--------------------------------------------------------------------------------
[1.0] Redfish API
--------------------------------------------------------------------------------
[] Run Redfish API commands interactively...

(redfish)
```

There are four main categories of commands that can be entered.
 
### Help

help - provides a list of available commands
help [command name] - provides details on a command

### Configuration Commands

There are several configuration commands useful to set up communications and tracing.

!dump - will print out all configuration options. This is useful to learn what settings are available.
![option] [value] - will change the value for that setting.

To configure which controller to talk to:

!mcip 10.235.221.120 - will change all HTTP communications to use this new ip address.
!username [name] - will change the username to '[name]' that is used to log in to the Redfish Service.
!password [password] - will change the password to '[password]' that is used to log in to the Redfish Service.

When running commands, you have several options to help debug issues:

!dumpjsondata 1 - Will display all JSON data read from the Redfish Service. Zero will turn it off.
!dumppostdata 1 - Will display all data that is sent via an HTTP POST operation. Zero will turn it off.
!trace 5 - will turn on additional tracing at a VERBOSE level.
!trace 6 - will turn on additional tracing at a VERBOSE level.
!trace 7 - will turn on additional tracing at a VERBOSE level.
!trace 4 - will reset tracing to the default INFO level.

### Redfish Commands

Most commands require that you establish a session with the target Redfish Service. To do so, use 'redfish session'.
This command will use the configuration settings, listed above, such as mcip, username, and password and attempt to
establish a session.

```bash
(redfish) redfish session

++ Establish Redfish session: (/redfish/v1/SessionService/Sessions)...
[] Redfish session established (key=8356051e862ca5de23bc2850a3903ad6)

[] Elapsed time: 0m 1s to execute command
```

The main redfish commands are used for debugging or learning more about the data returned by the Redfish Service.

For example:

redfish json <url> - will display the JSON data returned from a GET to <url>. Errors are also reported.
redfish urls [optional url] - will traverse every URL reported by the service, validate them, and produce a report.
                              If no optional url is specified, then the traversing starts with '/redfish/v1'.


### Systems Commands

The system commands use the Redfish Service API to create volumes, display disks, and other configuration and
maintenance items.

For example:

(redfish) show disks - will display all disk drives in the system
(redfish) show pools - will display all configured virtual pools

### Design

If you want to make changes to this reference client, there is a design document that provides an overview
of how to make changes and add new commands. The main system design allows you to add commands, and help for
commands, without having to change any of the underlying core files. The only step needed is to add your new
command to the 'commands' folder using the prescribed template.

 