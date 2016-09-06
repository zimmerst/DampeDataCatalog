'''
Created on Sep 6, 2016

@author: zimmer
'''
from random import choice, randint
from string import ascii_letters, digits

def random_string_generator(size=16, chars=ascii_letters + digits):
    return ''.join(choice(chars) for _ in range(size))
