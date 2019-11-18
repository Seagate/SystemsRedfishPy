# *************************************************************************************
#
# redfishAPI - Module to run commands using the Systems Redfish API
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

import argparse
import sys

from redfishConfig import RedfishConfig
from redfishScript import RedfishScript
from redfishInteractive import RedfishInteractive
from trace import TraceLevel, Trace

version = '1.0.5'

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
    print('[{}] Redfish API'.format(version))
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
        rs = RedfishScript()
        returncode = rs.execute_script(redfishConfig, args.scriptfile)

    sys.exit(returncode)
