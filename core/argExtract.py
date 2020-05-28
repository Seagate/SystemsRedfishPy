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
# argExtract.py - A module used to extract values or JSON data from command line arguments. 
#
# ******************************************************************************************
#

import json
from core.trace import TraceLevel, Trace

################################################################################
# JsonExtract
################################################################################
class ArgExtract:

    @classmethod
    def get_value(cls, command, position):
        """Extract the specified argument from the comamnd line string."""

        Trace.log(TraceLevel.TRACE, '   ++ get_value: position ({}), command ({})'.format(position, command))
        success = False
        argument = ''
        words = command.split(' ')
        Trace.log(TraceLevel.TRACE, '   ++ get_value: len ({}), words ({})'.format(len(words), words))

        if (len(words) >= position):
            argument = words[position]
            success = True
        else:
            success = False

        return success, argument

    @classmethod
    def get_json(cls, command, position):
        """Extract inline JSON data, or JSON data from a file, and return that data to caller."""

        success = False
        jsonData = None

        Trace.log(TraceLevel.TRACE, '   ++ get_json: command ({})'.format(command))

        #
        # Inline JSON data must be contaiined with brackets: { and }
        # Otherwise, an attempt is made to extract a filename and read JSON data from the file.
        # 
        pos1 = command.find('{')
        if pos1 == -1:
            # Treat the parameter as a filename
            words = command.split(' ')
            Trace.log(TraceLevel.TRACE, '   ++ get_json: len ({}), words ({})'.format(len(words), words))
            if (len(words) >= position):
                filename = words[position]
                Trace.log(TraceLevel.TRACE, '   >> get_json: open ({})'.format(filename))
                with open(filename) as json_file:
                    jsonData = json.load(json_file)
                    success = True
            else:
                Trace.log(TraceLevel.ERROR, '   get_json: position ({}) is not within range of tokens ({})'.format(position, len(words)))

        else:
            # Treat the parameter as inline JSON data
            pos2 = command.find('}')
            if pos2 == -1:
                Trace.log(TraceLevel.ERROR, '   get_json: Unable to find a matching end bracket (}) for inline JSON data')
            else:
                try:
                    jsonText = command[pos1:pos2+1]

                except Exception as e:
                    jsonText = ''
                    Trace.log(TraceLevel.ERROR, '   -- get_json: Unable to extract JSON text: Exception: {}'.format(str(e)))
                    pass

                Trace.log(TraceLevel.TRACE, '   ++ get_json: JSON Text: ({})'.format(jsonText))
                jsonData = json.loads(jsonText)
                success = True

        return success, jsonData
