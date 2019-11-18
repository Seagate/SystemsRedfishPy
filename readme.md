
# Seagate Systems Redfish Python Reference Client


## Introduction

The Seagate Systems (aka EDS) provides a Redfish/Swordfish Service that was first released in 2019. This new service was first
featured on the Seagate Indium product line, and then the PODs product line. This package provides a reference client that can
be used on any computer with Python installed. This reference client enables you to perform configuration and maintenance
operations on a Indium controller using the Redfish/Swordfish API.

The Redfish API is a standard REST API maintained by [DMTF Redfish](https://www.dmtf.org/standards/redfish). The Swordfish API
is an extension to the Redfish API maintained by [SNIA Swordfish](https://www.snia.org/forums/smi/swordfish).

|           **Contributors**           |
| ------------------------------------ |
| Joe Skazinski, Seagate Technologies  |


## Installation

This project is maintained under the [EDS ADT seagit repository](https://seagit.okla.seagate.com/eds-adt/SystemsRedfishPy).

The process to use this client is to clone a copy of the project on your local hard drive. Once you have the project run:

### Using SSH to Clone the Project Under Linux

You won't be able to pull or push project code via SSH until you add an SSH key to your profile. SSH keys allow you to establish a secure connection between your computer and GitLab.

1. Check for an existing SSH Key - [Seagit Readme](https://seagit.okla.seagate.com/help/ssh/README)

2) Generate a new SSH key pair, follow the prompts and use the default filename suggested
```
ssh-keygen -t rsa -C "your.email@example.com" -b 4096
```

3) Copy your public SSH key to the clipboard
```
cat ~/.ssh/id_rsa.pub
```
Then select and copy the output.

4) Paste this key into the GitLab Settings page

* Open a web browser to - (https://seagit.okla.seagate.com/groups/eds-adt)
* Click on the down-arrow in the upper right-hand corner, next to your picture
* Choose Settings
* Click on SSH Keys
* Paste your publick Key into the 'Key' text box
* Click Add Key

5) Clone the project
```
cd base_directory
git clone git@seagit.okla.seagate.com:eds-adt/SystemsRedfishPy.git (Enter your password for your private key)
cd SystemsRedfishPy
python3 redfishAPI.py
```

### Using HTTPS to Clone the Project Under Windows

```
$ cd <working-folder>
$ git clone https://seagit.okla.seagate.com/eds-adt/SystemsRedfishPy.git
$ cd SystemsRedfishPy
$ python redfishAPI.py -h
```


## Requirements

Your client computer must have Python3 installed. You will also need network access to the desired controller, and know the 
IP Address of the target controller running the Redfish Service.


## Quick Tutorial

This client can run in either an interactive mode, or by parsing a script file. This quick tutorial demonstrates the
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

| Command           | Description |
| ----------------- | ----------- |
| !dump             | Print out all configuration options. This is useful to learn what settings are available. |
| ![option] [value] | Change the value for that setting. |

To configure which controller to talk to:

| Command              | Description |
| -------------------- | ----------- |
| !mcip 10.235.221.120 | Change all HTTP communications to use this new ip address. |
| !username [name]     | Change the username to '[name]' that is used to log in to the Redfish Service. |
| !password [password] | Change the password to '[password]' that is used to log in to the Redfish Service. |

When running commands, you have several options to help debug issues:

| Command              | Description |
| -------------------- | ----------- |
| !dumpjsondata 1      | Display all JSON data read from the Redfish Service. Zero will turn it off. |
| !dumppostdata 1      | Display all data that is sent via an HTTP POST operation. Zero will turn it off. |
| !trace 5             | Turn on additional tracing at a VERBOSE level. |
| !trace 6             | Turn on additional tracing at a DEBUG level. |
| !trace 7             | Turn on additional tracing at a TRACE level. |
| !trace 4             | Reset tracing to the default INFO level. |

### Redfish Commands

Most commands require that you establish a session with the target Redfish Service. To do so, use 'create session'.
This command will use the configuration settings, listed above, such as mcip, username, and password and attempt to
establish a session.

```bash
(redfish) create session

++ Establish Redfish session: (/redfish/v1/SessionService/Sessions)...
[] Redfish session established (key=8356051e862ca5de23bc2850a3903ad6)

[] Elapsed time: 0m 1s to execute command
```

The main redfish commands are used for debugging or learning more about the data returned by the Redfish Service.

For example:


| Command                     | Description |
| --------------------------- | ----------- |
| redfish json <url>          | Display the JSON data returned from a GET to <url>. Errors are also reported. |
| redfish urls [optional url] | Traverse every URL reported by the service, validate them, and produce a report. If no optional url is specified, then traversing starts with '/redfish/v1'. |


### Systems Commands

The system commands use the Redfish Service API to create volumes, display disks, and other configuration and
maintenance items.

For example:

```bash
(redfish) show disks - will display all disk drives in the system
(redfish) show pools - will display all configured virtual pools
(redfish) show volumes - will display all configured volumes
(redfish) create diskgroup name=dgA01 disks=0.7,0.8 pool=A level=raid1 - to create a new RAID1 disk group
(redfish) create volume name=TestVol01 size=100000000000 pool=A - to create a new volume
```

### Design

If you want to make changes to this reference client, there is a [design document](design.md) that provides an overview
of how to make changes and add new commands. The main system design allows you to add commands, and help for
commands, without having to change any of the underlying core files. The only step needed is to add your new
command to the 'commands' folder using the prescribed template.

 