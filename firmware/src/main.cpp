#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <DHT.h>
#include <ArduinoOTA.h>
#include "secrets.h"
#define DHTPIN 4
#define DHTTYPE DHT22
#define LED_PIN 2
DHT dht(DHTPIN, DHTTYPE);
WiFiClientSecure tlsClient;
PubSubClient mqttClient(tlsClient);
static const char* TELEMETRY_TOPIC = "devices/" DEVICE_ID "/telemetry";
static const char* STATUS_TOPIC    = "devices/" DEVICE_ID "/status";
static const char* CMD_TOPIC       = "devices/" DEVICE_ID "/cmd";
unsigned long lastTelemetryMs = 0, telemetryIntervalMs = 5000;
float lastTemp = NAN, lastHum = NAN;

static void syncTime(){ configTime(0,0,"pool.ntp.org","time.nist.gov"); struct tm ti; 
        for(int i=0;i<20 && !getLocalTime(&ti);++i) delay(500); }

static void publishStatus(bool online){ StaticJsonDocument<128> d; 
        d["device_id"]=DEVICE_ID; d["online"]=online; char b[128]; size_t n=serializeJson(d,b); 
        mqttClient.publish(STATUS_TOPIC,b,n,true); }

static void handleCommand(char*, byte* p, unsigned int n){ StaticJsonDocument<256> cmd; 
        if(deserializeJson(cmd,p,n)) return; if(cmd.containsKey("led")) digitalWrite(LED_PIN, 
        cmd["led"].as<bool>()?HIGH:LOW); 
        if(cmd.containsKey("interval_ms")) telemetryIntervalMs=cmd["interval_ms"].as<unsigned long>(); 
        }

static void reconnectMqtt(){ 
        while(!mqttClient.connected()){ String cid=String("esp32-")+DEVICE_ID+"-"+String(random(0xffff),HEX); 
        if(mqttClient.connect(cid.c_str(), MQTT_USERNAME, MQTT_PASSWORD, STATUS_TOPIC, 0, true, 
        "{\"online\":false}")){ mqttClient.subscribe(CMD_TOPIC); publishStatus(true);} else { delay(1000);} } }

static void connectWifi(){ WiFi.mode(WIFI_STA); 
        WiFi.begin(WIFI_SSID,WIFI_PASS); 
        unsigned long s=millis(); 
        while(WiFi.status()!=WL_CONNECTED && millis()-s<30000) delay(250); }

static void sendTelemetry(float t,float h){ StaticJsonDocument<256> d; d["device_id"]=DEVICE_ID; 
        d["ts"]=(uint64_t)millis(); 
        time_t now=time(nullptr); if(now>100000) d["ts"]=(uint64_t)now*1000ULL; 
        if(!isnan(t)) d["temp_c"]=t; if(!isnan(h)) d["hum_pct"]=h; char b[256]; size_t n=serializeJson(d,b); 
        mqttClient.publish(TELEMETRY_TOPIC,b,n,false); }

void setup(){ pinMode(LED_PIN,OUTPUT); Serial.begin(115200); delay(200); 
        dht.begin(); connectWifi(); syncTime(); 
        tlsClient.setCACert(ROOT_CA_PEM); tlsClient.setTimeout(15000); 
        mqttClient.setServer(MQTT_HOST,MQTT_PORT); mqttClient.setCallback(handleCommand); 
        ArduinoOTA.setHostname(DEVICE_ID); ArduinoOTA.begin(); }

void loop(){ if(WiFi.status()!=WL_CONNECTED) connectWifi(); 
        if(!mqttClient.connected()) reconnectMqtt(); 
        mqttClient.loop(); ArduinoOTA.handle(); unsigned long now=millis(); 
        if(now-lastTelemetryMs>=telemetryIntervalMs){ lastTelemetryMs=now; 
        float h=dht.readHumidity(), t=dht.readTemperature(); 
        if(!isnan(t)) lastTemp=t; 
        if(!isnan(h)) lastHum=h; sendTelemetry(lastTemp,lastHum);} }
        