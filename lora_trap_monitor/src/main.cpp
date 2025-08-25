#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <Update.h>
#include <ESPmDNS.h>   // optional, for <hostname>.local
#include "httpota.h"
#include "lora.h"

#define FIRMWARE_VERSION "0.0.4"

// ── Wi‑Fi ─────────────────────────────────────────────────────────────
const char* WIFI_SSID = "scoltock";
const char* WIFI_PASS = "nowireshere";

// Optional mDNS hostname -> http://trap-monitor-1.local
const char* HOSTNAME  = "trap-monitor-1";

// Singleton instance for use in main.cpp
HttpOta httpOta("admin", "changeme");

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Initialize onboard LED for debugging
  pinMode(21, OUTPUT); // GPIO 21 is the onboard LED on Seeed

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.printf("Connecting to %s", WIFI_SSID);
  while (WiFi.status() != WL_CONNECTED) { delay(250); Serial.print("."); }
  Serial.printf("\nConnected. IP: %s\n", WiFi.localIP().toString().c_str());
  Serial.printf("Firmware Version: %s\n", FIRMWARE_VERSION);

  
  // Optional mDNS
  if (MDNS.begin(HOSTNAME)) {
    MDNS.addService("http", "tcp", 80);
    Serial.printf("mDNS: http://%s.local/\n", HOSTNAME);
  } else {
    Serial.println("mDNS start failed");
  }
  httpOta.begin();  // Start the HTTP OTA server

  //Check LoRa module presence
  lora myLora;
  if (myLora.isPresent()) {
    Serial.println("LoRa module is present.");
  } else {
    Serial.println("LoRa module is NOT present.");  
  }
}

void heartbeat() {
  // on every 500th loop iteration, print a dot to indicate the device is alive
  static int count = 0;
  static int nextChange = 200;

  if (++count % nextChange == 0) {
    Serial.print(". ");
    //digitalWrite(21, !digitalRead(21));
    if (nextChange == 500) nextChange = 20; else nextChange = 200;
    count = 0;  
    }  
}

void loop() {
  httpOta.handleClient();    // keep web server responsive
  delay(1);                 // yield to Wi‑Fi stack
  heartbeat();
}
