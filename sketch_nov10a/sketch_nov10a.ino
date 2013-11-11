// color swirl! connect an RGB LED to the PWM pins as indicated
// in the #defines
// public domain, enjoy!
 
#define BLUEPIN 6
#define GREENPIN 5
#define REDPIN 3
 
#define FADESPEED 5     // make this higher to slow down
byte incomingByte = 0;
void setup() {
  Serial.begin(9600);
  pinMode(REDPIN, OUTPUT);
  pinMode(GREENPIN, OUTPUT);
  pinMode(BLUEPIN, OUTPUT);
}
 
 
void loop() {

        // send data only when you receive data:
        if (Serial.available() == 3) {
                // read the incoming byte:         
                byte r = Serial.read();
                byte g = Serial.read();
                byte b = Serial.read();
                analogWrite(REDPIN, r);
                analogWrite(GREENPIN, g);
                analogWrite(BLUEPIN, b);
//                int counter = 0;
//                while(counter <= 2)
//                {
//                  incomingByte = Serial.read();
//                  // say what you got:
//                  //Serial.print("Counter: ");
//                  //Serial.println(counter, DEC);
//                  //Serial.print("Read: ");
//                  //Serial.println(incomingByte, DEC);
//                  if (incomingByte == 0){
//                    counter += 1;
//                  }
//                  else{
//                    counter = 0;
//                  }
//                }
        }
}
 
//void loop() {
//  int r, g, b;
//  r = 0;
//  b = 0;
//  g = 0;
//  
//  
//  //if (Serial.available() >= 16)
//  //{
//    g = 100;
//    int counter = 0;
//    while(counter < 3)
//    {
//      //int check = Serial.parseInt();
//      //Serial.print(5);
//      //if (check == 0){
//      //  counter++;
//      //}
//      //else
//      //{
//      //  counter = 0;
//      //}
//    }
//    //r = Serial.parseInt();
//    //g = Serial.parseInt();
//    //b = Serial.parseInt();
//  //}
//  //else
//  //{
//  //  b = 100;
//  //}
//  analogWrite(REDPIN, r);
//  analogWrite(GREENPIN, g);
//  analogWrite(BLUEPIN, b);
//}
