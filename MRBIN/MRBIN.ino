/*  CODE       FOR
 *  INITIAL DESIGN
 *  FOR THESIS  II
 *  BY: REX ENDOZO
 *   &  JR NAVARRO
 *
*/
#include <LiquidCrystal_I2C.h>

#define bottleHeight 20.5
#define totalWidth 40
#define totalLength 25

LiquidCrystal_I2C lcd(0x27, 16, 2);

bool debugSensors = false;

const int sensor1Trig = 2;
const int sensor1Echo = 3;

const int sensor2Trig = 4;
const int sensor2Echo = 5;

const int sensor3Trig = 6;
const int sensor3Echo = 7;

const int sensor4Trig = 8;
const int sensor4Echo = 9;

const int buttonPin1 = 10;
const int buttonPin2 = 11;

unsigned long timer1 = 0;
unsigned long timer2 = 0;
int lastButtonReading1 = LOW;
int lastButtonReading2 = LOW;
int buttonState1 = LOW;
int buttonState2 = LOW;

bool viewSamples = false;

double volArr[20];
double samples[10];
int sampleCount = 0;
int dispSample = 0;

void setup() {
  pinMode(buttonPin1, INPUT);
  pinMode(buttonPin2, INPUT);
  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  for(int i = 1; i <= 4; i++)
    Serial.println(getDistance(i)); // Test ultrasonic sensors
  delay(1000);
}

void loop() {
  if(debugSensors == true){
    Serial.print("Sensor 1: ");
    Serial.print(getDistance(1));
    Serial.println("cm");
  
   Serial.print("Sensor 2: ");
   Serial.print(getDistance(2));
   Serial.println("cm");
  
    Serial.print("Sensor 3: ");
    Serial.print(getDistance(3));
   Serial.println("cm");
  
    Serial.print("Sensor 4: ");
    Serial.print(getDistance(4));
    Serial.println("cm");
    
   delay(500);
  }
  
  else{
    int count = 0; // Ultrasonic sensor reading count
    double aveVol = 0; // Average volume of the object
    bool startScan = false; // Indicates if scanning of object is initialized or not
    bool readSuccess = false; // Indicates if scanning of object is successful or not
    
    while(objectDetected() && count < 500){ // First checks if there is an object inside the container
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("     OBJECT     ");
      lcd.setCursor(0, 1);
      lcd.print("    DETECTED!   ");
      
      int buttonReading1 = digitalRead(buttonPin1); // Save button reading
      
      if(buttonReading1 != lastButtonReading1) // If the current button reading is different from the last button reading
        timer1 = millis(); // Sets the timer to millis
        
      if((millis() - timer1) > 50){ // If the time the button has been pressed exceeds 50 milliseconds
        if(buttonReading1 != buttonState1){ // If the state of the button is different from the reading of the button
          buttonState1 = buttonReading1; // Sets the state of the button as the current reading of the button
          if(buttonReading1 == HIGH) // If the button is pressed down
            startScan = true; // Set startScan to TRUE
        }
      }
  
      if(startScan == true){ // If the user pressed the button to scan
        while(count < 20) //
         volArr[count++] = getVolume(); // Inserts the first 20 data into the array
      
      if(count >= 20){
        for(int i = 0; i < 19; i++) // Shifts the data to the left to make room for the new datum
          volArr[i] = volArr[i+1]; 
        
          volArr[19] = getVolume(); // Insert the latest data into the array
          count++;
      }
      
        aveVol = 0; // Resets aveVol for recalculation
        
        for(int i = 0; i < 20; i++) // Adds all the data
          aveVol += volArr[i];
  
      aveVol /= 20; // Divide the sum by the total number of data to get the average
      if(count < 399){
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("    SCANNING    ");
        lcd.setCursor(0, 1);
        lcd.print("  PLEASE  WAIT  ");
      }
      if(count >= 399)
        dispToLCD(aveVol); // Display the average volume
        
      if(count == 499){
        samples[sampleCount++] = aveVol;
        readSuccess = true;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("    READING     ");
        lcd.setCursor(0, 1);
        lcd.print("    SUCCESS!!   ");
        if(sampleCount > 9)
          sampleCount = 0;
        delay(5000);
      }
    }
    lastButtonReading1 = buttonReading1;
  }
  
  int buttonReading2 = digitalRead(buttonPin2);
  if(buttonReading2 != lastButtonReading2)
    timer2 = millis();
      
  if((millis() - timer2) > 50){
    if(buttonState2 != buttonReading2){
      buttonState2 = buttonReading2;
      if(buttonState2 == HIGH){
        if(viewSamples == false)
          dispSample = 0;
        else
          dispSample++;
         
        viewSamples = true;
        if(dispSample >= sampleCount)
          viewSamples = false;
      }
    }
  }
    /*
    for(int i = 0; i < 10; i++){
      Serial.print("Reading ");
      Serial.print(i+1);
      Serial.print(": ");
      Serial.print(samples[i]);
      Serial.println("mL");
    }
    */
    lastButtonReading2 = buttonReading2;

  if(viewSamples = true){
    if(sampleCount == 0){
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("  SAMPLES  ARE  ");
      lcd.setCursor(0, 1);
      lcd.print("     EMPTY!     ");
      delay(1000);
      viewSamples = false;
    }
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("    SAMPLE ");
    lcd.print(dispSample+1);
    lcd.print("    ");
    lcd.setCursor(0, 1);
    lcd.print("  ");
    lcd.print(samples[dispSample++]);
    lcd.print("mL");
  }
  else{
    if(readSuccess == false){
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("  CONTAINER IS  ");
      lcd.setCursor(0, 1);
      lcd.print("     EMPTY!     ");
    }
    delay(100);
    }
  }
}

