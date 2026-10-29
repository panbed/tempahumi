#include <Arduino.h>
#include <DHT.h>
#include <WiFiManager.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// pin/dht config
#define DHTPIN 21
#define DHTTYPE DHT11

// func declarations:
DHT dht(DHTPIN, DHTTYPE);
WebServer server(80);

void sendResponse();
void setupApi();

float humidity;
float temperature;

StaticJsonDocument<1024> jsonDocument;
char buffer[1024];

uint32_t measureDelay = 3000;
uint32_t lastTimeRan;

void setup() {
  // setup serial
  Serial.begin(115200);
  delay(1500);

  // setup wifi
  WiFi.mode(WIFI_STA);
  WiFiManager wm;
  bool res;
  res = wm.autoConnect("AutoConnectAP", "password");

  if (!res) {
    Serial.println("Failed to connect!");
    ESP.restart();
  }
  else {
    Serial.println("Connect to internet!");
  }

  setupApi();

  Serial.println("Starting temperature and humidity sensor readings...");
  dht.begin();
}

void loop() {
  server.handleClient();

  if (millis() > lastTimeRan + measureDelay) {
    // read sensors
    humidity = dht.readHumidity();
    temperature = dht.readTemperature(true); // fahrenheit

    lastTimeRan = millis();

    Serial.printf("Humidity: ");
    Serial.printf("%f%\n", humidity);

    Serial.print("Temperature: ");
    Serial.printf("%f°F\n", temperature);
  }
}

// func definitions:
void sendResponse() {
  Serial.println("Sending response!");
  
  // setup JSON document to send
  jsonDocument.clear();
  jsonDocument["temperature"] = temperature;
  jsonDocument["humidity"] = humidity;
  serializeJson(jsonDocument, buffer);

  server.send(200, "application/json", buffer);

}

void setupApi() {
  server.on("/", sendResponse);
  server.begin();
}