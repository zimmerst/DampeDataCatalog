'''
Created on Sep 6, 2016

@author: zimmer
'''
from random import choice, randint
from string import ascii_letters, digits

def random_string_generator(size=16, chars=ascii_letters + digits):
    return ''.join(choice(chars) for _ in range(size))

def convertBytesToHuman(num):
    """ 
        returns a human readable format, assumes input to be in bytes 
        shamelessly stolen from: http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
    
    """
    from math import log
    unit_list = zip(['bytes', 'kB', 'MB', 'GB', 'TB', 'PB'], [0, 0, 1, 2, 2, 2])
    if num > 1:
        exponent = min(int(log(num, 1024)), len(unit_list) - 1)
        quotient = float(num) / 1024**exponent
        unit, num_decimals = unit_list[exponent]
        format_string = '{:.%sf} {}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    else:
        return '1 byte'