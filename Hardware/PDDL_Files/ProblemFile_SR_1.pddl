( define (problem case01) 
(:domain studyRoom)

(:objects
    SR_1 - room
    ac1 - airConditioning
    h1 -heater
    l1 -light
    b1 -blinds
    m1 -motion
)

(:init
	(hum_isGood SR_1)
	(outside_isVerySunny SR_1)
	(temp_isHot SR_1)
	(airConditioning_on ac1 SR_1)
	(motion_detected SR_1)
)

(:goal (and
	(temp_isGood SR_1)
	(inside_isLight SR_1)
) )
)