void dispToLCD(double volume){
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Volume: ");
  lcd.print(volume);
  lcd.print("mL");
  delay(100);
}

bool objectDetected(){
  double dist1 = getDistance(1);
  double dist2 = getDistance(2);
  double dist3 = getDistance(3);
  double dist4 = getDistance(4);
  if(dist1 < 23.00 && dist2 < 23.00 && dist3 < 23.00 && dist4 < 23.00)
    return true;
  else
    return false;
}

double getVolume(){
  double sensor1 = getDistance(1);
  double sensor2 = getDistance(2);
  double sensor3 = getDistance(3);
  double sensor4 = getDistance(4);
  double d = totalLength - (((sensor1+sensor2)/2)+((sensor3+sensor4)/2));
  double h = bottleHeight;
  double r = d/2;
  double vol = (3.14)*(r*r)*(h);

  /*DEBUG
    Serial.print("Diameter: ");
    Serial.print(d);
    Serial.println("cm");
    Serial.print("Height: ");
    Serial.print(h);
    Serial.println("cm");
  */
  return vol;
}

double getDistance(int sensor){
  float duration; // Since the time of receiving the transmitted signal is usually in microseconds, we use float datatype to utilize alot of decimals
  int trig, echo;
  double distance;
  switch (sensor){ // Selects which sensor will be active
    case 1: trig = sensor1Trig;
            echo = sensor1Echo;
            break;
    case 2: trig = sensor2Trig;
            echo = sensor2Echo;              
            break;
    case 3: trig = sensor3Trig;
            echo = sensor3Echo;
            break;
    case 4: trig = sensor4Trig;
            echo = sensor4Echo;              
            break;
    default: Serial.print("Error");
    }
 pinMode(trig, OUTPUT); // Sets active trig pin to OUTPUT mode
 digitalWrite(trig, LOW);
 digitalWrite(echo, LOW); 
 delayMicroseconds(2);
 
 digitalWrite(trig, HIGH); // Send a HIGH signal to trig pin for 10 microseconds
 delayMicroseconds(10); 
 digitalWrite(trig, LOW); 
 
 pinMode(echo, INPUT); // Sets active echo pin to INPUT mode
 duration = pulseIn(echo, HIGH); // Waits for rising edge signal in echo pin and counts the duration(in uS) of which the 40khz signal is returned
 distance = duration * 340/20000; // To get the distance in cm: duration/2(us / 1000) = duration/2(ms) * 340m/s = meters/100 = centimeters
 delayMicroseconds(100); // We divide the duration by 2 as the time is doubled with the process of transmitting->reflect->receiving (RADAR principle)
 return distance; // Gives the distance value to whoever called this function
}

/* NOT USED
int getAverageDistance(int sensor){
  int totalDist;
  int currDist;
  totalDist = 0;
    for(int i= 0; i < 10; i++){
      do{
      currDist = getDistance(sensor);
      Serial.println(currDist);
      }while(currDist < 2 || currDist > 26);
      totalDist += currDist;
      delay(1);
}
  totalDist /= 10;
  return totalDist;
}
*/
