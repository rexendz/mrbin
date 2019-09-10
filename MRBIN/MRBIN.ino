/*  9/4/19 12:44AM
 *  CODE       FOR
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

const int trigX1 = 2;
const int echoX1 = 3;
const int trigX2 = 4;
const int echoX2 = 5;
const int trigY1 = 6;
const int echoY1 = 7;
const int trigY2 = 8;
const int echoY2 = 9;

double volArr[20];

void setup() {
  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  for(int i = 1; i <= 4; i++){
    Serial.println(getDistance(i));
  }
  delay(1000);
}

void loop() {
  int count = 0;
  double aveVol = 0;
  
  while(objectDetected()){ // First checks if there is an object inside the container
    if(count < 20){
    do{
      volArr[count++] = getVolume(); // Inserts the first 20 data into the array
    }while(count < 20);
    }
    
    else{
    for(int i = 0; i < 19; i++) // Shifts the data to the left to make room for the new data
      volArr[i] = volArr[i+1]; 
      
    volArr[19] = getVolume(); // Insert the latest data into the array
    }
      aveVol = 0; // Resets aveVol for recalculation
    for(int i = 0; i < 20; i++) // Adds all the data
      aveVol += volArr[i];

    aveVol /= 20; // Divide the sum by the total number of data to get the average
    
    dispToLCD(aveVol); // Display the average volume
    
    delay(1);
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("  CONTAINER IS  ");
  lcd.setCursor(1, 0);
  lcd.print("     EMPTY!     ");
  
  delay(100);
}

void dispToLCD(double volume){
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Volume: ");
  lcd.print(volume);
  lcd.print(" mL");
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
  double d = totalLength - (((sensor1+sensor4)/2)+((sensor2+sensor3)/2));
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
    case 1: trig = trigX1;
            echo = echoX1;
            break;
    case 2: trig = trigX2;
            echo = echoX2;              
            break;
    case 3: trig = trigY1;
            echo = echoY1;
            break;
    case 4: trig = trigY2;
            echo = echoY2;              
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
