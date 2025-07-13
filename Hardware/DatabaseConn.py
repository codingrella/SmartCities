# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 00:59:29 2025

@author: Vivienne Beck
"""

import psycopg2




class NumericDatabaseInterface:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="SmartCities25_realTimeData",
            user="postgres",
            password="Tn#2SKSS25",
            port = 5432 )
        
        self.cur = self.conn.cursor()
        
        
    def updateMotion(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET motion={value==1}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()   
        
        
    def updateLightLevel(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET lightlevel={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()   
        
    def updateNoiseLevel(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET noiselevel={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()  
        
    def updateTemperature(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET temperature={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit() 
        
        
    def updateHumidity(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET humidity={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit() 
        
    
    def closeConnection(self):
        self.cur.close()
        self.conn.close()
        
        
    
    
class AbstractedDatabaseInterface:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="SmartCities25",
            user="postgres",
            password="Tn#2SKSS25",
            port = 5432 )
        
        self.cur = self.conn.cursor()
        
        self.upperThresholds = {
            'hum_good': 40,
            'hum_mid': 50,
            'issunny': 1000,
            'iscloudy': 700,
            'iscold': 20,
            'isgood': 24
            }
    
    def updateMotion(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET motion={value==1}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()   
        
        
    def updateLightLevel(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET lightlevel={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()   
        
    def updateNoiseLevel(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET noiselevel={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit()  
        
    def updateTemperature(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET temperature={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit() 
        
        
    def updateHumidity(self, value):
        self.cur.execute(f""" UPDATE public.roomdata
                        SET humidity={value}
                        WHERE RoomID='StudyRoom';
                    """) 
        self.conn.commit() 
        
    
    def closeConnection(self):
        self.cur.close()
        self.conn.close()
    
    
