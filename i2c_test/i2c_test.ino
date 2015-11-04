#include <Arduino.h>
#include <i2c_t3.h>

#define MPU9250_ADDRESS 0x69  // Device address when ADO = 1

#define WHO_AM_I_MPU9250 0x75 // Should return 0x71

#define RED_LED             15 // A1

void setup()
{
  Serial3.begin(57600);

  Serial3.println("\nSetup test");
  Serial3.flush();

  pinMode(RED_LED, OUTPUT);

  Wire.begin(I2C_MASTER, 0x00, I2C_PINS_18_19, I2C_PULLUP_EXT, I2C_RATE_100);
  //Wire.begin(I2C_MASTER, 0x00, I2C_PINS_18_19, I2C_PULLUP_INT, I2C_RATE_100);
}

void loop()
{
  static bool first = true;
  uint8_t res;
  uint8_t i_am = 0xAA;
  
  //if (first) {
    first = false;

    Wire.beginTransmission(MPU9250_ADDRESS);
    Wire.write(WHO_AM_I_MPU9250);
    res = Wire.endTransmission(I2C_NOSTOP);

    Serial3.print("res = ");
    Serial3.println(res, DEC);
    
    Wire.requestFrom(MPU9250_ADDRESS, 1);
    i_am = Wire.readByte();
    
    Serial3.print("i_am = ");
    Serial3.println(i_am, HEX);

    Serial3.println("Test done");
    Serial3.flush();
  //}

  delay(3000);
}

