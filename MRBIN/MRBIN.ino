#include <LiquidCrystal_I2C.h>
#include <math.h>
double totalWidth = 20;
double totalLength = 40;

LiquidCrystal_I2C lcd(0x27, 16, 2);

// ULTRASONIC SENSORS
const int sensor1Trig = 2;
const int sensor1Echo = 3;
const int sensor2Trig = 4;
const int sensor2Echo = 5;
const int sensor3Trig = 6;
const int sensor3Echo = 7;
const int sensor4Trig = 8;
const int sensor4Echo = 9;

double volArray[20];
double samples[100];
int sampleCount = 0;

void setup(){
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("  INITIALIZING  ");
  lcd.setCursor(0, 1);
  lcd.print("  PLEASE  WAIT  ");
  for(int j = 0; j < 20; j++){
  for(int i = 1; i <= 4; i++)
    Serial.println(getDistance(i)); // warm up the sensors
  }

  mapDimensions(); // Get the exact dimensions of the container from the perspective of the sensors
  Serial.print("Total Length: ");
  Serial.print(totalLength);
  Serial.println("cm");
  Serial.print("Total Width: ");
  Serial.print(totalWidth);
  Serial.println("cm");
}

void loop(){
  scanObject(); // Method to get the volume and save it
  
  lcd.clear(); // Print these if there is no object inside the container
  lcd.setCursor(0, 0);
  lcd.print("  CONTAINER IS  ");
  lcd.setCursor(0, 1);
  lcd.print("     EMPTY!     ");
}

void mapDimensions(){
  double dist1, dist2, dist3, dist4;
  for(int i = 0; i < 10; i++){
    do{
      dist1 = getDistance(1);
    }while(dist1 <= 20 && dist1 > 18);
    do{
      dist2 = getDistance(2);
    }while(dist2 <= 20 && dist2 > 18);
    do{
      dist3 = getDistance(3);
    }while(dist3 <= 40 && dist3 > 38);
    do{
      dist4 = getDistance(4);
    }while(dist4 <= 40 && dist4 > 38);
  }
  dist1/=10;
  dist2/=10;
  dist3/=10;
  dist4/=10;
  totalWidth = (dist1+dist2)/2;
  totalLength = (dist3+dist4)/2;
}

void scanObject(){ // Get dimensions of the object inside the container (if any)
  int count = 0; // Number of scanning iteration
  double aveVol = 0; // Average volume calculated of an object (Formula based on a right cylinder model: V=πr2h)

  while(objectDetected() && count < 300){ // Keep on getting dimensions while there is an object in the container and count iteration is less than 300
    if(count == 0){ // Start of scanning iteration, lets user know that scanning is in progress
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("    SCANNING    ");
      lcd.setCursor(0, 1);
      lcd.print("  PLEASE  WAIT  ");
      delay(10);
    }
    
    while(count < 20) // Inserts first 20 data into the array
      volArray[count++] = getVolume();

    if(count >= 20){
      for(int i = 0; i < 19; i++) // Shifts the array to the left to make room for new datum
        volArray[i] = volArray[i+1];

      volArray[19] = getVolume(); // Insert new datum into the array
      count++; // Increment the scanning count
    }
    aveVol = 0; // Set aveVol to 0 for calculation of the average volume in the array

    for(int i = 0; i < 20; i++) // Sums all the 20 data from the array
      aveVol += volArray[i];

    aveVol /= 20; // Divides the sum by the total number of data to get the average volume

    if(count >= 99){ // Halfway through the scanning process, show the user the current average volume reading because why not
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Volume: ");
      lcd.print(aveVol);
      lcd.print("mL");
      delay(10);
    }
    if(count == 299){ // When the object scanning is finished
      samples[sampleCount++] = aveVol; // Save the current reading to samples for research purposes
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("    READING     ");
      lcd.setCursor(0, 1);
      lcd.print("    SUCCESS!!   ");
      delay(1000); // 5 seconds delay between scans
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("  FINAL VOLUME  ");
      lcd.setCursor(0, 1);
      lcd.print(aveVol);
      delay(4000);
    }
  }
}

bool objectDetected(){ // Checks if there is an object in the container
  double sensor1 = getDistance(1); // Get sensor1 distance
  double sensor2 = getDistance(2); // Get sensor2 distance
  if(sensor1 < (totalWidth-2) && sensor2 < (totalWidth-2)) // If there is an object blocking sensor1 and sensor2, then we can conclude that there IS an object in the container
    return true; // Return true indicating that there is an object in the container
  else
    return false; // Return false indicating that there isn't any object in the container
}

double getVolume(){ // VOLUME CALCULATION IS MODELED BASED ON A RIGHT CYLINDER (Which most PET bottles more or less are shaped)
  double sensor1 = getDistance(1); // WIDTH-side distance
  double sensor2 = getDistance(2); // WIDTH-side distance
  double sensor3 = getDistance(3); // LENGTH-side distance
  double sensor4 = getDistance(4); // LENGTH-side distance
  double diameter = totalWidth - (sensor1 + sensor2); // We can get the diameter of the object by subtracting the sum of the distances of the WIDTH-side sensors from the total width
  double radius = diameter/2; // We can then get the radius by simply dividing the diameter by 2
  double height = totalLength - (sensor3 + sensor4); // We can get the height of the object by subtracting the sum of the distances of the LENGTH-side sensors from the total length
  double volume = (M_PI)*(pow(radius, 2))*(height); // M_PI is a predefined constant in the math.h library which equals to the value of pi
  return volume;
}

double getDistance(int sensor){ // Get distance using ultrasonic sensor
  int trig, echo; // The active trig and echo pins
  switch(sensor){ // Switch through which sensor will be used (1-4)
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
    default: Serial.println("Error: Out of bounds");
  }
  pinMode(trig, OUTPUT); // Set the active trig pin as OUTPUT
  digitalWrite(trig, LOW);
  digitalWrite(echo, LOW);
  delayMicroseconds(2);
  
  digitalWrite(trig, HIGH); // Send out a 10 microsecond pulse in the trig pin
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  
  pinMode(echo, INPUT);
  double duration = pulseIn(echo, HIGH); // Count the time it took for the echo to detect the rising edge of the pulse
  double distance = duration * 340/20000; // Calculate the distance in centimeters
  delayMicroseconds(100); // Delay between scans
  return distance;
}
