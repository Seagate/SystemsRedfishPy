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
# redfishAPI.py - Module to run commands using the Systems Redfish API. 
#
# ******************************************************************************************
#

import argparse
import sys
from core.redfishConfig import RedfishConfig
from core.redfishScript import RedfishScript
from core.redfishInteractive import RedfishInteractive
from version import __version__


################################################################################
# main()
################################################################################

if __name__ == '__main__':

    redfishCLIEpilog = '''Examples:
  >> Run Redfish API commands interactively. 
  python redfishAPI.py
  
  >> Run a Redfish API script file. The text script file can be a series of program configuration and API commands.
  python redfishAPI.py -s <scriptfile>
  
  >> Run a Redfish API script file with full debugging.
  python redfishAPI.py -s <scriptfile> -t 6
  '''
    
    print('')
    print('-' * 80)
    print('[{}] Redfish API'.format(__version__))
    print('-' * 80)

    returncode = 0
    
    parser = argparse.ArgumentParser(
        description='Run the Seagate Systems Redfish API command processor.',
        epilog=redfishCLIEpilog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-s', '--scriptfile', help='Specify the Redfish API script file.')
    parser.add_argument('-t', '--tracelevel', help='Set the trace level (4, 5, 6, or 7) INFO=4, VERBOSE=5, DEBUG=5, TRACE=6', nargs='?', const=1, type=int)

    args = parser.parse_args()

    # Load configuration settings, which can be overwritten at the command line or in a script file
    redfishConfig = RedfishConfig('redfishAPI.json')

    if (args.tracelevel != None):
        redfishConfig.update('trace', args.tracelevel)

    if (args.scriptfile == None):
        # Run interactive mode
        ri = RedfishInteractive()
        ri.execute(redfishConfig)
    else:
        # Run script mode
        returncode = RedfishScript.execute_script(redfishConfig, args.scriptfile)

    sys.exit(returncode)
