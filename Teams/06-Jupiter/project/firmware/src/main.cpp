#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <Adafruit_MLX90614.h>
#include <ArduinoJson.h>
#include "esp_camera.h"
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"
#include <WebServer.h>

const char* ssid = "GB";
const char* password = "GB2548000000";
const char* api_url = "http://10.37.50.169:3000/inspection";

// ESP32-S3 WROOM CAM Pins
#define PWDN_GPIO_NUM     -1
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     10
#define SIOD_GPIO_NUM     40
#define SIOC_GPIO_NUM     39
#define Y9_GPIO_NUM       48
#define Y8_GPIO_NUM       11
#define Y7_GPIO_NUM       12
#define Y6_GPIO_NUM       14
#define Y5_GPIO_NUM       16
#define Y4_GPIO_NUM       18
#define Y3_GPIO_NUM       17
#define Y2_GPIO_NUM       15
#define VSYNC_GPIO_NUM    38
#define HREF_GPIO_NUM     47
#define PCLK_GPIO_NUM     13

#define LED_PIN           2  // Built-in LED on many ESP32 boards
#define SDA_PIN           41
#define SCL_PIN           42

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
WebServer server(80);

unsigned long lastReadTime = 0;
unsigned long lastSendTime = 0;
float tempBuffer[10] = {0};
int bufIdx = 0;
bool bufferFull = false;
int partCounter = 0;

float lastObjTemp = 0.0;
float lastAmbTemp = 0.0;
String lastStatus = "---";

void blinkLED(int times) {
  for(int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(100);
    digitalWrite(LED_PIN, LOW);
    if(i < times - 1) delay(150);
  }
}

void startCameraServer();
void handleSnapshot();
void handleStream();

void startCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.frame_size = FRAMESIZE_VGA;
  config.pixel_format = PIXFORMAT_JPEG;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 12;
  config.fb_count = 2;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }
  Serial.println("Camera initialized.");
}

void handleSnapshot() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    server.send(500, "text/plain", "Camera capture failed");
    return;
  }
  server.sendHeader("Content-Type", "image/jpeg");
  server.sendHeader("Content-Disposition", "inline; filename=capture.jpg");
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.client().write(fb->buf, fb->len);
  esp_camera_fb_return(fb);
}

#define MIN_FRAME_TIME_MS 100
#define STREAM_CHUNK_SIZE 4096
#define SEND_INTERVAL 3000 // Define SEND_INTERVAL for sendData calls

void sendData(float obj, float amb, float var) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_url);
    http.addHeader("Content-Type", "application/json");

    String uid = "PART-" + String(millis()) + "-" + String(random(1000, 9999));
    String snapUrl = "http://" + WiFi.localIP().toString() + "/snapshot";
    long rssi = WiFi.RSSI();
    String st = getStatus(var);

    StaticJsonDocument<512> doc;
    doc["part_uid"] = uid;
    doc["temperature"] = obj;
    doc["ambient_temp"] = amb;
    doc["variance"] = var;
    doc["component_name"] = "Automotive Part";
    doc["device_id"] = "ESP32S3-CAM-01";
    doc["wifi_rssi"] = rssi;
    doc["status"] = st;
    doc["image_path"] = snapUrl;
    
    String payload;
    serializeJson(doc, payload);
    
    int httpCode = http.POST(payload);
    if(httpCode > 0) {
      // Serial.printf("POST success: %d\n", httpCode);
    } else {
      Serial.printf("POST error: %d\n", httpCode);
    }
    http.end();
  }
}

