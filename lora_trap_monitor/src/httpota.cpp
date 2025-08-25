#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Update.h>
#include "httpota.h"

// Constructor
HttpOta::HttpOta(const char* user, const char* pass)
    : UPDATE_USER(user), UPDATE_PASS(pass), server(80) {}

// Public methods
void HttpOta::begin() {
    // Routes
    server.on("/", HTTP_GET, [this]() { handleRoot(); });
    server.on("/update", HTTP_GET, [this]() { handleUpdatePage(); });
    server.on(
        "/update", HTTP_POST,
        [this]() { handleUpdateDone(); },       // called when upload finished
        [this]() { handleUpdateUpload(); }      // receives data chunks
    );
    server.onNotFound([this] { server.send(404, "text/plain", "Not Found"); });

    server.begin();
    Serial.println("HTTP OTA server started on port 80");
}

void HttpOta::handleClient() {
    server.handleClient();
}

// Private methods
void HttpOta::handleRoot() {
    String html =
        "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>ESP32 Web Updater</title></head><body>"
        "<h1>ESP32-S3 Web Updater</h1>"
        "<p>IP: " + WiFi.localIP().toString() + "</p>"
        "<p><a href='/update'>Go to /update</a></p>"
        "</body></html>";
    server.send(200, "text/html", html);
}

bool HttpOta::checkAuth() {
    if (!server.authenticate(UPDATE_USER, UPDATE_PASS)) {
        server.requestAuthentication();
        return false;
    }
    return true;
}

void HttpOta::handleUpdatePage() {
    if (!checkAuth()) return;
    const char* form =
        "<!doctype html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>Upload firmware</title></head><body>"
        "<h2>Upload new firmware (.bin)</h2>"
        "<form method='POST' action='/update' enctype='multipart/form-data'>"
        "<input type='file' name='firmware' accept='.bin'>"
        "<input type='submit' value='Update'>"
        "</form>"
        "</body></html>";
    server.send(200, "text/html", form);
}

void HttpOta::handleUpdateUpload() {
    if (!checkAuth()) return;

    Serial.println("[OTA] Uploading firmware...");

    HTTPUpload& upload = server.upload();
    static size_t written = 0;

    Serial.printf("[OTA] Upload: %s, size=%u\n", upload.filename.c_str(), upload.totalSize);
    if (upload.status == UPLOAD_FILE_START) {
        written = 0;
        if (!Update.begin()) { // max available space
            Update.printError(Serial);
        }
        Serial.printf("[OTA] Start: %s, size=%u\n", upload.filename.c_str(), upload.totalSize);
    } else if (upload.status == UPLOAD_FILE_WRITE) {
        size_t w = Update.write(upload.buf, upload.currentSize);
        written += w;
        if (w != upload.currentSize) {
            Serial.println("[OTA] Write mismatch");
        }
    } else if (upload.status == UPLOAD_FILE_END) {
        if (Update.end(true)) {
            Serial.printf("[OTA] Success: %u bytes written, rebooting...\n", written);
        } else {
            Update.printError(Serial);
        }
    } else if (upload.status == UPLOAD_FILE_ABORTED) {
        Update.end();
        Serial.println("[OTA] Aborted");
    }
    yield();
}

void HttpOta::handleUpdateDone() {
    if (!checkAuth()) return;
    if (Update.hasError()) {
        server.send(200, "text/plain", "Update FAILED");
    } else {
        server.send(200, "text/plain", "Update OK. Rebooting...");
        delay(500);
        ESP.restart();
    }
}
