# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 12:55:21 2025

@author: Vivienne Beck
"""

import grovepi


def getData(port):
    return grovepi.analogRead(port)