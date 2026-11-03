#ifndef SERVER_H
#define SERVER_H
#include <string>

// Starts the CyberGuard web server on 127.0.0.1:<port> and serves the frontend folder.
// Blocks until the server stops. Returns 0 on a normal exit, 1 on a start-up error.
int runServer(const std::string& frontendDir, int port);
#endif
