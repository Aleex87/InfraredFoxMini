import time
time.sleep(0.1) 

from machine import Pin, PWM

# Sensors
# The system is designed for two IR break beam sensors 
# GPIO 2 = Warning sensor 
# GPIO 3 = Danger sensor 
# For the classroom demo push buttons were connected to the same GPIO pins to simulate the sensor events and make the demo more reliable 
IR_Warningsensor = Pin(2, Pin.IN, Pin.PULL_UP)
IR_Dangersensor = Pin(3, Pin.IN, Pin.PULL_UP)

# Real IR break-beam sensors used in the intended hardware setup:
# IR_Warningsensor = Pin(2, Pin.IN, Pin.PULL_UP)
# IR_Dangersensor = Pin(3, Pin.IN, Pin.PULL_UP)

# Buttons used in the final demo as a sensor simulation / fallback.
# The system is designed for two IR break-beam sensors.
# For the final classroom demo, push buttons were connected to the same GPIO pins
# to simulate the sensor events and make the demo more reliable.

# LED
green_led = Pin(9, Pin.OUT)
warning_led = Pin(10, Pin.OUT)
red_led = Pin(11, Pin.OUT)

zone = "SAFE" # Default mode 
object_in_zone = False

# Buzzer *LLM USAGE*.In the following part i took assistance from LLM.
buzzer = PWM(Pin(5))
buzzer.freq(1000)
buzzer.duty_u16(0)


# Timing duration of zones 
starttime_dangerzone = None 
danger_duration = 0

starttime_warningzone = None 
zone_duration = 0

# State of sensors 

previouswarning_state = 1  # 1 = beam is clear 0 = beam is broken !
previousDanger_state = 1  


# Direction of person/object : TOWARDS DANGER or TOWARDS SAFEZONE
direction = None 


while True: 

    # Reading sensor states 

    current_danger = IR_Dangersensor.value()
    current_warning = IR_Warningsensor.value()
    # Create crossing events 
    # Only when beam changes from 1 clear to 0 broken 
    warningzone_crossed = previouswarning_state == 1 and current_warning == 0
    dangerzone_crossed = previousDanger_state == 1 and current_danger == 0


# SAFE TO WARNING 
    if warningzone_crossed and zone == "SAFE":
        direction = "TOWARDS_DANGER"
        zone = "WARNING"


# WARNING TO DANGER 
    elif dangerzone_crossed and zone == "WARNING":
        direction = "TOWARDS_DANGER"
        zone = "DANGER"

 
  
    # RETURNING LOGIC . Return to SAFE zone
    # DANGER -> WARNING
    elif dangerzone_crossed and zone == "DANGER":
        direction = "TOWARDS_SAFE"
        zone = "WARNING"

# WARNING->SAFE
    elif  warningzone_crossed and zone == "WARNING" and direction == "TOWARDS_SAFE":
         zone = "SAFE"
         direction = None 
         
    
# Check if beam is broken

    if previouswarning_state == 1 and current_warning == 0:
        print("Warning sensor crossed !")

    if previousDanger_state == 1 and current_danger == 0:
        print("Danger sensor crossed!")

 # zone controls LED buzzer timer 
    if zone == "DANGER":  # Danger must have highest priority
        object_in_zone = True 
        buzzer.duty_u16(5000) # buzzer activates 
        
        
    # Timer starts
        if starttime_dangerzone is None:
            starttime_dangerzone = time.ticks_ms()
            print("IMMEDIATE DANGER") 

        green_led.value(0)
        red_led.value(1)
        warning_led.value(0)


    elif zone == "WARNING": # 2nd priority but still high risk area
        object_in_zone = True
        buzzer.duty_u16(3000) # Lower sound
       
        if starttime_warningzone is None:
            starttime_warningzone = time.ticks_ms() 
            print("High risk ")

        green_led.value(0)
        warning_led.value(1) # Only this led will be on
        red_led.value(0)

    else:
        
        object_in_zone = False
        zone = "SAFE"
        buzzer.duty_u16(0)

        green_led.value(1)
        warning_led.value(0)
        red_led.value(0)


    if starttime_dangerzone is not None and zone != "DANGER":
        danger_duration = time.ticks_diff(
            time.ticks_ms(),
            starttime_dangerzone
        )

        danger_duration = danger_duration / 1000

        print(
            "Amount of time in danger zone",
            danger_duration, "seconds")
    
        starttime_dangerzone = None


    if starttime_warningzone is not None and zone != "WARNING":
        zone_duration = time.ticks_diff(
            time.ticks_ms(),
            starttime_warningzone 
        )

        zone_duration = zone_duration / 1000

        print("Amount of time in warning zone",
               zone_duration, "seconds")

        starttime_warningzone = None 


    # Saving sensor values for next loop
    previouswarning_state = current_warning
    previousDanger_state = current_danger

    time.sleep(0.1)
