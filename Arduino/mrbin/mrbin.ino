/* TRIG1  4
 * ECHO1  5
 * SERVO  6
 * LED    7
 * BUZZER 8
 * RST    9
 * SDA   10
 * MOSI  11
 * MISO  12
 * SCK   13
 * TRIG2 A0
 * ECHO2 A1
 * TRIG3 A2
 * ECHO3 A3
 */

#include <MFRC522.h>
#include <Servo.h>
#define LED 7
#define BUZZER 8

Servo servo;
MFRC522 rfid(10, 9);

const int t1 = 4;
const int e1 = 5;
const int t2 = A0;
const int e2 = A1;
const int t3 = A2;
const int e3 = A3;

unsigned long timer = 0;
bool readStatus = false;
bool userAuthenticated = false;
char started;

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  servo.attach(6);
  SPI.begin();
  rfid.PCD_Init();
  for(int i = 0; i < 10; i++)
    Serial.write('\n');
  delay(5);
  digitalWrite(LED, LOW);
  servo.write(50);
}

void loop() {
  started = Serial.read();
  while(started == 'Y'){
    while(!readStatus){
      if(rfid.PICC_IsNewCardPresent()){
        if(rfid.PICC_ReadCardSerial()){
          byte uid[rfid.uid.size];
          if((millis() - timer) > 1000){
            for(int i = 0; i < rfid.uid.size; i++)
              uid[i] = rfid.uid.uidByte[i];
  
            for(int i = 0; i < sizeof(uid); i++){
              if(uid[i] < 0x10)
                Serial.print('0');
  
              Serial.print(uid[i], HEX);
            }
            Serial.println();
            readStatus = true;
            timer = millis();
            delay(100);
          }
          
        }
      }
    }
  
    if(readStatus){
      while(!Serial.available());
    
      char rx;
    
      while(Serial.available())
        rx = Serial.read();
      
      if(rx == 'O'){
      tone(BUZZER, 2500);
      delay(100);
      noTone(BUZZER);
      userAuthenticated = true;
      }
      else{
        tone(BUZZER, 1000);
        delay(50);
        noTone(BUZZER);
        delay(30);
        tone(BUZZER, 1000);
        delay(50);
        noTone(BUZZER);
        readStatus = false;
      }
    }
    
    while(userAuthenticated){
      char rx;
      rx = Serial.read();
      if(rx == 'X'){
        digitalWrite(LED, LOW);
        userAuthenticated = false;
        readStatus = false;
        started = 'N';
      }
      else if(rx == 'S'){
        for(int i = 50; i <= 120; i++){
          servo.write(i);
          delay(10);
        }
        delay(2000);
        for(int i = 120; i >= 50; i--){
          servo.write(i);
          delay(10);
        }
      }
      else{
        digitalWrite(LED, HIGH);
        double dist1 = getDistance(1);
        double dist2 = getDistance(2);
        double dist3 = getDistance(3);
        if((dist1 > 2 && dist1 <= 15) || (dist2 > 2 && dist2 <= 30) || (dist3 >2 && dist3 <= 30))
          Serial.println('O');
        delay(100);
      }
    }
  }
}

double getDistance(int sensor){
  float duration;
  int trig;
  int echo;
  switch(sensor){
    case 1:
    trig = t1;
    echo = e1;
    break;
    case 2:
    trig = t2;
    echo = e2;
    break;
    case 3:
    trig = t3;
    echo = e3;
    break;
  }
  
  pinMode(trig, OUTPUT);
  digitalWrite(trig, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);

  pinMode(echo, INPUT);
  duration = pulseIn(echo, HIGH);
  double distance = duration * 340/20000;
  delayMicroseconds(100);
  return distance;
}
