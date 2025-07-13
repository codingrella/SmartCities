( define (domain studyRoom)

(:types room system -object
        airConditioning light blinds heater -system 
        )

( :predicates 
    ; -------------------------------------- SENSORS --------------------------------------
    ; TEMPERATURE SENSOR
    (temp_isCold ?r -room)
    (temp_isGood ?r -room)
    (temp_isHot ?r -room)
    ; HUMIDITY SENSOR 
    (hum_isGood ?r -room)
    (hum_isMid ?r -room)
    (hum_isBad ?r -room)
    ; LIGHT SENSOR
    (outside_isVerySunny ?r -room)
    (outside_isDark ?r -room)
    (inside_isLight ?r -room)
    ; MOTION SENSOR
    (motion_detected ?r -room)
    ; SEAT 'SENSOR'
    (seat_occupied  ?r -room)
    
    ; SaveEnergy Goals, 
    ; combines actuator states (for multiple actuators of same kind)
    (saveEnergy_acs ?r -room)
    (saveEnergy_lights ?r -room)
    (saveEnergy_heater ?r -room)
    
    
    ; -------------------------------------- SYSTEM --------------------------------------
    ; AIRCONDITIONING
    (airConditioning_on ?ac -airConditioning ?r -room)
    ; LIGHTING
    (lighting_on ?l -light ?r -room)
    ; BLINDS 
    (blinds_down ?b -blinds ?r -room)
    ; heater
    (heater_on ?h -heater ?r -room)
    
)

(:action turnOnAC
    :parameters (?ac -airConditioning ?r -room)
    :precondition (and (not (airConditioning_on ?ac ?r))
                       (or (temp_isHot ?r)
                       (hum_isBad ?r)))
    :effect (and (temp_isGood ?r)
                 (hum_isGood ?r)
                 (airConditioning_on ?ac ?r))
)

(:action turnOffAC
    :parameters (?ac -airConditioning ?r -room)
    :precondition (and (airConditioning_on ?ac ?r))
    :effect (and (saveEnergy_acs ?r)
                 (not (airConditioning_on ?ac ?r)))
)

(:action turnOnHeater
    :parameters (?h -heater ?r -room)
    :precondition (and (not(heater_on ?h ?r))
                       (temp_isCold ?r))
    :effect (and (temp_isGood ?r)
                 (heater_on ?h ?r))
)

(:action turnOffHeater
    :parameters (?h -heater ?r -room)
    :precondition (and (heater_on ?h ?r))
    :effect (and (saveEnergy_heater ?r)
                 (not (heater_on ?h ?r)))
)

(:action turnOnLight
    :parameters (?l -light ?r -room)
    :precondition (and (not (inside_isLight ?r))
                       (motion_detected ?r)
                       (not(lighting_on ?l ?r)))
    :effect (and (inside_isLight ?r)
                 (lighting_on ?l ?r))
)

(:action turnOffLight
    :parameters (?l -light ?r -room)
    :precondition (and (not (outside_isVerySunny ?r))
                       (not(motion_detected ?r))
                       (lighting_on ?l ?r))
    :effect (and (saveEnergy_lights ?r)
                 (not(lighting_on ?l ?r)))
)

; also close blinds if light is turned on?
(:action closeBlinds
    :parameters (?b -blinds ?r -room)
    :precondition (and  (or (outside_isVerySunny ?r)
                        (outside_isDark ?r))
                        (not(blinds_down ?b ?r)))
    :effect (and (not (inside_isLight ?r))
                 (blinds_down ?b ?r))
)

(:action openBlinds
    :parameters (?b -blinds ?r -room)
    :precondition (and  (not (outside_isVerySunny ?r))
                        (not (outside_isDark ?r))
                        (blinds_down ?b ?r))
    :effect (and (inside_isLight ?r)
                 (not(blinds_down ?b ?r)))
)

)
