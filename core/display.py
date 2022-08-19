#
# Do NOT modify or remove this copyright and license
#
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates, All Rights Reserved
#
# This software is subject to the terms of the MIT License. If a copy of the license was
# not distributed with this file, you can obtain one at https://opensource.org/licenses/MIT.
#
# ******************************************************************************************
#
# display.py - Common display helper routines
#
# ******************************************************************************************
#

from string import Formatter

# max_width: Given a format string, determine the total width of the string
#
# Example: width=max_width('{username: >16}  {roles: >36}  {enabled: >7}  {locked: >7}  {types: >16}  {description: >20}')
#          width=112
#
def max_width(format_string):
    width = 0
    for t in Formatter().parse(format_string):
        # First argument is the spacing between format characters {}
        if t[0] is not None:
            width += len(t[0])
        # Second argument is the variable tag, such as username, roles, etc., which is ignored
        # Third argument is a width parameter, such as >16, >36 etc.
        if t[2] is not None and t[2] != '':
            width += int(t[2].strip(' <>'))

    return width
