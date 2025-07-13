# -*- coding: utf-8 -*-
"""
Created on Sat Jul 12 21:58:09 2025

@author: Vivienne Beck
"""

import os
import shutil
import psycopg2



class AIPlannerInterface():
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="SmartCities25",
            user="postgres",
            password="Tn#2SKSS25",
            port = 5432 )
        
        self.cur = self.conn.cursor()
    
    def _AIPlanner_getHumidityInits(self, room):
        self.cur.execute(f"""SELECT 
                             case 
                                when isgood=true then '(hum_isGood {room})'
                                when ismedium=true then '(hum_isMid {room})'
                                when isbad=true then '(hum_isBad {room})'
                             end as col
                            from public.humidity
                            where roomid='{room}';""")
        return [element[0] for element in self.cur.fetchall()]
    
    def _AIPlanner_getLightInits(self, room):
        results = []
        self.cur.execute(f"""SELECT
                             case 
                                when outside_isverysunny=true then '(outside_isVerySunny {room})'
                             end as col
                            from public.lighting
                            where roomid='{room}';""")            
        results.extend(self.cur.fetchall())
        self.cur.execute(f"""SELECT
                             case
                                when outside_isdark=true then '(outside_isDark {room})'
                             end as col
                            from public.lighting
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        self.cur.execute(f"""SELECT
                             case 
                                when inside_issunny=true then '(inside_isLight {room})'
                             end as col
                            from public.lighting
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        return [element[0] for element in results if element[0] is not None ]
    
    def _AIPlanner_getTemperatureInits(self, room):
        self.cur.execute(f"""SELECT
                             case 
                                when iscold=true then '(temp_isCold {room})'
                                when isgood=true then '(temp_isGood {room})'
                                when ishot=true then '(temp_isHot {room})'
                             end as col
                            from public.temperature
                            where roomid='{room}';""")
        return [element[0] for element in self.cur.fetchall()]
    
    def _AIPlanner_getActuatorInits(self, room):
        results = []
        
        if 'SR_1': roomNr = '1'
        elif 'SR_2': roomNr = '2'
        
        self.cur.execute(f"""SELECT
                             case 
                                when airconditioning_on=true then '(airConditioning_on ac{roomNr} {room})'
                             end as col
                            from public.actuators
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        self.cur.execute(f"""SELECT
                              case 
                                when lighthing_on=true then '(lighting_on l{roomNr} {room})'
                              end as col
                            from public.actuators
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        self.cur.execute(f"""SELECT
                              case 
                                when blinds_down=true then '(blinds_down b{roomNr} {room})'
                              end as col
                            from public.actuators
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        self.cur.execute(f"""SELECT
                             case 
                                when heater_on=true then '(heater_on h{roomNr} {room})'
                             end as col
                            from public.actuators
                            where roomid='{room}';""")
        results.extend(self.cur.fetchall())
        
        return [element[0] for element in results if element[0] is not None ]
    
    def _AIPlanner_getMotionInits(self, room):
        self.cur.execute("""SELECT
                             case 
                                when motiondetected=true then '(motion_detected {room})'
                             end as col
                            from public.motion
                            where roomid='{room}';""")
        return [element[0] for element in self.cur.fetchall()]
        
        
    def getAIPlannerInits(self, room):
        result = []
        result.extend(self._AIPlanner_getHumidityInits(room))
        result.extend(self._AIPlanner_getLightInits(room))
        result.extend(self._AIPlanner_getTemperatureInits(room))
        result.extend(self._AIPlanner_getActuatorInits(room))
        result.extend(self._AIPlanner_getMotionInits(room))
        
        return result
    
    def getAIPlannerGoals(self, inits, room):
        goals = []
        if 'SR_1': roomNr = '1'
        elif 'SR_2': roomNr = '2'
        
        if f'(hum_isGood {room})' in inits and f'(temp_isGood {room})' in inits: goals.append(f'(saveEnergy_acs {room})')
        elif f'(hum_isGood {room})' not in inits: goals.append(f'(hum_isGood {room})')
        elif f'(temp_isGood {room})' not in inits: goals.append(f'(temp_isGood {room})')
        elif f'(temp_isGood {room})' in inits: goals.append(f'(saveEnergy_heater {room})')
        
        if f'(motion_detected {room})' in inits: goals.append(f'(inside_isLight {room})')
        elif f'(motion_detected {room})' not in inits: goals.append(f'(saveEnergy_lights {room})')
        
        return goals
    
    def createAIProblemFile(self, inits, goals, room):
        dirname = os.path.dirname(__file__)
        
        src = dirname + f'\PDDL_Files\ProblemFile_{room}_Temp.pddl'
        dst = dirname + f'\PDDL_Files\ProblemFile_{room}.pddl'
        
        path = shutil.copy2(src,dst)
        
        text_init = "(:init\n"
        for init in inits:
            text_init += ('\t' + init + '\n')
        text_init += ')\n\n'
        
        text_goal = "(:goal (and\n"
        for goal in goals:
            text_goal += ('\t' + goal + '\n')
        text_goal += ') )\n)'
        
        with open(path, "a") as myfile:
            myfile.write(text_init)
            myfile.write(text_goal)
        
        
        
if __name__ == "__main__":
    AIPlanner = AIPlannerInterface()
    
    inits = AIPlanner.getAIPlannerInits('SR_1')    
    goals = AIPlanner.getAIPlannerGoals(inits, 'SR_1')
    
    AIPlanner.createAIProblemFile(inits, goals, 'SR_1')
    
    
    
    