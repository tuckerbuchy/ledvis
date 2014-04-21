#define BLUEPIN 6
#define GREENPIN 5
#define REDPIN 3

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
        }
}