#include <SoftwareSerial.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// --- Bluetooth Setup ---
SoftwareSerial btSerial(8, 9);  // RX, TX

// --- OLED Setup ---
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// --- Message buffer ---
String messageBuffer = "";

void setup() {
  Serial.begin(38400);
  btSerial.begin(38400);

  Serial.println("Bluetooth + OLED test started");

  // Initialize OLED
  if(!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("SSD1306 allocation failed");
    for(;;);
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0,0);
  display.println("Waiting for Bluetooth...");
  display.display();
}

void loop() {
  // --- From Bluetooth ---
  while (btSerial.available()) {
    char c = btSerial.read();
    messageBuffer += c;  // accumulate message
    Serial.write(c);     // also print to USB Serial

    // If newline received, display full message
    if (c == '\n' || messageBuffer.length() >= 100) {
      displayMessage(messageBuffer);
      messageBuffer = "";  // reset buffer
    }
  }

  // --- From PC USB Serial to Bluetooth ---
  while (Serial.available()) {
    char c = Serial.read();
    btSerial.write(c);
  }
}

void displayMessage(String msg) {
  display.clearDisplay();
  display.setCursor(0,0);
  display.println("Received:");
  display.println(msg);
  display.display();
}
 
