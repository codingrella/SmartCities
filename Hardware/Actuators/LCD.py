# -*- coding: utf-8 -*-
"""
Created on Sun Jul  6 14:51:11 2025

@author: Vivienne Beck
"""

import grovepi
from grove_rgb_lcd import *


def getNoiseLevelText(noiseLevel):
    text = "Noise Level: \n"
    
    noiseScale = int(noiseLevel / 8.4)
    
    text += ''.join([chr(219)] * noiseScale)
    text += ''.join([chr(255)] * (12-noiseScale))
    
    if noiseScale <= 3:
        text += "  <3"
    elif noiseScale <= 6:
        text += "  :)"
    elif noiseScale <= 9:
        text += "  :|"
    else:
        text += " >:("
        
    return text
    

def writeData(text):
    setText(text)
    