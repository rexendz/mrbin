/* TRIG   4
 * ECHO   5
 * LED    7
 * BUZZER 8
 * RST    9
 * SDA   10
 * MOSI  11
 * MISO  12
 * SCK   13
 */

#include <MFRC522.h>
#define trig 4
#define echo 5
#define LED 7
#define BUZZER 8

MFRC522 rfid(10, 9);

unsigned long timer = 0;
bool readStatus = false;
bool userAuthenticated = false;

void setup() {
  pinMode(LED, OUTPUT);
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  for(int i = 0; i < 10; i++)
    Serial.write('\n');
  delay(5);
  digitalWrite(LED, LOW);
}

void loop() {
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
    digitalWrite(LED, HIGH);
    Serial.println(getDistance());
    delay(100);
  }
}

double getDistance(){
  float duration;
  
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
