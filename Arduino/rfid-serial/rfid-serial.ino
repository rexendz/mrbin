#include <MFRC522.h>
#define GREEN_LED 6
#define RED_LED 7
#define BUZZER 8

MFRC522 rfid(10, 9);

unsigned long timer = 0;
bool readStatus = false;

void setup() {
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  for(int i = 0; i < 10; i++)
    Serial.write('\n');
  delay(5);
  digitalWrite(RED_LED, HIGH);
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
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    tone(BUZZER, 2500);
    delay(100);
    noTone(BUZZER);
    readStatus = false;
    }
    else{
      digitalWrite(RED_LED, LOW);
      digitalWrite(GREEN_LED, LOW);
      tone(BUZZER, 1000);
      delay(50);
      noTone(BUZZER);
      delay(30);
      tone(BUZZER, 1000);
      delay(50);
      noTone(BUZZER);
      digitalWrite(RED_LED, HIGH);
      readStatus = false;
    }
  }
}
