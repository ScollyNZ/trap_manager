#include <Arduino.h>
#include <RadioLib.h>
#include "lora.h"

// Pin map for XIAO ESP32-S3 + Wio-SX1262 via B2B
#define PIN_LORA_CS    41
#define PIN_LORA_SCK   7    //18
#define PIN_LORA_MOSI  9    //16
#define PIN_LORA_MISO  8    //14
#define PIN_LORA_BUSY  40   //48
#define PIN_LORA_DIO1  39   //47
#define PIN_LORA_DIO2  38   
#define PIN_LORA_RST   42   //21

// Constructor
lora::lora() {
    // Initialize LoRa module here if needed
}

// Check if LoRa module is present
bool lora::isPresent() {
    //SPIClass spiFSPI(FSPI);
    SX1262 lora = new Module(PIN_LORA_CS, PIN_LORA_DIO1, PIN_LORA_RST, PIN_LORA_BUSY);

    // init SPI bus
    //spiFSPI.begin(PIN_LORA_SCK, PIN_LORA_MISO, PIN_LORA_MOSI, PIN_LORA_CS);

    // try to begin the radio (freq doesn't matter here, just a valid band)
        int state = lora.begin(915.0);
        if (state == RADIOLIB_ERR_NONE) {
            Serial.println("LoRa board detected and initialized!");
            return true;
        } else {
            Serial.print("LoRa board NOT found, error code: ");
            Serial.println(state);
            return false;
        }
    }

