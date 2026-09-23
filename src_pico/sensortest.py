import time
from machine import Pin

IR_Warningsensor = Pin(2, Pin.IN, Pin.PULL_UP)
IR_Dangersensor = Pin(3, Pin.IN, Pin.PULL_UP)

previous_warning = IR_Warningsensor.value()
previous_danger = IR_Dangersensor.value()

start_time = time.ticks_ms()

print("Sensor test started")
print("Initial warning value:", previous_warning)
print("Initial danger value:", previous_danger)

while True:
    current_warning = IR_Warningsensor.value()
    current_danger = IR_Dangersensor.value()

    if current_warning != previous_warning:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000

        print("Time:", elapsed, "seconds | GPIO 2:", current_warning)

        previous_warning = current_warning

    if current_danger != previous_danger:
        elapsed = time.ticks_diff(time.ticks_ms(), start_time) / 1000

        print("Time:", elapsed, "seconds | GPIO 3:", current_danger)

        previous_danger = current_danger

    time.sleep_ms(10)
