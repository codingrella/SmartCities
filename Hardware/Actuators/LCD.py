# -*- coding: utf-8 -*-



from grove_rgb_lcd import *


def getNoiseLevelText(noiseLevel):
    maxThreshold = 350
    minThreshold = 190
    
    if noiseLevel < minThreshold:
        noisePercentage = 0
    elif noiseLevel > maxThreshold:
        noisePercentage = 100
    else:
        noisePercentage = ((noiseLevel - minThreshold) * 100) / (maxThreshold - minThreshold)
    
    text = "Noise Level: \n"
    
    noiseScale = int(noisePercentage / 8.3)
    
    print(noiseScale)
    
    text += ''.join([chr(255)] * noiseScale)
    text += ''.join([chr(219)] * (12-noiseScale))
    
    if noiseScale <= 3:
        text += "  <3"
    elif noiseScale <= 6:
        text += "  :)"
    elif noiseScale <= 9:
        text += "  :|"
    else:
        text += " >:("
        
    return text
    

def writeDataToLCD(text):
    setText(text)
    