void handleStream() {
  WiFiClient client = server.client();
  client.setNoDelay(true);

  client.print("HTTP/1.1 200 OK\r\n");
  client.print("Content-Type: multipart/x-mixed-replace; boundary=--jpgboundary\r\n");
  client.print("Access-Control-Allow-Origin: *\r\n");
  client.print("Cache-Control: no-store, no-cache\r\n");
  client.print("Connection: close\r\n\r\n");

  unsigned long lastFrameTime = 0;

  while (client.connected()) {
    if (millis() - lastFrameTime < MIN_FRAME_TIME_MS) {
      delay(1); continue;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) { delay(5); continue; }

    char hdr[256];
    int hdrLen = snprintf(hdr, sizeof(hdr),
      "--jpgboundary\r\n"
      "Content-Type: image/jpeg\r\n"
      "Content-Length: %u\r\n"
      "X-Object-Temp: %.1f\r\n"
      "X-Ambient-Temp: %.1f\r\n"
      "X-Temp-Status: %s\r\n"
      "\r\n",
      (uint32_t)fb->len,
      lastObjTemp,
      lastAmbTemp,
      lastStatus.c_str()
    );
    client.write((uint8_t*)hdr, hdrLen);

    size_t remaining = fb->len;
    uint8_t *ptr     = fb->buf;
    bool failed      = false;
    while (remaining > 0) {
      size_t toSend  = min(remaining, (size_t)STREAM_CHUNK_SIZE);
      size_t written = client.write(ptr, toSend);
      if (written == 0) { failed = true; break; }
      ptr       += written;
      remaining -= written;
    }
    client.write((uint8_t*)"\r\n", 2);
    esp_camera_fb_return(fb);

    if (failed) break;
    lastFrameTime = millis();
  }
}

void connectWiFi() {
  if(WiFi.status() == WL_CONNECTED) return;
  Serial.print("Connecting to WiFi");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

float calculateVariance() {
  if(!bufferFull && bufIdx == 0) return 0;
  int count = bufferFull ? 10 : bufIdx;
  
  float sum = 0;
  for(int i=0; i<count; i++) sum += tempBuffer[i];
  float mean = sum / count;
  
  float varSum = 0;
  for(int i=0; i<count; i++) {
    varSum += (tempBuffer[i] - mean) * (tempBuffer[i] - mean);
  }
  return varSum / count;
}

String getStatus(float var) {
  if (var < 1.5) return "OK";
  if (var < 4.0) return "WARNING";
  return "NOK";
}

void setup() {
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); 
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  connectWiFi();
  startCamera();
  
  Wire.begin(SDA_PIN, SCL_PIN);
  if (!mlx.begin(0x5A, &Wire)) {
    Serial.println("Error connecting to MLX sensor. Check wiring.");
  }

  server.on("/snapshot", HTTP_GET, handleSnapshot);
  server.on("/stream", HTTP_GET, handleStream);
  server.begin();
  Serial.println("Camera HTTP server started on port 80");
}

void loop() {
  server.handleClient();
  connectWiFi();

  unsigned long now = millis();
  
  // Read Temp every 500ms
  if (now - lastReadTime >= 500) {
    lastReadTime = now;
    float obj = mlx.readObjectTempC();
    float amb = mlx.readAmbientTempC();
    if (!isnan(obj)) {
      lastObjTemp = obj;
      lastAmbTemp = amb;
      lastStatus  = getStatus(calculateVariance());
      tempBuffer[bufIdx] = obj;
      bufIdx = (bufIdx + 1) % 10;
      if (bufIdx == 0) bufferFull = true;
    }
  }

  // Send record every 3s
  if (now - lastSendTime >= 3000) {
    lastSendTime = now;
    
    float var = calculateVariance();
    String st = lastStatus;
    partCounter++;
    
    Serial.printf("Part: %d | Ambient: %.2f C | Object: %.2f C | Variance: %.2f | Status: %s\n", 
                  partCounter, lastAmbTemp, lastObjTemp, var, st.c_str());
    
    if (st == "OK") blinkLED(1);
    else if (st == "WARNING") blinkLED(3);
    else blinkLED(5);

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(api_url);
      http.addHeader("Content-Type", "application/json");

      String uid = "PART-" + String(millis()) + "-" + String(random(1000, 9999));
      String snapUrl = "http://" + WiFi.localIP().toString() + "/snapshot";
      long rssi = WiFi.RSSI();

      StaticJsonDocument<512> doc;
      doc["part_uid"] = uid;
      doc["temperature"] = lastObjTemp;
      doc["ambient_temp"] = lastAmbTemp;
      doc["variance"] = var;
      doc["component_name"] = "Automotive Part";
      doc["device_id"] = "ESP32S3-CAM-01";
      doc["wifi_rssi"] = rssi;
      doc["status"] = st;
      doc["image_path"] = snapUrl;
      
      String payload;
      serializeJson(doc, payload);
      
      int httpCode = http.POST(payload);
      if(httpCode > 0) {
        // Serial.printf("POST success: %d\n", httpCode);
      } else {
        Serial.printf("POST error: %d\n", httpCode);
      }
      http.end();
    }
  }
}
