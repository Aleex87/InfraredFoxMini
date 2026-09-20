import time
from machine import Pin

IR_Warningsensor = Pin(2, Pin.IN, Pin.PULL_UP)

previous_value = IR_Warningsensor.value()
start_time = time.ticks_ms()

print("Sensor test started")
print("Initial value:", previous_value)

while True:
    current_value = IR_Warningsensor.value()

    if current_value != previous_value:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000

        print("Time:", elapsed, "seconds | GPIO 2:", current_value)

        previous_value = current_value

    time.sleep_ms(10)
