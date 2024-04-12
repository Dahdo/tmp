#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>

#define GPIO_PIN_LED "XX"  // Replace XX with the GPIO pin number for the LED
#define GPIO_PIN_BTN "YY"  // Replace YY with the GPIO pin number for the button

void export_gpio(const char *gpio_pin) {
    int fd_export = open("/sys/class/gpio/export", O_WRONLY);
    if (fd_export < 0) {
        perror("Error exporting GPIO");
        exit(EXIT_FAILURE);
    }
    write(fd_export, gpio_pin, strlen(gpio_pin));
    close(fd_export);
}

void unexport_gpio(const char *gpio_pin) {
    int fd_unexport = open("/sys/class/gpio/unexport", O_WRONLY);
    if (fd_unexport < 0) {
        perror("Error unexporting GPIO");
        exit(EXIT_FAILURE);
    }
    write(fd_unexport, gpio_pin, strlen(gpio_pin));
    close(fd_unexport);
}

void set_direction(const char *gpio_pin, const char *direction) {
    char path[50];
    sprintf(path, "/sys/class/gpio/gpio%s/direction", gpio_pin);
    int fd_direction = open(path, O_WRONLY);
    if (fd_direction < 0) {
        perror("Error setting GPIO direction");
        exit(EXIT_FAILURE);
    }
    write(fd_direction, direction, strlen(direction));
    close(fd_direction);
}

int read_button(const char *gpio_pin) {
    char path[50];
    sprintf(path, "/sys/class/gpio/gpio%s/value", gpio_pin);
    int fd_value = open(path, O_RDONLY);
    if (fd_value < 0) {
        perror("Error reading GPIO value");
        exit(EXIT_FAILURE);
    }
    char value;
    read(fd_value, &value, 1);
    close(fd_value);
    return (value == '1');
}

int main() {
    export_gpio(GPIO_PIN_LED);
    export_gpio(GPIO_PIN_BTN);
    set_direction(GPIO_PIN_LED, "out");
    set_direction(GPIO_PIN_BTN, "in");

    int led_state = 0;

    while (1) {
        if (read_button(GPIO_PIN_BTN)) {
            led_state = !led_state;
            set_value(GPIO_PIN_LED, led_state ? "1" : "0");
            usleep(500000);  // Debounce delay
        }
    }

    unexport_gpio(GPIO_PIN_LED);
    unexport_gpio(GPIO_PIN_BTN);
    return 0;
}
