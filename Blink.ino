#define REDPIN 5
#define GREENPIN 6
#define BLUEPIN 3
 
#define FADESPEED 5     // make this higher to slow down
 
int incomingByte = 0;  // for incoming serial data

void setup() {
        Serial.begin(9600);     // opens serial port, sets data rate to 9600 bps
}

void loop() {

        // send data only when you receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                incomingByte = Serial.read();

                // say what you got:
                Serial.print("I received: ");
                Serial.println(incomingByte, DEC);
        }
}

//THIS IS THE CODE TO CONTROL THE LED CONTROL THROUGH PWM
// 
//void setup() {
//  pinMode(REDPIN, OUTPUT);
//  pinMode(GREENPIN, OUTPUT);
//  pinMode(BLUEPIN, OUTPUT);
//}
// 
// 
//void loop() {
//  int r, g, b;
// 
//  // fade from blue to violet
//  for (r = 0; r < 256; r++) { 
//    analogWrite(REDPIN, r);
//    delay(FADESPEED);
//  } 
//  // fade from violet to red
//  for (b = 255; b > 0; b--) { 
//    analogWrite(BLUEPIN, b);
//    delay(FADESPEED);
//  } 
//  // fade from red to yellow
//  for (g = 0; g < 256; g++) { 
//    analogWrite(GREENPIN, g);
//    delay(FADESPEED);
//  } 
//  // fade from yellow to green
//  for (r = 255; r > 0; r--) { 
//    analogWrite(REDPIN, r);
//    delay(FADESPEED);
//  } 
//  // fade from green to teal
//  for (b = 0; b < 256; b++) { 
//    analogWrite(BLUEPIN, b);
//    delay(FADESPEED);
//  } 
//  // fade from teal to blue
//  for (g = 255; g > 0; g--) { 
//    analogWrite(GREENPIN, g);
//    delay(FADESPEED);
//  } 
//}
