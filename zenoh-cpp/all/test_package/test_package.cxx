#include <cstdlib>
#include "zenoh.hxx"
using namespace zenoh;

int main(int argc, char **argv) {
    (void)argc;
    (void)argv;

#ifdef ZENOHCXX_ZENOHC
    init_log_from_env_or("error");
#endif
    Config config = Config::create_default();
    (void)config;
    return EXIT_SUCCESS;
}
