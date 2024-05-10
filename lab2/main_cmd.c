#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define GPIO_PIN_LED "XX"  // Replace XX with the GPIO pin number for the LED
#define GPIO_PIN_BTN "YY"  // Replace YY with the GPIO pin number for the button
#define TB_MAX 0.01         // Maximum expected duration of bouncing in seconds

void export_gpio(const char *gpio_pin) {
    char command[50];
    sprintf(command, "echo %s > /sys/class/gpio/export", gpio_pin);
    system(command);
}

void unexport_gpio(const char *gpio_pin) {
    char command[50];
    sprintf(command, "echo %s > /sys/class/gpio/unexport", gpio_pin);
    system(command);
}

void set_direction(const char *gpio_pin, const char *direction) {
    char command[50];
    sprintf(command, "echo %s > /sys/class/gpio/gpio%s/direction", direction, gpio_pin);
    system(command);
}

char read_button(const char *gpio_pin) {
    char value;
    char command[50];
    sprintf(command, "cat /sys/class/gpio/gpio%s/value", gpio_pin);
    FILE *fp = popen(command, "r");
    if (fp == NULL) {
        perror("Error reading GPIO value");
        exit(EXIT_FAILURE);
    }
    fread(&value, sizeof(value), 1, fp);
    pclose(fp);
    return value;
}

void debounce(const char *gpio_pin) {
    char command[50];
    sprintf(command, "cat /sys/class/gpio/gpio%s/value > /dev/null", gpio_pin);
    system(command);  // Clear any existing interrupt
    sleep(TB_MAX);
}

int main() {
    export_gpio(GPIO_PIN_LED);
    export_gpio(GPIO_PIN_BTN);
    set_direction(GPIO_PIN_LED, "out");
    set_direction(GPIO_PIN_BTN, "in");

    // Set edge to "both" for interrupt detection
    char command[50];
    sprintf(command, "echo both > /sys/class/gpio/gpio%s/edge", GPIO_PIN_BTN);
    system(command);

    while (1) {
        debounce(GPIO_PIN_BTN); // Wait for debounce
        char buf = read_button(GPIO_PIN_BTN);
        if (buf == '1') {
            // Button pressed, toggle LED
            char value = read_button(GPIO_PIN_LED);
            sprintf(command, "echo %c > /sys/class/gpio/gpio%s/value", (value == '1') ? '0' : '1', GPIO_PIN_LED);
            system(command);
        }
    }

    unexport_gpio(GPIO_PIN_LED);
    unexport_gpio(GPIO_PIN_BTN);
    return 0;
}
