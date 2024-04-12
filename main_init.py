import os
import time

GPIO_PIN_LED = "XX"  # Replace XX with the GPIO pin number for the LED
GPIO_PIN_BTN = "YY"  # Replace YY with the GPIO pin number for the button

def export_gpio(gpio_pin):
    with open("/sys/class/gpio/export", "w") as export_file:
        export_file.write(gpio_pin)

def unexport_gpio(gpio_pin):
    with open("/sys/class/gpio/unexport", "w") as unexport_file:
        unexport_file.write(gpio_pin)

def set_direction(gpio_pin, direction):
    with open(f"/sys/class/gpio/gpio{gpio_pin}/direction", "w") as direction_file:
        direction_file.write(direction)

def read_button(gpio_pin):
    with open(f"/sys/class/gpio/gpio{gpio_pin}/value", "r") as value_file:
        return value_file.read().strip() == "1"

def main():
    export_gpio(GPIO_PIN_LED)
    export_gpio(GPIO_PIN_BTN)
    set_direction(GPIO_PIN_LED, "out")
    set_direction(GPIO_PIN_BTN, "in")

    led_state = 0

    try:
        while True:
            if read_button(GPIO_PIN_BTN):
                led_state = not led_state
                with open(f"/sys/class/gpio/gpio{GPIO_PIN_LED}/value", "w") as value_file:
                    value_file.write("1" if led_state else "0")
                time.sleep(0.5)  # Debounce delay
    except KeyboardInterrupt:
        pass
    finally:
        unexport_gpio(GPIO_PIN_LED)
        unexport_gpio(GPIO_PIN_BTN)

if __name__ == "__main__":
    main()
