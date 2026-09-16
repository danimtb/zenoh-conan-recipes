#include <stdlib.h>
#include "zenoh.h"

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;
    z_owned_config_t config;
    z_config_default(&config);
    z_drop(z_move(config));
    return EXIT_SUCCESS;
}
