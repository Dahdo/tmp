import os
import time

GPIO_PIN_LED = "XX"  # Replace XX with the GPIO pin number for the LED
GPIO_PIN_BTN = "YY"  # Replace YY with the GPIO pin number for the button

tbmax = 0.01  # Maximum expected duration of bouncing in seconds

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

def debounce(button_fd):
    try:
        os.lseek(button_fd, 0, os.SEEK_SET)  # Clear any existing interrupt
        os.read(button_fd, 2)  # Read to clear the interrupt
        poll_obj = select.poll()
        poll_obj.register(button_fd, select.POLLPRI)
        events = poll_obj.poll(int(tbmax * 1000))  # Convert tbmax to milliseconds
        if events:
            debounce(button_fd)  # Change detected before timeout, debounce again
    except Exception as e:
        print("Error during debounce:", e)

def main():
    export_gpio(GPIO_PIN_LED)
    export_gpio(GPIO_PIN_BTN)
    set_direction(GPIO_PIN_LED, "out")
    set_direction(GPIO_PIN_BTN, "in")
    
    # Set edge to "both" for interrupt detection
    with open(f"/sys/class/gpio/gpio{GPIO_PIN_BTN}/edge", "w") as edge_file:
        edge_file.write("both")

    button_fd = os.open(f"/sys/class/gpio/gpio{GPIO_PIN_BTN}/value", os.O_RDONLY)

    try:
        while True:
            debounce(button_fd)  # Wait for debounce
            os.lseek(button_fd, 0, os.SEEK_SET)  # Clear interrupt
            buf = os.read(button_fd, 2)
            if buf[0] == b'1':
                # Button pressed, toggle LED
                led_state = not read_button(GPIO_PIN_LED)
                with open(f"/sys/class/gpio/gpio{GPIO_PIN_LED}/value", "w") as value_file:
                    value_file.write("1" if led_state else "0")
    except KeyboardInterrupt:
        pass
    finally:
        os.close(button_fd)
        unexport_gpio(GPIO_PIN_LED)
        unexport_gpio(GPIO_PIN_BTN)

if __name__ == "__main__":
    main()
