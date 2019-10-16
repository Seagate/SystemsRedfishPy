
# Redfish Reference Client - Design Overview


## Introduction

This reference client was built using the Python programming language and relies on Python 3. This document provides a
very quick overview of the design intent and provides a guideline for making changes to the client.

The redfishAPI.py module is the main function entry point. The client runs in a script mode or an interactive mode. Both
handlers, script and interactive, rely on redfishConfig and redfishCommand. Configuration data is stored in the JSON file
redfishAPI.json.

All modules rely heavily on a Trace facility and a common UrlAccess class.

The bulk of this client is implemented using commands, all of which are defined in the 'commands' sub-folder. 


## Main Module

The redfishAPI.py module is the main function entry point. Its main logic is to parse command line arguments and run
either the scripting mode or the interactive mode.

The scripting mode simply parses a text file and calls a RedfishCommand object to execute each line. The interactive
mode simply reads from standard input and calls a RedfishCommand object to execute each entry. Configuration data is
central to the processing of all commands and is described in the next section.


## Configuration Data

All configuration data is stored in the redishAPI.json file. Options specified on the command line overwrite settings in
the JSON file and are in updated in the JSON file.

To change any configuration value, either in a script file, or interactively, the exclamation point character ('!') is used
to designate a configuration change. The special command '!dump' displays all current values.

To add a new configuration setting, add it to the RedfishConfig() constructor. It will be written to, and read from, the
JSON file automatically. There are also several RedfishConfig routines that should be used to get configuration values.


## Commands

All available commands are located in the 'commands' folder. The name of the file must match the desired command. The
'show volumes' command will be handled by a Python module labeled 'commands/show_volumes.py'. To add a new command, just
create a new file in the 'commands' folder and implement the three required methods.

For example, to create a 'my command' create a file called 'commands/my_command.py' and implement prepare_url(), process_json(),
and display_results(). These methods were chosen since this is a REST API client which relies on HTTP requests to URLs.  

__Note:__ Adding new commands does not require any changes to the other modules (redfishAPI, redfishCommand, etc.). The
RedfishCommand() uses the importlib to dynamically import the required Python code for a given command. The current requirement
though is that all commands be two words and the Pythoin code reside in a file called 'word1_word2.py' in the 'commands' folder.

All commands are derived from the base class __CommandHandlerBase__ which provides several common routines to be used by commands.

All commands are executed in three steps, although simple comamnds can do nothing in the first and last step.

__Note:__ Currently, 'help' is the only single word command and exception to the two word rule.

### Step 1: prepare_url()

This method is called and it must return a string containing the URL that you want passed to the 2nd step.

### Step 2: process_json()

This method is called and passed configuration data and the URL returned from the first step. This is the main
handler for a command, and its intent is to execute a command by sending an HTTP request to a specified URL. This
command is intended to process and store results in an internal data structure that is used in step 3 to display
results.

### Step 3: display_results()

This method is called to display the results of the executing command. For some commands, this method does nothing 
since it made more sense to display results in the process_json() step. 


## Trace

A trace module is provided to add various levels of debug output. It is simply a print command with one additional
argument, the trace level. Entries are either printed or not based on the current __'!trace'__ level.

The trace levels of FATAL, ERROR and WARNING print out an additional preface string to provide a consistent format for
these types of trace entries.

A TraceLevel.INFO is expected to always be printed. And then the levels of VERBOSE, DEBUG, TRACE are intended to add
more and more information to help debugging without changing the source code. The default !trace level is INFO.
 
Here are a few examples:

``` 
Trace.log(TraceLevel.ERROR, 'Unexpected error while executing command ({}): {} -- {}'.format(command, sys.exc_info()[0], inst))
Trace.log(TraceLevel.INFO, '++ Create Disk Group: ({})...'.format(self.command))
Trace.log(TraceLevel.TRACE, '   -- {0: <12}: {1}'.format('Id', link.jsonData['Id']))
```

## UrlAccess

This is a common class for handling all HTTP requests. The process_request() is designed to handle all request
types - 'GET', 'DELETE', 'POST'. Session authentification is included in the request when 'addAuth' is True. But
in practive, the user must run 'create session' to obtain an authentification certificate.

The URL passed in to process_request() should not include HTTP, HTTPS, or the IP Address. That information is 
added to the passed in URL based on the configuration data. This allows a user to interactively, or in a script
file, change the destination IP Address for a Redfish Service.

For commands that require POST data, it should be passed in as a JSON data object.

In order to create a JSON data representation of an object, the convert_to_dict() method is used. This uses the standard
python feature to create a dictionary representation of an object. The class for that JSON data does have to match the
desired JSON format, using dictionary and lists, but hopefully this more readable as a class that is converted to JSON.
Several examples can be found in commands such as *'create_volume.py'* and *'create_diskgroup'*.


## Command Help

Help for each command is built into the Python file for each command. The 'help' command parses every Python file in the
'commands' folder extracting any help data available. When 'help' is executed from the interactive prompt, a list of all
commands and their synopsis is displayed. When 'help [command]' is executed from the interactive prompt, the command and
full description is displayed, as formatted. The tags used for help extraction are: 

| Command            | Description |
| ------------------ | ----------- |
| @command           | The command available for execution. |
| @synopsis          | A shot description of what the command performs. |
| @description-start | The start of a longer description for the command. |
| @description-end   | The end of a longer description for the command. |

Example: 

```bash
#
# @command create session
#
# @synopsis Establish a session with the Redfish Service (using mcip, username, and password)
#
# @description-start
#
# This command attempts to establish a session with the Redfish Service. It will use the
# mcip, username, and password that are defined in the configuration settings. Use '!dump' to
# view all configuration settings. Use '!setting value' to update the setting and value.
#
# Example:
# 
# (redfish) create session
# 
# ++ Establish Redfish session: (/redfish/v1/SessionService/Sessions)...
# [] Redfish session established (key=5ecff24c0259db2b810327047538dc9f)
# 
# @description-end
#
```
 