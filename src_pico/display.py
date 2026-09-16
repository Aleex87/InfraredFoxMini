from machine import Pin
from gpio_lcd import GpioLcd

BUTTON_PIN = 13

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

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


def show_ready():
    lcd.clear()
    lcd.putstr("SYSTEM READY")


def show_train_warning():
    lcd.clear()
    lcd.putstr("ATTENTION!")
    lcd.move_to(0, 1)
    lcd.putstr("TRAIN ARRIVING")


def button_pressed():
    return button.value() == 0
