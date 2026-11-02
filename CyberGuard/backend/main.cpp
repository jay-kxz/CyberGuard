#include <iostream>
#include <string>

#include "server.h"

int main(int argc, char** argv) {
    std::string frontendDir = "frontend";    // relative to where you start the program
    int port = 8080;
    if (argc > 1) frontendDir = argv[1];
    if (argc > 2) {
        try { port = std::stoi(argv[2]); } catch (...) { port = 0; }
        if (port < 1024 || port > 65535) {
            std::cerr << "Port must be a number from 1024 to 65535.\n";
            return 1;
        }
    }
    return runServer(frontendDir, port);
}
