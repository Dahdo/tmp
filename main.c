#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <poll.h>

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

void debounce(int button_fd) {
    struct pollfd fds;
    fds.fd = button_fd;
    fds.events = POLLPRI;

    char buf[2];
    lseek(button_fd, 0, SEEK_SET);  // Clear any existing interrupt
    read(button_fd, buf, sizeof(buf));

    int ret = poll(&fds, 1, tbmax * 1000);  // Convert tbmax to milliseconds
    if (ret > 0 && (fds.revents & POLLPRI)) {
        // Change detected before timeout, debounce again
        debounce(button_fd);
    }
}

int main() {
    export_gpio(GPIO_PIN_LED);
    export_gpio(GPIO_PIN_BTN);
    set_direction(GPIO_PIN_LED, "out");
    set_direction(GPIO_PIN_BTN, "in");
    
    // Set edge to "both" for interrupt detection
    FILE *edge_file = fopen("/sys/class/gpio/gpio" GPIO_PIN_BTN "/edge", "w");
    if (edge_file == NULL) {
        perror("Error opening edge file");
        exit(EXIT_FAILURE);
    }
    fprintf(edge_file, "both");
    fclose(edge_file);

    int button_fd = open("/sys/class/gpio/gpio" GPIO_PIN_BTN "/value", O_RDONLY);
    if (button_fd < 0) {
        perror("Error opening button value file");
        exit(EXIT_FAILURE);
    }

    while (1) {
        debounce(button_fd); // Wait for debounce
        lseek(button_fd, 0, SEEK_SET);  // Clear interrupt
        char buf[2];
        read(button_fd, buf, sizeof(buf));
        if (buf[0] == '1') {
            // Button pressed, toggle LED
            int led_state = !read_button(GPIO_PIN_LED);
            char value[2];
            snprintf(value, sizeof(value), "%d", led_state);
            int fd_led = open("/sys/class/gpio/gpio" GPIO_PIN_LED "/value", O_WRONLY);
            if (fd_led < 0) {
                perror("Error opening LED value file");
                exit(EXIT_FAILURE);
            }
            write(fd_led, value, strlen(value));
            close(fd_led);
        }
    }

    close(button_fd);
    unexport_gpio(GPIO_PIN_LED);
    unexport_gpio(GPIO_PIN_BTN);
    return 0;
}
