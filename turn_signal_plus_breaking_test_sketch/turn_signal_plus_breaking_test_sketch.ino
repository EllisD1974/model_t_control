/*
  Brake + Turn Signal Controller
  --------------------------------
  Buttons (active LOW, INPUT_PULLUP):
    Pin 7 - Brake
    Pin 6 - Left
    Pin 5 - Right

  LEDs:
    A0 - Front Left
    A1 - Front Right
    A2 - Rear Left
    A3 - Rear Right
*/

//////////////////////
// Pin Definitions //
//////////////////////
const int BRAKE_BTN = 7;
const int LEFT_BTN  = 6;
const int RIGHT_BTN = 5;

const int FRONT_LEFT  = A0;
const int FRONT_RIGHT = A1;
const int REAR_LEFT   = A2;
const int REAR_RIGHT  = A3;

//////////////////////
// Timing           //
//////////////////////
const unsigned long BLINK_INTERVAL = 500;

unsigned long lastBlinkTime = 0;
bool blinkState = false;

//////////////////////
// Input Bit Masks //
//////////////////////
#define BRAKE 0b001
#define LEFT  0b010
#define RIGHT 0b100

//////////////////////
// Light Actions   //
//////////////////////
enum LightAction : uint8_t {
  OFF,
  ON,
  BLINK
};

//////////////////////
// Blink Modes     //
//////////////////////
enum BlinkMode : uint8_t {
  BLINK_NONE,
  BLINK_LEFT,
  BLINK_RIGHT,
  BLINK_HAZARD
};

//////////////////////
// State Structure //
//////////////////////
struct LightState {
  LightAction frontLeft;
  LightAction frontRight;
  LightAction rearLeft;
  LightAction rearRight;
};

//////////////////////
// Lookup Table    //
//////////////////////
const LightState stateTable[8] = {
  //  R L B
  { OFF,   OFF,   OFF,   OFF },   // 0b000
  { OFF,   OFF,   ON,    ON  },   // 0b001 BRAKE
  { BLINK, OFF,   BLINK, OFF },   // 0b010 LEFT
  { BLINK, OFF,   BLINK, ON  },   // 0b011 BRAKE + LEFT
  { OFF,   BLINK, OFF,   BLINK }, // 0b100 RIGHT
  { OFF,   BLINK, ON,    BLINK }, // 0b101 BRAKE + RIGHT
  { BLINK, BLINK, BLINK, BLINK }, // 0b110 HAZARD
  { BLINK, BLINK, ON,    ON  }    // 0b111 BRAKE + HAZARD ✅
};

//////////////////////
// Blink Tracking  //
//////////////////////
BlinkMode lastBlinkMode = BLINK_NONE;

//////////////////////
// Helper Functions//
//////////////////////
BlinkMode getBlinkMode(uint8_t inputState) {
  bool left  = inputState & LEFT;
  bool right = inputState & RIGHT;

  if (left && right) return BLINK_HAZARD;
  if (left)          return BLINK_LEFT;
  if (right)         return BLINK_RIGHT;
  return BLINK_NONE;
}

void applyLight(int pin, LightAction action) {
  if (action == ON) {
    digitalWrite(pin, HIGH);
  }
  else if (action == BLINK) {
    digitalWrite(pin, blinkState ? HIGH : LOW);
  }
  else {
    digitalWrite(pin, LOW);
  }
}

//////////////////////
// Setup           //
//////////////////////
void setup() {
  pinMode(BRAKE_BTN, INPUT_PULLUP);
  pinMode(LEFT_BTN,  INPUT_PULLUP);
  pinMode(RIGHT_BTN, INPUT_PULLUP);

  pinMode(FRONT_LEFT,  OUTPUT);
  pinMode(FRONT_RIGHT, OUTPUT);
  pinMode(REAR_LEFT,   OUTPUT);
  pinMode(REAR_RIGHT,  OUTPUT);
}

//////////////////////
// Main Loop       //
//////////////////////
void loop() {
  bool braking = digitalRead(BRAKE_BTN) == LOW;
  bool left    = digitalRead(LEFT_BTN)  == LOW;
  bool right   = digitalRead(RIGHT_BTN) == LOW;

  uint8_t inputState = 0;
  if (braking) inputState |= BRAKE;
  if (left)    inputState |= LEFT;
  if (right)   inputState |= RIGHT;

  BlinkMode currentBlinkMode = getBlinkMode(inputState);

  // Reset blink phase ONLY when blink mode changes
  if (currentBlinkMode != lastBlinkMode && currentBlinkMode != BLINK_NONE) {
    blinkState = true;
    lastBlinkTime = millis();
  }

  lastBlinkMode = currentBlinkMode;

  // Update blink timing
  if (currentBlinkMode != BLINK_NONE) {
    if (millis() - lastBlinkTime >= BLINK_INTERVAL) {
      lastBlinkTime = millis();
      blinkState = !blinkState;
    }
  } else {
    blinkState = false;
  }

  const LightState& s = stateTable[inputState];

  applyLight(FRONT_LEFT,  s.frontLeft);
  applyLight(FRONT_RIGHT, s.frontRight);
  applyLight(REAR_LEFT,   s.rearLeft);
  applyLight(REAR_RIGHT,  s.rearRight);
}

