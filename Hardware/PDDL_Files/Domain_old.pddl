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
    (isVerySunny ?r -room)
    (isSunny ?r -room)
    (isDark ?r -room)
    ; MOTION SENSOR
    (motion_detected ?r -room)
    ; SEAT 'SENSOR'
    (seat_occupied  ?r -room)
    
    ; -------------------------------------- SYSTEM --------------------------------------
    ; AIRCONDITIONING
    (airConditioning_on ?ac -airConditioning ?r -room)
    ; LIGHTING
    (lighthing_on ?l -light ?r -room)
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
    :effect (airConditioning_on ?ac ?r)
)

(:action turnOffAC
    :parameters (?ac -airConditioning ?r -room)
    :precondition (and (airConditioning_on ?ac ?r)
                       (or (temp_isGood ?r)
                       (hum_isGood ?r)))
    :effect (not (airConditioning_on ?ac ?r))
)

(:action turnOnHeater
    :parameters (?h -heater ?r -room)
    :precondition (and (not(heater_on ?h ?r))
                       (temp_isHot ?r))
    :effect (heater_on ?h ?r)
)

(:action turnOffHeater
    :parameters (?h -heater ?r -room)
    :precondition (and (heater_on ?h ?r)
                       (temp_isGood ?r))
    :effect (not (heater_on ?h ?r))
)

(:action turnOnLight
    :parameters (?l -light ?b -blinds ?r -room)
    :precondition (and (or(isDark ?r)
                       (blinds_down ?b ?r))
                       (motion_detected ?r)
                       (not(lighthing_on ?l ?r)))
    :effect (lighthing_on ?l ?r)
)

(:action turnOffLight
    :parameters (?l -light ?b -blinds ?r -room)
    :precondition (and (or(isSunny ?r)
                       (not(blinds_down ?b ?r)))
                       (not(motion_detected ?r))
                       (lighthing_on ?l ?r))
    :effect (not(lighthing_on ?l ?r))
)

; also close blinds if light is turned on?
(:action closeBlinds
    :parameters (?b -blinds ?r - room)
    :precondition (and  (isVerySunny ?r)
                        (not(blinds_down ?b ?r)))
    :effect (blinds_down ?b ?r)
)

(:action openBlinds
    :parameters (?b -blinds ?r - room)
    :precondition (and  (isSunny ?r)
                        (blinds_down ?b ?r))
    :effect (not(blinds_down ?b ?r))
)

)