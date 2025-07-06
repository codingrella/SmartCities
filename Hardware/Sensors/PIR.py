# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 14:47:23 2025

@author: Vivienne Beck
"""

import grovepi


def getData(port):
    return grovepi.analogRead(port)