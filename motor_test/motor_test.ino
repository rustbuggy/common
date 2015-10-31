#include <Servo.h>

//#define serial Serial3 // XBee

//#define RED_LED             15 // A1

#define STEERING_PWM_PIN    4
#define DRIVE_PWM_PIN       3

Servo steeringservo;
Servo drivingservo;

bool first = true;

void setup()
{
  //pinMode(RED_LED, OUTPUT);
  //digitalWrite(RED_LED, HIGH);

  steeringservo.attach(STEERING_PWM_PIN);
  drivingservo.attach(DRIVE_PWM_PIN);

  steeringservo.write(90);
  drivingservo.write(95);
}

void loop()
{
  delay(1000);

  if (first)
  {
    first = false;
    drivingservo.write(95);
    //digitalWrite(RED_LED, LOW);
  }

  /*
  for (uint8_t i = 90; i >= 60; --i) {
   steeringservo.write(i);
   delay(100);
   }
   for (uint8_t i = 60; i <= 160; ++i) {
   steeringservo.write(i);
   delay(100);
   }
   for (uint8_t i = 160; i >= 90; --i) {
   steeringservo.write(i);
   delay(100);
   }
   */

  /*
  for (uint8_t i = 95; i <= 120; ++i) {
   drivingservo.write(i);
   delay(20);
   }
   for (uint8_t i = 120; i >= 95; --i) {
   drivingservo.write(i);
   delay(20);
   }
   */
}


