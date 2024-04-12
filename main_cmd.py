import subprocess
import time

GPIO_PIN_LED = "XX"  # Replace XX with the GPIO pin number for the LED
GPIO_PIN_BTN = "YY"  # Replace YY with the GPIO pin number for the button
TB_MAX = 0.01         # Maximum expected duration of bouncing in seconds

def export_gpio(gpio_pin):
    subprocess.run(["echo", gpio_pin, ">", "/sys/class/gpio/export"], shell=True)

def unexport_gpio(gpio_pin):
    subprocess.run(["echo", gpio_pin, ">", "/sys/class/gpio/unexport"], shell=True)

def set_direction(gpio_pin, direction):
    subprocess.run(["echo", direction, ">", f"/sys/class/gpio/gpio{gpio_pin}/direction"], shell=True)

def read_button(gpio_pin):
    value = subprocess.run(["cat", f"/sys/class/gpio/gpio{gpio_pin}/value"], capture_output=True, text=True, shell=True)
    return value.stdout.strip()

def debounce(gpio_pin):
    subprocess.run(["cat", f"/sys/class/gpio/gpio{gpio_pin}/value", ">", "/dev/null"], shell=True)  # Clear any existing interrupt
    time.sleep(TB_MAX)

def main():
    export_gpio(GPIO_PIN_LED)
    export_gpio(GPIO_PIN_BTN)
    set_direction(GPIO_PIN_LED, "out")
    set_direction(GPIO_PIN_BTN, "in")

    # Set edge to "both" for interrupt detection
    subprocess.run(["echo", "both", ">", f"/sys/class/gpio/gpio{GPIO_PIN_BTN}/edge"], shell=True)

    while True:
        debounce(GPIO_PIN_BTN)  # Wait for debounce
        button_state = read_button(GPIO_PIN_BTN)
        if button_state == "1":
            # Button pressed, toggle LED
            led_state = read_button(GPIO_PIN_LED)
            subprocess.run(["echo", "0" if led_state == "1" else "1", ">", f"/sys/class/gpio/gpio{GPIO_PIN_LED}/value"], shell=True)

    unexport_gpio(GPIO_PIN_LED)
    unexport_gpio(GPIO_PIN_BTN)

if __name__ == "__main__":
    main()
