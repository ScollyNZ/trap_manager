#pragma once

#include <Arduino.h>
#include <WebServer.h>

// HttpOta class declaration
class HttpOta {
  public:
    HttpOta(const char* user, const char* pass);
    void begin();
    void handleClient();
  private:
    const char* UPDATE_USER;
    const char* UPDATE_PASS;
    WebServer server;
    void handleRoot();
    bool checkAuth();
    void handleUpdatePage();
    void handleUpdateUpload();
    void handleUpdateDone();
};


