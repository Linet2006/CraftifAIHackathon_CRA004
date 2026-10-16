/*
 * ==============================================================================
 * Workplace Safety Sentinel - ESP32 Physical Actuator Firmware
 * HackwithBangalore 4.0 / CraftifAI Physical AI Closed-Loop Bonus
 * 
 * Hardware Pin Mapping:
 * - Pin 2  : Built-in Heartbeat LED
 * - Pin 18 : High-Power Visual Strobe Beacon
 * - Pin 19 : Machine Emergency Stop (E-Stop) Relay Interlock
 * - Pin 21 : Industrial Piezo Warning Siren (PWM)
 * - Pin 22 : WS2812B NeoPixel RGB Health Strip
 * ==============================================================================
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Network Credentials
const char* ssid = "Hackathon_Mesh_WiFi";
const char* password = "hackwithbangalore";
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
const char* alert_topic = "workplace/safety/alerts";
const char* telemetry_topic = "workplace/safety/actuator_status";

// Pin Assignments
const int PIN_HEARTBEAT = 2;
const int PIN_STROBE = 18;
const int PIN_ESTOP_RELAY = 19;
const int PIN_SIREN = 21;

WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastHeartbeat = 0;
bool alarmState = false;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_HEARTBEAT, OUTPUT);
  pinMode(PIN_STROBE, OUTPUT);
  pinMode(PIN_ESTOP_RELAY, OUTPUT);
  pinMode(PIN_SIREN, OUTPUT);

  // Initial Safe State
  digitalWrite(PIN_STROBE, LOW);
  digitalWrite(PIN_ESTOP_RELAY, LOW); // Relay normal operation
  digitalWrite(PIN_SIREN, LOW);

  Serial.println("\n[ESP32 Sentinel Actuator] Initialized. Awaiting PipeGen commands...");
  
  WiFi.begin(ssid, password);
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqttCallback);
}

void mqttCallback(char* topic, byte* payload, unsigned int length) {
  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload, length);
  if (error) {
    Serial.print("[JSON Parse Error]: ");
    Serial.println(error.c_str());
    return;
  }

  const char* cmd = doc["cmd"];
  const char* event_type = doc["event_type"];
  const char* severity = doc["severity"];

  Serial.print("[MQTT Action Triggered]: ");
  Serial.print(event_type ? event_type : cmd);
  Serial.print(" | Severity: ");
  Serial.println(severity ? severity : "N/A");

  if (strcmp(severity, "CRITICAL") == 0 || (cmd && strcmp(cmd, "ALARM_CRITICAL") == 0)) {
    triggerCriticalAlarm();
  } else if (strcmp(severity, "WARNING") == 0 || (cmd && strcmp(cmd, "ALARM_WARNING") == 0)) {
    triggerWarningAlarm();
  } else {
    resetAllClear();
  }
}

void triggerCriticalAlarm() {
  alarmState = true;
  digitalWrite(PIN_STROBE, HIGH);
  digitalWrite(PIN_ESTOP_RELAY, HIGH); // Open safety contact - HALT MACHINERY
  tone(PIN_SIREN, 2400); // 2.4kHz piercing industrial tone
  Serial.println(">>> [ACTUATION] E-STOP RELAY ENGAGED! SIREN ACTIVE! <<<");
}

void triggerWarningAlarm() {
  alarmState = false;
  digitalWrite(PIN_STROBE, HIGH);
  digitalWrite(PIN_ESTOP_RELAY, LOW);
  noTone(PIN_SIREN);
  Serial.println(">>> [ACTUATION] WARNING STROBE ACTIVE. PPE NON-COMPLIANCE. <<<");
}

void resetAllClear() {
  alarmState = false;
  digitalWrite(PIN_STROBE, LOW);
  digitalWrite(PIN_ESTOP_RELAY, LOW);
  noTone(PIN_SIREN);
  Serial.println(">>> [ACTUATION] NORMAL GREEN STATE RESTORED. <<<");
}

void loop() {
  // Check Serial commands from direct USB connection
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    StaticJsonDocument<256> doc;
    if (!deserializeJson(doc, input)) {
      const char* cmd = doc["cmd"];
      if (cmd && strcmp(cmd, "ALARM_CRITICAL") == 0) triggerCriticalAlarm();
      else if (cmd && strcmp(cmd, "ALARM_WARNING") == 0) triggerWarningAlarm();
      else resetAllClear();
    }
  }

  // Heartbeat blink
  if (millis() - lastHeartbeat > 500) {
    lastHeartbeat = millis();
    digitalWrite(PIN_HEARTBEAT, !digitalRead(PIN_HEARTBEAT));
  }
}
