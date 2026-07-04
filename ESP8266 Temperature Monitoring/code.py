#include <ESP8266WiFi.h>
#include "max6675.h"

// Shared pins
int thermoSO = D6;
int thermoSCK = D5;

// Individual CS pins
int thermoCS1 = D1;
int thermoCS2 = D2;
int thermoCS3 = D3;
int thermoCS4 = D4;

// MAX6675 objects
MAX6675 tc1(thermoSCK, thermoCS1, thermoSO);
MAX6675 tc2(thermoSCK, thermoCS2, thermoSO);
MAX6675 tc3(thermoSCK, thermoCS3, thermoSO);
MAX6675 tc4(thermoSCK, thermoCS4, thermoSO);

// WiFi AP credentials
const char* ssid = "ESP_Thermo";
const char* password = "12345678";

WiFiServer server(80);

// Temperature variables
float t1 = 0, t2 = 0, t3 = 0, t4 = 0;
float prev_t1 = 0, prev_t2 = 0, prev_t3 = 0, prev_t4 = 0;
float diff_t1 = 0, diff_t2 = 0, diff_t3 = 0, diff_t4 = 0;

unsigned long lastUpdate = 0;
const unsigned long interval = 5000; // update every 5 sec

void setup() {
  Serial.begin(115200);
  WiFi.softAP(ssid, password);
  server.begin();
}

void loop() {

  // Update temperatures every 5 seconds
  if (millis() - lastUpdate >= interval) {
    lastUpdate = millis();

    prev_t1 = t1;
    prev_t2 = t2;
    prev_t3 = t3;
    prev_t4 = t4;

    t1 = tc1.readCelsius();
    t2 = tc2.readCelsius();
    t3 = tc3.readCelsius();
    t4 = tc4.readCelsius();

    diff_t1 = t1 - prev_t1;
    diff_t2 = t2 - prev_t2;
    diff_t3 = t3 - prev_t3;
    diff_t4 = t4 - prev_t4;
  }

  WiFiClient client = server.available();
  if (!client) return;

  while (!client.available()) delay(1);
  client.readStringUntil('\r');
  client.flush();

  String html = "<!DOCTYPE html><html><head>";

  //  Auto refresh every 5 seconds
  html += "<meta http-equiv='refresh' content='5'/>";

  html += "<meta name='viewport' content='width=device-width, initial-scale=1'>";
  html += "<style>";
  html += "body{background:#111;color:#fff;font-family:Arial;text-align:center;}";
  html += "table{width:90%;margin:auto;border-collapse:collapse;font-size:20px;}";
  html += "th,td{padding:10px;border-bottom:1px solid #333;}";
  html += "h2,h3{font-weight:normal;}";
  html += "</style>";
  html += "</head><body>";

  html += "<h2>ESP8266 - Thermocouple Monitor</h2>";

  // Current values table
  html += "<h3>Current Values</h3>";
  html += "<table>";
  html += "<tr><th>Sensor</th><th>Temperature (°C)</th><th>Difference (°C)</th></tr>";
  html += "<tr><td>T1</td><td>" + String(t1) + "</td><td>" + String(diff_t1) + "</td></tr>";
  html += "<tr><td>T2</td><td>" + String(t2) + "</td><td>" + String(diff_t2) + "</td></tr>";
  html += "<tr><td>T3</td><td>" + String(t3) + "</td><td>" + String(diff_t3) + "</td></tr>";
  html += "<tr><td>T4</td><td>" + String(t4) + "</td><td>" + String(diff_t4) + "</td></tr>";
  html += "</table>";

  // Previous values table
  html += "<h3>Previous Values</h3>";
  html += "<table>";
  html += "<tr><th>Sensor</th><th>Previous Temp (°C)</th></tr>";
  html += "<tr><td>T1</td><td>" + String(prev_t1) + "</td></tr>";
  html += "<tr><td>T2</td><td>" + String(prev_t2) + "</td></tr>";
  html += "<tr><td>T3</td><td>" + String(prev_t3) + "</td></tr>";
  html += "<tr><td>T4</td><td>" + String(prev_t4) + "</td></tr>";
  html += "</table>";

  html += "</body></html>";

  client.print("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n");
  client.print(html);
}