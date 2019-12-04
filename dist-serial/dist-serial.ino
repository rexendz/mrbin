#define trig 4
#define echo 5

void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println(getDistance());
  delay(100);
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
