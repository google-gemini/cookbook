/*
Copyright 2025 Google LLC.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#include <Arduino.h>
#include <WiFi.h>
#include <FS.h>
#include <SD.h>
#include <HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include <Adafruit_NeoPixel.h>

// Pins
const int SD_CS = 5;
const int AUDIO_PIN = 34;
const int BUTTON_PIN = 32;
const int LED_PIN = 33;
const int NEOPIXEL_PIN = 15

// Configs for LED ring
const int NEOPIXEL_COUNT = 24;
int red = 255;
int green = 255;
int blue = 255;

// Configuration for audio recording
const int SAMPLE_RATE = 8000;
const int BIT_DEPTH = 16;
const int RECORD_DURATION = 2;

Adafruit_NeoPixel pixels(NEOPIXEL_COUNT, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// WIFI connection
String SSID = "";
String PASSWORD = "";

// Gemini API key
String API_KEY = "";

void setupWifi() {
  WiFi.begin(SSID, PASSWORD);
  while (WiFi.status()!= WL_CONNECTED) {
    delay(1000);
    Serial.print("...");
  }
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void toggleLights(bool on) {
  if( on ) {
    Serial.println("Turning on lights");
    int color = 255;
    for (int i = 0; i < NEOPIXEL_COUNT; i++) {
     pixels.setPixelColor(i, pixels.Color(red, green, blue));
     pixels.setBrightness(255);
    }
    pixels.show();
  } else {
    Serial.println("Turning off lights");
    pixels.clear();
    pixels.show(); 
  }
}

void recordAudio() {
  if (!SD.begin(SD_CS, SPI, 1000000)) {
    Serial.println("SD card initialization failed!");
    while (1);
  } else {
    Serial.println("SD card initialized!");
  }

  if (SD.exists("/tmp.wav")) {
    if (SD.remove("/tmp.wav")) {
      Serial.println("Previous audio file deleted.");
    } else {
      Serial.println("Failed to delete previous audio file.");
      return;
    }
  } else {
    Serial.println("No previous audio file detected, starting new");
  }

  File audioFile = SD.open("/tmp.wav", FILE_WRITE);
  if (!audioFile) {
    Serial.println("Failed to create audio file.");
    return;
  }

  Serial.println("Start recording");
  writeWavHeader(audioFile, SAMPLE_RATE, BIT_DEPTH, 1);

  int numSamples = SAMPLE_RATE * RECORD_DURATION;
  for (int i = 0; i < numSamples; i++) {
    int rawValue = analogRead(AUDIO_PIN);
    int16_t sample = map(rawValue, 0, 4095, -32768, 32767);
    audioFile.write((uint8_t*)&sample, 2);
    delayMicroseconds(1000000 / SAMPLE_RATE);
  }

  audioFile.close();
  Serial.println("Audio recorded to /tmp.wav");
}

void writeWavHeader(File& file, int sampleRate, int bitDepth, int channels) {
  uint32_t byteRate = sampleRate * channels * bitDepth / 8;
  uint16_t blockAlign = channels * bitDepth / 8;

  file.write((const uint8_t*)"RIFF", 4);
  uint32_t fileSize = 36 + RECORD_DURATION * byteRate;
  file.write((uint8_t*)&fileSize, 4); 
  file.write((const uint8_t*)"WAVE", 4);
  file.write((const uint8_t*)"fmt ", 4);
  uint32_t subchunk1Size = 16;
  file.write((uint8_t*)&subchunk1Size, 4);
  uint16_t audioFormat = 1;
  file.write((uint8_t*)&audioFormat, 2);
  file.write((uint8_t*)&channels, 2);
  file.write((uint8_t*)&sampleRate, 4);
  file.write((uint8_t*)&byteRate, 4);
  file.write((uint8_t*)&blockAlign, 2);
  file.write((uint8_t*)&bitDepth, 2);
  file.write((const uint8_t*)"data", 4);
  uint32_t subchunk2Size = RECORD_DURATION * byteRate;
  file.write((uint8_t*)&subchunk2Size, 4);
}

String base64Encode(const uint8_t* data, size_t length) {
  const char* b64_alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
  String encodedString = "";
  uint32_t i = 0;
  uint8_t b1, b2, b3;

  while (i < length) {
    b1 = data[i++];
    encodedString += b64_alphabet[b1 >> 2];
    if (i < length) {
      b2 = data[i++];
      encodedString += b64_alphabet[((b1 & 0x03) << 4) | (b2 >> 4)];
    } else {
      encodedString += b64_alphabet[(b1 & 0x03) << 4];
      encodedString += "==";
      break;
    }
    if (i < length) {
      b3 = data[i++];
      encodedString += b64_alphabet[((b2 & 0x0F) << 2) | (b3 >> 6)];
      encodedString += b64_alphabet[b3 & 0x3F];
    } else {
      encodedString += b64_alphabet[(b2 & 0x0F) << 2];
      encodedString += '=';
      break;
    }
  }
  return encodedString;
}

void createAudioJsonRequest() {
  if (SD.exists("/request-tmp.json")) {
    if (SD.remove("/request-tmp.json")) {
      Serial.println("Previous request file deleted.");
    } else {
      Serial.println("Failed to delete previous request file.");
      return;
    }
  } else {
    Serial.println("No previous request file detected, starting new");
  }

  File stringFile = SD.open("/audiostring.txt", FILE_READ);
  if (!stringFile) {
    Serial.println("Failed to open audiostring.txt for reading");
    return;
  }

  // Read the base64 encoded audio data from the file
  String base64EncodedData = stringFile.readString();
  stringFile.close();

  // Create the JSON document
  const size_t jsonBufferSize = 1024 * 64; // Adjust as needed
  DynamicJsonDocument doc(jsonBufferSize);

  // Set up REST call to call custom functions based on sent audio clip
  JsonArray contents = doc.createNestedArray("contents");
  JsonObject content = contents.createNestedObject();
  JsonArray parts = content.createNestedArray("parts");

  JsonObject textPart = parts.createNestedObject();
  textPart["text"] = "Trigger a function based on this audio input.";

  JsonObject audioPart = parts.createNestedObject();
  JsonObject inlineData = audioPart.createNestedObject("inline_data");
  inlineData["mime_type"] = "audio/x-wav";
  inlineData["data"] = base64EncodedData; // Use the data read from the file

  JsonArray tools = doc.createNestedArray("tools");
  JsonObject tool = tools.createNestedObject();
  JsonArray functionDeclarations = tool.createNestedArray("function_declarations");

  JsonObject changeColor = functionDeclarations.createNestedObject();
  changeColor["name"] = "changeColor";
  changeColor["description"] = "Change the default color for the lights in an RGB format. Example: Green would be 0 255 0.";

  JsonObject parametersChangeColor = changeColor.createNestedObject("parameters");
  parametersChangeColor["type"] = "object";
  JsonObject propertiesChangeColor = parametersChangeColor.createNestedObject("properties");

  JsonObject red = propertiesChangeColor.createNestedObject("red");
  red["type"] = "integer";
  red["description"] = "A value from 0 to 255 for the color RED in an RGB color code";

  JsonObject green = propertiesChangeColor.createNestedObject("green");
  green["type"] = "integer";
  green["description"] = "A value from 0 to 255 for the color GREEN in an RGB color code";

  JsonObject blue = propertiesChangeColor.createNestedObject("blue");
  blue["type"] = "integer";
  blue["description"] = "A value from 0 to 255 for the color BLUE in an RGB color code";

  JsonArray requiredChangeColor = parametersChangeColor.createNestedArray("required");
  requiredChangeColor.add("red");
  requiredChangeColor.add("green");
  requiredChangeColor.add("blue");

  JsonObject toggleLights = functionDeclarations.createNestedObject();
  toggleLights["name"] = "toggleLights";
  toggleLights["description"] = "Turn on or off the lights";

  JsonObject parametersToggleLights = toggleLights.createNestedObject("parameters");
  parametersToggleLights["type"] = "object";
  JsonObject propertiesToggleLights = parametersToggleLights.createNestedObject("properties");

  JsonObject toggle = propertiesToggleLights.createNestedObject("toggle");
  toggle["type"] = "boolean";
  toggle["description"] = "Determine if the lights should be turned on or off.";

  JsonArray requiredToggleLights = parametersToggleLights.createNestedArray("required");
  requiredToggleLights.add("toggle");

  // Open a file on the SD card for writing the JSON request
  File jsonFile = SD.open("/request-tmp.json", FILE_WRITE);
  if (!jsonFile) {
    Serial.println("Failed to open JSON file for writing");
    return;
  }

  // Serialize the JSON document to the file
  serializeJson(doc, jsonFile);
  jsonFile.close();

  Serial.println("JSON request saved to /request-tmp.json");
}

void sendAudio() {
  WiFiClientSecure client;
  client.setInsecure();
  HTTPClient http;

  if (http.begin(client, "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + API_KEY)) {
    http.addHeader("Content-Type", "application/json");

    File file = SD.open("/request-tmp.json", FILE_READ);
    if (!file) {
      Serial.println("Failed to open file for reading from SD card");
      return;
    }

    const int BUFFER_SIZE = 64;
    uint8_t fileBuffer[BUFFER_SIZE];

    const int JSON_STRING_SIZE = 65536; // Allocate 64kb for the audio file request. Likely smaller.
    char *jsonString = (char *)malloc(JSON_STRING_SIZE); 
    if (jsonString == NULL) {
      Serial.println("Failed to allocate memory for JSON string");
      file.close();
      return;
    }
    int jsonStringIndex = 0;

    while (file.available()) {
      int bytesRead = file.read(fileBuffer, BUFFER_SIZE);
      for (int i = 0; i < bytesRead && jsonStringIndex < JSON_STRING_SIZE - 1; i++) {
        jsonString[jsonStringIndex++] = fileBuffer[i];
      }
    }
    jsonString[jsonStringIndex] = '\0';

    file.close();
    SD.end(); // Close the SD connection after reading the file
    
    int httpCode = http.POST(jsonString);
    free(jsonString);
    Serial.print(F("Http code: "));
    Serial.println(httpCode);

    if (httpCode == HTTP_CODE_OK) {
      String payload = http.getString();
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print(F("deserializeJson() failed: "));
        Serial.println(error.c_str());
        return;
      }

      if (doc["candidates"][0]["content"]["parts"][0].containsKey("functionCall") &&
                    doc["candidates"][0]["content"]["parts"][0]["functionCall"].is<JsonObject>()) {

        JsonObject functionCall =
            doc["candidates"][0]["content"]["parts"][0]["functionCall"].as<JsonObject>();

        if (functionCall.containsKey("name")) {
          String functionName = functionCall["name"].as<String>();

          if( functionName == "toggleLights") {
            if (functionCall.containsKey("args") && functionCall["args"].is<JsonObject>()) {
                JsonObject args = functionCall["args"].as<JsonObject>();
                if (args.containsKey("toggle")) {
                  bool toggleValue = args["toggle"].as<bool>();
                  toggleLights(toggleValue);
                } else {
                  Serial.println("Toggle argument not found.");
                }
            } else {
              Serial.println("Args not found in function call.");
            }
          } else if( functionName == "changeColor") {
            if (functionCall.containsKey("args") && functionCall["args"].is<JsonObject>()) {
                JsonObject args = functionCall["args"].as<JsonObject>();
                red = args["red"].as<int>();
                green = args["green"].as<int>();
                blue = args["blue"].as<int>();
                toggleLights(true);
            } else {
              Serial.println("Args not found in function call.");
            }
          } 
        } else {
          Serial.println("Function name not found.");
        }
      } else {
        Serial.println("Function call not found.");
      }
      
    } else {
      Serial.println("HTTP POST request failed");
    }
    http.end();
  } else {
    Serial.println("HTTP begin failed");
  }
}

void saveAudioString() {
  File audioFile = SD.open("/tmp.wav", FILE_READ);
  if (!audioFile) {
    Serial.println("Failed to open audio file for reading");
    return;
  }

  size_t fileSize = audioFile.size();
  uint8_t* audioData = (uint8_t*)malloc(fileSize);
  if (audioData == NULL) {
    Serial.println("Failed to allocate memory for audio data");
    audioFile.close();
    return;
  }
  audioFile.read(audioData, fileSize);
  audioFile.close();

  String base64AudioData = base64Encode(audioData, fileSize);
  free(audioData);

  File stringFile = SD.open("/audiostring.txt", FILE_WRITE);
  if (!stringFile) {
    Serial.println("Failed to open audiostring.txt for writing");
    return;
  }
  stringFile.print(base64AudioData);
  stringFile.close();

  Serial.println("Audio base64 string saved to /audiostring.txt");
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);
  WRITE_PERI_REG(RTC_CNTL_WDTCONFIG0_REG, 0);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LED_PIN, OUTPUT);
  pixels.begin();
  pixels.show();

  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  while (!Serial);
  
  setupWifi();
}

void loop() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    digitalWrite(LED_PIN, HIGH);
    
    // This delay is to debounce the button and allow time to speak
    delay(500); 

    recordAudio();
    digitalWrite(LED_PIN, LOW);
    saveAudioString();
    createAudioJsonRequest();
    sendAudio();
  }
}