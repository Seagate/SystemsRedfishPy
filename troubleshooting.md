# Redfish Client Troubleshooting

#### Copyright (c) 2021 Seagate Technology LLC and/or its Affiliates, All Rights Reserved

## Introduction

This document provides troubleshooting tips.

## Topics

* [ImportError: No module named enum](#tip1)
* [Errno 111 Connection refused](#tip2)
* [WinError 10061 No connection could be made](#tip3)


## <a name="tip1">ImportError: No module named enum</a>

You run `python redfishAPI.py -c myconfig.json` and it fails immediately. This may be caused by using a python2 version instead of python3. Run `python --version` to ensure you are running the correct version of Python.

```
$ python redfishAPI.py -c myconfig.json
Traceback (most recent call last):
  File "redfishAPI.py", line 16, in <module>
    from core.label import Label
  File "/mnt/c/repos/gitlab.seagit/SystemsRedfishPy/core/label.py", line 17, in <module>
    from core.trace import TraceLevel, Trace
  File "/mnt/c/repos/gitlab.seagit/SystemsRedfishPy/core/trace.py", line 16, in <module>
    from enum import IntEnum
ImportError: No module named enum

$ python --version
Python 2.7.18

$ python3 --version
Python 3.8.5

$ python3 redfishAPI.py -c myconfig.json

--------------------------------------------------------------------------------
[2.1.0] Redfish API
--------------------------------------------------------------------------------
-- Reading history (redfishAPI.hist) [100]
[] Run Redfish API commands interactively...

(redfish)
```

## <a name="tip2">[Errno 111] Connection refused</a>

You run a simple command that does not require authentication and tit fails with the following error message. This is most likely caused
by the storage controller not be up and running on the provided IP Address.

```
(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)

[] URL        : /redfish/v1
[] Status     : 0
[] Reason     : [Errno 111] Connection refused
```

## <a name="tip3">[WinError 10061] No connection could be made because the target machine actively refused it</a>

You run a simple command that does not require authentication and tit fails with the following error message. This is most likely caused
by the storage controller not be up and running on the provided IP Address.

```
(redfish) http get /redfish/v1
[] http get: url (/redfish/v1)

[] URL        : /redfish/v1
[] Status     : 0
[] Reason     : [WinError 10061] No connection could be made because the target machine actively refused it
```
