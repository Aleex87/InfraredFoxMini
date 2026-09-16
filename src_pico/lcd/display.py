from machine import Pin
from .gpio_lcd import GpioLcd

button = Pin(6, Pin.IN, Pin.PULL_UP)

lcd = GpioLcd(
    rs_pin=Pin(22),
    enable_pin=Pin(21),
    d4_pin=Pin(20),
    d5_pin=Pin(19),
    d6_pin=Pin(18),
    d7_pin=Pin(17),
    num_lines=2,
    num_columns=16,
)


def update_display():
    lcd.clear()

    if button.value() == 0:
        lcd.putstr("TRAIN")
        lcd.move_to(0, 1)
        lcd.putstr("APPROACHING")
    else:
        lcd.putstr("NO TRAIN")
