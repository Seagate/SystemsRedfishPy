#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2019 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# redfishUnittest.py - Module to run and report on all unit tests. 
#
# ******************************************************************************************
#

from core.label import Label
from core.trace import TraceLevel, Trace
import argparse
import config
import sys
import unittest
import HtmlTestRunner
import xmlrunner

################################################################################
# main()
################################################################################

if __name__ == '__main__':
    
    print('')
    print('-' * 80)
    print('[] Redfish Unit Tests')
    print('-' * 80)

    returncode = 0

    redfishUnittestEpilog = '''Examples:
  >> Run Redfish unit tests and generate an HTML report. 
  python redfishUnittest.py --html
  
  >> Run Redfish unit tests and generate an XML report. 
  python redfishUnittest.py --xml   
  '''

    parser = argparse.ArgumentParser(
        description='Run Seagate Systems Redfish unit tests and generate a report.',
        epilog=redfishUnittestEpilog,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-c', '--config', help='Specify the Redfish API JSON configuration file.')
    parser.add_argument('--html', help='Generate an HTML unit test report', action='store_true', required=False)
    parser.add_argument('--xml', help='Generate an XML unit test report', action='store_true')

    args = parser.parse_args()

    Label.encode(config.sessionConfig, config.defaultConfigFile if args.config == None else args.config)

    extension = ''
    testFiles = 'test*.py'

    if (args.xml):
        Trace.log(TraceLevel.INFO, '++ Generate XML Report')
        extension = 'xml'
        tests = unittest.TestLoader().discover(config.testFolder, pattern=testFiles)
        testRunner = xmlrunner.XMLTestRunner(output=config.reportFolder)
        testRunner.run(tests)
    else:
        Trace.log(TraceLevel.INFO, '++ Generate HTML Report')
        extension = 'html'
        tests = unittest.TestLoader().discover(config.testFolder, pattern=testFiles)
        testRunner = HtmlTestRunner.HTMLTestRunner(combine_reports=True, open_in_browser=True, add_timestamp=True) 
        testRunner.run(tests)

    sys.exit(returncode)
