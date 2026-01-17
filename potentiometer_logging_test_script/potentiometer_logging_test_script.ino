//// Arduino script to read two potentiometers (A6 and A7) and send CSV: raw,voltage for both

const int potPin1 = A6;
const int potPin2 = A7;

void setup() {
  Serial.begin(115200);
}

void loop() {
  // Read first potentiometer
  int potValue1 = analogRead(potPin1);
  float voltage1 = potValue1 * (5.0 / 1023.0);

  // Read second potentiometer
  int potValue2 = analogRead(potPin2);
  float voltage2 = potValue2 * (5.0 / 1023.0);

  // Send as CSV: voltage1,voltage2
  Serial.print(voltage1, 2);
  Serial.print(",");
  Serial.println(voltage2, 2);

  delay(20); // faster updates for real-time plotting (~50Hz)
}

//// FOR SINGLE POT
//const int potPin = A6;
//
//void setup() {
//  Serial.begin(115200);
//}
//
//void loop() {
//  int potValue = analogRead(potPin);
//  float voltage = potValue * (5.0 / 1023.0);
//
//  Serial.print(potValue);
//  Serial.print(",");
//  Serial.println(voltage, 2); // CSV: raw,voltage
//
//  delay(50);
//}

