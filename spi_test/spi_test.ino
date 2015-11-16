#include <SPI.h>

#define SPI_SPEED 500000
#define IMU_CHIP_SELECT  10

#define MPU9250_WHO_AM_I            0x75

SPISettings m_SPISettings;

void setup() {
  Serial3.begin(57600);

  Serial3.println("\nSetup test");
  Serial3.flush();

  SPI.begin();
  pinMode(IMU_CHIP_SELECT, OUTPUT);
  m_SPISettings = SPISettings(SPI_SPEED, MSBFIRST, SPI_MODE0);
}

bool SPIRead(unsigned char regAddr, unsigned char length, unsigned char *data)
{
  SPI.beginTransaction(m_SPISettings);
  digitalWrite(IMU_CHIP_SELECT, LOW);
  SPI.transfer(regAddr | 0x80);
  for (int i = 0; i < length; i++)
    data[i] = SPI.transfer(0);
  digitalWrite(IMU_CHIP_SELECT, HIGH);
  SPI.endTransaction();
  return true;
}

void loop() {
  uint8_t result;
  SPIRead(MPU9250_WHO_AM_I, 1, &result);

  Serial3.print("result = ");
  Serial3.println(result, HEX);

  delay(3000);
}
